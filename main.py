import requests
import json
import time
import os
from keep_alive import keep_alive

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Origin': 'https://www.roblox.com',
    'Connection': 'keep-alive',
    'Referer': 'https://www.roblox.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}

params = {
    'universeIds': str(os.environ.get("UniversalId")), 
}

def GetStats():
    response = requests.get('https://games.roblox.com/v1/games', params=params, headers=headers)

    if response.status_code == 200:
        data_json = json.loads(response.text)
        if data_json and "data" in data_json and len(data_json["data"]) > 0:
            data = data_json["data"][0]

            visits = data["visits"]
            favorites = data["favoritedCount"]
            playing_count = data["playing"]
            last_updated = data["updated"]
            game_name = data["name"]
            description = data["description"]

            print("Visits:", visits)
            print("Favorites:", favorites)
            print("PlayingCount:", playing_count)
            print("Lastupdated:", last_updated)

            webhook_url = str(os.environ.get("WEBHOOK"))


            webhook_data = {
                "content": "",
                "embeds": [
                    {
                        "title": game_name,
                        "description": description,
                        "color": 3066993,  # Green color
                        "fields": [
                            {
                                "name": "Visits",
                                "value": str(visits),
                                "inline": True
                            },
                            {
                                "name": "Favorites",
                                "value": str(favorites),
                                "inline": True
                            },
                            {
                                "name": "Playing Now",
                                "value": str(playing_count),
                                "inline": True
                            },
                            {
                                "name": "Last Updated",
                                "value": last_updated,
                                "inline": False
                            }
                        ],
                        "footer": {
                            "text": "Roblox Game Updates"
                        }
                    }
                ]
            }

            response = requests.post(webhook_url, json=webhook_data)

            if response.status_code == 204:
                print("Webhook sent successfully!")
            else:
                print(f"Failed to send webhook: {response.status_code}")
    else:
        print(f"Failed to fetch data: {response.status_code}")

keep_alive()

while True:
    GetStats()
    time.sleep(60)
