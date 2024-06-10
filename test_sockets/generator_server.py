# generator_server.py
import asyncio
import websockets
import json

messages = {0: "Hello", 1: "World", 2: "I", 3: "Am", 4: "Attempting", 5: "To", 6: "Connect"}

class MessageGenerator:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def generate_messages(self):
        count = 0
        messages_id = 0
        while True:
            message = {'message': f'Message: {messages[messages_id]}, count: {count}'}
            await self.queue.put(message)
            print(f'Generated: {message}')
            count += 1
            messages_id += 1
            if messages_id > 6:
                messages_id = 0
            await asyncio.sleep(1)

    async def send_messages(self, websocket, path):
        while True:
            if not self.queue.empty():
                message = await self.queue.get()
                await websocket.send(json.dumps(message))
                print(f'Sent: {message}')
                await asyncio.sleep(1.5)

    async def handler(self, websocket, path):
        print("Client connected")
        producer_task = asyncio.create_task(self.generate_messages())
        consumer_task = asyncio.create_task(self.send_messages(websocket, path))
        await asyncio.gather(producer_task, consumer_task)

    def start(self):
        ipadd = "localhost"
        start_server = websockets.serve(self.handler, ipadd, 8765)
        print(f"WebSocket server started on ws://{ipadd}:8765")
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    print("Starting server...")
    generator = MessageGenerator()
    generator.start()
