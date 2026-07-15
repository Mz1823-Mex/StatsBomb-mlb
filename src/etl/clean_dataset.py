"""Data cleaning and preprocessing utilities."""

import logging
from typing import Dict, List, Optional

import pandas as pd
import numpy as np


class DataCleaner:
    """Clean and preprocess raw data."""

    def __init__(self, config: Dict):
        """Initialize cleaner.
        
        Args:
            config: Configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def clean(
        self,
        df: pd.DataFrame,
        remove_duplicates: bool = True,
        handle_missing: bool = True,
        remove_outliers: bool = False,
    ) -> pd.DataFrame:
        """Apply all cleaning operations to dataframe.
        
        Args:
            df: Input dataframe.
            remove_duplicates: Whether to remove duplicate rows.
            handle_missing: Whether to handle missing values.
            remove_outliers: Whether to remove outliers.
            
        Returns:
            Cleaned dataframe.
        """
        self.logger.info(f"Starting data cleaning on {len(df)} rows")
        
        df_clean = df.copy()
        
        # Remove duplicates
        if remove_duplicates:
            initial_rows = len(df_clean)
            df_clean = self._remove_duplicates(df_clean)
            removed = initial_rows - len(df_clean)
            if removed > 0:
                self.logger.info(f"Removed {removed} duplicate rows")
        
        # Handle missing values
        if handle_missing:
            df_clean = self._handle_missing_values(df_clean)
        
        # Remove outliers
        if remove_outliers:
            initial_rows = len(df_clean)
            df_clean = self._remove_outliers(df_clean)
            removed = initial_rows - len(df_clean)
            if removed > 0:
                self.logger.info(f"Removed {removed} outlier rows")
        
        self.logger.info(f"Cleaning complete. Final rows: {len(df_clean)}")
        
        return df_clean
    
    def _remove_duplicates(
        self,
        df: pd.DataFrame,
        subset: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Remove duplicate rows.
        
        Args:
            df: Input dataframe.
            subset: Columns to check for duplicates.
            
        Returns:
            Dataframe with duplicates removed.
        """
        return df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values with context-dependent strategy.
        
        Args:
            df: Input dataframe.
            
        Returns:
            Dataframe with missing values handled.
        """
        config = self.config.get("data", {}).get("validation", {})
        max_missing_percent = config.get("max_missing_percent", 30)
        
        # Check for columns with too many missing values
        missing_pct = (df.isnull().sum() / len(df)) * 100
        cols_to_drop = missing_pct[missing_pct > max_missing_percent].index.tolist()
        
        if cols_to_drop:
            self.logger.warning(f"Dropping columns with >{max_missing_percent}% missing: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
        
        # Fill missing values with zeros for counting stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ["home_runs", "rbis", "walks", "strikeouts", "earned_runs", "hits_allowed"]:
                df[col] = df[col].fillna(0)
            else:
                df[col] = df[col].fillna(df[col].mean())
        
        # Fill categorical with forward fill then backward fill
        cat_cols = df.select_dtypes(include=["object", "category"]).columns
        for col in cat_cols:
            df[col] = df[col].fillna(method="ffill").fillna(method="bfill")
        
        return df
    
    def _remove_outliers(
        self,
        df: pd.DataFrame,
        method: str = "iqr",
        threshold: float = 3.0,
    ) -> pd.DataFrame:
        """Remove outliers using IQR or zscore method.
        
        Args:
            df: Input dataframe.
            method: 'iqr' or 'zscore'.
            threshold: Threshold for outlier detection.
            
        Returns:
            Dataframe with outliers removed.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if method == "iqr":
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        elif method == "zscore":
            from scipy import stats
            z_scores = np.abs(stats.zscore(df[numeric_cols]))
            df = df[(z_scores < threshold).all(axis=1)]
        
        return df.reset_index(drop=True)
    
    def validate_schema(
        self,
        df: pd.DataFrame,
        required_columns: List[str],
    ) -> bool:
        """Validate dataframe has required columns.
        
        Args:
            df: Input dataframe.
            required_columns: List of required column names.
            
        Returns:
            True if valid, False otherwise.
        """
        missing = set(required_columns) - set(df.columns)
        
        if missing:
            self.logger.error(f"Missing required columns: {missing}")
            return False
        
        self.logger.info("Schema validation passed")
        return True
