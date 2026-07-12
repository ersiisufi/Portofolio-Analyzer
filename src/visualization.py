# src/visualization.py
import logging
from pathlib import Path
import os

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from src.conifg import IMAGE_DIR, REPORT_DIR

logger = logging.getLogger(__name__)

class FinancialVisualizer:
    """
    Generates professional-grade charts for financial data.
    Ensures charts are automatically saved down to the images/ or reports/ directory.
    """
    def __init__(self, output_dir = IMAGE_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Apply professional chart stylings globally
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

    def plot_correlation_heatmap(self, corr_matrix: pd.DataFrame, filename: str = "correlation_heatmap.png") -> None:
        """Generates and saves a clean, presentation-ready correlation heatmap."""
        logger.info("Generating correlation heatmap visualization.")
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            cmap="coolwarm", 
            vmin=-1, 
            vmax=1, 
            linewidths=0.5,
            fmt=".2f"
        )
        plt.title("Portfolio Asset Correlation Matrix", fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300)
        plt.close()
        logger.info(f"Correlation heatmap exported to: {filepath}")

    def plot_return_distributions(self, log_rets: pd.DataFrame, filename: str = "return_distributions.png") -> None:
        """Plots kernel density estimates of asset log returns to visually spot skewness and heavy tails."""
        logger.info("Generating return distribution charts.")
        
        plt.figure(figsize=(10, 6))
        for col in log_rets.columns:
            sns.kdeplot(log_rets[col], label=col, fill=True, alpha=0.2)
            
        plt.title("Asset Log Return Distributions (KDE)", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Daily Log Return")
        plt.ylabel("Density")
        plt.legend(loc="upper right")
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300)
        plt.close()
        logger.info(f"Return distributions chart exported to: {filepath}")

    def plot_portfolio_drawdowns(self, price_df: pd.DataFrame, filename: str = "asset_drawdowns.png") -> None:
        """
        Computes and plots historical underwater drawdown curves for all assets.
        """
        logger.info("Generating historical drawdown curve charts.")
        
        plt.figure(figsize=(12, 6))
        
        # Calculate individual drawdown time series
        rolling_peaks = price_df.cummax()
        drawdown_series = (price_df - rolling_peaks) / rolling_peaks
        
        # Plot each asset path
        for col in drawdown_series.columns:
            plt.plot(drawdown_series.index, drawdown_series[col], label=col, linewidth=1.5)
            
        plt.title("Historical Asset Drawdown Comparison (Underwater Plot)", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Date")
        plt.ylabel("Drawdown (%)")
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y*100:.0f}%'))
        plt.legend(loc="lower left")
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        logger.info(f"Drawdown charts successfully exported to: {filepath}")
    
    def plot_efficient_frontier(
        self, 
        sim_metrics: np.ndarray, 
        max_sharpe_point: tuple, 
        min_var_point: tuple, 
        filename: str = "efficient_frontier.png"
    ) -> None:
        """
        Plots the Efficient Frontier scatter map of random portfolios 
        and marks the specific locations of the optimal strategies.
        """
        logger.info("Generating Efficient Frontier scatter visualization.")
        
        plt.figure(figsize=(10, 6))
        
        # Extract simulated arrays
        # sim_metrics[1, :] is volatility (X-axis), sim_metrics[0, :] is return (Y-axis)
        sc = plt.scatter(
            sim_metrics[1, :], 
            sim_metrics[0, :], 
            c=sim_metrics[2, :], 
            cmap='viridis', 
            marker='o', 
            s=4, 
            alpha=0.4
        )
        
        # Mark Max Sharpe Portfolio (Red Star)
        plt.scatter(max_sharpe_point[1], max_sharpe_point[0], color='red', marker='*', s=200, label='Max Sharpe Ratio')
        
        # Mark Min Variance Portfolio (Blue Star)
        plt.scatter(min_var_point[1], min_var_point[0], color='blue', marker='*', s=200, label='Minimum Variance')
        
        plt.title("Efficient Frontier & Optimal Asset Allocations", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Annualized Volatility (Risk)", fontsize=11)
        plt.ylabel("Annualized Expected Return", fontsize=11)
        
        # Add a sleek colorbar to show Sharpe Ratio values
        cbar = plt.colorbar(sc)
        cbar.set_label('Sharpe Ratio', rotation=270, labelpad=15)
        
        plt.legend(loc='upper left', frameon=True, facecolor='white')
        plt.tight_layout()
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        logger.info(f"Efficient Frontier plot exported successfully to: {filepath}")