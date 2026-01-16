# Earnings Announcements and Volatility

## Overview
This project quantifies the "volatility expansion" that occurs during discrete earnings events. 
While standard models often assume continuous price paths, earnings represent significant jumps. 
I analyze the relationship between baseline daily volatility and realized event moves across all GICS sectors 
in the S&P 500 around the past years earnings reports to identify volatility shocks in different VIX regimes using yfinance.

Key terms: Baseline Volatility (σ base): 10-day rolling standard deviation of log returns prior to the event;
Earnings Multiplier (M): The ratio of the absolute realized earnings move to the baseline daily volatility (∣R 
event ∣/σ base); Directional Bias: Probability of positive price gaps (Win Rate) and mean return per sector.

## Key Results
- Average Multiplier: The cross-sector average multiplier is 3.32x, meaning earnings moves are typically three standard deviation events relative to quiet periods.
- Sector Dispersion: Communication Services and Health Care exhibit the highest multipliers (>4.1x), signaling higher "jump risk" than Energy or Utilities (~2.0x).
- VIX Normalization: Multipliers contract significantly in High VIX regimes (1.47x) vs. Low VIX regimes (3.69x). This suggests that while absolute moves are larger in crashes, the relative shock of earnings is diminished when market-wide noise is high.
- Directional Skew: Energy showed a notably lower win rate (40%), suggesting a "sell-the-news" tendency in the observed period.

## Known Limitations & Future Work (The "IV" Roadmap)
- Realized vs. Implied (Current Limitation): This model uses Realized Volatility (P-measure) as a proxy for expectation. A true quant approach requires Implied Volatility (Q-measure) from the option chain.
- The "IV Crush" Analysis: Future iterations will integrate historical option chains to measure the Volatility Risk Premium (VRP) specifically for the earnings event window.
- Better Data: Plan to transition from yfinance to Polygon.io or ThetaData to extract the ATM Straddle price at T−1 to compute a true "Market Implied Move" and compare it against the "Realized Move."
- Jump-Diffusion Modeling: Use these results to calibrate a Merton Jump-Diffusion model, treating the earnings multiplier as the jump intensity parameter.

## Files
- `earnings_vol.ipynb`: Main notebook
- `src/histAnalyzer.py`: Main class-based implementation of historical volatility approach
- `data/`: Exported results as CSVs
