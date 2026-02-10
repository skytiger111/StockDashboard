import pandas as pd

def scan_potential_stocks(data_dict):
    """
    Scan for potential stocks based on squeeze and dry-up logic.
    """
    results = []
    
    for symbol, df in data_dict.items():
        if df is None or df.empty or len(df) < 60:
            continue
            
        last_row = df.iloc[-1]
        
        # 1. 均線糾結 (Squeeze)
        ma20 = last_row['SMA20']
        ma60 = last_row['SMA60']
        squeeze_val = abs(ma20 - ma60) / ma60
        is_squeeze = squeeze_val < 0.05
        
        # 2. 量能急凍 (Dry-up)
        # Assuming we calculated VOL_SMA20 in technical.py
        is_dry_up = last_row['Volume'] < 0.7 * last_row['VOL_SMA20']
        
        # 3. 低波動 (Low Volatility)
        # STD20 compared to historical range
        std20_current = last_row['STD20']
        std20_history = df['STD20'].dropna()
        if len(std20_history) > 0:
            std20_rank = (std20_history < std20_current).mean()
            is_low_vol = std20_rank < 0.3 # Lower 30% percentile
        else:
            is_low_vol = False
            
        if is_squeeze or is_dry_up or is_low_vol:
            conditions = []
            if is_squeeze: conditions.append("均線糾結")
            if is_dry_up: conditions.append("量能急凍")
            if is_low_vol: conditions.append("波動率低")
            
            results.append({
                "代碼": symbol,
                "均線糾結%": round(squeeze_val * 100, 2),
                "量能比": round(last_row['Volume'] / last_row['VOL_SMA20'], 2) if last_row['VOL_SMA20'] > 0 else 0,
                "符合條件": ", ".join(conditions),
                "原始波動度": round(std20_current, 2),
                "波動百分位": round(std20_rank * 100, 2) if is_low_vol else 0
            })
            
    return pd.DataFrame(results)
