import logging
import numpy as np
import pandas as pd
from typing import Tuple, Dict

logger = logging.getLogger(__name__)

class PortfolioEngine:
    """
    Handles mathematical modeling for portfolio aggregation, 
    risk-return evaluation, and random portfolio generation.
    """
    def __init__(self, trading_days_per_year: int = 252):
        self.days_per_year = trading_days_per_year

    def calculate_metrics(
        self, 
        weights: np.ndarray, 
        ann_mean_returns: pd.Series, 
        ann_cov_matrix: pd.DataFrame, 
        rf_rate: float = 0.04
    ) -> Tuple[float, float, float]:
        """
        Computes the annualized performance statistics for a specific weight vector.
        
        Returns:
        --------
        (Portfolio Return, Portfolio Volatility, Sharpe Ratio)
        """
        # Expected Return: w^T * R
        p_return = np.sum(ann_mean_returns * weights)
        
        # Expected Volatility: sqrt(w^T * Sigma * w)
        p_variance = np.dot(weights.T, np.dot(ann_cov_matrix, weights))
        p_volatility = np.sqrt(p_variance)
        
        # Sharpe Ratio
        p_sharpe = (p_return - rf_rate) / p_volatility if p_volatility > 0 else 0.0
        
        return float(p_return), float(p_volatility), float(p_sharpe)

    def generate_random_portfolios(
        self, 
        num_portfolios: int, 
        ann_mean_returns: pd.Series, 
        ann_cov_matrix: pd.DataFrame, 
        rf_rate: float = 0.04
    ) -> Dict[str, np.ndarray]:
        """
        Generates random allocation matrices to simulate the risk-return field.
        """
        logger.info(f"Simulating {num_portfolios} random allocations for the Efficient Frontier.")
        num_assets = len(ann_mean_returns)
        
        results = np.zeros((3, num_portfolios))
        weights_record = []
        
        for i in range(num_portfolios):
            # Generate random numbers and normalize so the sum of weights equals 1.0 (fully invested)
            weights = np.random.random(num_assets)
            weights /= np.sum(weights)
            weights_record.append(weights)
            
            p_ret, p_vol, p_sharpe = self.calculate_metrics(weights, ann_mean_returns, ann_cov_matrix, rf_rate)
            results[0, i] = p_ret
            results[1, i] = p_vol
            results[2, i] = p_sharpe
            
        return {
            "metrics": results, # Rows: [Return, Volatility, Sharpe]
            "weights": np.array(weights_record)
        }