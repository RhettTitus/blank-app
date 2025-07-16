import requests

def get_weather(game_id):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        weather = data.get("gameData", {}).get("weather", {})
        return {
            "temp": weather.get("temp"),
            "wind_speed": weather.get("windSpeed"),
            "wind_direction": weather.get("windDirection"),
            "condition": weather.get("condition"),
        }
    except Exception as e:
        print(f"⚠️ Weather fetch failed for game {game_id}: {e}")
        return {"temp": None, "wind_speed": None, "wind_direction": None, "condition": None}
