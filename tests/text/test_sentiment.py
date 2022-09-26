""" Test audio sentiment extraction classes and methods """

import platform
import pytest
from spacy.language import Vocab
from spacy.tokens import Doc
from mexca.text.sentiment import SequenceClassifier, SentimentExtractor


@pytest.mark.skipif(
    platform.system() in ['Windows', 'Linux'],
    reason='VMs run out of memory on Windows and Linux'
)
class TestSequenceClassifier:
    # Inititating the object causes memory issues on Windows and Linux
    if platform.system() not in ['Windows', 'Linux']:
        classifier = SequenceClassifier("cardiffnlp/twitter-xlm-roberta-base-sentiment")
        text = 'Today was a good day!'
        reference = [0.01545323, 0.06419527, 0.9203513]

    def test_properties(self):
        with pytest.raises(TypeError):
            self.classifier.model = 3.0

        with pytest.raises(TypeError):
            self.classifier.tokenizer = 'k'

        with pytest.raises(TypeError):
            self.classifier.classifier = 'k'


    def test_apply(self):
        scores = self.classifier.apply(self.text)
        assert pytest.approx(scores[0].tolist()) == self.reference


@pytest.mark.skipif(
    platform.system() in ['Windows', 'Linux'],
    reason='VMs run out of memory on Windows and Linux'
)
class TestSentimentExtractor:
    # Inititating the object causes memory issues on Windows and Linux
    if platform.system() not in ['Windows', 'Linux']:
        extractor = SentimentExtractor()
        doc = Doc(
            Vocab(),
            words=['Today', 'was', 'a', 'good', 'day', '!'],
            spaces=[True, True, True, True, False, False],
            sent_starts=[True, False, False, False, False, False]
        )
        reference = [0.01545323, 0.06419527, 0.9203513]

    def test_properties(self):
        with pytest.raises(TypeError):
            self.extractor.roberta = 'k'


    def test_apply(self):
        sentiment = self.extractor.apply(self.doc)
        assert pytest.approx(sentiment[0].tolist()) == self.reference
