import requests
import json
import time
import os
import csv
import threading
from datetime import datetime, timedelta
from keep_alive import keep_alive

UniverseId = str(os.environ.get("UniversalId"))
Webhook1 = str(os.environ.get("WEBHOOK"))
Webhook2 = str(os.environ.get("WEBHOOK2"))

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
    'universeIds': UniverseId, 
}

def save_daily_stats(stats):
    filename = 'stats.csv'
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['date', 'visits', 'favorites', 'playing_count'])
        writer.writerow([stats['date'], stats['visits'], stats['favorites'], stats['playing_count']])

def get_30_day_stats():
    filename = 'stats.csv'
    if not os.path.isfile(filename):
        print("No data available.")
        return None

    data = []
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)

    # Filter the last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_data = [row for row in data if datetime.strptime(row['date'], '%Y-%m-%d') >= thirty_days_ago]

    if len(recent_data) == 0:
        print("No data available for the last 30 days.")
        return None

    # Calculate averages
    total_visits = sum(int(row['visits']) for row in recent_data)
    total_favorites = sum(int(row['favorites']) for row in recent_data)
    total_playing_count = sum(int(row['playing_count']) for row in recent_data)
    num_days = len(recent_data)

    return {
        'average_visits': total_visits / num_days,
        'average_favorites': total_favorites / num_days,
        'average_playing_count': total_playing_count / num_days
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

            webhook_url = Webhook1

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

def daily_stats_report():
    while True:
        today = datetime.now().strftime('%Y-%m-%d')
        response = requests.get('https://games.roblox.com/v1/games', params=params, headers=headers)

        if response.status_code == 200:
            data_json = json.loads(response.text)
            if data_json and "data" in data_json and len(data_json["data"]) > 0:
                data = data_json["data"][0]

                visits = data["visits"]
                favorites = data["favoritedCount"]
                playing_count = data["playing"]

                daily_stats = {
                    'date': today,
                    'visits': visits,
                    'favorites': favorites,
                    'playing_count': playing_count
                }
                save_daily_stats(daily_stats)

                webhook_url = Webhook2

                stats_30_days = get_30_day_stats()
                if stats_30_days:
                    webhook_data = {
                        "content": "",
                        "embeds": [
                            {
                                "title": "30-Day Statistics",
                                "description": "Average stats for the last 30 days",
                                "color": 15158332,  # Red color
                                "fields": [
                                    {
                                        "name": "30-Day Average Visits",
                                        "value": f"{stats_30_days['average_visits']:.2f}",
                                        "inline": True
                                    },
                                    {
                                        "name": "30-Day Average Favorites",
                                        "value": f"{stats_30_days['average_favorites']:.2f}",
                                        "inline": True
                                    },
                                    {
                                        "name": "30-Day Average Playing",
                                        "value": f"{stats_30_days['average_playing_count']:.2f}",
                                        "inline": True
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
                        print("30-Day Webhook sent successfully!")
                    else:
                        print(f"Failed to send 30-Day webhook: {response.status_code}")
        else:
            print(f"Failed to fetch daily data: {response.status_code}")

        time.sleep(86400)  # Run once per day

def start_bot():
    threading.Thread(target=daily_stats_report).start()
    while True:
        GetStats()
        time.sleep(60)

keep_alive()
start_bot()
