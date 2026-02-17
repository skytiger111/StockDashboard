import pandas as pd

def calculate_health_score(df):
    """
    Calculate health score for a stock based on processed dataframe.
    Returns (score, rating, reason_list)
    """
    if df is None or df.empty or len(df) < 60:
        return 0.0, "數據不足", []

    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]
    
    score = 0.0
    reasons = []
    
    # 趨勢與策略面 (40%) - 融入主人「右側交易」邏輯
    if last_row['Close'] > last_row['SMA20']:
        score += 1.0
        reasons.append("收盤在月線上 (+1)")
    if last_row['Close'] > last_row['SMA60']:
        score += 1.0
        reasons.append("收盤在季線上 (+1)")
    
    # 右側交易強度確認 (MA5 > MA10 且 Price > MA10)
    if last_row['SMA5'] > last_row['SMA10'] and last_row['Close'] > last_row['SMA10']:
        score += 2.0
        reasons.append("右側交易訊號：5MA 站上 10MA 且股價站穩 (+2)")
    elif last_row['Close'] > last_row['SMA10']:
        score += 1.0
        reasons.append("股價站上 10MA (+1)")
        
    # 動能面 (30%)
    if last_row['RSI'] > 50:
        score += 1.5
        reasons.append("RSI > 50 (+1.5)")
    if last_row['Volume'] > last_row['VOL_SMA5']:
        score += 1.5
        reasons.append("量增 (+1.5)")
        
    # 型態面 (30%)
    # Using MACDh_12_26_9 for histogram
    if last_row['MACDh_12_26_9'] > 0:
        score += 1.5
        reasons.append("MACD紅柱 (+1.5)")
    if last_row['Close'] > last_row['BBM_20_2.0']:
        score += 1.5
        reasons.append("站上布林中軌 (+1.5)")
        
    # 扣分項
    daily_return = (last_row['Close'] - prev_row['Close']) / prev_row['Close']
    if last_row['Close'] < last_row['SMA20'] and daily_return < -0.03:
        score -= 2.0
        reasons.append("破月線且重挫 (-2)")
        
    # Final clamping
    score = max(0.0, min(10.0, score))
    
    rating = "中立"
    if score >= 7:
        rating = "健康"
    elif score <= 4:
        rating = "危險"
        
    return score, rating, reasons
