import speech_recognition as sr
import argparse
import os
from queue import Queue
from sys import platform
'''
Arguments - for tweaking parameters.
parser is a global variable.
'''

parser = argparse.ArgumentParser()
parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
parser.add_argument("--record_timeout", default=2,
                    help="How real time the recording is in seconds.", type=float)
parser.add_argument("--phrase_timeout", default=3,
                    help="How much empty space between recordings before we "
                            "consider it a new line in the transcription.", type=float)
if 'linux' in platform:
            parser.add_argument("--default_microphone", default='pulse',
                                help="Default microphone name for SpeechRecognition. "
                                    "Run this with 'list' to view available Microphones.", type=str)
        
'''
the Recorder model class is essentially a audio data buffer
'''

class Recorder():
    def __init__(self, args):
        self.args = parser.parse_args()
        recorder = sr.Recognizer()
        recorder.energy_threshold = args.energy_threshold
        recorder.dynamic_energy_threshold = False
        source = sr.Microphone(sample_rate=16000)
