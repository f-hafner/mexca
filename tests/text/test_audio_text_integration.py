""" Test Audio text integration classes and methods """

import json
import os
import pytest
from mexca.core.exceptions import TimeStepError
from mexca.text.transcription import AudioTextIntegrator, AudioTranscriber, TextRestaurator, SentimentExtractor


class TestAudioTextIntegration:
    audio_text_integrator = AudioTextIntegrator(
        audio_transcriber=AudioTranscriber(language='dutch'),
        text_restaurator=TextRestaurator(),
        sentiment_extractor=SentimentExtractor()
    )
    filepath = os.path.join('tests', 'test_files', 'test_dutch_5_seconds.wav')

    # reference output
    with open(
        os.path.join('tests', 'reference_files', 'reference_dutch_5_seconds.json'),
        'r', encoding="utf-8") as file:
        text_audio_transcription = json.loads(file.read())


    def test_properties(self):
        with pytest.raises(TypeError):
            self.audio_text_integrator.audio_transcriber = 'k'

        with pytest.raises(ValueError):
            self.audio_text_integrator.time_step = -2.0

        with pytest.raises(TypeError):
            self.audio_text_integrator.time_step = 'k'


    def test_apply(self):
        with pytest.raises(TypeError):
            out  = self.audio_text_integrator.apply(self.filepath, 'k')

        out  = self.audio_text_integrator.apply(self.filepath, self.text_audio_transcription['time'])
        assert all(out['text_token_id'] == self.text_audio_transcription['text_token_id'])
        assert [token in ['', 'maak', 'en', 'er', 'groen', 'als'] for token in out['text_token']]
        assert all(out['text_token_start'] == self.text_audio_transcription['text_token_start'])
        assert all(out['text_token_end'] == self.text_audio_transcription['text_token_end'])


    def test_apply_error(self):
        with pytest.raises(TimeStepError):
            self.audio_text_integrator.apply(self.filepath, time=None)
