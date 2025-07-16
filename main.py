import pandas as pd
import time
from utils.weather import get_weather
from utils.game_results import get_nrfi_result

ranked = pd.DataFrame({
    'game_id': ['123456789', '987654321'],
    'team': ['Yankees', 'Dodgers'],
    'opponent_team': ['Red Sox', 'Giants'],
    'pitcher': ['Gerrit Cole', 'Walker Buehler'],
    'whip': [0.98, 1.12],
    'xba': [0.215, 0.225],
    'lineup_status': ['confirmed', 'unconfirmed'],
    'home_or_away': ['home', 'away'],
    'market_odds': [-120, +110],
    'sp_nrfi': [0.89, 0.85],
    'team_nrfi': [0.75, 0.7],
    'teamrankings_nrfi': [0.77, 0.72],
    'model_probability': [0.84, 0.79]
})

print("🌤️  Fetching weather for all games...")
weather_data = pd.DataFrame([get_weather(gid) for gid in ranked['game_id']])
ranked = pd.concat([ranked.reset_index(drop=True), weather_data], axis=1)

print("🔬 Adding placeholder hitter stats...")
ranked['top4_avg_vs_pitcher'] = [0.212, 0.198]
ranked['top4_obp_vs_pitcher'] = [0.287, 0.301]

print("🧪 Checking actual NRFI outcomes...")
ranked['nrfi_occurred'] = ranked['game_id'].apply(get_nrfi_result)
time.sleep(1)

def american_odds_to_decimal(odds):
    return (odds / 100) + 1 if odds > 0 else (100 / abs(odds)) + 1

def calculate_profit(row):
    odds = row['market_odds']
    result = row['nrfi_occurred']
    if pd.isna(odds) or pd.isna(result):
        return None
    decimal_odds = american_odds_to_decimal(odds)
    return (decimal_odds - 1) * 100 if result == 1 else -100

ranked['profit'] = ranked.apply(calculate_profit, axis=1)

daily_output = ranked[[
    'game_id', 'team', 'opponent_team', 'pitcher', 'whip', 'xba',
    'lineup_status', 'home_or_away', 'market_odds', 'sp_nrfi',
    'team_nrfi', 'teamrankings_nrfi', 'model_probability',
    'top4_avg_vs_pitcher', 'top4_obp_vs_pitcher',
    'temp', 'wind_speed', 'wind_direction', 'condition',
    'nrfi_occurred', 'profit'
]]

daily_output.to_csv("output/daily_nrfi_report.csv", index=False)

try:
    historical = pd.read_csv("output/historical_nrfi.csv")
    historical = pd.concat([historical, daily_output], ignore_index=True)
except FileNotFoundError:
    historical = daily_output

historical.to_csv("output/historical_nrfi.csv", index=False)
print("✅ Historical NRFI data updated.")
