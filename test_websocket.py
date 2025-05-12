"""
Test script to verify WebSocket chat functionality with authentication.
"""

import argparse
import asyncio
import json
import websockets
import requests

async def test_websocket_connection(token, room_id=1):
    """Test WebSocket connection with authentication token."""
    ws_url = f"ws://localhost:8000/ws/chat/chat_{room_id}/?token={token}"
    
    print(f"Connecting to {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("Connected to WebSocket server!")
            
            # Send a test message
            test_message = {
                "type": "chat_message", 
                "content": "Test message from script",
                "sender_id": 1,  # Use your actual user ID
                "chatroom_id": room_id
            }
            
            print(f"Sending message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            print("Waiting for messages...")
            for _ in range(3):  # Wait for up to 3 messages
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"Received: {response}")
                except asyncio.TimeoutError:
                    print("No more messages.")
                    break
                    
            print("Test complete!")
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")

async def test_api_endpoints(token):
    """Test HTTP API endpoints with authentication token."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test auth check endpoint
        print("Testing auth-check endpoint...")
        response = requests.get("http://localhost:8000/api/auth-check/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test chatrooms endpoint
        print("\nTesting chatrooms endpoint...")
        response = requests.get("http://localhost:8000/api/chatrooms/", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing API endpoints: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test WebSocket chat functionality.")
    parser.add_argument("token", help="JWT token for authentication")
    parser.add_argument("--room", type=int, default=1, help="Chat room ID (default: 1)")
    args = parser.parse_args()

    print("Starting WebSocket test...")
    asyncio.run(test_websocket_connection(args.token, args.room))
    
    print("\nStarting API test...")
    asyncio.run(test_api_endpoints(args.token))
