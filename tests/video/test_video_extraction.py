""" Test facial feature extraction class and methods """

import json
import os
import numpy as np
import platform
import pytest
from moviepy.editor import VideoFileClip
from mexca.video.extraction import FaceExtractor


class TestFaceExtractor:
    extractor = FaceExtractor(min_clusters=1, max_clusters=4)
    filepath = os.path.join(
        'tests', 'test_files', 'test_video_multi_5_frames.mp4'
    )
    with open(os.path.join(
            'tests', 'reference_files', 'features_video_multi_5_frames.json'
        ), 'r', encoding="utf-8") as file:
        features = json.loads(file.read())


    def test_detect(self):
        with VideoFileClip(self.filepath, audio=False) as clip:
            features = {
                'face_box': [],
                'face_prob': []
            }
            for frame in clip.iter_frames():
                _, boxes, probs = self.extractor.detect(frame)
                for box, prob in zip(boxes, probs):
                    features['face_box'].append(box.tolist())
                    features['face_prob'].append(prob)

            assert np.array(features['face_box']).shape == np.array(self.features['face_box']).shape
            assert features['face_prob'] == self.features['face_prob']


    def test_identify(self):
        with VideoFileClip(self.filepath, audio=False) as clip:
            embeddings = []
            for frame in clip.iter_frames():
                faces, _, _ = self.extractor.detect(frame)
                embs = self.extractor.encode(faces)

                for emb in embs:
                    embeddings.append(emb)

            labels = self.extractor.identify(np.array(embeddings)).tolist()

            assert labels == self.features['face_id']


    def test_extract(self):
        with VideoFileClip(self.filepath, audio=False) as clip:
            features = {
                'face_landmarks': [],
                'face_aus': []
            }
            for frame in clip.iter_frames():
                _, boxes, _ = self.extractor.detect(frame)
                landmarks, aus = self.extractor.extract(frame, boxes)
                landmarks_np = np.array(landmarks).squeeze()
                for landmark, au in zip(landmarks_np, aus):
                    features['face_landmarks'].append(landmark)
                    features['face_aus'].append(au)

            assert np.array(features['face_landmarks']).shape == np.array(self.features['face_landmarks']).shape
            assert np.array(features['face_aus']).shape == np.array(self.features['face_aus']).shape


    # @pytest.mark.skipif(
    #    platform.system() == 'Windows',
    #    reason='VMs run out of memory on windows'
    # )
    def test_apply(self): # Tests JAANET AU model
        features = self.extractor.apply(self.filepath, show_progress=False)
        assert features['frame'] == self.features['frame']
        assert features['time'] == self.features['time']
        assert np.array(features['face_box']).shape == np.array(self.features['face_box']).shape
        assert features['face_prob'] == self.features['face_prob']
        assert features['face_id'] == self.features['face_id']
        assert np.array(features['face_landmarks']).shape == np.array(self.features['face_landmarks']).shape
        assert np.array(features['face_aus']).shape == np.array(self.features['face_aus']).shape


    # @pytest.mark.skipif(
    #     platform.system() == 'Windows',
    #     reason='VMs run out of memory on windows'
    # )
    def test_pyfeat_svm(self): # Tests SVM AU model
        svm_extractor = FaceExtractor(au_model='svm')
        features = svm_extractor.apply(self.filepath, show_progress=False)

        assert np.array(features['face_aus']).shape == np.array(self.features['face_aus_svm']).shape


    # @pytest.mark.skipif(
    #     platform.system() == 'Windows',
    #     reason='VMs run out of memory on windows'
    # )
    def test_pyfeat_logistic(self): # Tests logistic AU model
        svm_extractor = FaceExtractor(au_model='logistic')
        features = svm_extractor.apply(self.filepath, show_progress=False)

        assert np.array(features['face_aus']).shape == np.array(self.features['face_aus_logistic']).shape
