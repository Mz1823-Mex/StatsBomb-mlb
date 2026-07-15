import json
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = Path(".")
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
RAW.mkdir(parents=True, exist_ok=True)
PROCESSED.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_json(url, params=None):
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def fetch_html(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def get_mlb_teams(season=2026):
    url = "https://statsapi.mlb.com/api/v1/teams"
    data = fetch_json(url, params={"sportId": 1, "season": season})
    rows = []
    for t in data.get("teams", []):
        rows.append({
            "team_id": t.get("id"),
            "team_name": t.get("name"),
            "abbreviation": t.get("abbreviation"),
            "season": season,
            "source": "mlb_api"
        })
    return pd.DataFrame(rows)

def scrape_espn_standings(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    tables = pd.read_html(html)
    if not tables:
        return pd.DataFrame()
    df = tables[0].copy()
    df["source"] = "espn_scraping"
    df["scraped_url"] = url
    return df

def main():
    teams = get_mlb_teams(season=2026)
    teams.to_csv(PROCESSED / "mlb_teams_2026.csv", index=False)

    espn_url = "https://www.espn.com/mlb/standings"
    espn_df = scrape_espn_standings(espn_url)
    espn_df.to_csv(PROCESSED / "espn_standings_2026.csv", index=False)

    summary = {
        "mlb_rows": int(len(teams)),
        "espn_rows": int(len(espn_df)),
        "generated_at_epoch": int(time.time())
    }
    with open(PROCESSED / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if len(teams) == 0:
        raise ValueError("MLB API no devolvió filas")
    print(summary)

if __name__ == "__main__":
    main()
