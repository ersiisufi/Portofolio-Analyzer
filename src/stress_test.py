import logging
import numpy as np
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)

class PortfolioStressTester:
    """
    Evaluates optimized portfolio allocations under historical 
    macroeconomic shocks and market crisis regimes.
    """
    def __init__(self):
        # Define historical shock windows present within the 2016-2026 data range
        self.scenarios = {
            "2020 COVID Crash": ("2020-02-19", "2020-03-23"),
            "2022 Inflationary Bear Market": ("2022-01-03", "2022-12-30"),
            "2024 Tech/Carry-Trade Shock": ("2024-07-16", "2024-08-07")
        }

    def run_stress_test(self, simple_returns: pd.DataFrame, weights: np.ndarray) -> pd.DataFrame:
        """
        Calculates the performance of a portfolio across defined crisis windows.
        """
        logger.info("Initiating historical portfolio stress testing sequence.")
        
        # Calculate daily portfolio returns sequence: R_p = Sum(w_i * R_i)
        portfolio_returns = simple_returns.dot(weights)
        
        results = {}
        
        for scenario_name, (start, end) in self.scenarios.items():
            try:
                # Isolate the crisis window from our return time series
                scenario_rets = portfolio_returns.loc[start:end]
                
                if scenario_rets.empty:
                    logger.warning(f"Scenario '{scenario_name}' date bounds fell outside dataset range.")
                    continue
                
                # Calculate Cumulative Return over the crash window
                cumulative_return = (1 + scenario_rets).prod() - 1
                
                # Calculate Peak-to-Trough Maximum Drawdown during this specific crash
                wealth_index = (1 + scenario_rets).cumprod()
                rolling_peak = wealth_index.cummax()
                drawdowns = (wealth_index - rolling_peak) / rolling_peak
                max_dd = drawdowns.min()
                
                results[scenario_name] = {
                    "Start Date": start,
                    "End Date": end,
                    "Total Return": f"{cumulative_return * 100:.2f}%",
                    "Max Drawdown": f"{max_dd * 100:.2f}%"
                }
            except Exception as e:
                logger.error(f"Failed to process stress scenario '{scenario_name}': {str(e)}")
                
        return pd.DataFrame(results).T