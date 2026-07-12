
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class RiskEngine:
    """
    A quantitative risk engine computing tail-risk, drawdown, 
    and downside metrics for financial time series.
    """
    def __init__(self):
        pass

    def calculate_max_drawdown(self, price_series: pd.Series) -> float:
        """
        Calculates the maximum peak-to-trough drawdown for a given price series.
        """
        logger.info(f"Calculating Maximum Drawdown for series: {price_series.name}")
        
        # Calculate the running cumulative maximum peak
        rolling_peak = price_series.cummax()
        
        # Calculate drawdown series
        drawdowns = (price_series - rolling_peak) / rolling_peak
        
        # Find the maximum peak-to-trough drop
        max_drawdown = drawdowns.min()
        
        return float(max_drawdown)

    def calculate_historical_var_cvar(self, returns_series: pd.Series, confidence_level: float = 0.95) -> tuple[float, float]:
        """
        Computes Historical Value at Risk (VaR) and Conditional VaR (CVaR / Expected Shortfall).
        
        Parameters:
        -----------
        returns_series : pd.Series
            The daily simple or log returns of the asset.
        confidence_level : float
            The confidence threshold (e.g., 0.95 for 95% VaR).
            
        Returns:
        --------
        (VaR, CVaR) as a tuple of floats. Both values are returned as positive loss numbers.
        """
        logger.info(f"Calculating Historical VaR/CVaR ({confidence_level*100}%) for: {returns_series.name}")
        
        # Clean any remaining NaNs just in case
        clean_rets = returns_series.dropna()
        
        # Calculate the percentile threshold for loss (e.g., 5th percentile for 95% confidence)
        alpha = 1 - confidence_level
        var_threshold = np.percentile(clean_rets, alpha * 100)
        
        # VaR is typically expressed as a positive loss magnitude
        var = -var_threshold
        
        # CVaR is the mean of all returns that fall below the VaR threshold
        tail_losses = clean_rets[clean_rets <= var_threshold]
        cvar = -tail_losses.mean()
        
        return float(var), float(cvar)
    
    def calculate_sharpe_ratio(self, returns_series: pd.Series, risk_free_rate_annual: float = 0.04) -> float:
        """
        Calculates the annualized Sharpe Ratio for an asset return series.
        """
        logger.info(f"Calculating Annualized Sharpe Ratio for: {returns_series.name}")
        
        # Convert annual risk-free rate to daily base approximation
        daily_rf = risk_free_rate_annual / 252
        
        excess_returns = returns_series - daily_rf
        daily_mean_excess = excess_returns.mean()
        daily_std = returns_series.std()
        
        if daily_std == 0:
            return 0.0
            
        # Scale the ratio from daily space to annual space
        sharpe_ratio = (daily_mean_excess / daily_std) * np.sqrt(252)
        return float(sharpe_ratio)

    def calculate_sortino_ratio(self, returns_series: pd.Series, risk_free_rate_annual: float = 0.04) -> float:
        """
        Calculates the annualized Sortino Ratio focusing strictly on downside deviation.
        """
        logger.info(f"Calculating Annualized Sortino Ratio for: {returns_series.name}")
        
        daily_rf = risk_free_rate_annual / 252
        excess_returns = returns_series - daily_rf
        
        # Isolate only negative excess returns; set positive ones to zero
        downside_returns = np.minimum(0, excess_returns)
        
        # Calculate downside variance and standard deviation
        downside_variance = np.mean(downside_returns ** 2)
        daily_downside_std = np.sqrt(downside_variance)
        
        if daily_downside_std == 0:
            return 0.0
            
        # Scale to annual metric
        sortino_ratio = (excess_returns.mean() / daily_downside_std) * np.sqrt(252)
        return float(sortino_ratio)