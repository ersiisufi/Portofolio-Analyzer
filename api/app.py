# api/app.py
import os
import sys
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

# Ensure the root directory is accessible for local src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.financial_statistics import FinancialStatistics
from src.optimization import PortfolioOptimizer
from src.simulation import MonteCarloSimulator
from src.portfolio import PortfolioEngine

app = FastAPI(
    title="Dynamic Quantitative Risk Engine API",
    version="2.0.0"
)

# Helper function to fetch returns on demand
def fetch_dynamic_returns(tickers: List[str], start_date: str = "2016-01-01", end_date: str = "2026-01-01") -> pd.DataFrame:
    """Fetches historical price data and computes simple returns for any given tickers."""
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False)
        # Handle MultiIndex if yfinance returns it
        if isinstance(data.columns, pd.MultiIndex):
            adj_close = data['Close']
        else:
            adj_close = data['Adj Close'] if 'Adj Close' in data else data['Close']
            
        # Standardize single asset outputs to DataFrame format
        if isinstance(adj_close, pd.Series):
            adj_close = adj_close.to_frame()
            
        simple_returns = adj_close.pct_change().dropna()
        return simple_returns
    except Exception as e:
        raise RuntimeError(f"Failed fetching data from Yahoo Finance: {str(e)}")

# Updated Request Schemas to accept custom asset vectors
class OptimizationRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=10, description="List of tickers to optimize")
    rf_rate: float = Field(..., ge=0.0, le=0.2)

class SimulationRequest(BaseModel):
    tickers: List[str] = Field(..., min_items=2, max_items=10)
    strategy: str = Field(..., description="'max_sharpe' or 'min_variance'")
    initial_capital: float = Field(..., gt=0.0)
    rf_rate: float = Field(..., ge=0.0, le=0.2)
    n_days: int = Field(252, ge=10, le=504)
    n_simulations: int = Field(2000, ge=100, le=20000)

@app.post("/api/v1/optimize")
def run_portfolio_optimization(payload: OptimizationRequest):
    """Dynamically downloads and computes SLSQP matrix optimizations for any user-defined assets."""
    try:
        # 1. Fetch data dynamically
        simple_returns = fetch_dynamic_returns(payload.tickers)
        actual_assets = simple_returns.columns.tolist()
        
        # 2. Run statistical processing mapping
        stats_engine = FinancialStatistics()
        summary_stats = stats_engine.compute_summary_statistics(simple_returns, simple_returns)
        matrices = stats_engine.get_matrices(simple_returns)
        
        ann_returns = summary_stats["Annualized Return"].values
        ann_cov = matrices["covariance"].values
        
        # 3. Optimize weights vector
        optimizer = PortfolioOptimizer(rf_rate=payload.rf_rate)
        max_s_weights = optimizer.optimize_max_sharpe(ann_returns, ann_cov)
        min_v_weights = optimizer.optimize_min_variance(ann_returns, ann_cov)
        
        return {
            "assets": actual_assets,
            "max_sharpe_weights": max_s_weights.tolist(),
            "min_variance_weights": min_v_weights.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulate")
def run_stochastic_simulation(payload: SimulationRequest):
    """Dynamically calculates path matrices and tail limits for custom selected universes."""
    try:
        simple_returns = fetch_dynamic_returns(payload.tickers)
        actual_assets = simple_returns.columns.tolist()
        
        stats_engine = FinancialStatistics()
        summary_stats = stats_engine.compute_summary_statistics(simple_returns, simple_returns)
        matrices = stats_engine.get_matrices(simple_returns)
        ann_returns = summary_stats["Annualized Return"].values
        ann_cov = matrices["covariance"].values
        
        optimizer = PortfolioOptimizer(rf_rate=payload.rf_rate)
        portfolio_engine = PortfolioEngine()
        simulator = MonteCarloSimulator()
        
        if payload.strategy == "max_sharpe":
            weights = optimizer.optimize_max_sharpe(ann_returns, ann_cov)
        else:
            weights = optimizer.optimize_min_variance(ann_returns, ann_cov)
            
        p_ret, p_vol, _ = portfolio_engine.calculate_metrics(weights, ann_returns, ann_cov, payload.rf_rate)
        
        paths = simulator.simulate_gbm(
            initial_value=payload.initial_capital,
            mu=p_ret,
            sigma=p_vol,
            n_days=payload.n_days,
            n_simulations=payload.n_simulations
        )
        
        terminal_values = paths[-1, :]
        percentiles = np.percentile(terminal_values, [5, 50, 95])
        prob_loss = float(np.mean(terminal_values < payload.initial_capital) * 100)
        
        parametric_var_95_dollar = payload.initial_capital * (1.645 * (p_vol / np.sqrt(252)))
        visual_paths = paths[:, :100].tolist()

        return {
            "portfolio_annualized_return": float(p_ret),
            "portfolio_annualized_volatility": float(p_vol),
            "parametric_var_95_dollar": float(parametric_var_95_dollar),
            "median_ending_value": float(percentiles[1]),
            "worst_case_5th_percentile": float(percentiles[0]),
            "best_case_95_percentile": float(percentiles[2]),
            "probability_of_capital_loss_pct": prob_loss,
            "simulated_paths_preview": visual_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))