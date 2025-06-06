import asyncio
import websockets
import json

async def send_heartbeat(websocket):
    try:
        await websocket.send(json.dumps({"type": "Heartbeat"}))
        print("Sent heartbeat")
    except Exception as e:
        print("Failed to send heartbeat:", e)

async def send_node_start(websocket):
    try:
        await websocket.send(json.dumps({"type": "NodeStart"}))
        print("Sent NodeStart")
    except Exception as e:
        print("Failed to send NodeStart:", e)

async def receive_messages(websocket):
    async for message in websocket:
        print("Received:", message)
        try:
            data = json.loads(message)
            if data.get("type") == "connected":
                print("Connected response received")
                await send_node_start(websocket)
            elif data.get("type") == "NodeUpdate":
                print("Node status:", data)
            elif data.get("type") == "PointsUpdate":
                print("Points update:", data)
        except Exception as e:
            print("Error processing message:", e)

async def main():
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2Nzk3OTUyMGYxM2Q2NTZiY2JmYTA3MzUiLCJpYXQiOjE3NDg5MjA3NjAsImV4cCI6MTc0OTUyNTU2MCwianRpIjoiMTU5MzM1MTQtZWM4NS00OTIwLWFjMmItM2FiM2JiMzkwYjc2IiwicHVycG9zZSI6IndlYnNvY2tldCJ9.MMaFRUPrfQsfGll1nBe761wxl4vtTwC6STTX9pVpqUw" #put your wsToken here
    websocket_url = f"wss://websocket.layeredge.io/ws/node?token={token}"

    while True:
        try:
            async with websockets.connect(websocket_url) as websocket:
                print("Connected to WebSocket server")

                async def heartbeat_loop():
                    while True:
                        await send_heartbeat(websocket)
                        await asyncio.sleep(5)

                receive_task = asyncio.create_task(receive_messages(websocket))
                send_task = asyncio.create_task(heartbeat_loop())

                done, pending = await asyncio.wait(
                    [send_task, receive_task],
                    timeout=60,
                    return_when=asyncio.FIRST_EXCEPTION
                )
                for task in pending:
                    task.cancel()

                print("Wait for 1 minute...")

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(5)

asyncio.run(main())
