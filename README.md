# 📊 Quantitative Portfolio Analyzer

A full-stack quantitative finance application that combines **Modern Portfolio Theory**, **Portfolio Optimization**, and **Monte Carlo Simulation** into an interactive web-based dashboard.

The project provides investors and analysts with a comprehensive risk analysis workspace by integrating statistical analysis, optimization techniques, and stochastic simulations through a FastAPI backend and a Streamlit frontend.

---

## 🚀 Features

- 📈 Historical financial data analysis
- 📊 Portfolio optimization using Modern Portfolio Theory
- 🎯 Maximum Sharpe Ratio portfolio optimization
- 🛡️ Minimum Variance portfolio optimization
- 📉 Efficient Frontier visualization
- 📋 Portfolio performance metrics
- 📊 Covariance and Correlation matrix analysis
- 💹 Monte Carlo (Geometric Brownian Motion) simulations
- ⚠️ Parametric Value at Risk (VaR) estimation
- 📌 Probability of portfolio loss estimation
- 🌐 REST API built with FastAPI
- 🎨 Interactive dashboard built with Streamlit
- 📈 Interactive Plotly visualizations

---

# 🏗️ Project Architecture

```
                    Historical Market Data
                              │
                              ▼
                  Financial Statistics Engine
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                                           ▼
 Portfolio Optimization                    Risk Analytics
 (Maximum Sharpe / Min Variance)        Monte Carlo Simulation
        │                                           │
        └─────────────────────┬─────────────────────┘
                              ▼
                      FastAPI REST Backend
                              │
                              ▼
                  Streamlit Interactive Dashboard
```

---

# 📂 Project Structure

```
Portfolio-Analyzer/
│
├── api/
│   └── app.py
│
├── app/
│   └── main.py
│
├── src/
│   ├── optimization.py
│   ├── simulation.py
│   ├── portfolio.py
│   ├── financial_statistics.py
│   └── ...
│
├── data/
│   └── processed/
│
├── images/
│
├── notebooks/
│
├── requirements.txt
│
└── README.md
```

---

# 📐 Mathematical Background

The project implements several quantitative finance techniques.

## Modern Portfolio Theory

Portfolio expected return

\[
E(R_p)=\sum_{i=1}^{n}w_iR_i
\]

Portfolio variance

\[
\sigma_p^2=w^T\Sigma w
\]

where

- **w** represents the portfolio weights
- **Σ** is the covariance matrix

---

## Maximum Sharpe Ratio

The optimal portfolio maximizes

\[
\frac{R_p-R_f}{\sigma_p}
\]

where

- \(R_p\) = portfolio return
- \(R_f\) = risk-free rate
- \(\sigma_p\) = portfolio volatility

---

## Minimum Variance Portfolio

Finds the allocation that minimizes

\[
w^T\Sigma w
\]

subject to

- Fully invested portfolio
- Long-only constraints

---

## Monte Carlo Simulation

Future portfolio values are simulated using a **Geometric Brownian Motion (GBM)** process

\[
dS=\mu Sdt+\sigma SdW
\]

allowing thousands of stochastic price paths to estimate future uncertainty.

---

## Value at Risk (VaR)

The project estimates the 95% Parametric Value at Risk using the portfolio volatility.

---

# 🖥️ Dashboard

The interactive dashboard allows users to:

- Select optimization strategy
- Set initial investment capital
- Configure risk-free rate
- Adjust simulation horizon
- Change the number of Monte Carlo paths

The dashboard displays:

- Optimal asset allocations
- Annualized expected return
- Portfolio volatility
- Parametric Value at Risk
- Probability of capital loss
- Monte Carlo simulation paths
- Future wealth percentiles

---

# ⚙️ Technologies Used

### Backend

- FastAPI
- Pydantic
- NumPy
- Pandas

### Frontend

- Streamlit
- Plotly

### Financial Modeling

- Modern Portfolio Theory
- Mean-Variance Optimization
- Monte Carlo Simulation
- Geometric Brownian Motion
- Value at Risk (VaR)

### Data Science

- NumPy
- Pandas
- Scikit-Learn
- Matplotlib
- Seaborn
- yfinance

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/Portfolio-Analyzer.git

cd Portfolio-Analyzer
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Backend

Start the FastAPI server

```bash
uvicorn api.app:app --reload
```

The API will be available at

```
http://localhost:8000
```

Swagger documentation

```
http://localhost:8000/docs
```

---

# ▶️ Running the Dashboard

Launch the Streamlit application

```bash
streamlit run app/main.py
```

The dashboard will automatically connect to the FastAPI backend.

---

# 📡 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/assets` | Returns available assets |
| POST | `/api/v1/optimize` | Computes optimal portfolio weights |
| POST | `/api/v1/simulate` | Runs Monte Carlo portfolio simulations |

---

# 📈 Example Outputs

The project generates

- Efficient Frontier
- Correlation Heatmap
- Covariance Matrix
- Monte Carlo Simulation Paths
- Portfolio Allocation Charts
- Portfolio Performance Metrics

---

# 🎯 Learning Objectives

This project demonstrates practical applications of

- Portfolio Optimization
- Quantitative Risk Management
- Financial Econometrics
- Numerical Optimization
- Monte Carlo Methods
- REST API Development
- Interactive Data Visualization
- Full-Stack Python Development

---

# 🔮 Future Improvements

- Black-Litterman Portfolio Optimization
- Conditional Value at Risk (CVaR)
- GARCH Volatility Forecasting
- Multi-factor Asset Pricing Models
- Live Market Data Streaming
- Portfolio Backtesting Engine
- Portfolio Rebalancing Strategies
- User Authentication
- Docker Deployment
- Cloud Deployment

---

# 📜 License

This project is developed for educational and research purposes.

---

# 👨‍💻 Author

**Ersi**

Econometrics • Quantitative Finance • Machine Learning

If you found this project useful, consider giving it a ⭐ on GitHub!