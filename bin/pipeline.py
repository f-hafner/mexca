"""Apply the mexca pipeline to a video file from the command line.

This script is used by the docker container.

"""

import argparse
import json
from json import JSONEncoder
import numpy as np
from mexca.audio.extraction import VoiceExtractor
from mexca.audio.features import FeaturePitchF0
from mexca.audio.identification import SpeakerIdentifier
from mexca.audio.integration import AudioIntegrator
from mexca.core.pipeline import Pipeline
from mexca.text.transcription import AudioTextIntegrator
from mexca.text.transcription import AudioTranscriber
from mexca.video.extraction import FaceExtractor

class NumpyArrayEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.ndarray, np.float32, np.chararray)):
            return o.tolist()
        return JSONEncoder.default(self, o)


parser = argparse.ArgumentParser(description='Apply the mexca pipeline to a video file.')
parser.add_argument('-f', '--filepath', type=str, required=True, dest='filepath')
parser.add_argument('-o', '--output', type=str, required=True, dest='output')
parser.add_argument('-l', '--lang', type=str, default='english',
    help='The language that is transcribed. Currently only Dutch and English are avaiable.', dest='language')
parser.add_argument('--face-min', default=2,
    help='The minimum number of faces that should be identified.', dest='min_clusters')
parser.add_argument('--face-max', default=None,
    help='The maximum number of faces that should be identified.', dest='max_clusters')
parser.add_argument('--speakers', default=None,
    help='The number of speakers that should be identified.', dest='num_speakers')
parser.add_argument('--pitch-low', type=float, default=75.0,
    help='The lower bound frequency of the pitch calculation.', dest='pitch_low')
parser.add_argument('--pitch-high', type=float, default=300.0,
    help='The upper bound frequency of the pitch calculation.', dest='pitch_high')
parser.add_argument('--time-step', default=None,
    help='The interval between time points at which features are extracted. Only used when video processing is disabled.',
    dest='time_step')
parser.add_argument('--skip', type=int, default=1,
    help='Skips every nth video frame.', dest='skip_frames')
parser.add_argument('--subclip', nargs=2, default=[0, None],
    help='Process only a part of the video clip.', dest='process_subclip')
parser.add_argument('--no-video', action='store_true', default=False,
    help='Disables the video processing part of the pipeline.', dest='no_video')
parser.add_argument('--no-audio', action='store_true', default=False,
    help='Disables the audio processing part of the pipeline.', dest='no_audio')
parser.add_argument('--no-text', action='store_true', default=False,
    help='Disables the text processing part of the pipeline.', dest='no_text')

args = parser.parse_args()

pipeline = Pipeline(
    video=None if args.no_video else FaceExtractor(
        min_clusters=args.min_clusters,
        max_clusters=args.max_clusters
    ),
    audio=None if args.no_audio else AudioIntegrator(
        SpeakerIdentifier(num_speakers=args.num_speakers),
        VoiceExtractor(
            time_step=args.time_step,
            features={
                'pitchF0': FeaturePitchF0(
                    pitch_floor=args.pitch_low,
                    pitch_ceiling=args.pitch_high
                )
            }
        )
    ),
    text=None if args.no_text else AudioTextIntegrator(
        audio_transcriber=AudioTranscriber(args.language),
        time_step=args.time_step
    )
)

output = pipeline.apply(
    filepath=args.filepath,
    skip_frames=args.skip_frames,
    process_subclip=args.process_subclip
)

with open(args.output, 'w', encoding='utf-8') as file:
    json.dump(output.features, file, cls=NumpyArrayEncoder, indent=2)
