import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import requests
import twstock

@st.cache_data(ttl=86400)
def get_stock_name(symbol):
    """
    Get the friendly name of the stock in Traditional Chinese if possible.
    """
    # Manual mapping for high-quality stocks to ensure Traditional Chinese
    tw_names = {
        "2330.TW": "台積電", "2317.TW": "鴻海", "2454.TW": "聯發科", "2308.TW": "台達電", 
        "2303.TW": "聯電", "2881.TW": "富邦金", "2882.TW": "國泰金", "2886.TW": "兆豐金",
        "2884.TW": "玉山金", "2891.TW": "中信金", "2892.TW": "第一金", "5880.TW": "合庫金",
        "2880.TW": "華南金", "2885.TW": "元大金", "2887.TW": "台新金", "2890.TW": "永豐金",
        "0050.TW": "元大台灣50", "0056.TW": "元大高股息", "00878.TW": "國泰永續高股息",
        "00919.TW": "群益台灣精選高息", "00929.TW": "復華台灣科技優息", "3037.TW": "欣興",
        "3008.TW": "大立光", "2327.TW": "國巨", "2357.TW": "華碩", "2382.TW": "廣達",
        "3231.TW": "緯創", "2376.TW": "技嘉", "2377.TW": "微星", "2603.TW": "長榮",
        "2609.TW": "陽明", "2615.TW": "萬海", "2610.TW": "華航", "2618.TW": "長榮航",
        "2002.TW": "中鋼", "1301.TW": "台塑", "1303.TW": "南亞", "1326.TW": "台化",
        "6505.TW": "台塑化", "1216.TW": "統一", "2912.TW": "統一超", "9910.TW": "豐泰",
        "1476.TW": "儒鴻", "1101.TW": "台泥", "1102.TW": "亞泥", "1504.TW": "東元",
        "2105.TW": "正新", "2207.TW": "和泰車", "2301.TW": "光寶科", "2395.TW": "研華",
        "2412.TW": "中華電", "3045.TW": "台灣大", "4904.TW": "遠傳", "3711.TW": "日月光投控",
        "3034.TW": "聯詠", "2379.TW": "瑞昱", "6669.TW": "緯穎", "6415.TW": "矽力*-KY",
        "8046.TW": "南電", "4938.TW": "和碩", "0052.TW": "富邦科技", "3481.TW": "群創",
        "2409.TW": "友達", "2344.TW": "華邦電", "2883.TW": "開發金", "2408.TW": "南亞科",
        "2337.TW": "旺宏", "2345.TW": "智邦", "3017.TW": "奇鋐", "3035.TW": "智原",
        "3661.TW": "世芯-KY", "5269.TW": "祥碩", "6409.TW": "旭隼", "6414.TW": "樺漢"
    }
    
    clean_sym = symbol.upper()
    if clean_sym in tw_names:
        return tw_names[clean_sym]

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        name = info.get('shortName') or info.get('longName') or symbol
        # If it's a known placeholder or still looks too English, return symbol
        return name
    except:
        return symbol

@st.cache_data(ttl=604800) # Update weekly
def get_tw_stock_candidates():
    """
    Generate a list of high-quality Taiwan stock symbols (0050 + 0051 + 0052 approx).
    Returns a list of symbols ending with .TW.
    """
    # Simple Version: Curated Top ~160 high-quality stocks (0050 + 0051 + Some tech)
    # This list is stable and ensures the scanner has good targets.
    core_list = [
        # 0050 Constituents (Top 50)
        "1101.TW", "1102.TW", "1216.TW", "1301.TW", "1303.TW", "1326.TW", "1402.TW", "1504.TW", "1590.TW", "2002.TW",
        "2105.TW", "2207.TW", "2301.TW", "2303.TW", "2308.TW", "2317.TW", "2327.TW", "2330.TW", "2357.TW", "2379.TW",
        "2382.TW", "2395.TW", "2408.TW", "2409.TW", "2412.TW", "2454.TW", "2603.TW", "2609.TW", "2610.TW", "2615.TW",
        "2801.TW", "2880.TW", "2881.TW", "2882.TW", "2883.TW", "2884.TW", "2885.TW", "2886.TW", "2887.TW", "2891.TW",
        "2892.TW", "2912.TW", "3008.TW", "3034.TW", "3037.TW", "3045.TW", "3231.TW", "3711.TW", "4904.TW", "4938.TW",
        "5871.TW", "5876.TW", "5880.TW", "6415.TW", "6505.TW", "6669.TW", "8046.TW", "9910.TW",
        # 0051 & High Volume Quality Stocks (Next ~100)
        "1210.TW", "1227.TW", "1319.TW", "1440.TW", "1476.TW", "1477.TW", "1503.TW", "1513.TW", "1519.TW", "1605.TW",
        "1717.TW", "1722.TW", "1723.TW", "1802.TW", "1904.TW", "2006.TW", "2014.TW", "2104.TW", "2106.TW", "2201.TW",
        "2204.TW", "2206.TW", "2313.TW", "2324.TW", "2337.TW", "2344.TW", "2345.TW", "2347.TW", "2352.TW", "2353.TW",
        "2354.TW", "2356.TW", "2360.TW", "2371.TW", "2376.TW", "2377.TW", "2383.TW", "2385.TW", "2392.TW", "2404.TW",
        "2439.TW", "2449.TW", "2451.TW", "2458.TW", "2474.TW", "2480.TW", "2492.TW", "2498.TW", "2501.TW", "2542.TW",
        "2601.TW", "2605.TW", "2606.TW", "2607.TW", "2618.TW", "2707.TW", "2809.TW", "2812.TW", "2834.TW", "2845.TW",
        "2851.TW", "2855.TW", "2867.TW", "2888.TW", "2889.TW", "2890.TW", "2903.TW", "2915.TW", "3004.TW", "3005.TW",
        "3017.TW", "3023.TW", "3035.TW", "3044.TW", "3406.TW", "3443.TW", "3481.TW", "3532.TW", "3533.TW", "3583.TW",
        "3596.TW", "3661.TW", "3702.TW", "4739.TW", "4919.TW", "4958.TW", "4961.TW", "5269.TW", "5434.TW", "6176.TW",
        "6205.TW", "6206.TW", "6213.TW", "6239.TW", "6269.TW", "6278.TW", "6285.TW", "6409.TW", "6414.TW", "6446.TW",
        "6719.TW", "8028.TW", "8150.TW", "8215.TW", "8454.TW", "8464.TW", "9904.TW", "9921.TW", "9945.TW"
    ]
    
    # Optional: Try to fetch Top Volume 300 from a public source to supplement
    # Since scraper is brittle, we stick to the core high-quality list.
    return sorted(list(set(core_list)))

def fetch_stock_data(symbol, period="1y"):
    """
    Fetch historical stock data for a given symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        if df.empty:
            return None
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def fetch_multiple_stocks(symbols, period="1y"):
    """
    Fetch historical data for multiple stocks.
    """
    data_dict = {}
    for symbol in symbols:
        df = fetch_stock_data(symbol, period)
        if df is not None:
            data_dict[symbol] = df
    return data_dict

@st.cache_data(ttl=3600)
def get_institutional_data(stock_id):
    """
    抓取三大法人買賣超資料 (最近 30 日)
    使用 FinMind API
    
    Args:
        stock_id: 股票代號 (如 "2330.TW" 或 "2330")
    
    Returns:
        DataFrame 包含: 日期、外資買賣超、投信買賣超、自營商買賣超
        若失敗則回傳空 DataFrame
    """
    try:
        from FinMind.data import DataLoader
        
        # 移除 .TW 後綴，取得純股票代號
        clean_id = stock_id.replace('.TW', '').replace('.tw', '')
        
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)  # 多抓一些確保有 30 個交易日
        
        # 格式化日期為 YYYY-MM-DD
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 使用 FinMind DataLoader
        dl = DataLoader()
        
        # 抓取個股三大法人買賣超資料
        df = dl.taiwan_stock_institutional_investors(
            stock_id=clean_id,
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        if df is None or df.empty:
            return pd.DataFrame()
        
        # FinMind 資料結構：每個法人是分開的行，用 name 欄位區分
        # 欄位：date, stock_id, buy, sell, name
        # name 值：Foreign_Investor (外資), Investment_Trust (投信), Dealer_self (自營商自營)
        
        # 按日期分組處理
        result_data = []
        for date, group in df.groupby('date'):
            trade_date = pd.to_datetime(date)
            
            # 初始化各法人買賣超
            foreign = 0
            trust = 0
            dealer = 0
            
            # 找出各法人的買賣超 (buy - sell，單位：千股)
            for _, row in group.iterrows():
                investor_type = row['name']
                buy_sell_diff = (float(row.get('buy', 0)) - float(row.get('sell', 0))) / 1000  # 轉張數
                
                if investor_type == 'Foreign_Investor':
                    foreign = buy_sell_diff
                elif investor_type == 'Investment_Trust':
                    trust = buy_sell_diff
                elif investor_type == 'Dealer_self':
                    dealer = buy_sell_diff
            
            result_data.append({
                '日期': trade_date,
                '外資買賣超': foreign,
                '投信買賣超': trust,
                '自營商買賣超': dealer
            })
        
        if not result_data:
            return pd.DataFrame()
        
        # 轉換為 DataFrame
        result_df = pd.DataFrame(result_data)
        result_df = result_df.sort_values('日期', ascending=False).head(30)
        result_df = result_df.sort_values('日期')
        
        return result_df
        
    except Exception as e:
        print(f"抓取 {stock_id} 法人資料時發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
