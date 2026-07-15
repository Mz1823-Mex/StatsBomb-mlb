"""Data transformation utilities."""

import logging
from typing import Dict, List

import pandas as pd
import numpy as np


class DataTransformer:
    """Transform and standardize data."""

    def __init__(self, config: Dict):
        """Initialize transformer.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def transform(
        self,
        df: pd.DataFrame,
        standardize_columns: bool = True,
        convert_types: bool = True,
    ) -> pd.DataFrame:
        """Apply all transformations to dataframe.
        
        Args:
            df: Input dataframe.
            standardize_columns: Whether to standardize column names.
            convert_types: Whether to convert column types.
            
        Returns:
            Transformed dataframe.
        """
        self.logger.info("Starting data transformation")
        
        df_transformed = df.copy()
        
        if standardize_columns:
            df_transformed = self._standardize_columns(df_transformed)
        
        if convert_types:
            df_transformed = self._convert_types(df_transformed)
        
        self.logger.info("Transformation complete")
        
        return df_transformed
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase snake_case.
        
        Args:
            df: Input dataframe.
            
        Returns:
            Dataframe with standardized column names.
        """
        # Convert to lowercase and replace spaces with underscores
        df.columns = (
            df.columns
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        
        self.logger.info(f"Standardized {len(df.columns)} column names")
        
        return df
    
    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types.
        
        Args:
            df: Input dataframe.
            
        Returns:
            Dataframe with converted types.
        """
        # Convert ID columns to int
        id_cols = [col for col in df.columns if "id" in col.lower()]
        for col in id_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                except Exception as e:
                    self.logger.warning(f"Could not convert {col} to int: {e}")
        
        # Convert date columns
        date_cols = [col for col in df.columns if "date" in col.lower()]
        for col in date_cols:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception as e:
                    self.logger.warning(f"Could not convert {col} to datetime: {e}")
        
        # Convert numeric columns
        numeric_cols = df.select_dtypes(include=["object"]).columns
        for col in numeric_cols:
            try:
                # Try to convert to numeric
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception as e:
                self.logger.debug(f"Could not convert {col} to numeric: {e}")
        
        self.logger.info("Type conversion complete")
        
        return df
    
    def merge_datasets(
        self,
        df_batting: pd.DataFrame,
        df_pitching: pd.DataFrame,
        on: List[str] = None,
    ) -> pd.DataFrame:
        """Merge batting and pitching datasets.
        
        Args:
            df_batting: Batting statistics dataframe.
            df_pitching: Pitching statistics dataframe.
            on: Columns to merge on.
            
        Returns:
            Merged dataframe.
        """
        if on is None:
            on = ["player_id", "player_name", "season"]
        
        self.logger.info(f"Merging datasets on columns: {on}")
        
        # Filter to only common columns for merge
        merge_cols = [col for col in on if col in df_batting.columns and col in df_pitching.columns]
        
        if not merge_cols:
            self.logger.warning("No common columns found for merge")
            return df_batting
        
        # Merge with outer join to keep all records
        df_merged = df_batting.merge(
            df_pitching,
            on=merge_cols,
            how="outer",
            suffixes=("_batting", "_pitching"),
        )
        
        self.logger.info(f"Merged dataset has {len(df_merged)} rows and {len(df_merged.columns)} columns")
        
        return df_merged
    
    def create_player_season_view(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Create player-season aggregated view.
        
        Args:
            df: Input dataframe (likely at game level).
            
        Returns:
            Player-season aggregated dataframe.
        """
        self.logger.info("Creating player-season aggregated view")
        
        # Group by player and season
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        agg_dict = {col: "sum" for col in numeric_cols}
        
        df_agg = df.groupby(
            [col for col in ["player_id", "player_name", "season"] if col in df.columns]
        ).agg(agg_dict).reset_index()
        
        self.logger.info(f"Created aggregated view with {len(df_agg)} rows")
        
        return df_agg
