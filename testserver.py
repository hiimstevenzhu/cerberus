# websockets imports
import asyncio
import websockets
import json

async def handler(websocket, path):
    # basic implementation looks like this
    while True:
        message = ""
        # DO: get message

        await websocket.send(json.dumps(message))
        print("Message sent to client")
        await asyncio.sleep(0.1) # we sleep to save the processor
    
async def main():
    # setup model
    
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
    
    
    
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # Run forever