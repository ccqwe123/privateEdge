import asyncio
import websockets
import json
import requests
import time

# ------------------ Option 1: WebSocket Bot ------------------

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

async def run_websocket_bot():
    token = "YOUR_WS_TOKEN_HERE"  # Replace this with your actual token
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
            print(f"WebSocket error: {e}")
            await asyncio.sleep(5)

# ------------------ Option 2: HTTP Polling Bot ------------------

def fetch_node_status():
    url = "https://api.layeredge.io/api/epoch/node-status/67979520f13d656bcbfa0735?epochName=epoch%202"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "if-none-match": 'W/"2e-0xjAIIC4Onqw9flGLdVy2Y0C/GU"',
        "origin": "https://dashboard.layeredge.io",
        "priority": "u=1, i",
        "referer": "https://dashboard.layeredge.io/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status Code: {response.status_code}")

        if response.status_code == 200:
            json_data = response.json()
            data = json_data.get("data", {})
            status = data.get("status")
            total_points = data.get("totalEpochPoints")
            earnings = data.get("dailyEarnings")

            print("Connected")
            print(f"Status           : {status}")
            print(f"Epoch Points     : {total_points}")
            print(f"Daily Earnings   : {earnings}")
            print("-" * 40)
        else:
            print("Non-200 response or cached (possibly 304)")
    except Exception as e:
        print(f"HTTP Error: {e}")

def run_http_bot():
    while True:
        fetch_node_status()
        time.sleep(60)

# ------------------ Entry Point ------------------

def main():
    print("Select an option:")
    print("1. WebSocket Bot")
    print("2. HTTP Polling Bot")
    choice = input("Enter option (1 or 2): ").strip()

    if choice == "1":
        asyncio.run(run_websocket_bot())
    elif choice == "2":
        run_http_bot()
    else:
        print("Invalid option. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
