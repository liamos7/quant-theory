import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
import warnings
warnings.filterwarnings('ignore')
import os

# using historical volatility
class HistoricalVolEarningsAnalyzer:
    # constructor
    def __init__(self, lookback_days=365, vol_window=10):
        self.results = [] # future df
        self.sector_map = {} # dictionary to get sector from ticker
        self.lookback_days = lookback_days # days to look back for earnings
        self.vol_window = vol_window # days to compute historical volatility

    # get tickers with sectors
    def get_sp500_with_sectors(self, limit=None):
        try:
            # use requests to not get denied
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
            sp500 = pd.read_html(html)[0]
            sp500['Symbol'] = sp500['Symbol'].str.replace('.', '-', regex=False)
            self.sector_map = dict(zip(sp500['Symbol'], sp500['GICS Sector']))
            tickers = sp500['Symbol'].tolist()

            # prioritize liquid
            priority = ['AAPL','MSFT','GOOGL','AMZN','NVDA','META','TSLA','JPM','V','JNJ']
            tickers = sp500['Symbol'].tolist()
            priority = [t for t in priority if t in tickers]
            other = [t for t in tickers if t not in priority]

            return (priority + other)[:limit] if limit else priority + other
            
        except:
            # if wiki is broken/blocks
            self.sector_map = {
                'AAPL': 'Information Technology',
                'MSFT': 'Information Technology',
                'GOOGL': 'Communication Services',
                'NVDA': 'Information Technology',
                'META': 'Communication Services',
                'TSLA': 'Consumer Discretionary'
            }
            return list(self.sector_map.keys())

    # convert to tz-aware NY timestamps (yfinance throws exceptions otherwise)
    @staticmethod
    def ensure_nyse_timestamp(ts):
        ts = pd.Timestamp(ts)
        if ts.tzinfo is None:
            return ts.tz_localize('America/New_York', ambiguous='NaT', nonexistent='shift_forward')
        else:
            return ts.tz_convert('America/New_York')

    # get historical baseline volatility 
    def get_baseline_volatility(self, ticker, earnings_date, window=None):
        if window is None:
            window = self.vol_window
        try:
            earnings_date = self.ensure_nyse_timestamp(earnings_date)
            stock = yf.Ticker(ticker)

            # (look back window * 2) days to ensure enough trading days
            start_date = earnings_date - timedelta(days=window*2)
            end_date = earnings_date - timedelta(days=1)
            
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty or len(hist) < 2:
                return None, None

            # calc returns
            hist['ret'] = hist['Close'].pct_change()
            hist = hist.dropna()
            if hist.empty:
                return None, None
            daily_vol = hist['ret'].std()
            stock_price = hist['Close'].iloc[-1]
            
            # sd as percentage
            baseline_vol_pct = daily_vol * 100 
            return baseline_vol_pct, stock_price
            
        except Exception as e:
            print(f"Error computing vol for {ticker}: {e}")
            return None, None

    # calc realized move (absolute)
    def calculate_realized_move(self, ticker, earnings_date):
        try:
            earnings_date = self.ensure_nyse_timestamp(earnings_date)
            stock = yf.Ticker(ticker)
            
            # fetch small window around date
            hist = stock.history(start = (earnings_date - timedelta(days=4)), end = (earnings_date + timedelta(days=4)))
            if len(hist) < 2: 
                return None, None
                
            # find where earnings date is and get neighboring prices
            idx = hist.index.get_indexer([earnings_date], method='nearest')[0]
            if idx < 1 or idx >= len(hist)-1: 
                return None, None
            pre_price = hist['Close'].iloc[idx-1]
            post_price = hist['Close'].iloc[idx+1]

            # calc return and move
            raw_return = (post_price - pre_price) / pre_price * 100
            abs_move = abs(raw_return)
            
            return abs_move, raw_return # Return both
            
        except:
            return None, None

    # calc VIX regime for volatility
    def get_vix_regime(self, date):
        try:
            date = self.ensure_nyse_timestamp(date)
            vix = yf.Ticker("^VIX")
            hist = vix.history(start = (date - timedelta(days=3)), end = (date + timedelta(days=1)))
            
            if not hist.empty:
                # decide the VIX level: low/med/high
                vix_level = hist['Close'].iloc[-1]
                if vix_level < 15:
                    return "Low", vix_level
                elif vix_level < 25:
                    return "Medium", vix_level
                else:
                    return "High", vix_level
        except:
            pass 
        return "Unknown", None

    # analyze one ticker
    def analyze_ticker(self, ticker, sector="Unknown"):
        try:
            stock = yf.Ticker(ticker)
            earnings = stock.earnings_dates
            if earnings is None or earnings.empty:
                return
         
            # filter earnings within lookback-now
            cutoff = datetime.now() - timedelta(days=self.lookback_days)
            cutoff = self.ensure_nyse_timestamp(cutoff)
            right_now = self.ensure_nyse_timestamp(datetime.now())
            recent_earnings = earnings[(earnings.index >= cutoff) & (earnings.index <= right_now)]
            if recent_earnings.empty:
                return
            print(f"Found {len(recent_earnings)} earnings for {ticker}")

            # analyze recent earnings events
            for earnings_date in recent_earnings.index:
                # get baseline vol
                baseline_vol, stock_price = self.get_baseline_volatility(ticker, earnings_date)
                if baseline_vol is None or baseline_vol == 0:
                    continue

                # get realized move around earnings
                realized_move, raw_return = self.calculate_realized_move(ticker, earnings_date)
                if realized_move is None:
                    continue

                # get VIX
                vix_regime, vix_level = self.get_vix_regime(earnings_date)

                # earnings multiplier - how much bigger was the move than normal?
                multiplier = realized_move / baseline_vol

                self.results.append({
                    'ticker': ticker,
                    'sector': sector,
                    'earnings_date': earnings_date.strftime('%Y-%m-%d'),
                    'stock_price': stock_price,
                    'baseline_vol_1d': baseline_vol,
                    'raw_return': raw_return,
                    'realized_move': realized_move,
                    'earnings_multiplier': multiplier,
                    'vix_regime': vix_regime
                })

                print(f"  Date: {earnings_date.strftime('%Y-%m-%d')} | "
                      f"Normal Vol: {baseline_vol:.1f}% | "
                      f"Realized: {realized_move:.1f}% | "
                      f"Multiplier: {multiplier:.1f}x")

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")

    # do the analysis
    def run_analysis(self, num_tickers):
        print("HISTORICAL VOLATILITY EARNINGS ANALYSIS")
        print(f"Analyzing earnings from past {self.lookback_days} days using historical stock volatility")

        tickers = self.get_sp500_with_sectors(limit=num_tickers)
        for i, ticker in enumerate(tickers, 1):
            sector = self.sector_map.get(ticker, "Unknown")
            print(f"[{i}/{len(tickers)}] {ticker} ({sector})")
            self.analyze_ticker(ticker, sector)
            print()

        return pd.DataFrame(self.results)
        
    # print out summary statistics
    def generate_report(self, df):
        if df.empty:
            return "No data collected."

        # update aggregation for new metric
        ticker_summary = df.groupby('ticker').agg({
            'sector': 'first',
            'baseline_vol_1d': 'mean',
            'realized_move': 'mean',
            'earnings_multiplier': 'mean',
            'earnings_date': 'count'
        }).rename(columns={'earnings_date':'count'}).round(2)
    
        summary_lines = ["\nPER-TICKER SUMMARY:"]
        summary_lines.append("Ticker | Count | Avg Normal Vol | Avg Realized | Avg Multiplier")
        for ticker, row in ticker_summary.iterrows():
            summary_lines.append(
                f"{ticker:<6} | {row['count']:<5} | "
                f"{row['baseline_vol_1d']:.2f}%         | {row['realized_move']:.2f}%       | {row['earnings_multiplier']:.2f}x"
            )
    
        overall_stats = f"""
    OVERALL STATISTICS:
    • Sample Size: {len(df)} earnings events
    • Avg Normal Daily Vol: {df['baseline_vol_1d'].mean():.2f}%
    • Avg Realized Earnings Move: {df['realized_move'].mean():.2f}%
    • Avg Earnings Multiplier: {df['earnings_multiplier'].mean():.2f}x
    
    Takeaway: On average, stocks in this list move {df['earnings_multiplier'].mean():.1f} times more 
    on earnings days than they do on a normal trading day.
    """
    
        return "\n".join(summary_lines) + "\n" + overall_stats

        
    # rank sectors by earnings multiplier
    def analyze_sector_impact(self, df):
        if df.empty:
            print("No data available for sector analysis.")
            return None
            
        sector_stats = df.groupby('sector').agg({
            'earnings_multiplier': ['mean', 'median', 'std', 'count'],
            'realized_move': 'mean'
        }).round(2)
        
        # flatten columns, sort by the mean multiplier
        sector_stats.columns = ['Avg_Multiplier', 'Median_Multiplier', 'Std_Dev', 'Sample_Size', 'Avg_Realized_Move']
        sector_stats = sector_stats.sort_values(by='Avg_Multiplier', ascending=False)
        
        print("SECTOR IMPACT RANKING (By Multiplier)")
        print(sector_stats)

        # top sector
        top_sector = sector_stats.index[0]
        top_val = sector_stats.iloc[0]['Avg_Multiplier']
        
        print(f"\nInsight: The {top_sector} sector shows the highest relative impact,")
        print(f"moving {top_val}x its normal daily range during earnings.")
        
        return sector_stats

    # generate bar chart ranking sectors multiplier
    def plot_sector_impact(self, df):
        if df.empty:
            print("No data to plot.")
            return

        sector_means = df.groupby('sector')['earnings_multiplier'].mean().sort_values(ascending=False)

        # plotting
        plt.figure(figsize=(12, 7))
        sns.set_theme(style="whitegrid")
        colors = sns.color_palette("viridis", len(sector_means))
        ax = sns.barplot(x=sector_means.values, y=sector_means.index, palette=colors)
        plt.axvline(x=1.0, color='red', linestyle='--', alpha=0.7, label='Normal Day Baseline')
        
        # labels
        plt.title('Average Earnings Volatility Multiplier by Sector', fontsize=16, pad=20)
        plt.xlabel('Multiplier (Realized Move / Normal Daily Vol)', fontsize=12)
        plt.ylabel('Sector', fontsize=12)
        plt.legend()
        
        # values on the bars
        for i, v in enumerate(sector_means.values):
            ax.text(v + 0.1, i, f"{v:.2f}x", color='black', va='center', fontweight='bold')

        plt.tight_layout()
        plt.show()

    # analyze how multiplier changes across VIX regimes
    def analyze_vix_regime(self, df):
        if df.empty:
            return "No data for VIX analysis."

        vix_stats = df.groupby('vix_regime').agg({
            'earnings_multiplier': ['mean', 'count'],
            'realized_move': 'mean',
            'baseline_vol_1d': 'mean'
        }).round(2)

        print("VIX REGIME PERFORMANCE")
        print(vix_stats)
        return vix_stats
        
    # create heatmap showing avg multiplier for sector vs VIX
    def plot_vix_interaction(self, df):
        if df.empty:
            return

        # pivot table for heatmap
        pivot = df.pivot_table(values='earnings_multiplier', index='sector', columns='vix_regime', aggfunc='mean')
        
        # sort regimes
        order = ['Low', 'Medium', 'High']
        existing_order = [o for o in order if o in pivot.columns]
        pivot = pivot[existing_order]

        # plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot, annot=True, cmap="YlGnBu", fmt=".2f", cbar_kws={'label': 'Avg Multiplier'})
        plt.title('Impact Heatmap: Sector x VIX Regime', fontsize=15)
        plt.xlabel('VIX Regime (Market Volatility Context)')
        plt.ylabel('Sector')
        plt.tight_layout()
        plt.show()

    # calculate probability of positive move and avg return per sector
    def analyze_directional_bias(self, df):
        if df.empty:
            return "No data for directional analysis."

        # create bool column for positive moves
        df['is_positive'] = df['raw_return'] > 0
        
        direction_stats = df.groupby('sector').agg({
            'raw_return': ['mean', 'median'],
            'is_positive': 'mean',
            'ticker': 'count'
        }).round(2)

        direction_stats.columns = ['Avg_Return', 'Median_Return', 'Win_Rate', 'Sample_Size']
        direction_stats = direction_stats.sort_values(by='Win_Rate', ascending=False)

        print("DIRECTIONAL BIAS BY SECTOR")
        print(direction_stats)
        return direction_stats

    # bar chart of percentage of positive earnings moves by sector
    def plot_directional_bias(self, df):
        if df.empty:
            return
        
        sector_win_rate = df.groupby('sector')['is_positive'].mean().sort_values() * 100

        # plot
        plt.figure(figsize=(10, 6))
        colors = ['#ff9999' if x < 50 else '#66b3ff' for x in sector_win_rate.values]
        ax = sector_win_rate.plot(kind='barh', color=colors)
        plt.axvline(x=50, color='black', linestyle='--', alpha=0.5)
        plt.title('Percent of Positive Earnings Moves by Sector', fontsize=14)
        plt.xlabel('Win Rate (%)')
        plt.xlim(0, 100)
        
        # annotate percentages
        for i, v in enumerate(sector_win_rate.values):
            ax.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold')
            
        plt.tight_layout()
        plt.show()

    # save to CSV
    def export_results(self, df, sector_df=None, vix_df=None, direction_df=None, folder="earnings_exports"):
        # makedir
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # raw data
        raw_filename = f"{folder}/raw_earnings_data_{timestamp}.csv"
        df.to_csv(raw_filename, index=False)
        print(f"Saved Raw Data: {raw_filename}")

        # sector impact
        if sector_df is not None:
            sector_filename = f"{folder}/sector_impact_{timestamp}.csv"
            sector_df.to_csv(sector_filename)
            print(f"Saved Sector Analysis: {sector_filename}")

        # VIX analysis
        if vix_df is not None:
            vix_filename = f"{folder}/vix_regime_impact_{timestamp}.csv"
            vix_df.to_csv(vix_filename)
            print(f"Saved VIX Analysis: {vix_filename}")

        # directional bias
        if direction_df is not None:
            direction_filename = f"{folder}/directional_bias_{timestamp}.csv"
            direction_df.to_csv(direction_filename)
            print(f"Saved Directional Analysis: {direction_filename}")

