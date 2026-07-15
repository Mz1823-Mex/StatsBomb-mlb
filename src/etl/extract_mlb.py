"""MLB data extraction from API and fallback sources."""

import logging
from typing import Dict, List, Optional

import pandas as pd
from src.api.mlb_client import MLBClient
from src.utils.logger import setup_logger


class MLBDataExtractor:
    """Extract player and team data from MLB Stats API."""

    def __init__(self, config: Dict, client: Optional[MLBClient] = None):
        """Initialize extractor.
        
        Args:
            config: Configuration dictionary.
            client: MLBClient instance. If None, creates new client.
        """
        self.config = config
        self.client = client or MLBClient(
            base_url=config.get("api", {}).get("mlb_stats_base_url", "https://statsapi.mlb.com/api/v1"),
            timeout=config.get("api", {}).get("timeout", 30),
            max_retries=config.get("api", {}).get("max_retries", 3),
        )
        self.logger = setup_logger(__name__)
    
    def extract_player_stats(
        self,
        stat_type: str = "hitting",
        season: int = 2026,
    ) -> pd.DataFrame:
        """Extract player statistics from MLB API.
        
        Args:
            stat_type: Type of stats ('hitting', 'pitching', 'fielding').
            season: Season year.
            
        Returns:
            DataFrame with player statistics.
        """
        self.logger.info(f"Extracting {stat_type} stats for season {season}")
        
        try:
            # Get all players
            people_data = self.client.get_people(season=season)
            players = people_data.get("people", [])
            
            self.logger.info(f"Found {len(players)} players")
            
            all_stats = []
            
            for player in players:
                player_id = player.get("id")
                player_name = player.get("fullName", "Unknown")
                
                try:
                    # Get player stats
                    stats_data = self.client.get_player_stat(
                        player_id=player_id,
                        group=stat_type,
                        stat_type="season",
                        season=season,
                    )
                    
                    # Extract stats from response
                    stats_list = stats_data.get("stats", [])
                    
                    for stat in stats_list:
                        stat_dict = stat.get("stats", {})
                        
                        # Add player info
                        stat_dict["player_id"] = player_id
                        stat_dict["player_name"] = player_name
                        stat_dict["season"] = season
                        stat_dict["stat_type"] = stat_type
                        
                        all_stats.append(stat_dict)
                
                except Exception as e:
                    self.logger.warning(f"Failed to extract stats for player {player_name} (ID: {player_id}): {e}")
                    continue
            
            # Convert to DataFrame
            df = pd.DataFrame(all_stats)
            
            self.logger.info(f"Extracted {len(df)} {stat_type} records")
            
            return df
        
        except Exception as e:
            self.logger.error(f"Failed to extract player stats: {e}", exc_info=True)
            return pd.DataFrame()
    
    def extract_team_stats(
        self,
        season: int = 2026,
    ) -> pd.DataFrame:
        """Extract team statistics from MLB API.
        
        Args:
            season: Season year.
            
        Returns:
            DataFrame with team statistics.
        """
        self.logger.info(f"Extracting team stats for season {season}")
        
        try:
            # Get all teams
            teams_data = self.client.get_teams()
            teams = teams_data.get("teams", [])
            
            self.logger.info(f"Found {len(teams)} teams")
            
            all_team_stats = []
            
            for team in teams:
                team_id = team.get("id")
                team_name = team.get("name", "Unknown")
                team_abbr = team.get("abbreviation", "")
                
                try:
                    # Get team stats
                    stats_data = self.client.get_team_stat(
                        team_id=team_id,
                        stat_type="season",
                        season=season,
                    )
                    
                    stats_list = stats_data.get("stats", [])
                    
                    for stat in stats_list:
                        stat_dict = stat.get("stats", {})
                        stat_dict["team_id"] = team_id
                        stat_dict["team_name"] = team_name
                        stat_dict["team_abbr"] = team_abbr
                        stat_dict["season"] = season
                        
                        all_team_stats.append(stat_dict)
                
                except Exception as e:
                    self.logger.warning(f"Failed to extract stats for team {team_name}: {e}")
                    continue
            
            df = pd.DataFrame(all_team_stats)
            
            self.logger.info(f"Extracted {len(df)} team records")
            
            return df
        
        except Exception as e:
            self.logger.error(f"Failed to extract team stats: {e}", exc_info=True)
            return pd.DataFrame()
    
    def extract_standings(
        self,
        season: int = 2026,
    ) -> pd.DataFrame:
        """Extract season standings.
        
        Args:
            season: Season year.
            
        Returns:
            DataFrame with standings.
        """
        self.logger.info(f"Extracting standings for season {season}")
        
        try:
            standings_data = self.client.get_standings(
                league_id="103,104",  # AL and NL
                season=season,
            )
            
            records = standings_data.get("records", [])
            all_standings = []
            
            for division_record in records:
                teams = division_record.get("teamRecords", [])
                
                for team_record in teams:
                    standing_dict = {
                        "season": season,
                        "team_id": team_record.get("team", {}).get("id"),
                        "team_name": team_record.get("team", {}).get("name"),
                        "wins": team_record.get("wins", 0),
                        "losses": team_record.get("losses", 0),
                        "win_pct": team_record.get("winningPct", 0.0),
                        "games_back": team_record.get("gamesBack", 0.0),
                    }
                    all_standings.append(standing_dict)
            
            df = pd.DataFrame(all_standings)
            
            self.logger.info(f"Extracted {len(df)} standings records")
            
            return df
        
        except Exception as e:
            self.logger.error(f"Failed to extract standings: {e}", exc_info=True)
            return pd.DataFrame()
    
    def close(self) -> None:
        """Close API client connection."""
        if self.client:
            self.client.close()
            self.logger.info("Extractor closed")
