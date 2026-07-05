import os
import pandas as pd
import yfinance as yf
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class FinancialDataLoader:
    """
    A professional-grade utility to fetch, validate, and store 
    historical financial asset data from Yahoo Finance.
    """
    def __init__(self, data_dir: str = "../data/raw"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def fetch_historical_data(
        self, 
        tickers: List[str], 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetches Adjusted Close prices for a list of tickers.
        
        Parameters:
        -----------
        tickers : List[str]
            List of equity or ETF ticker symbols.
        start_date : str
            Start date string in 'YYYY-MM-DD' format.
        end_date : str
            End date string in 'YYYY-MM-DD' format.
            
        Returns:
        --------
        pd.DataFrame
            A cleaned DataFrame containing Adjusted Close prices with dates as index.
        """
        logger.info(f"Initiating market data download for tickers: {tickers} from {start_date} to {end_date}")        
        try:
            # We download Adjusted Close to properly account for dividends and stock splits
            data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
            
            # Handle the edge case of a single ticker returning a Series instead of a DataFrame
            if isinstance(data, pd.Series):
                data = data.to_frame(name=tickers[0])
                
            return data
            
        except Exception as e:
            logger.error(f"An error occurred during data retrieval: {e}")
            return pd.DataFrame()

    def save_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """Saves the retrieved DataFrame to the raw data directory."""
        if df.empty:
            logger.warning("Cannot save empty DataFrame.")
            return
        
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath)
        logger.info(f"Raw data successfully archived at: {filepath}")