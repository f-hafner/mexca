
# Multimodal Emotion Expression Capture Amsterdam



[![github license badge](https://img.shields.io/github/license/mexca/mexca)](https://github.com/mexca/mexca)
[![RSD](https://img.shields.io/badge/rsd-mexca-00a3e3.svg)](https://research-software-directory.org/software/mexca)
[![read the docs badge](https://readthedocs.org/projects/pip/badge/)](https://mexca.readthedocs.io/en/latest/index.html)
[![fair-software badge](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-yellow)](https://fair-software.eu)
[![workflow scq badge](https://sonarcloud.io/api/project_badges/measure?project=mexca_mexca&metric=alert_status)](https://sonarcloud.io/dashboard?id=mexca_mexca)
[![workflow scc badge](https://sonarcloud.io/api/project_badges/measure?project=mexca_mexca&metric=coverage)](https://sonarcloud.io/dashboard?id=mexca_mexca)
[![build](https://github.com/mexca/mexca/actions/workflows/build.yml/badge.svg)](https://github.com/mexca/mexca/actions/workflows/build.yml)
[![cffconvert](https://github.com/mexca/mexca/actions/workflows/cffconvert.yml/badge.svg)](https://github.com/mexca/mexca/actions/workflows/cffconvert.yml)
[![markdown-link-check](https://github.com/mexca/mexca/actions/workflows/markdown-link-check.yml/badge.svg)](https://github.com/mexca/mexca/actions/workflows/markdown-link-check.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6962473.svg)](https://doi.org/10.5281/zenodo.6962473)
[![docker build badge](https://img.shields.io/static/v1?label=docker&message=mexca&color=blue&style=flat&logo=docker)](https://hub.docker.com/repository/docker/mluken/mexca)

<div align="center">
<img src="mexca_logo.png">
</div>

Mexca is an open-source Python package which aims to capture emotion expression cues in human faces and speech by combining visual and auditory modalities (video/audio). 

## How To Use Mexca

Mexca provides a customizable yet easy-to-use pipeline for extracting emotion expression features from videos. It contains building blocks that can be used to extract features for individual modalities (i.e., facial expressions, voice, and dialogue/spoken text). The blocks can also be integrated into a single pipeline to extract the features from all modalities at once. Next to extracting features, mexca can also identify the speakers shown in the video by clustering speaker and face representations. This allows users to compare emotion expressions across speakers, time, and contexts.  

Please cite mexca if you use it for scientific or commercial purposes.

- Lüken, M., & Viviani, E. (2022). mexca: Capture emotion expressions from multiple modalities in videos (Version 1.0.0) [Computer software]. https://doi.org/10.5281/zenodo.6962473


## Installation
Mexca supports Python >=3.7 and Python <= 3.9. We recommend installing mexca via the terminal/command prompt.

### Installation Steps on Windows
Open the terminal/command prompt (by right-clicking the Windows icon in the bottom-left corner of your screen, or with the keyboard shortcut `Windows Key` + `X`). We recommend to install mexca in a new virtual environment, e.g., using `venv`, so type the following in the terminal:

```console
python3 -m venv mexca-venv
env/bin/activate
```

Alternatively, if you use conda:

```console
conda create -n mexca-venv
conda activate mexca-venv
```
Once you have activated your virtual environment (mexca-venv) you can then install mexca from PyPi:

```console
python3 -m pip install mexca
```

To install mexca from the GitHub repository, do:

```console
git clone https://github.com/mexca/mexca.git
cd mexca
python3 -m pip install .
```

Or via:

```console
python3 -m pip install git+https://github.com/mexca/mexca.git
```

### Installation Steps on Unix/macOS
Open the terminal (click the Launchpad icon in the Dock, type “Terminal” in the search field; otherwise, you can use the keyboard shortcut `Command` + `Space`, and type in “Terminal”).

We recommend to install mexca in a new virtual environment, e.g., using `venv`, so type the following within the terminal:

```console
python3 -m venv mexca-venv
source env/bin/activate
```

Alternatively, if you use conda:

```console
conda create -n mexca-venv
conda activate mexca-venv
```

Once you have activated your virtual environment (mexca-venv) you can then install mexca from PyPi:

```console
python3 -m pip install mexca
```

To install mexca from the GitHub repository, do:

```console
git clone https://github.com/mexca/mexca.git
cd mexca
python3 -m pip install .
```

Or via:

```console
python3 -m pip install git+https://github.com/mexca/mexca.git
```

#### Issues installing mexca for M1 Macbook users

Many deep learning libraries that we import in mexca do not fully support the Apple M1 yet, which can lead to several issues when installing mexca. We provide few workarounds for the most common issues. They have been tested on Python 3.9.0 in a conda environment (last update 3/10/2022).

Error n. 1: 

- OSError cannot load libsndfile.dylib (Github issue [#311](https://github.com/bastibe/python-soundfile/pull/311)):

```console
OSError: cannot load library '...venv/lib/python3.9/site-packages/_soundfile_data/libsndfile.dylib': dlopen(...venv/lib/python3.9/site-packages/_soundfile_data/libsndfile.dylib, 2): image not found
```

To fix this:

1. Make sure that you have installed libsndfile via brew, if not [install it](https://formulae.brew.sh/formula/libsndfile). 
2. Copy the libsndfile installed from Homebrew (/opt/homebrew/lib/_soundfile_data/libsndfile.dylib) into the expected folder ‘python3.9/site-packages/_soundfile_data/‘ 
3. Restart the kernel.

Error n. 2: 

- OSError cannot load libllvmlite.dylib (Github issue [#650](https://github.com/numba/llvmlite/issues/650)):

```console
OSError: Could not load shared object file: libllvmlite.dylib
```

To fix this:

1. Type in the terminal:

```console
conda install -c numba numba
conda install -c numba llvmlite
```

2. Restart the kernel.

*TIP:* Make sure to run those fixes in the terminal, or in the jupyter notebook in a cell preceded by the symbol '!'. Make sure that the activated environment you're running the fixes is the one where you are attempting to install mexca (i.e., if you followed the installation steps above, it will be 'mexca-venv').

## Getting Started

If you would like to learn how to use mexca, the best place to start is our [demo](https://github.com/mexca/mexca/tree/main/examples) tutorial. Note that the demo runs in a [jupyter notebook](https://jupyter.org/). Jupyter lets users easily combine markdown text with executable Python code on a canvas called 'notebook'. For installing jupyter, and using the notebook please refer to the [official installation guide](https://docs.jupyter.org/en/latest/install/notebook-classic.html).

*Note*: mexca builds on pretrained models from the pyannote.audio package. Since release 2.1.1, downloading the pretrained models requires the user to accept two user agreements on Hugging Face hub and generate an authentication token. Therefore, to run the mexca pipeline, please accept the user agreements on [here](https://huggingface.co/pyannote/speaker-diarization) and [here](https://huggingface.co/pyannote/segmentation). Then, generate an authentication token [here](https://huggingface.co/settings/tokens). Use this token to login to Hugging Face hub by running `notebook_login()` (from a jupyter notebook) or `huggingface-cli login` (from the command line). You only need to login when running mexca for the first time. See this [link](https://huggingface.co/docs/hub/models-adding-libraries) for details.

Emotion expression features can be extracted with mexca using the following lines of code:

```python
from mexca.core.pipeline import Pipeline

# Path to video file (consider using os.path.join())
filename = 'path/to/video'

# Create pipeline object from default constructor method
pipeline = Pipeline().from_default(language='english')

# Apply pipeline to video file (may take a long time depending on video length)
output = pipeline.apply(filename)
```

Mexca's pipeline returns a `Multimodal` object that contains the extracted emotion expression features in the `feature` attribute. We can convert the features into a `pandas.DataFrame` for further inspection and processing.

```python
df = pd.DataFrame(output.features)
df
```

This is what the output looks like:

|      |   frame |   time | face_box                                          |   face_prob | face_landmarks                | face_aus                                                               |   face_id |   pitchF0 |   segment_id |   segment_start |   segment_end | track   | speaker_id   |   text_token_id | text_token               |   text_token_start |   text_token_end |   match_id |
|-----:|--------:|-------:|:--------------------------------------------------|------------:|:------------------------------|:-----------------------------------------------------------------------|----------:|----------:|-------------:|----------------:|--------------:|:--------|:-------------|----------------:|:-------------------------|-------------------:|-----------------:|-----------:|
|   0 |      0 |   0.52 | [254.80342   52.627777 339.73337  162.48317]     |    0.999263 | [253.81114993 106.13823438]   | [1.7722143e-01 9.6993530e-01 3.4657875e-03 5.7775569e-01 ...] |         7 |  114.05050 |            1 |        0.497812 |       21.0178 | 0       | SPEAKER_00   |               0 |       is                  |               0.52    |             0.60    |          1 |
|   1 |      1 |   0.56 | [255.26508  52.85576 339.82748 162.45255]         |    0.999143 | [254.09605609 106.21201348]   | [1.7896292e-01 9.6784592e-01 3.4994783e-03 5.6765985e-01 ...] |         7 |  117.58867 |            1 |        0.497812 |       21.0178 | 0       | SPEAKER_00   |               0 |       is                  |               0.52    |             0.60    |          1 |

## Structure and Performance

Currently, mexca includes three independent submodules (video, audio and text). The `core` module is responsible for running a single pipeline which calls in turn all the other submodules.

The video submodule supports the extraction of facial features (e.g., facial landmarks, action units). It relies on [pyfeat](https://py-feat.org/pages/intro.html)[^1] and [facenet-pytorch](https://github.com/timesler/facenet-pytorch)[^2]. It includes the following components:

- Face detection with Multi-task Convolutional Neural Network (MTCNN; 0.95 on FDDB; 0.85 on WIDER FACE easy, 0.82 on medium, 0.61 on hard data subset; all AUC).
- Face identification with Inception ResNet v1 (supervised: Acc = 0.9965 on LFW dataset when trained on VGGFace2).
- Landmark detection (6.41$for Feat-PFLD; 6.00 for Feat-MobileFaceNet; 5.23 for Feat-MobileNet; all RMSE on 300W dataset).
- Action unit detection (0.22 for Feat-JaaNET; 0.52 for Feat-Logistic; 0.57 for Feat-SVM; all average F1 on DisfaPlus dataset; Feat-RF is currently not available).

The audio module relies on [praat-parselmouth](https://github.com/YannickJadoul/Parselmouth)[^3] for voice pitch analysis, and on [pyannote.audio](https://github.com/pyannote/pyannote-audio) for speaker diarization[^4]. It includes the following components:

- Voice pitch as fundamental frequency (F0).
- Speaker diarization with ECAPA-TDNN model (supervised: 2.65 with known # of speakers; 3.01 with estimated # of speakers; unsupervised: 18.2 with estimated # of speakers; all DER on AMI Mix-Headset only words test dataset).

The text module supports text transcriptions for Dutch and English audio files. It relies on a pre-trained model made available by [HuggingSound](https://github.com/jonatasgrosman/huggingsound) that is the wav2vec-large model[^5] fine-tuned on Dutch (WER = 15.7; CER = 5.4 on Common Voice nl test set) and English (WER = 19.1; CER = 7.7 on Common Voice en test set).


## Documentation

The documentation of mexca can be found on [Read the Docs](https://mexca.readthedocs.io/en/latest/index.html).

## Contributing

If you want to contribute to the development of mexca,
have a look at the [contribution guidelines](CONTRIBUTING.md).

## License

The code is licensed under the Apache 2.0 License. This means that mexca can be used, modified and redistributed for free, even for commercial purposes.

## Credits

Mexca is being developed by the [Netherlands eScience Center](https://www.esciencecenter.nl/) in collaboration with the [Hot Politics Lab](http://www.hotpolitics.eu/) at the University of Amsterdam.

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [NLeSC/python-template](https://github.com/NLeSC/python-template).

[^1]: Cheong, J. H., Xie, T., Byrne, S., & Chang, L. J. (2021). Py-feat: Python facial expression analysis toolbox. *arXiv*. https://doi.org/10.48550/arXiv.2104.03509

[^2]: Schroff, F., Kalenichenko, D., & Philbin, J. (2015). FaceNet: A unified embedding for face recognition and clustering. *arXiv*. https://doi.org/10.48550/arXiv.1503.03832

[^3]: Jadoul, Y., Thompson, B., & de Boer, B. (2018). Introducing Parselmouth: A Python interface to Praat. Journal of Phonetics, 71, 1-15. https://doi.org/10.1016/j.wocn.2018.07.001

[^4]: Bredin, H., & Laurent, A. (2021). End-to-end speaker segmentation for overlap-aware resegmentation. *arXiv*. https://doi.org/10.48550/arXiv.2104.04045

[^5]: Schneider, S., Baevski, A., Collobert, R., & Auli, M. (2019). wav2vec: Unsupervised pre-training for speech recognition. *arXiv*. https://doi.org/10.48550/arXiv.1904.05862
