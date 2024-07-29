import os
import sys
import json
import time
import random
import requests
import websocket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
status = os.getenv("status")  # online/dnd/idle
usertoken = os.getenv("token")

# Check if token is provided
if not usertoken:
    print("[ERROR] Please add a token inside Secrets.")
    sys.exit()

headers = {"Authorization": usertoken, "Content-Type": "application/json"}

# Validate token
validate = requests.get("https://canary.discordapp.com/api/v9/users/@me", headers=headers)
if validate.status_code != 200:
    print("[ERROR] Your token might be invalid. Please check it again.")
    sys.exit()

userinfo = validate.json()
username = userinfo["username"]
discriminator = userinfo["discriminator"]
userid = userinfo["id"]

# Load custom statuses from JSON file
with open("statuses.json", "r") as file:
    custom_statuses = json.load(file)

def get_random_status():
    return random.choice(custom_statuses)

def update_status(ws, token, status):
    custom_status = get_random_status()
    cstatus = {
        "op": 3,
        "d": {
            "since": 0,
            "activities": [
                {
                    "type": 4,
                    "state": custom_status,
                    "name": "Custom Status",
                    "id": "custom",
                }
            ],
            "status": status,
            "afk": False,
        },
    }
    ws.send(json.dumps(cstatus))
    # print(f"Updated status to: {custom_status}")

def establish_connection(token, status):
    ws = websocket.WebSocket()
    ws.connect("wss://gateway.discord.gg/?v=9&encoding=json")
    start = json.loads(ws.recv())
    heartbeat = start["d"]["heartbeat_interval"]

    auth = {
        "op": 2,
        "d": {
            "token": token,
            "properties": {
                "$os": "Linux",
                "$browser": "Python Script",
                "$device": "Raspberry Pi",
            },
            "presence": {"status": status, "afk": False},
        },
    }
    ws.send(json.dumps(auth))

    return ws, heartbeat

def run_onliner():
    os.system("clear")
    print(f"Logged in as {username}#{discriminator} ({userid}).")
    
    while True:
        try:
            ws, heartbeat = establish_connection(usertoken, status)
            update_status(ws, usertoken, status)

            # Wait for 60 seconds before updating the status again
            time.sleep(60)
        except websocket.WebSocketConnectionClosedException:
            print("Connection closed, reconnecting...")
            time.sleep(5)
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_onliner()
