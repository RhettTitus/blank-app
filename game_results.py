import requests

def get_nrfi_result(game_id):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        innings = data['liveData']['linescore']['innings']
        home_runs = innings[0]['home']['runs'] if 'home' in innings[0] else 0
        away_runs = innings[0]['away']['runs'] if 'away' in innings[0] else 0
        return 1 if (home_runs == 0 and away_runs == 0) else 0
    except Exception as e:
        print(f"⚠️ Error fetching NRFI result for game {game_id}: {e}")
        return None
