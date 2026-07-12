# src/optimization.py
import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from src.portfolio import PortfolioEngine

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    Uses numerical optimization solvers to isolate Maximum Sharpe 
    and Minimum Variance asset allocation strategies.
    """
    def __init__(self, rf_rate: float = 0.04):
        self.rf_rate = rf_rate
        self.engine = PortfolioEngine()

    def optimize_max_sharpe(self, ann_mean_returns: pd.Series, ann_cov_matrix: pd.DataFrame) -> np.ndarray:
        """Finds the allocation that maximizes the portfolio Sharpe Ratio."""
        logger.info("Executing Max Sharpe Optimization solver.")
        num_assets = len(ann_mean_returns)
        
        # Objective function to MINIMIZE: Negative Sharpe Ratio
        def objective(weights):
            _, _, p_sharpe = self.engine.calculate_metrics(weights, ann_mean_returns, ann_cov_matrix, self.rf_rate)
            return -p_sharpe
            
        # Equality Constraint: Sum of weights must equal 1.0
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        # Bounds: Long-only strategy (no short selling, weights between 0 and 1)
        bounds = tuple((0, 1) for _ in range(num_assets))
        # Equal initial guess distribution
        initial_guess = num_assets * [1.0 / num_assets]
        
        result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        return result.x

    def optimize_min_variance(self, ann_mean_returns: pd.Series, ann_cov_matrix: pd.DataFrame) -> np.ndarray:
        """Finds the allocation that minimizes total portfolio volatility."""
        logger.info("Executing Minimum Variance Optimization solver.")
        num_assets = len(ann_mean_returns)
        
        # Objective function to MINIMIZE: Volatility
        def objective(weights):
            _, p_vol, _ = self.engine.calculate_metrics(weights, ann_mean_returns, ann_cov_matrix, self.rf_rate)
            return p_vol
            
        constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_guess = num_assets * [1.0 / num_assets]
        
        result = minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
        return result.x