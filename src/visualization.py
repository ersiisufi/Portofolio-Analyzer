# src/visualization.py
import os
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

class FinancialVisualizer:
    """
    Generates professional-grade charts for financial data.
    Ensures charts are automatically saved down to the images/ or reports/ directory.
    """
    def __init__(self, output_dir: str = "../images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
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
        
        filepath = os.path.join(self.output_dir, filename)
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
        
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()
        logger.info(f"Return distributions chart exported to: {filepath}")