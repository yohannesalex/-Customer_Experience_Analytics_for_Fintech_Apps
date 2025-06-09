import os
import pandas as pd
import talib
import matplotlib.pyplot as plt
import seaborn as sns
from pynance import PyNance  # Optional (if using PyNance)

# ----------------------------
# 1. Load and Prepare Data
# ----------------------------
def load_stock_data(stock_symbol, data_dir="data/yfinance_data"):
    """Load historical stock data from CSV files."""
    file_path = os.path.join(data_dir, f"{stock_symbol}_historical_data.csv")
    try:
        data = pd.read_csv(file_path, parse_dates=['Date'], index_col='Date')
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        assert all(col in data.columns for col in required_cols), \
            f"Missing columns in {stock_symbol} data. Required: {required_cols}"
        return data.sort_index()  # Sort by date
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Example: Load AAPL data
stock_symbols = ['AAPL', 'AMZN', 'GOOG', 'META', 'MSFT', 'NVDA', 'TSLA']
all_data = {symbol: load_stock_data(symbol) for symbol in stock_symbols}

# ----------------------------
# 2. Calculate Technical Indicators (TA-Lib)
# ----------------------------
def calculate_indicators(data):
    """Add TA-Lib indicators to DataFrame."""
    if data is None:
        return None
    # Moving Averages
    data['SMA_50'] = talib.SMA(data['Close'], timeperiod=50)
    data['EMA_20'] = talib.EMA(data['Close'], timeperiod=20)
    # RSI (Relative Strength Index)
    data['RSI_14'] = talib.RSI(data['Close'], timeperiod=14)
    # MACD (Moving Average Convergence Divergence)
    data['MACD'], data['MACD_Signal'], _ = talib.MACD(data['Close'])
    return data

# Apply to all stocks
for symbol, data in all_data.items():
    all_data[symbol] = calculate_indicators(data)

# ----------------------------
# 3. PyNance Financial Metrics (Optional)
# ----------------------------
def calculate_pynance_metrics(data):
    """Example: Use PyNance for additional metrics (if installed)."""
    try:
        pn = PyNance(data)
        data['Sharpe_Ratio'] = pn.sharpe_ratio()
        data['Volatility'] = pn.volatility()
        return data
    except ImportError:
        print("PyNance not installed. Skipping...")
        return data

# Uncomment if using PyNance
# for symbol, data in all_data.items():
#     all_data[symbol] = calculate_pynance_metrics(data)

# ----------------------------
# 4. Visualize Data
# ----------------------------
def plot_technical_indicators(data, symbol):
    """Plot key technical indicators."""
    if data is None:
        return
    plt.figure(figsize=(14, 10))
    
    # Subplot 1: Price and Moving Averages
    plt.subplot(3, 1, 1)
    plt.plot(data['Close'], label='Close Price', color='blue')
    plt.plot(data['SMA_50'], label='50-day SMA', color='orange')
    plt.plot(data['EMA_20'], label='20-day EMA', color='green')
    plt.title(f'{symbol} - Price and Moving Averages')
    plt.legend()
    
    # Subplot 2: RSI
    plt.subplot(3, 1, 2)
    plt.plot(data['RSI_14'], label='RSI (14)', color='purple')
    plt.axhline(70, linestyle='--', color='red', alpha=0.5)
    plt.axhline(30, linestyle='--', color='green', alpha=0.5)
    plt.title('Relative Strength Index (RSI)')
    plt.legend()
    
    # Subplot 3: MACD
    plt.subplot(3, 1, 3)
    plt.plot(data['MACD'], label='MACD', color='blue')
    plt.plot(data['MACD_Signal'], label='Signal Line', color='red')
    plt.title('MACD')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f"plots/{symbol}_technical_indicators.png")  # Save plot
    plt.close()  # Close figure to free memory

# Create plots directory if it doesn't exist
os.makedirs("plots", exist_ok=True)

# Generate plots for all stocks
for symbol, data in all_data.items():
    plot_technical_indicators(data, symbol)

# ----------------------------
# 5. Save Processed Data (Optional)
# ----------------------------
def save_processed_data(data, symbol, output_dir="data/processed"):
    """Save DataFrame with indicators to CSV."""
    os.makedirs(output_dir, exist_ok=True)
    data.to_csv(os.path.join(output_dir, f"{symbol}_processed.csv"))

for symbol, data in all_data.items():
    save_processed_data(data, symbol)

print("Quantitative analysis completed! Check the 'plots/' folder for visualizations.")