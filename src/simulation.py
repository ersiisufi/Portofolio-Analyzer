# src/simulation.py
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class MonteCarloSimulator:
    """
    Simulates future pricing trajectories for optimized portfolios 
    using a Geometric Brownian Motion (GBM) stochastic framework.
    """
    def __init__(self, trading_days_per_year: int = 252):
        self.days_per_year = trading_days_per_year

    def simulate_gbm(
        self, 
        initial_value: float, 
        mu: float, 
        sigma: float, 
        n_days: int, 
        n_simulations: int
    ) -> np.ndarray:
        """
        Generates simulated matrix paths using GBM.
        
        Returns:
        --------
        np.ndarray
            A 2D array of shape (n_days + 1, n_simulations) containing price paths.
        """
        logger.info(f"Simulating {n_simulations} paths over {n_days} days (Drift: {mu:.4f}, Vol: {sigma:.4f}).")
        
        # Time step fraction
        dt = 1.0 / self.days_per_year
        
        # Structure the price grid array: Rows = Days, Columns = Individual Simulation Paths
        price_paths = np.zeros((n_days + 1, n_simulations))
        price_paths[0] = initial_value
        
        # Generate all random normal shocks ahead of time for performance acceleration
        random_shocks = np.random.normal(0, 1, (n_days, n_simulations))
        
        # Continuous compounding step translation loop
        drift_component = (mu - 0.5 * (sigma ** 2)) * dt
        vol_component = sigma * np.sqrt(dt)
        
        for t in range(1, n_days + 1):
            # Compound step: S_t = S_t-1 * exp(drift + shock)
            price_paths[t] = price_paths[t-1] * np.exp(drift_component + vol_component * random_shocks[t-1])
            
        return price_paths