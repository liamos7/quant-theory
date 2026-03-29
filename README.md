# Quantitative Finance: Theory and Applications

A collection of quantitative finance projects exploring derivatives pricing, 
risk management, and trading strategies. Combines mathematical theory with 
practical implementations in Python.

**Author:** Liam O'Shaughnessy  
**Background:** Princeton Physics (Senior) | HEP Research at CERN  
**Contact:** [email](liamos1618@gmail.com) | [LinkedIn](https://www.linkedin.com/in/liam-o-shaughnessy-155b66238/)

---

## Theoretical Foundation

I've compiled [comprehensive notes](notes/Quantitative_Finance_Notes.pdf) 
covering the mathematical foundations of quantitative finance:

- Stochastic calculus and martingale theory
- Derivatives pricing (Black-Scholes, exotic options)
- Interest rate and credit models
- Portfolio optimization and risk management
- Numerical methods (Monte Carlo, finite difference)

These notes synthesize material from Shreve, Bjork, and academic papers.

---

## Projects

### 1. [Volatility Surface Modeling](projects/01_volatility_surface/)
**Objective:** Model implied volatility dynamics using local and stochastic 
volatility frameworks.

**Key Techniques:**
- Implied volatility surface extraction from SPY options
- SVI/SSVI parametrization with arbitrage detection
- Dupire local volatility implementation
- Heston stochastic volatility calibration (Carr-Madan FFT and Lewis methods)
- Volatility risk premium estimation

**Results:** Identified and corrected arbitrage violations in raw SVI, 
calibrated Heston, estimated vol risk premium.

**Tech Stack:** Python, NumPy, SciPy, Plotly, yfinance

[View Project →](projects/01_volatility_surface/)

---
### 2. [Earnings Announcements and Volatility](/projects/02_earnings_vol)

**Objective:** Understand how historical volatility and implied volatility behave with stock behavior around earnings announcements.

**Key Techniques:**
* Historical Volatility (HV) baseline vs. Event-driven Realized Volatility
* "Earnings multiplier" analysis ($RV_{earnings} / \sigma_{baseline}$) across GICS sectors
* VIX regime conditioning
* Directional bias and "Win Rate" statistical testing
* IV analysis (coming soon with better historical data)

**Results:** Identified that the Communication Services sector exhibit the highest shock multiplier (~4.2x), while Energy displays the lowest (~2.0x). Confirmed that earnings multipliers contract during High-VIX regimes due to volatility normalization.

**Tech Stack:** Python, Pandas, Matplotlib, Seaborn, yfinance

[View Project →](projects/02_earnings_vol/)

---

### 3. [Options Greeks and Dynamic Hedging](projects/03_greeks_hedging/) *(Coming Soon)*
Simulation of delta-gamma hedging with transaction costs and comparison to 
theoretical costs.

---

## Tech Stack

- **Languages:** Python, C++ (for performance-critical components)
- **Libraries:** NumPy, SciPy, Pandas, Matplotlib/Plotly
- **Data:** Yahoo Finance, CBOE, Quandl
- **Tools:** Jupyter, Git, VS Code

---

## Background

I'm a Princeton physics senior with research experience in high-energy 
experimental physics at CERN, focusing on machine learning applications for 
particle detection and classification. I became interested in quantitative 
finance while exploring applications of stochastic processes and statistical 
methods to financial markets.

These projects represent my self-directed learning in mathematical finance, 
combining rigorous theory with practical implementation.

---

## Contact

Interested in collaborating or have feedback? Reach out:
- **Email:** lo8603@princeton.edu
- **LinkedIn:** [Liam O'Shaughnessy](https://www.linkedin.com/in/liam-o-shaughnessy-155b66238/)
- **GitHub:** [@liamos7](https://github.com/liamos7)

---

## References

Key resources used in developing these projects:
- Shreve, S. (2004). *Stochastic Calculus for Finance II*
- Bjork, T. (2009). *Arbitrage Theory in Continuous Time*
- Koralov and Sinai (1992). *Theory of Probability and Random Processes*
- Schilling and Partzsch (2010). *Brownian Motion*
- Gatheral, J. (2006). *The Volatility Surface*
- Taleb, N. (1997). *Dynamic Hedging*
