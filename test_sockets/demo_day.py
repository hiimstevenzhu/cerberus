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

import timeit # recording time elapsed

from concurrent.futures import ThreadPoolExecutor

# Create a thread pool for CPU-bound tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

# defining chunk_size?
CHUNK_SIZE = 16000 * 2  # 5 seconds of audio at 16 kHz

START_TIME = 0
END_TIME = 0

async def collect_audio(data_queue, audio_buffer):
    while True:
        if not data_queue.empty():
            data = data_queue.get_nowait()
            audio_buffer.extend(np.frombuffer(data, dtype=np.int16))
            print(f"Collected audio chunk, buffer size: {len(audio_buffer)}")
        else:
            await asyncio.sleep(0.1)

async def transcribe_audio(audio_buffer, transcription_queue, audio_model):
    while True:
        if len(audio_buffer) >= CHUNK_SIZE:
            print("Taking audio chunk...")
            chunk = np.array(audio_buffer[:CHUNK_SIZE], dtype=np.int16)
            del audio_buffer[:CHUNK_SIZE]
            
            # Offload CPU-intensive transcription to a thread
            text = await asyncio.to_thread(
                process_audio_chunk, 
                chunk, 
                audio_model
            )
            
            if text.strip():
                await transcription_queue.put(text)
        else:
            await asyncio.sleep(0.1)

def process_audio_chunk(chunk, audio_model):
    # Chunk is already a numpy array of int16, so we can directly convert it to float32
    print("Starting transcription...")
    audio_np = chunk.astype(np.float32) / 32768.0
    result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
    END_TIME = timeit.timeit()
    print(f"Transcription time: {END_TIME - START_TIME}")
    return result['text'].strip()

async def handle_client(websocket, path, transcription_queue):
    try:
        while True:
            text = await transcription_queue.get()
            message = {
                'message': text,
                'matches': 0,
                'matched_keywords': [],
                'match_dict': {},
            }
            await websocket.send(json.dumps(message))
            print(f"Sent: {message['message']}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def start_websocket_server(transcription_queue, port):
    server = await websockets.serve(
        lambda ws, path: handle_client(ws, path, transcription_queue),
        "localhost", port
    )
    print(f"WebSocket server started on ws://localhost:{port}")
    await server.wait_closed()

async def async_main(args):
    data_queue = Queue()
    transcription_queue = asyncio.Queue()
    audio_buffer = []

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
        print("callback, putting raw audio data into queue...")
        # RECORDING TIME ELAPSED
        START_TIME = timeit.timeit()
        data_queue.put_nowait(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=args.record_timeout)

    print("Model loaded.\n")

    tasks = [
        collect_audio(data_queue, audio_buffer),
        transcribe_audio(audio_buffer, transcription_queue, audio_model),
        start_websocket_server(transcription_queue, args.port)
    ]
    
    await asyncio.gather(*tasks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="small", help="Model to use",
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
    parser.add_argument("--port", default=8765, help="WebSocket server port", type=int)
    
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    
    args = parser.parse_args()

    try:
        asyncio.run(async_main(args))
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()