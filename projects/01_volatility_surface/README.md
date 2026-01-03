# Local and Stochastic Volatility Models

## Overview
This project explores the implied volatility surface from both static (local vol) 
and dynamic (stochastic vol) perspectives. Using SPY options data, I:

1. Compute realized volatility under the physical measure (P)
2. Extract implied volatility from option prices (risk-neutral measure Q)
3. Fit parametric models (SVI/SSVI) to the IV surface
4. Derive local volatility via Dupire's formula
5. Calibrate Heston stochastic volatility model
6. Estimate the volatility risk premium

## Key Results
- **Arbitrage detection**: Raw SVI exhibits butterfly violations; SSVI fixes this, along with proper smoothing
- **Heston calibration**: κ=5.0, θ=0.025, σ=0.65, ρ=-0.54, v₀=0.016
- **Vol risk premium**: Q-vol exceeds P-vol by 1.5%, indicating buyers willing to pay more than justified

## Technical Implementation
- **Data**: Yahoo Finance API (SPY options, 2022-2026)
- **Models**: Black-Scholes IV inversion, SVI/SSVI parametrization, Dupire local vol, Heston characteristic function pricing
- **Optimization**: Scipy least_squares (SVI), differential_evolution (Heston)
- **Visualization**: Plotly 3D surfaces

## Known Limitations

1. **Data quality**: Yahoo Finance can have stale quotes
   - Filtered by volume/OI, but some illiquid options remain
   - Could improve by using Bloomberg/CBOE data

2. **Heston calibration**: Sensitive to initial conditions
   - Used differential_evolution (global search) to mitigate
   - Still possible to find local minima; could improve with better bounds or penalty functions
   - Could use Lewis instead of Carr-Madan, but large runtime differences

3. **VRP calculation**: Looks backward (P) vs forward (Q)
   - Assumes past 30 days predicts next 30 days
   - Market may know something we don't (earnings, Fed meetings, etc.)

## Future Work

1. Analyze more assets
  
2. Compare Heston vs Local Vol for exotic pricing (barrier option pricing in both models, difference in Greeks)
   
3. Add more stochastic vol models (SABR)

4. Machine learning for vol forecasting

## Files
- `local_and_stochastic_vol.ipynb`: Main analysis
- See [quant-theory notes](link) for mathematical background

## References
- Dupire (1994) - Pricing with a Smile
- Heston (1993) - Closed-Form Solution for Options with Stochastic Volatility
- Lewis (2001) - A Simple Option Formula for General Jump-Diffusion and Other Exponential Levy Processes
