# websockets imports
import asyncio
import websockets
import json

# model imports
import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform

# Args for setup
parser = argparse.ArgumentParser()
parser.add_argument("--model", default="medium", help="Model to use",
                    choices=["tiny", "base", "small", "medium", "large"])
parser.add_argument("--non_english", action='store_false', # CHANGE THIS PART ONCE SUPPORT MULTIPLE LANG
                    help="Don't use the english model.")
parser.add_argument("--energy_threshold", default=1000,
                    help="Energy level for mic to detect.", type=int)
parser.add_argument("--record_timeout", default=2,
                    help="How real time the recording is in seconds.", type=float)
parser.add_argument("--phrase_timeout", default=3,
                    help="How much empty space between recordings before we "
                            "consider it a new line in the transcription.", type=float)
args = parser.parse_args()

# Global variable - our model
audio_model = None


# Setup function for model loading based on arguments
def setup():
    # Load model
    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    return model
    
async def handler(websocket, path):
    print("Starting handler...")
    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False
    # Microphone setup - Linux users will have to edit this line based on the source code, which supports linux implementations
    source = sr.Microphone(sample_rate=16000)
    
    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = ['']
    
    with source:
        recorder.adjust_for_ambient_noise(source)
        
    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)
    print("Listening...")
    
    #  # Create an asyncio event that will continuously listen for audio data
    # async def listen_audio():
    #     print("Listening...")
    #     while True:
    #         # Record audio data
    #         with source as src:
    #             audio_data = recorder.listen(src, timeout=record_timeout)
            
    #         # Push audio data to the queue
    #         data = audio_data.get_raw_data()
    #         data_queue.put(data)
            
    #         await asyncio.sleep(0)  # Allow other tasks to run
    
    # listen_task = asyncio.create_task(listen_audio())
    
    while True:
        message = {
            "current_line": "",
            "matches": 100,
            "matched_keywords": ["keyword1", "keyword2", "keyword3"],
            "match_dict": {
                "keyword1": 1,
                "keyword2": 2,
                "keyword3": 3,
            },
        }
        # DO: get message
        try:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now
                
                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                print("Current transcription: ", transcription[-1])
                message["current_line"] = transcription[-1]
                await websocket.send(json.dumps(message))
                print("Message sent to client")
        except KeyboardInterrupt:
            break
        # print("Sleeping...")
        # await asyncio.sleep(2) # we sleep to save the processor

    
async def main():
    print("Starting main...")
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # run forever
    # server = await websockets.serve(handler, "localhost", 8765)
    # print("WebSocket server created.")
    # async with server:
    #     print("WebSocket server is running on ws://localhost:8765")
    #     await server.wait_closed()  # ensure it stays open
    #     print("Server closed...?")

        
if __name__ == "__main__":
    model = setup()
    audio_model = whisper.load_model(model)
    print("Model loaded.\n")
    if audio_model:
        asyncio.run(main())

