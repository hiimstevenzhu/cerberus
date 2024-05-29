import asyncio
import websockets

async def handler(websocket, path):
    item = 0
    while True:
        item += 1
        message = {
            "current_line": "Hello, client!",
            "matches": item,
            "matched_keywords": ["keyword1", "keyword2", "keyword3"],
            "match_dict": {
                "keyword1": 1,
                "keyword2": 2,
                "keyword3": 3,
            },
        }
        await websocket.send(json.dumps(message))
        print("Message sent to client")
        await asyncio.sleep(2)

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server is running on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    import json
    asyncio.run(main())
