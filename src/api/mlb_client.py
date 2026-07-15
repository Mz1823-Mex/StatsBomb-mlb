"""MLB Stats API client for data extraction."""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MLBClient:
    """HTTP client for MLB Stats API with retry logic and rate limiting."""

    def __init__(
        self,
        base_url: str = "https://statsapi.mlb.com/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: int = 2,
    ):
        """Initialize MLB API client.
        
        Args:
            base_url: MLB Stats API base URL.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            retry_delay: Base delay between retries in seconds.
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)
        
        # Set up session with retry strategy
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy.
        
        Returns:
            Configured requests.Session.
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set user agent
        session.headers.update({
            "User-Agent": "StatsBomb-MLB-Pipeline/0.1.0",
        })
        
        return session
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP GET request to API endpoint.
        
        Args:
            endpoint: API endpoint (e.g., '/people').
            params: Query parameters.
            
        Returns:
            JSON response as dictionary.
            
        Raises:
            requests.RequestException: If request fails.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            self.logger.debug(f"Request successful: {url}")
            return response.json()
        
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout: {url}")
            raise
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error {response.status_code}: {url}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {url} - {e}")
            raise
    
    def get_people(
        self,
        person_id: Optional[int] = None,
        season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get player information.
        
        Args:
            person_id: Specific player ID. If None, gets all players.
            season: Season year.
            
        Returns:
            Player data.
        """
        endpoint = "/people" if person_id is None else f"/people/{person_id}"
        params = {}
        
        if season:
            params["season"] = season
        
        return self._make_request(endpoint, params)
    
    def get_player_stat(
        self,
        player_id: int,
        group: str = "hitting",
        stat_type: str = "season",
        season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get player statistics.
        
        Args:
            player_id: MLB player ID.
            group: Stat group ('hitting', 'pitching', 'fielding').
            stat_type: Type of stats ('season', 'career', etc.).
            season: Season year.
            
        Returns:
            Player statistics data.
        """
        endpoint = f"/people/{player_id}/stat"
        params = {
            "group": group,
            "type": stat_type,
        }
        
        if season:
            params["season"] = season
        
        return self._make_request(endpoint, params)
    
    def get_team_stat(
        self,
        team_id: int,
        stat_type: str = "season",
        season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get team statistics.
        
        Args:
            team_id: MLB team ID.
            stat_type: Type of stats ('season', 'career', etc.).
            season: Season year.
            
        Returns:
            Team statistics data.
        """
        endpoint = f"/teams/{team_id}/stat"
        params = {"type": stat_type}
        
        if season:
            params["season"] = season
        
        return self._make_request(endpoint, params)
    
    def get_games(
        self,
        sport_id: int = 1,
        season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get games.
        
        Args:
            sport_id: Sport ID (1 for MLB).
            season: Season year.
            
        Returns:
            Games data.
        """
        endpoint = "/games"
        params = {"sportId": sport_id}
        
        if season:
            params["season"] = season
        
        return self._make_request(endpoint, params)
    
    def get_standings(
        self,
        league_id: Optional[str] = None,
        season: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get season standings.
        
        Args:
            league_id: League ID(s) as string (e.g., '103,104' for AL and NL).
            season: Season year.
            
        Returns:
            Standings data.
        """
        endpoint = "/standings"
        params = {}
        
        if league_id:
            params["leagueId"] = league_id
        if season:
            params["season"] = season
        
        return self._make_request(endpoint, params)
    
    def get_teams(
        self,
        team_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get team information.
        
        Args:
            team_id: Specific team ID. If None, gets all teams.
            
        Returns:
            Team data.
        """
        endpoint = "/teams" if team_id is None else f"/teams/{team_id}"
        return self._make_request(endpoint)
    
    def close(self) -> None:
        """Close session and cleanup resources."""
        self.session.close()
        self.logger.info("API client session closed")
