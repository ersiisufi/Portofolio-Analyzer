import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    Handles data validation, filling missing exchange values, 
    and transforming prices into simple and log return matrices.
    """
    def __init__(self):
        pass

    def clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cleans raw data by dropping entirely blank rows and forward-filling missing pricing ticks."""
        logger.info("Starting data cleaning pipeline...")
        
        cleaned_df = df.dropna(how='all')
        
        initial_missing = cleaned_df.isnull().sum().sum()
        if initial_missing > 0:
            logger.warning(f"Detected {initial_missing} missing value(s) in raw dataset. Applying forward-fill (stale price assumption).")
            cleaned_df = cleaned_df.ffill().bfill() # Forward fill, backward fill any remaining edge elements
        else:
            logger.info("Data integrity check passed: Zero missing values detected.")
            
        return cleaned_df

    def calculate_returns(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Computes both simple and log daily returns for the given price matrix.
        
        Returns:
        --------
        (pd.DataFrame, pd.DataFrame) : (Simple Returns, Log Returns)
        """
        logger.info("Computing daily return vectors (Simple and Log variants)...")
        
        # Simple Returns: (P_t / P_t-1) - 1
        simple_returns = df.pct_change().dropna()
        
        # Log Returns: ln(P_t / P_t-1)
        log_returns = np.log(df / df.shift(1)).dropna()
        
        logger.info(f"Returns matrices generated. Active records: {len(simple_returns)} trading days.")
        return simple_returns, log_returns