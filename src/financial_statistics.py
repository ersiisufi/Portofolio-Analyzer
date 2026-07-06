import logging
import numpy as np
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)

class FinancialStatistics:
    """
    Computes statistical and econometric moments for financial asset return series.
    Supports both simple and log returns where appropriate.
    """
    def __init__(self, trading_days_per_year: int = 252):
        self.days_per_year = trading_days_per_year

    def compute_summary_statistics(self, simple_rets: pd.DataFrame, log_rets: pd.DataFrame) -> pd.DataFrame:
        """
        Generates a comprehensive econometric summary profile for all assets.
        """
        logger.info("Generating baseline financial statistics profiles...")
        stats_dict = {}
        
        for col in simple_rets.columns:
            # Annualized Return (Geometric mean for simple returns to capture compounding drag)
            # Prod(1 + R_i)^(252/N) - 1
            total_prod = (1 + simple_rets[col]).prod()
            n_obs = len(simple_rets[col])
            ann_return = (total_prod ** (self.days_per_year / n_obs)) - 1
            
            # Annualized Volatility (Daily standard deviation scaled by sqrt of trading days)
            ann_vol = simple_rets[col].std() * np.sqrt(self.days_per_year)
            
            # Distribution Shapes (Using log returns for structural symmetry)
            skew = log_rets[col].skew()
            kurt = log_rets[col].kurt()  # Excess Kurtosis (Normal distribution = 0)
            
            stats_dict[col] = {
                "Annualized Return": ann_return,
                "Annualized Volatility": ann_vol,
                "Daily Mean": simple_rets[col].mean(),
                "Daily Median": simple_rets[col].median(),
                "Skewness": skew,
                "Excess Kurtosis": kurt
            }
            
        return pd.DataFrame(stats_dict).T

    def get_matrices(self, simple_rets: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Calculates annualized covariance and asset correlation matrices."""
        logger.info("Computing asset covariance and correlation matrices.")
        return {
            "covariance": simple_rets.cov() * self.days_per_year,
            "correlation": simple_rets.corr()
        }