import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch
import asyncio
import websockets
import json
import setuptools.dist
from queue import Queue

from datetime import datetime, timedelta
from sys import platform

async def transcribe_audio(data_queue, transcription_queue, audio_model, record_timeout, phrase_timeout):
    phrase_time = None
    transcription = ['']

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                phrase_time = now
                
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                await transcription_queue.put(text)
                print(f"Got: {text}")
            else:
                await asyncio.sleep(0.25)
        except KeyboardInterrupt:
            break

async def send_transcription(transcription_queue, websocket_uri):
    async with websockets.connect(websocket_uri) as websocket:
        while True:
            try:
                if not transcription_queue.empty():
                    text = await transcription_queue.get()
                    message = {
                        'message': text,
                        'matches': 0,
                        'matched_keywords': [],
                        'match_dict': {},
                    }
                    print(f"Sent: {message['message']}")
                    await websocket.send(json.dumps(message))
                else:
                    await asyncio.sleep(0.25)
            except KeyboardInterrupt:
                break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    parser.add_argument("--websocket_uri", default="ws://localhost:8765", help="WebSocket server URI", type=str)
    
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    
    args = parser.parse_args()

    data_queue = Queue()
    transcription_queue = asyncio.Queue()
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False
    source = sr.Microphone(sample_rate=16000)

    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio: sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put_nowait(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=args.record_timeout)

    print("Model loaded.\n")

    loop = asyncio.get_event_loop()
    tasks = [
        transcribe_audio(data_queue, transcription_queue, audio_model, args.record_timeout, args.phrase_timeout),
        send_transcription(transcription_queue, args.websocket_uri)
    ]
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == "__main__":
    main()
