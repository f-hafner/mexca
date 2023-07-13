"""Action unit (AU) relationship-aware node feature learning (ANFL).

Implementation of the ANFL module from the paper:

    Luo, C., Song, S., Xie, W., Shen, L., Gunes, H. (2022). Learning multi-dimentionsal edge
    feature-based AU relation graph for facial action unit recognition. *arXiv*.
    `<https://arxiv.org/pdf/2205.01782.pdf>`_

Code adapted from the `OpenGraphAU <https://github.com/lingjivoo/OpenGraphAU/tree/main>`_ code base
(licensed under Apache 2.0).

"""

# pylint: disable=invalid-name

import math

import torch
from torch import nn

from mexca.video.helper_classes import AUPredictor, LinearBlock


class GNN(nn.Module):
    """Apply a graph neural network (GNN) layer.

    Transform action unit (AU) features using digraph connectivity.
    Inputs and outputs correspond to AU features.

    Parameters
    ----------
    in_features: int
        Size of each input sample.
    n_nodes: int
        Number of nodes in the digraph.
    n_neighbors: int, default=4
        Number of top K similar neighbors for computing graph connectivity.

    Notes
    -----
    See eq. 1 in the corresponding `paper <https://arxiv.org/abs/2205.01782>`_.
    Functions :math:`{g, r}` are linear and the nonlinear activation function :math:`\\sigma` is ReLU.
    Linear layer weights are initialized with :math:`N(0, \\sqrt{\\frac{2}{out\\_features}})`.
    Batch norm weights are initialized as 1 and biases as 0.

    """

    def __init__(self, in_features: int, n_nodes: int, n_neighbors: int = 4):
        super().__init__()
        self.in_features = in_features
        self.n_nodes = n_nodes
        self.n_neighbors = n_neighbors

        # Layers
        self.linear_u = nn.Linear(self.in_features, self.in_features)
        self.linear_v = nn.Linear(self.in_features, self.in_features)
        self.bnv = nn.BatchNorm1d(n_nodes)
        self.relu = nn.ReLU()

        # Param init
        self.linear_u.weight.data.normal_(0, math.sqrt(2.0 / self.in_features))
        self.linear_v.weight.data.normal_(0, math.sqrt(2.0 / self.in_features))
        self.bnv.weight.data.fill_(1)
        self.bnv.bias.data.zero_()

    @staticmethod
    def _calc_adj_mat(x: torch.Tensor, k: int) -> torch.Tensor:
        # Calculate adjacency matrix between nodes as thresholded dot product similarity
        b, n, _ = x.shape
        sim = x.detach()
        # Calc dot product
        sim = torch.einsum("b i j, b j k -> b i k", sim, sim.transpose(1, 2))
        # Get top k similar nodes
        threshold = sim.topk(k=k, dim=-1, largest=True)[0][:, :, -1].view(
            b, n, 1
        )
        adj_mat = (sim >= threshold).float()
        return adj_mat

    @staticmethod
    def _normalize_digraph(adj_mat: torch.Tensor) -> torch.Tensor:
        # Normalize adjacency matrix to 0 and 1 by sqrt(degree)
        b, n, _ = adj_mat.shape
        node_degrees = adj_mat.detach().sum(dim=-1)
        degs_inv_sqrt = node_degrees**-0.5
        norm_degs_matrix = torch.eye(n)
        dev = adj_mat.get_device()

        if dev >= 0:
            norm_degs_matrix = norm_degs_matrix.to(dev)

        norm_degs_matrix = norm_degs_matrix.view(1, n, n) * degs_inv_sqrt.view(
            b, n, 1
        )
        norm_adj_mat = torch.bmm(
            torch.bmm(norm_degs_matrix, adj_mat), norm_degs_matrix
        )

        return norm_adj_mat

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Calc adjacency matrix (0, 1)
        adj_mat = self._calc_adj_mat(x, self.n_neighbors)
        # Calc connectivity matrix
        con_mat = self._normalize_digraph(adj_mat)
        # eq. 1
        aggregate = torch.einsum(
            "b i j, b j k -> b i k", con_mat, self.linear_v(x)
        )
        x = self.relu(x + self.bnv(aggregate + self.linear_u(x)))
        return x


class AUFeatureGenerator(nn.Module):
    """Generate action unit (AU) features.

    Inputs correspond to face representations (embeddings) and outputs to AU features.

    Parameters
    ----------
    in_features: int
        Size of each input sample.
    out_features: int, default=27
        Size of each output sample.

    Notes
    -----
    AU specific features are generated by individual linear and global average pooling transformations.

    """

    def __init__(self, in_features: int, out_features: int = 27):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        # FC layers
        self.main_node_linear_layers = nn.ModuleList(
            [
                LinearBlock(self.in_features, self.in_features)
                for _ in range(self.out_features)
            ]
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Linear FC layers
        x = [layer(x).unsqueeze(1) for layer in self.main_node_linear_layers]
        x = torch.cat(x, dim=1)
        # Global average pooling
        x = x.mean(dim=-2)
        return x


class FacialGraphGenerator(AUPredictor):
    """Generate action unit (AU) activations from AU features using a facial graph.

    Inputs correspond to AU features and outputs to AU activations. Main plus sub nodes represent facial AUs.
    Sub nodes represent left and right activations of AUs 1, 2, 4, 6, 10, 12, and 14.

    Parameters
    ----------
    in_features: int
        Size of each input sample.
    n_main_nodes: int, default=27
        Number of main nodes in the facial graph.
    n_sub_nodes: int, default=14
        Number of sub nodes in the facial graph.
    n_neighbors: int, default=4
        Number of top K similar neighbors for computing graph connectivity.

    Notes
    -----
    First applies a graph neural network (:func:`GNN`) transformation to AU features.
    Transformed features are fed into similarity calculating (SC) layers for main and sub
    nodes as in eq. 2 of the corresponding `paper <https://arxiv.org/abs/2205.01782>`_.
    Sub node activations are calulated based on matching main node features.
    SC layer weights are initialized using Glorot initialization (see :func:`torch.nn.init.xavier_uniform`).

    """

    def __init__(
        self,
        in_features: int,
        n_main_nodes: int = 27,
        n_sub_nodes: int = 14,
        n_neighbors: int = 4,
    ):
        super().__init__(in_features, n_main_nodes, n_sub_nodes)

        # Layers
        self.gnn = GNN(
            self.in_features, self.n_main_nodes, n_neighbors=n_neighbors
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        f_v = self.gnn(x)
        # Predict action unit activations
        return super().forward(f_v)


class ANFL(nn.Module):
    """Apply AU relationship-aware node feature learning (ANFL).

    Transform face representations into facial action unit (AU) activations.
    Inputs correspond to facial representations (embeddings) and outputs to AU activations.

    Parameters
    ----------
    in_features: int
        Size of each input sample.
    n_main_aus: int, default=27
        Number of main AUs.
    n_sub_aus: int, default=14
        Number of sub AUs.
    n_neighbors: int, default=4
        Number of top K similar neighbors for computing graph connectivity.

    Notes
    -----
    First generates AU features from face representations (see :func:`AUFeatureGenerator`)
    and then transforms them into activations using a facial graph (see :func:`FacialGraphGenerator`).

    """

    def __init__(
        self,
        in_features: int,
        n_main_aus: int = 27,
        n_sub_aus: int = 14,
        n_neighbors: int = 4,
    ):
        super().__init__()
        self.in_features = in_features
        self.n_main_aus = n_main_aus
        self.n_sub_aus = n_sub_aus
        self.n_neighbors = n_neighbors

        # Modules
        self.afg = AUFeatureGenerator(self.in_features, self.n_main_aus)
        self.fgg = FacialGraphGenerator(
            self.in_features, self.n_main_aus, self.n_sub_aus, self.n_neighbors
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.afg(x)
        x = self.fgg(x)

        return x
