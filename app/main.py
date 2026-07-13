# app/main.py
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Page Configuration Setup
st.set_page_config(
    page_title="Quantitative Risk Workspace",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Institutional Portfolio Optimization & Risk Workspace")
st.markdown("An interactive econometric dashboard rendering real-time matrix solvers and stochastic projections.")

# Backend Base API Endpoint URL
API_URL = "http://localhost:8000/api/v1"

# --- Sidebar Inputs Control Layer ---
st.sidebar.header("🛠️ Model Parameter Controls")

initial_capital = st.sidebar.number_input(
    "Seed Investment Capital ($)", 
    min_value=1000, 
    max_value=10000000, 
    value=10000, 
    step=1000
)

rf_rate_pct = st.sidebar.slider(
    "Risk-Free Rate Assumption (%)", 
    min_value=0.0, 
    max_value=10.0, 
    value=4.0, 
    step=0.1
)
rf_rate = rf_rate_pct / 100.0

strategy_selector = st.sidebar.selectbox(
    "Target Strategy Deployment",
    options=["max_sharpe", "min_variance"],
    format_func=lambda x: "Maximum Sharpe Ratio" if x == "max_sharpe" else "Minimum Variance Floor"
)

sim_paths = st.sidebar.slider("Parallel Simulation Paths Count", min_value=500, max_value=10000, value=2000, step=500)
sim_days = st.sidebar.slider("Forward Horizons Tracked (Trading Days)", min_value=63, max_value=504, value=252, step=63)

# --- Fetch API Core Calculations ---
try:
    # 1. Trigger Optimization Request
    opt_response = requests.post(f"{API_URL}/optimize", json={"rf_rate": rf_rate}).json()
    
    # 2. Trigger Simulation/Risk Request
    sim_payload = {
        "strategy": strategy_selector,
        "initial_capital": initial_capital,
        "rf_rate": rf_rate,
        "n_days": sim_days,
        "n_simulations": sim_paths
    }
    sim_response = requests.post(f"{API_URL}/simulate", json=sim_payload).json()
    
    # --- Layout Grid Metric Cards Display Layer ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ann. Expected Return", f"{sim_response['portfolio_annualized_return']*100:.2f}%")
    with col2:
        st.metric("Ann. Portfolio Volatility", f"{sim_response['portfolio_annualized_volatility']*100:.2f}%")
    with col3:
        st.metric("95% 1-Day Parametric VaR", f"${sim_response['parametric_var_95_dollar']:,.2f}")
    with col4:
        st.metric("Probability of Capital Loss", f"{sim_response['probability_of_capital_loss_pct']:.2f}%")

    st.markdown("---")

    # --- Allocation Distribution & Path Visualization Section ---
    viz_col1, viz_col2 = st.columns([1, 2])

    with viz_col1:
        st.subheader("🎯 Optimal Allocation Weights")
        
        # Parse corresponding engine array vectors
        target_weights_key = "max_sharpe_weights" if strategy_selector == "max_sharpe" else "min_variance_weights"
        weights_data = opt_response[target_weights_key]
        assets = opt_response["assets"]
        
        weights_df = pd.DataFrame({
            "Asset Ticker": assets,
            "Target Weight Allocation": weights_data
        })
        
        # Display crisp clean interactive pie structure charts via Plotly
        fig_pie = go.Figure(data=[go.Pie(
            labels=weights_df["Asset Ticker"], 
            values=weights_df["Target Weight Allocation"],
            hole=0.4,
            marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        )])
        fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=280)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Format printing visual tabular layout mapping
        st.dataframe(
            weights_df.style.format({"Target Weight Allocation": "{:.2%}"}),
            use_container_width=True,
            hide_index=True
        )

    with viz_col2:
        st.subheader("🔮 Forward Capital Projections (Stochastic GBM Paths Preview)")
        
        # Reconstruct paths matrix array out of nested JSON response lists
        raw_paths_preview = np.array(sim_response["simulated_paths_preview"])
        days_axis = np.arange(raw_paths_preview.shape[0])
        
        fig_line = go.Figure()
        
        # Plot downsampled trajectory lines paths overlay
        for i in range(raw_paths_preview.shape[1]):
            fig_line.add_trace(go.Scatter(
                x=days_axis, 
                y=raw_paths_preview[:, i], 
                mode='lines', 
                line=dict(width=0.6),
                opacity=0.4,
                showlegend=False
            ))
            
        fig_line.update_layout(
            xaxis_title="Trading Days Forward",
            yaxis_title="Portfolio Capital Net Asset Value ($)",
            margin=dict(t=20, b=20, l=20, r=20),
            height=360,
            template="plotly_white"
        )
        st.plotly_chart(fig_line, use_container_width=True)

    # --- Distribution Bracket Summaries ---
    st.markdown("---")
    st.subheader("📈 Forward Capital Distribution Percentile Brackets")
    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.info(f"**95% Confidence Floor (5th Percentile):** ${sim_response['worst_case_5th_percentile']:,.2f}")
    with p_col2:
        st.success(f"**Median Expected Target (50th Percentile):** ${sim_response['median_ending_value']:,.2f}")
    with p_col3:
        st.info(f"**Optimistic Growth Ceiling (95th Percentile):** ${sim_response['best_case_95_percentile']:,.2f}")

except requests.exceptions.ConnectionError:
    st.error("❌ Unable to connect to the Back-End Risk API. Please verify that your FastAPI daemon service app is running on port 8000.")
except Exception as e:
    st.error(f"❌ Application interface runtime encountered an unexpected failure condition: {str(e)}")