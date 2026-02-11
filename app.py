import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from streamlit_extras.metric_cards import style_metric_cards
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.fetcher import fetch_multiple_stocks, fetch_stock_data, get_stock_name, get_tw_stock_candidates
from utils.technical import calculate_indicators
from utils.scorer import calculate_health_score
from utils.scanner import scan_potential_stocks
from utils.ai_writer import generate_stock_script

# Page Config
st.set_page_config(page_title="台股全方位戰情室", layout="wide", initial_sidebar_state="expanded")

# --- Helper Functions ---
# 獲取專案根目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "stock_list.json")

def load_stock_list():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_stock_list(stocks):
    data_dir = os.path.dirname(DATA_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(DATA_FILE, "w") as f:
        json.dump(stocks, f)

# --- Sidebar ---
st.sidebar.title("🛠️ 控制中心")
stock_list = load_stock_list()

# Add/Remove Stocks
new_stock = st.sidebar.text_input("新增股票代號 (如 2330.TW)", key="new_stock")
if st.sidebar.button("➕ 新增"):
    if new_stock and new_stock not in stock_list:
        stock_list.append(new_stock)
        save_stock_list(stock_list)
        st.sidebar.success(f"{new_stock} 已新增")
        st.rerun()

selected_to_remove = st.sidebar.selectbox("刪除自選股", ["選擇股票"] + stock_list)
if st.sidebar.button("➖ 刪除"):
    if selected_to_remove != "選擇股票":
        stock_list.remove(selected_to_remove)
        save_stock_list(stock_list)
        st.sidebar.warning(f"{selected_to_remove} 已刪除")
        st.rerun()

# Settings
rsi_period = st.sidebar.slider("RSI 週期", 5, 30, 14)

# Update Data Button
if st.sidebar.button("🔄 更新數據"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📈 全局分析對象")
if stock_list:
    stock_options = {f"{get_stock_name(s)} ({s})": s for s in stock_list}
    global_selected_label = st.sidebar.selectbox("選擇要分析的個股", list(stock_options.keys()), key="global_stock_selector")
    st.session_state.selected_stock = stock_options[global_selected_label]
else:
    st.sidebar.warning("請先新增股票")
    st.session_state.selected_stock = None

st.sidebar.divider()
st.sidebar.subheader("📍 導覽選單")
nav_options = {
    "🏥 持股健康度": "health",
    "📈 技術分析": "tech",
    "💎 潛力尋寶": "scanner"
}
selection = st.sidebar.radio("跳轉至", list(nav_options.keys()))
page = nav_options[selection]

st.sidebar.divider()
st.sidebar.subheader("🔑 AI 設定")
# 先從環境變數讀取預設值
default_api_key = os.getenv("GEMINI_API_KEY", "")
gemini_api_key = st.sidebar.text_input("Gemini API Key", value=default_api_key, type="password", help="用於生成 AI 解盤腳本")
if not gemini_api_key:
    st.sidebar.info("💡 請輸入 API Key 或在 .env 設定 GEMINI_API_KEY 以啟用功能")

# --- Data Loading ---
@st.cache_data(ttl=3600)
def get_all_data(symbols):
    data = fetch_multiple_stocks(symbols)
    processed_data = {}
    for sym, df in data.items():
        processed_data[sym] = calculate_indicators(df)
    return processed_data

with st.spinner("🚀 正在獲取最新行情..."):
    all_processed_data = get_all_data(stock_list)

# --- Main App ---
# 改用導覽選單判斷顯示內容，徹底解決跳轉問題
if page == "health":
    if not all_processed_data:
        st.info("請在側邊欄新增股票以開始分析。")
    else:
        # Calculate scores for all
        health_results = []
        for sym, df in all_processed_data.items():
            score, rating, reasons = calculate_health_score(df)
            name = get_stock_name(sym)
            last_row = df.iloc[-1]
            bias_60 = (last_row['Close'] - last_row['SMA60']) / last_row['SMA60'] * 100
            health_results.append({
                "代號": sym,
                "名稱": name,
                "健康分": score,
                "評級": rating,
                "收盤價": last_row['Close'],
                "RSI": round(last_row['RSI'], 2),
                "季線乖離%": round(bias_60, 2),
                "建議": "續抱" if rating == "健康" else ("觀望" if rating == "中立" else "減碼/停損"),
                "原因": ", ".join(reasons)
            })
        
        health_df = pd.DataFrame(health_results)
        
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("總持股數", len(stock_list))
        col2.metric("平均健康分", round(health_df['健康分'].mean(), 1))
        
        best_stock = health_df.sort_values("健康分", ascending=False).iloc[0]
        col3.metric("今日最強股", f"{best_stock['名稱']} ({best_stock['代號']})")
        style_metric_cards(background_color="#262730", border_left_color="#FF4B4B")
        
        # Chart: Matrix Bubble Chart
        st.subheader("位階矩陣氣泡圖")
        fig_matrix = px.scatter(
            health_df, 
            x="RSI", 
            y="季線乖離%", 
            size="健康分", 
            color="健康分",
            text="代號",
            hover_name="名稱",
            color_continuous_scale="RdYlGn",
            hover_data=["評級", "收盤價"],
            height=500,
            template="plotly_dark"
        )
        fig_matrix.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_matrix.add_vline(x=50, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Table
        st.subheader("詳細評分表")
        st.dataframe(health_df.sort_values("健康分", ascending=False), use_container_width=True)

# --- Tab 2: Technical Analysis ---
elif page == "tech":
    st.header("📈 技術分析")
    if not stock_list:
        st.info("請先新增股票。")
    elif st.session_state.selected_stock:
        selected_stock = st.session_state.selected_stock
        if selected_stock in all_processed_data:
            df = all_processed_data[selected_stock]
            
            # Candlestick Chart
            fig = go.Figure()
            # K-line
            fig.add_trace(go.Candlestick(
                x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                name="K線"
            ))
            # Bollinger Bands
            fig.add_trace(go.Scatter(x=df.index, y=df['BBU_20_2.0'], name='布林上軌', line=dict(color='rgba(173, 216, 230, 0.4)')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BBM_20_2.0'], name='布林中軌', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=df.index, y=df['BBL_20_2.0'], name='布林下軌', line=dict(color='rgba(173, 216, 230, 0.4)'), fill='tonexty'))
            
            fig.update_layout(height=600, template="plotly_dark", title=f"{selected_stock} 技術圖表", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # MACD Chart
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Bar(x=df.index, y=df['MACDh_12_26_9'], name='MACD柱子'))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_12_26_9'], name='MACD', line=dict(color='yellow')))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACDs_12_26_9'], name='Signal', line=dict(color='cyan')))
            fig_macd.update_layout(height=300, template="plotly_dark", title="MACD 指標")
            st.plotly_chart(fig_macd, use_container_width=True)

# --- Tab 3: Gem Scanner ---
elif page == "scanner":
    st.header("💎 潛力尋寶：尋找壓縮待變")
    
    scan_mode = st.radio("掃描範圍", ["僅自選股", "全市場優質股 (約 160 檔)"], horizontal=True)
    
    if scan_mode == "僅自選股":
        scanner_data = all_processed_data
    else:
        with st.spinner("🔍 正在掃描全市場優質個股，請稍候... (約需 20-30 秒)"):
            candidates = get_tw_stock_candidates()
            # Use shorter period for scanning to speed up
            scanner_data_raw = fetch_multiple_stocks(candidates, period="6mo")
            scanner_data = {}
            for sym, df in scanner_data_raw.items():
                scanner_data[sym] = calculate_indicators(df)
    
    scanner_df = scan_potential_stocks(scanner_data)
    
    if scanner_df.empty:
        st.write("目前範圍中暫無符合「均線糾結/量低/波動小」條件的股票。")
    else:
        # Add Names
        scanner_df['名稱'] = scanner_df['代碼'].apply(get_stock_name)
        
        # Scatter Plot for Scanning
        fig_scan = px.scatter(
            scanner_df,
            x="均線糾結%",
            y="量能比",
            color="原始波動度",
            text="代碼",
            hover_name="名稱",
            color_continuous_scale="Viridis",
            labels={"均線糾結%": "均線糾結度 (%)", "量能比": "成交量比(今日/20日均)"},
            title=f"潛力股分佈 ({scan_mode})",
            template="plotly_dark",
            height=600
        )
        st.plotly_chart(fig_scan, use_container_width=True)
        
        st.write("#### 篩選清單")
        st.dataframe(scanner_df, use_container_width=True)

        # --- AI Script Generator Section ---
        st.divider()
        st.subheader("🎬 AI 解盤腳本生成器")
        
        col_select, col_btn = st.columns([3, 1])
        with col_select:
            # 建立選擇選單：名稱 (代碼)
            script_options = {f"{row['名稱']} ({row['代碼']})": row['代碼'] for _, row in scanner_df.iterrows()}
            selected_script_label = st.selectbox("選擇一檔潛力股生成腳本", list(script_options.keys()))
            selected_stock_code = script_options[selected_script_label]
        
        with col_btn:
            st.write(" ") # 調整對齊
            generate_btn = st.button("✨ 生成解盤腳本", use_container_width=True)
            
        if generate_btn:
            if not gemini_api_key:
                st.error("❌ 請先在側邊欄輸入 Gemini API Key！")
            else:
                selected_row = scanner_df[scanner_df['代碼'] == selected_stock_code].iloc[0].to_dict()
                with st.spinner(f"正在為 {selected_row['名稱']} 撰寫劇本..."):
                    script_content = generate_stock_script(gemini_api_key, selected_row['名稱'], selected_row)
                    st.session_state['generated_script'] = script_content
        
        if 'generated_script' in st.session_state:
            st.divider()
            st.info("✅ 腳本生成完畢！")
            st.code(st.session_state['generated_script'], language="markdown")
            st.caption("💡 提示：點擊右上角按鈕即可複製腳本")
