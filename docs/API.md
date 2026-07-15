# MLB Stats API Documentation

## Overview

The `MLBClient` provides a Python interface to the MLB Stats API for retrieving baseball statistics and information.

## Installation

The client is included in the main package. Install dependencies:

```bash
pip install requests urllib3
```

## Quick Start

```python
from src.api.mlb_client import MLBClient

# Initialize client
client = MLBClient()

# Get player info
player_data = client.get_people(person_id=123456, season=2026)

# Get player stats
stats = client.get_player_stat(
    player_id=123456,
    group="hitting",
    stat_type="season",
    season=2026
)

# Don't forget to close when done
client.close()
```

## Available Methods

### get_people(person_id=None, season=None)
Retrieve player biographical information.

**Parameters:**
- `person_id` (int, optional): Specific player ID. If None, returns all players.
- `season` (int, optional): Filter by season year.

**Returns:** Dictionary with player data.

**Example:**
```python
# Get specific player
player = client.get_people(person_id=543829)  # Mike Trout

# Get all players
all_players = client.get_people(season=2026)
```

---

### get_player_stat(player_id, group="hitting", stat_type="season", season=None)
Retrieve player statistics.

**Parameters:**
- `player_id` (int, required): MLB player ID.
- `group` (str): Stat group - 'hitting', 'pitching', or 'fielding'. Default: 'hitting'.
- `stat_type` (str): Type of statistics - 'season', 'career', etc. Default: 'season'.
- `season` (int, optional): Filter by season year.

**Returns:** Dictionary with player statistics.

**Example:**
```python
# Get 2026 batting stats for player
batting_stats = client.get_player_stat(
    player_id=543829,
    group="hitting",
    season=2026
)

# Get pitching stats
pitching_stats = client.get_player_stat(
    player_id=543829,
    group="pitching",
    season=2026
)
```

---

### get_team_stat(team_id, stat_type="season", season=None)
Retrieve team statistics.

**Parameters:**
- `team_id` (int, required): MLB team ID.
- `stat_type` (str): Type of statistics. Default: 'season'.
- `season` (int, optional): Filter by season year.

**Returns:** Dictionary with team statistics.

**Example:**
```python
team_stats = client.get_team_stat(
    team_id=108,  # LA Dodgers
    season=2026
)
```

---

### get_games(sport_id=1, season=None)
Retrieve games.

**Parameters:**
- `sport_id` (int): Sport ID (1 for MLB). Default: 1.
- `season` (int, optional): Filter by season year.

**Returns:** Dictionary with games data.

**Example:**
```python
games = client.get_games(season=2026)
```

---

### get_standings(league_id=None, season=None)
Retrieve season standings.

**Parameters:**
- `league_id` (str, optional): League ID(s). Use '103' for AL, '104' for NL, or '103,104' for both.
- `season` (int, optional): Filter by season year.

**Returns:** Dictionary with standings data.

**Example:**
```python
# Get AL and NL standings
standings = client.get_standings(
    league_id="103,104",
    season=2026
)

# Get just AL standings
al_standings = client.get_standings(league_id="103", season=2026)
```

---

### get_teams(team_id=None)
Retrieve team information.

**Parameters:**
- `team_id` (int, optional): Specific team ID. If None, returns all teams.

**Returns:** Dictionary with team data.

**Example:**
```python
# Get all teams
all_teams = client.get_teams()

# Get specific team
lodgers = client.get_teams(team_id=108)
```

---

## Configuration

Customize client behavior:

```python
client = MLBClient(
    base_url="https://statsapi.mlb.com/api/v1",
    timeout=30,              # Request timeout in seconds
    max_retries=3,           # Number of retry attempts
    retry_delay=2,           # Base delay between retries
)
```

## Error Handling

The client raises `requests.RequestException` on errors:

```python
from requests.exceptions import RequestException

try:
    data = client.get_people(person_id=123456)
except RequestException as e:
    print(f"API error: {e}")
finally:
    client.close()
```

## Rate Limiting

The client automatically handles:
- Retries with exponential backoff
- HTTP 429 (Too Many Requests) responses
- Connection timeouts

## Best Practices

1. **Close connections**: Always call `client.close()` when done.

```python
try:
    data = client.get_people()
finally:
    client.close()
```

2. **Use context manager** (if implemented):

```python
with MLBClient() as client:
    data = client.get_people()
    # Connection automatically closed
```

3. **Log responses**: Check logs for API issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Now client logs all requests
```

## Common MLB IDs

### Teams
- 108: Los Angeles Dodgers
- 109: Arizona Diamondbacks
- 110: Los Angeles Angels
- 111: San Francisco Giants
- 112: St. Louis Cardinals
- 113: Chicago Cubs
- 114: Cleveland Guardians
- 115: Detroit Tigers
- 116: Houston Astros
- 117: Kansas City Royals
- 118: Los Angeles Angels
- 119: Washington Nationals
- 120: New York Yankees
- 121: New York Mets
- 133: Toronto Blue Jays
- 134: Tampa Bay Rays
- 135: Chicago White Sox
- 136: Miami Marlins
- 137: Milwaukee Brewers
- 138: Philadelphia Phillies
- 139: Pittsburgh Pirates
- 140: Cincinnati Reds
- 141: Colorado Rockies
- 142: Texas Rangers
- 143: Minnesota Twins
- 144: Boston Red Sox
- 145: Oakland Athletics
- 146: Seattle Mariners
- 147: Baltimore Orioles

### Leagues
- 103: American League (AL)
- 104: National League (NL)
- 105: Major League Baseball (MLB)

## Troubleshooting

### "Connection timeout"
- Increase timeout: `MLBClient(timeout=60)`
- Check internet connection
- Verify API is accessible

### "Rate limit exceeded"
- Automatic retry logic should handle this
- If persistent, add delays between requests

### "API response error"
- Check endpoint documentation
- Verify parameters are correct
- Review API logs for details
