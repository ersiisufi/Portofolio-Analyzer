# api/app.py
import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure the root directory is accessible for local src imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.financial_statistics import FinancialStatistics
from src.optimization import PortfolioOptimizer
from src.simulation import MonteCarloSimulator
from src.portfolio import PortfolioEngine

app = FastAPI(
    title="Quantitative Risk Engine API",
    description="High-performance REST API calculating portfolio optimization matrices and stochastic path simulations.",
    version="1.0.0"
)

# Load data once at engine startup for maximum efficiency
DATA_PATH = os.path.join("data", "processed", "simple_returns.csv")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Missing processed historical returns at: {DATA_PATH}. Run data ingestion first.")

simple_returns = pd.read_csv(DATA_PATH, index_col="Date", parse_dates=True)
asset_names = simple_returns.columns.tolist()

# Pre-calculate annualized inputs via Phase 5 Statistics Engine
stats_engine = FinancialStatistics()
summary_stats = stats_engine.compute_summary_statistics(simple_returns, simple_returns)
matrices = stats_engine.get_matrices(simple_returns)
ann_returns = summary_stats["Annualized Return"].values
ann_cov = matrices["covariance"].values

# Define Pydantic Payload Schemas for Strong Data Validation
class OptimizationRequest(BaseModel):
    rf_rate: float = Field(..., ge=0.0, le=0.2, description="Risk-free rate assumption (e.g., 0.04)")

class SimulationRequest(BaseModel):
    strategy: str = Field(..., description="Target optimization strategy: 'max_sharpe' or 'min_variance'")
    initial_capital: float = Field(..., gt=0.0, description="Seed cash allocation pool")
    rf_rate: float = Field(..., ge=0.0, le=0.2)
    n_days: int = Field(252, ge=10, le=504, description="Trading days forward to simulate")
    n_simulations: int = Field(5000, ge=100, le=20000, description="Total parallel paths")

@app.get("/api/v1/assets")
def get_tracked_assets():
    """Returns list of tracked active tickers."""
    return {"assets": asset_names}

@app.post("/api/v1/optimize")
def run_portfolio_optimization(payload: OptimizationRequest):
    """Executes SLSQP solvers dynamically given a dynamic risk-free rate constraint."""
    try:
        optimizer = PortfolioOptimizer(rf_rate=payload.rf_rate)
        
        max_s_weights = optimizer.optimize_max_sharpe(ann_returns, ann_cov)
        min_v_weights = optimizer.optimize_min_variance(ann_returns, ann_cov)
        
        return {
            "assets": asset_names,
            "max_sharpe_weights": max_s_weights.tolist(),
            "min_variance_weights": min_v_weights.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solver execution failure: {str(e)}")

@app.post("/api/v1/simulate")
def run_stochastic_simulation(payload: SimulationRequest):
    """Calculates forward pricing paths and tail metrics dynamically using GBM."""
    try:
        optimizer = PortfolioOptimizer(rf_rate=payload.rf_rate)
        portfolio_engine = PortfolioEngine()
        simulator = MonteCarloSimulator()
        
        # Determine weight vector based on selected UI configuration
        if payload.strategy == "max_sharpe":
            weights = optimizer.optimize_max_sharpe(ann_returns, ann_cov)
        elif payload.strategy == "min_variance":
            weights = optimizer.optimize_min_variance(ann_returns, ann_cov)
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy selector key.")
            
        # Calculate dynamic portfolio returns/risk profile
        p_ret, p_vol, _ = portfolio_engine.calculate_metrics(weights, ann_returns, ann_cov, payload.rf_rate)
        
        # Execute fast multi-path GBM loop
        paths = simulator.simulate_gbm(
            initial_value=payload.initial_capital,
            mu=p_ret,
            sigma=p_vol,
            n_days=payload.n_days,
            n_simulations=payload.n_simulations
        )
        
        # Isolate terminal metrics distributions
        terminal_values = paths[-1, :]
        percentiles = np.percentile(terminal_values, [5, 50, 95])
        prob_loss = float(np.mean(terminal_values < payload.initial_capital) * 100)
        
        # Calculate Historical 95% Parametric VaR limit for the portfolio
        z_score = 1.645
        daily_vol = p_vol / np.sqrt(252)
        parametric_var_pct = (z_score * daily_vol)
        var_dollar_impact = payload.initial_capital * parametric_var_pct

        # Downsample tracking path lines to prevent payload bloat over HTTP JSON packets
        # Return first 100 paths for UI timeline visualization render
        visual_paths = paths[:, :100].tolist()

        return {
            "portfolio_annualized_return": float(p_ret),
            "portfolio_annualized_volatility": float(p_vol),
            "parametric_var_95_dollar": float(var_dollar_impact),
            "median_ending_value": float(percentiles[1]),
            "worst_case_5th_percentile": float(percentiles[0]),
            "best_case_95_percentile": float(percentiles[2]),
            "probability_of_capital_loss_pct": prob_loss,
            "simulated_paths_preview": visual_paths
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation path engine failure: {str(e)}")