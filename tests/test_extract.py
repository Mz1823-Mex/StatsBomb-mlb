"""Tests for data extraction module."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.api.mlb_client import MLBClient


class TestMLBClient:
    """Tests for MLBClient."""

    @pytest.fixture
    def client(self):
        """Create MLBClient instance."""
        return MLBClient()
    
    def test_client_initialization(self, client):
        """Test client initializes with correct defaults."""
        assert client.base_url == "https://statsapi.mlb.com/api/v1"
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.session is not None
    
    def test_custom_initialization(self):
        """Test client initializes with custom parameters."""
        client = MLBClient(
            base_url="http://custom.api",
            timeout=60,
            max_retries=5,
        )
        
        assert client.base_url == "http://custom.api"
        assert client.timeout == 60
        assert client.max_retries == 5
    
    @patch('src.api.mlb_client.requests.Session.get')
    def test_get_people_success(self, mock_get, client):
        """Test successful player data retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "people": [
                {
                    "id": 123456,
                    "fullName": "Test Player",
                    "position": {"code": "C"},
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Call method
        result = client.get_people(season=2026)
        
        # Verify
        assert result == mock_response.json.return_value
        mock_get.assert_called_once()
    
    @patch('src.api.mlb_client.requests.Session.get')
    def test_get_player_stat_hitting(self, mock_get, client):
        """Test retrieval of hitting statistics."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "stats": [{"stats": {"hitting": {"avg": ".300"}}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = client.get_player_stat(
            player_id=543829,
            group="hitting",
            season=2026
        )
        
        assert result == mock_response.json.return_value
    
    @patch('src.api.mlb_client.requests.Session.get')
    def test_get_standings_success(self, mock_get, client):
        """Test retrieval of season standings."""
        mock_response = Mock()
        mock_response.json.return_value = {"records": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = client.get_standings(
            league_id="103,104",
            season=2026
        )
        
        assert result == mock_response.json.return_value
    
    def test_close_session(self, client):
        """Test session closes properly."""
        assert client.session is not None
        client.close()
        # Session should be closed
        # (actual verification would depend on session state)
