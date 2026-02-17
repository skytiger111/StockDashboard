import pandas as pd
import numpy as np

def calculate_indicators(df):
    """
    Calculate technical indicators for the given dataframe without pandas_ta.
    """
    if df is None or df.empty:
        return df
    
    # Copy to avoid modifying original
    df = df.copy()
    
    # Moving Averages
    df['SMA5'] = df['Close'].rolling(window=5).mean()
    df['SMA10'] = df['Close'].rolling(window=10).mean()
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA60'] = df['Close'].rolling(window=60).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    # Handle division by zero
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50) # Default to 50 if calculation fails
    
    # MACD (12, 26, 9)
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD_12_26_9'] = ema12 - ema26
    df['MACDs_12_26_9'] = df['MACD_12_26_9'].ewm(span=9, adjust=False).mean()
    df['MACDh_12_26_9'] = df['MACD_12_26_9'] - df['MACDs_12_26_9']
    
    # Bollinger Bands (20, 2)
    df['BBM_20_2.0'] = df['Close'].rolling(window=20).mean()
    std20 = df['Close'].rolling(window=20).std()
    df['BBU_20_2.0'] = df['BBM_20_2.0'] + (2 * std20)
    df['BBL_20_2.0'] = df['BBM_20_2.0'] - (2 * std20)
    
    # Volume MA
    df['VOL_SMA5'] = df['Volume'].rolling(window=5).mean()
    df['VOL_SMA20'] = df['Volume'].rolling(window=20).mean()
    
    # Standard Deviation for Volatility (20 days)
    df['STD20'] = df['Close'].rolling(window=20).std()
    
    return df
