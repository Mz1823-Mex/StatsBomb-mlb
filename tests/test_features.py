"""Tests for feature engineering."""

import pytest
import pandas as pd
import numpy as np


class TestFeatureCalculations:
    """Tests for sabermetric feature calculations."""

    @pytest.fixture
    def sample_batter(self):
        """Create sample batter data."""
        return {
            "at_bats": 500,
            "hits": 150,
            "doubles": 30,
            "triples": 2,
            "home_runs": 30,
            "walks": 60,
            "hit_by_pitch": 5,
            "sacrifice_flies": 2,
            "plate_appearances": 567,
            "strikeouts": 100,
        }
    
    @pytest.fixture
    def sample_pitcher(self):
        """Create sample pitcher data."""
        return {
            "innings_pitched": 200,
            "earned_runs": 60,
            "hits_allowed": 180,
            "walks": 50,
            "strikeouts": 200,
            "home_runs_allowed": 20,
        }
    
    def test_batting_average(self, sample_batter):
        """Test batting average calculation."""
        avg = sample_batter["hits"] / sample_batter["at_bats"]
        assert 0.0 <= avg <= 1.0
        assert abs(avg - 0.300) < 0.001  # .300 AVG
    
    def test_obp_calculation(self, sample_batter):
        """Test on-base percentage calculation."""
        numerator = (sample_batter["hits"] + 
                    sample_batter["walks"] + 
                    sample_batter["hit_by_pitch"])
        denominator = (sample_batter["at_bats"] + 
                      sample_batter["walks"] + 
                      sample_batter["hit_by_pitch"] + 
                      sample_batter["sacrifice_flies"])
        obp = numerator / denominator
        
        assert 0.0 <= obp <= 1.0
        assert obp > sample_batter["hits"] / sample_batter["at_bats"]  # OBP > AVG
    
    def test_slugging_percentage(self, sample_batter):
        """Test slugging percentage calculation."""
        singles = sample_batter["hits"] - (sample_batter["doubles"] + 
                                          sample_batter["triples"] + 
                                          sample_batter["home_runs"])
        total_bases = (singles + 
                      2 * sample_batter["doubles"] + 
                      3 * sample_batter["triples"] + 
                      4 * sample_batter["home_runs"])
        slg = total_bases / sample_batter["at_bats"]
        
        assert 0.0 <= slg <= 4.0
    
    def test_ops_calculation(self, sample_batter):
        """Test OPS (OBP + SLG) calculation."""
        # AVG
        avg = sample_batter["hits"] / sample_batter["at_bats"]
        
        # OBP
        obp = (sample_batter["hits"] + sample_batter["walks"] + sample_batter["hit_by_pitch"]) / \
              (sample_batter["at_bats"] + sample_batter["walks"] + sample_batter["hit_by_pitch"] + sample_batter["sacrifice_flies"])
        
        # SLG
        singles = sample_batter["hits"] - (sample_batter["doubles"] + sample_batter["triples"] + sample_batter["home_runs"])
        total_bases = singles + 2 * sample_batter["doubles"] + 3 * sample_batter["triples"] + 4 * sample_batter["home_runs"]
        slg = total_bases / sample_batter["at_bats"]
        
        ops = obp + slg
        
        assert 0.0 <= ops <= 5.0
        assert ops > obp  # OPS > OBP
        assert ops > slg   # OPS > SLG
    
    def test_era_calculation(self, sample_pitcher):
        """Test ERA calculation."""
        era = (sample_pitcher["earned_runs"] * 9) / sample_pitcher["innings_pitched"]
        
        assert 0.0 <= era
        assert abs(era - 2.70) < 0.01  # Should be ~2.70 ERA
    
    def test_whip_calculation(self, sample_pitcher):
        """Test WHIP calculation."""
        whip = (sample_pitcher["walks"] + sample_pitcher["hits_allowed"]) / sample_pitcher["innings_pitched"]
        
        assert 0.5 <= whip <= 3.0
        assert abs(whip - 1.15) < 0.01  # Should be ~1.15 WHIP
    
    def test_k9_calculation(self, sample_pitcher):
        """Test K/9 calculation."""
        k9 = (sample_pitcher["strikeouts"] * 9) / sample_pitcher["innings_pitched"]
        
        assert 0.0 <= k9 <= 14.0
        assert abs(k9 - 9.0) < 0.01  # Should be 9.0 K/9
    
    def test_bb9_calculation(self, sample_pitcher):
        """Test BB/9 calculation."""
        bb9 = (sample_pitcher["walks"] * 9) / sample_pitcher["innings_pitched"]
        
        assert 0.0 <= bb9
        assert abs(bb9 - 2.25) < 0.01  # Should be ~2.25 BB/9


class TestDataCleaning:
    """Tests for data cleaning operations."""
    
    @pytest.fixture
    def sample_data(self, sample_data):
        """Use sample data fixture from conftest."""
        return sample_data
    
    def test_no_negative_stats(self, sample_data):
        """Verify no negative values in count statistics."""
        count_cols = ["at_bats", "hits", "home_runs", "rbis"]
        for col in count_cols:
            if col in sample_data.columns:
                assert (sample_data[col] >= 0).all()
    
    def test_hits_less_than_at_bats(self, sample_data):
        """Verify hits <= at_bats."""
        if "hits" in sample_data.columns and "at_bats" in sample_data.columns:
            assert (sample_data["hits"] <= sample_data["at_bats"]).all()
    
    def test_home_runs_less_than_hits(self, sample_data):
        """Verify home_runs <= hits."""
        if "home_runs" in sample_data.columns and "hits" in sample_data.columns:
            assert (sample_data["home_runs"] <= sample_data["hits"]).all()
