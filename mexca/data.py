"""Objects for storing multimodal data.
"""

import json
import sys
from dataclasses import asdict, dataclass, field, fields
from datetime import timedelta
from functools import reduce
from typing import Any, Dict, List, Optional, TextIO, Union
import numpy as np
import pandas as pd
import srt
from intervaltree import Interval, IntervalTree


@dataclass
class VideoAnnotation:
    """Video annotation class for storing facial features.

    Parameters
    ----------
    frame : list, optional
        Index of each frame.
    time : list, optional
        Timestamp of each frame in seconds.
    face_box : list, optional
        Bounding box of a detected face. Is `numpy.nan` if no face was detected.
    face_prob : list, optional
        Probability of a detected face. Is `numpy.nan` if no face was detected.
    face_landmarks : list, optional
        Facial landmarks of a detected face. Is `numpy.nan` if no face was detected.
    face_aus : list, optional
        Facial action unit activations of a detected face. Is `numpy.nan` if no face was detected.
    face_label : list, optional
        Label of a detected face. Is `numpy.nan` if no face was detected.
    face_confidence : list, optional
        Confidence of the `face_label` assignment. Is `numpy.nan` if no face was detected or
        only one face label was assigned.

    """
    frame: Optional[List[int]] = field(default_factory=list)
    time: Optional[List[float]] = field(default_factory=list)
    face_box: Optional[List[List[float]]] = field(default_factory=list)
    face_prob: Optional[List[float]] = field(default_factory=list)
    face_landmarks: Optional[List[List[List[float]]]] = field(default_factory=list)
    face_aus: Optional[List[List[float]]] = field(default_factory=list)
    face_label: Optional[List[Union[str, int]]] = field(default_factory=list)
    face_confidence: Optional[List[float]] = field(default_factory=list)


    @classmethod
    def _from_dict(cls, data: Dict):
        field_names = [f.name for f in fields(cls)]
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)


    @classmethod
    def from_json(cls, filename: str):
        """Load a video annotation from a JSON file.

        Parameters
        ----------
        filename: str
            Name of the JSON file from which the object should be loaded.
            Must have a .json ending.

        """
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return cls._from_dict(data=data)


    def write_json(self, filename: str):
        """Write the video annotation to a JSON file.

        Arguments
        ---------
        filename: str
            Name of the destination file. Must have a .json ending.

        """
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(asdict(self), file, allow_nan=True)


@dataclass
class VoiceFeatures:
    """Class for storing voice features.

    Features are stored as lists (like columns of a data frame).
    Optional features are initialized as empty lists.

    Parameters
    ----------
    frame: list
        The frame index for which features were extracted.
    time: list
        The time stamp at which features were extracted.
    pitch_f0: list, optional
        The voice pitch measured as the fundamental frequency F0.

    """
    frame: List[int]
    time: List[float]
    pitch_f0: Optional[List[float]] = field(default_factory=list)


    @classmethod
    def _from_dict(cls, data: Dict):
        field_names = [f.name for f in fields(cls)]
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered_data)


    @classmethod
    def from_json(cls, filename: str):
        """Load voice features from a JSON file.

        Parameters
        ----------
        filename: str
            Name of the JSON file from which the object should be loaded.
            Must have a .json ending.

        """
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return cls._from_dict(data=data)


    def write_json(self, filename: str):
        """Store voice features in a JSON file.

        Arguments
        ---------
        filename: str
            Name of the destination file. Must have a .json ending.

        """
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(asdict(self), file, allow_nan=True)


def _get_rttm_header() -> List[str]:
    return ["type", "file", "chnl", "tbeg", 
            "tdur", "ortho", "stype", "name", 
            "conf"]


@dataclass
class SegmentData:
    """Class for storing speech segment data

    Parameters
    ----------
    filename : str
        Name of the file from which the segment was obtained.
    channel : int
        Channel index.
    name : str, optional, default=None
        Speaker label.
    conf : float, optional, default=None
        Confidence of speaker label.

    """
    filename: str
    channel: int
    name: Optional[str] = None
    conf: Optional[float] = None


class SpeakerAnnotation(IntervalTree):
    """Class for storing speaker and speech segment annotations.

    Stores speech segments as ``intervaltree.Interval`` in an ``intervaltree.IntervalTree``.
    Speaker labels are stored in `SegmentData` objects in the `data` attribute of each interval.

    """
    def __str__(self, end: str = "\t", file: TextIO = sys.stdout, header: bool = True):
        if header:
            for h in _get_rttm_header():
                print(h, end=end, file=file)

            print("", file=file)

        for seg in self.items():
            for col in (
                "SPEAKER", seg.data.filename, seg.data.channel, seg.begin, seg.end,
                None, None, None, seg.data.name, seg.data.conf
            ):
                if col is not None:
                    if isinstance(col, float):
                        col = round(col, 2)
                    print(col, end=end, file=file)
                else:
                    print('<NA>', end=end, file=file)

            print("", file=file)

        return ""


    @classmethod
    def from_pyannote(cls, annotation: Any):
        """Create a `SpeakerAnnotation` object from a ``pyannote.core.Annotation`` object.

        Parameters
        ----------
        annotation : pyannote.core.Annotation
            Annotation object containing speech segments and speaker labels.

        """
        segment_tree = cls()

        for seg, _, spk in annotation.itertracks(yield_label=True):
            segment_tree.add(Interval(
                begin=seg.start,
                end=seg.end,
                data=SegmentData(
                    filename=annotation.uri,
                    channel=1,
                    name=str(spk)
                )
            ))

        return segment_tree


    @classmethod
    def from_rttm(cls, filename: str):
        """Load a speaker annotation from an RTTM file.

        Parameters
        ----------
        filename : str
            Path to the file. Must have an RTTM ending.

        """
        with open(filename, "r", encoding='utf-8') as file:
            segment_tree = cls()
            for row in file:
                row_split = [None if cell == "<NA>" else cell for cell in row.split(" ")]
                segment = Interval(
                    begin=float(row_split[3]),
                    end=float(row_split[3]) + float(row_split[4]),
                    data=SegmentData(
                        filename=row_split[1],
                        channel=int(row_split[2]),
                        name=row_split[7],
                    )
                )
                segment_tree.add(segment)

            return segment_tree


    def write_rttm(self, filename: str):
        """Write a speaker annotation to an RTTM file.

        Parameters
        ----------
        filename : str
            Path to the file. Must have an RTTM ending.

        """
        with open(filename, "w", encoding='utf-8') as file:
            self.__str__(end=" ", file=file, header=False) #pylint: disable=unnecessary-dunder-call


@dataclass
class TranscriptionData:
    index: int
    text: str


class AudioTranscription:
    def __init__(self,
        filename: str,
        subtitles: Optional[IntervalTree] = None
    ):
        self.filename = filename
        self.subtitles = subtitles


    def __len__(self) -> int:
        return len(self.subtitles)


    @classmethod
    def from_srt(cls, filename: str):
        with open(filename, 'r', encoding='utf-8') as file:
            subtitles = srt.parse(file)

            intervals = []

            for sub in subtitles:
                intervals.append(Interval(
                    begin=sub.start.total_seconds(),
                    end=sub.end.total_seconds(),
                    data=TranscriptionData(
                        index=sub.index,
                        text=sub.content
                    )
                ))

            return cls(filename=filename, subtitles=IntervalTree(intervals))


    def write_srt(self, filename: str):
        subtitles = []

        for iv in self.subtitles.all_intervals:
            subtitles.append(srt.Subtitle(
                index=iv.data.index,
                start=timedelta(seconds=iv.begin),
                end=timedelta(seconds=iv.end),
                content=iv.data.text
            ))

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(srt.compose(subtitles))


@dataclass
class Sentiment:
    index: int
    pos: float
    neg: float
    neu: float


@dataclass
class SentimentAnnotation:
    sentiment: List[Sentiment] = field(default_factory=list)


    @classmethod
    def from_dict(cls, data: Dict):
        field_names = [f.name for f in fields(cls)]
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        filtered_data['sentiment'] = [Sentiment(
            index=s['index'],
            pos=s['pos'],
            neg=s['neg'],
            neu=s['neu']
        ) for s in filtered_data['sentiment']]
        return cls(**filtered_data)


    @classmethod
    def from_json(cls, filename: str):
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return cls.from_dict(data=data)


    def write_json(self, filename: str):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(asdict(self), file, allow_nan=True)


class Multimodal:
    """Class for storing multimodal features.

    See the `Output <https://mexca.readthedocs.io/en/latest/output.html>`_
    section for details.

    Parameters
    ----------
    filename : str
        Name of the file from which features were extracted.
    duration : float, optional, default=None
        Video duration in seconds.
    fps: : float
        Frames per second.
    fps_adjusted : float
        Frames per seconds adjusted for skipped frames.
        Mostly needed for internal computations.
    video_annotation : VideoAnnotation
        Object containing facial features.
    audio_annotation : SpeakerAnnotation
        Object containing speech segments and speakers.
    voice_features : VoiceFeatures
        Object containing voice features.
    transcription : AudioTranscription
        Object containing transcribed speech segments split into sentences.
    Sentiment : SentimentAnnotation
        Object containing sentiment scores for transcribed sentences.

    """
    def __init__(self,
        filename: str,
        duration: Optional[float] = None,
        fps: Optional[int] = None,
        fps_adjusted: Optional[int] = None,
        video_annotation: Optional[VideoAnnotation] = None,
        audio_annotation: Optional[SpeakerAnnotation] = None,
        voice_features: Optional[VoiceFeatures] = None,
        transcription: Optional[AudioTranscription] = None,
        sentiment: Optional[SentimentAnnotation] = None,
        features: Optional[pd.DataFrame] = None
    ):
        self.filename = filename
        self.duration = duration
        self.fps = fps
        self.fps_adjusted = fps if fps_adjusted is None else fps_adjusted
        self.video_annotation = video_annotation
        self.audio_annotation = audio_annotation
        self.voice_features = voice_features
        self.transcription = transcription
        self.sentiment = sentiment
        self.features = features


    def _merge_video_annotation(self, data_frames: List):
        if self.video_annotation:
            data_frames.append(pd.DataFrame(asdict(self.video_annotation)).set_index(['frame', 'time']))


    def _merge_audio_text_features(self, data_frames: List):
        if self.audio_annotation: #pylint: disable=too-many-nested-blocks
            audio_annotation_dict = {
                "frame": [],
                "time": [],
                "segment_start": [],
                "segment_end": [],
                "segment_speaker_label": []
            }

            time = np.arange(0.0, self.duration, 1/self.fps_adjusted, dtype=np.float32)
            frame = np.arange(0, self.duration*self.fps, self.fps_adjusted, dtype=np.int32)

            if self.transcription:
                text_features_dict = {
                    "frame": [],
                    "time": [],
                    "span_start": [],
                    "span_end": [],
                    "span_text": []
                }

                if self.sentiment:
                    text_features_dict['span_sent_pos'] = []
                    text_features_dict['span_sent_neg'] = []
                    text_features_dict['span_sent_neu'] = []

            for i, t in zip(frame, time):
                for seg in self.audio_annotation[t]:
                    audio_annotation_dict['frame'].append(i)
                    audio_annotation_dict['time'].append(t)
                    audio_annotation_dict['segment_start'].append(seg.begin)
                    audio_annotation_dict['segment_end'].append(seg.end)
                    audio_annotation_dict['segment_speaker_label'].append(seg.data.name)

                if self.transcription and self.sentiment:
                    for span, sent in zip(self.transcription.subtitles[t], self.sentiment.sentiment):
                        text_features_dict['frame'].append(i)
                        text_features_dict['time'].append(t)
                        text_features_dict['span_start'].append(span.start.total_seconds())
                        text_features_dict['span_end'].append(span.end.total_seconds())
                        text_features_dict['span_text'].append(span.content)

                        if span.index == sent.index:
                            text_features_dict['span_sent_pos'].append(sent.pos)
                            text_features_dict['span_sent_neg'].append(sent.neg)
                            text_features_dict['span_sent_neu'].append(sent.neu)

                elif self.transcription:
                    for span in self.transcription.subtitles:
                        if span.start.total_seconds() <= t <= span.end.total_seconds():
                            text_features_dict['frame'].append(i)
                            text_features_dict['time'].append(t)
                            text_features_dict['span_start'].append(span.start.total_seconds())
                            text_features_dict['span_end'].append(span.end.total_seconds())
                            text_features_dict['span_text'].append(span.content)
                    
            audio_text_features_df = pd.DataFrame(audio_annotation_dict).set_index(['frame', 'time'])

            if self.transcription:
                audio_text_features_df = audio_text_features_df.merge(
                    pd.DataFrame(text_features_dict).set_index(['frame', 'time']),
                    on=['frame', 'time'],
                    how='left'
                )

            data_frames.append(audio_text_features_df)


    def _merge_voice_features(self, data_frames: List):
        if self.voice_features:
            data_frames.append(pd.DataFrame(asdict(self.voice_features)).set_index(['frame', 'time']))


    def merge_features(self) -> pd.DataFrame:
        """Merge multimodal features from pipeline components into a common data frame.

        Transforms and merges the available output stored in the `Multimodal` object
        based on the `'frame'` variable. Stores the merged features as a `pandas.DataFrame`
        in the `features` attribute.

        Returns
        -------
        pandas.DataFrame
            Merged multimodal features.

        """

        dfs = []

        self._merge_video_annotation(data_frames=dfs)

        self._merge_audio_text_features(data_frames=dfs)

        self._merge_voice_features(data_frames=dfs)

        if len(dfs) > 0:
            self.features = reduce(lambda left, right:
                pd.merge(left , right,
                    on = ["frame", "time"],
                    how = "left"),
                dfs
            ).reset_index()

        return self.features
