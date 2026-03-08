import vectorbt as vbt
import pandas as pd
import streamlit as st

def run_taiwan_stock_backtest(df, symbol_name="個股"):
    # 1. 定義策略邏輯 (以你的右側交易為例：收盤 > 5MA & 10MA)
    close = df['Close']
    ma5 = vbt.MA.run(close, 5).ma
    ma10 = vbt.MA.run(close, 10).ma
    
    # 進場：站上雙均線；出場：跌破 10MA
    entries = (close > ma5) & (close > ma10)
    exits = close < ma10

    # 2. 設置台股交易成本 (假設券商打 28 折)
    # 手續費: 0.1425% * 0.28 = 0.000399
    # 證交稅: 0.003
    fees = 0.000399 
    slippage = 0.001 # 考慮滑價 0.1%

    # 3. 執行回測
    pf = vbt.Portfolio.from_signals(
        close, 
        entries, 
        exits, 
        init_cash=1000000, # 初始百萬資金
        fees=fees,
        slippage=slippage,
        freq='1D'
    )

    # 4. Streamlit 介面呈現
    display_integrated_backtest_ui(pf, df, symbol_name)
    
    return pf

def display_integrated_backtest_ui(pf, df, symbol_name):
    import numpy as np
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.subheader(f"📊 {symbol_name} 策略深度分析")

    # --- 第一層：核心指標 (Metrics) ---
    m1, m2, m3, m4 = st.columns(4)

    total_ret = pf.total_return() * 100
    mdd = pf.stats()['Max Drawdown [%]'] if 'Max Drawdown [%]' in pf.stats().index else 0.0
    win_rate = pf.trades.win_rate() * 100 if pf.trades.count() > 0 else 0.0
    pf_factor = pf.trades.profit_factor() if pf.trades.count() > 0 else 0.0

    win_rate = 0.0 if np.isnan(win_rate) else win_rate
    pf_factor = 0.0 if np.isnan(pf_factor) else pf_factor

    m1.metric("累積報酬率", f"{total_ret:.2f}%")
    m2.metric("勝率 (Win Rate)", f"{win_rate:.2f}%")
    m3.metric("最大回撤 (MDD)", f"{mdd:.2f}%")
    m4.metric("獲利因子 (PF)", f"{pf_factor:.2f}")

    # --- AI 評論區 (Benchmark Comparison) ---
    st.divider()
    st.subheader("💡 Tiger's Insight (績效評估與盲點)")
    st.info("""
    **績效對比邏輯 (Benchmark Comparison):**
    在強多頭走勢中，右側交易可能會因「頻繁止損」或「太晚進場」而落後大盤。
    此時可考慮：
    1. 放寬出場條件（例如：改跌破 20MA 才出場）。
    2. 或引入左側思維，在乖離過大時進行部位調節。
    """)
    st.divider()

    # --- 計算繪圖用資料 ---
    equity = pf.value()
    cumulative_returns = (equity / equity.iloc[0] - 1) * 100
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max * 100

    close = df['Close']
    ma5 = vbt.MA.run(close, 5).ma
    ma10 = vbt.MA.run(close, 10).ma
    entries_sig = (close > ma5) & (close > ma10)
    exits_sig = close < ma10

    # --- 第二層：分頁整合 (Tabs) ---
    tab_charts, tab_signals, tab_data, tab_opt = st.tabs(["📈 績效曲線", "📍 進出場點", "📄 交易明細", "🔥 參數尋優"])

    with tab_charts:
        fig_perf = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                 row_heights=[0.65, 0.35], vertical_spacing=0.06,
                                 subplot_titles=("累積報酬率 (%)", "水下圖 Drawdown (%)"))
        fig_perf.add_trace(go.Scatter(
            x=cumulative_returns.index, y=cumulative_returns,
            name="累積報酬", fill='tozeroy',
            line=dict(color='#00d4aa', width=2)
        ), row=1, col=1)
        fig_perf.add_trace(go.Scatter(
            x=drawdown.index, y=drawdown,
            name="回撤", fill='tozeroy',
            line=dict(color='#ff4b4b', width=1.5)
        ), row=2, col=1)
        fig_perf.update_layout(height=500, template="plotly_dark", margin=dict(t=30),
                               showlegend=False)
        st.plotly_chart(fig_perf, use_container_width=True)

    with tab_signals:
        fig_signals = go.Figure()
        fig_signals.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'], name="K線"
        ))
        fig_signals.add_trace(go.Scatter(
            x=df.index, y=ma5, name="5MA",
            line=dict(color='yellow', width=1)
        ))
        fig_signals.add_trace(go.Scatter(
            x=df.index, y=ma10, name="10MA",
            line=dict(color='cyan', width=1)
        ))
        # 標注進場點
        entry_dates = df.index[entries_sig & ~entries_sig.shift(1, fill_value=False)]
        fig_signals.add_trace(go.Scatter(
            x=entry_dates, y=df.loc[entry_dates, 'Low'] * 0.98,
            mode='markers', name='進場',
            marker=dict(symbol='triangle-up', size=10, color='#00d4aa')
        ))
        # 標注出場點
        exit_dates = df.index[exits_sig & ~exits_sig.shift(1, fill_value=False)]
        fig_signals.add_trace(go.Scatter(
            x=exit_dates, y=df.loc[exit_dates, 'High'] * 1.02,
            mode='markers', name='出場',
            marker=dict(symbol='triangle-down', size=10, color='#ff4b4b')
        ))
        fig_signals.update_layout(height=550, template="plotly_dark",
                                  xaxis_rangeslider_visible=False,
                                  title=f"{symbol_name} 進出場點位")
        st.plotly_chart(fig_signals, use_container_width=True)

    with tab_data:
        st.subheader("策略統計摘要")
        
        # 取得 stats 並將小數點統一處理 (例如 2 位數)
        stats_df = pd.DataFrame(pf.stats())
        stats_df.columns = ["數值"]
        
        # 針對浮點數欄位做四捨五入格式化
        def format_value(x):
            if isinstance(x, float):
                return round(x, 2)
            return x
            
        stats_df["數值"] = stats_df["數值"].apply(format_value)
        st.dataframe(stats_df, use_container_width=True)

        st.subheader("每筆交易明細")
        try:
            st.dataframe(pf.trades.records_readable, use_container_width=True)
        except Exception:
            st.dataframe(pd.DataFrame(pf.trades.records), use_container_width=True)

    with tab_opt:
        run_parameter_optimization(df)

def run_parameter_optimization(df):
    import numpy as np
    import vectorbt as vbt
    import plotly.graph_objects as go
    import streamlit as st
    import pandas as pd
    
    st.subheader("🔥 均線參數熱力圖 (參數尋優)")
    
    close = df['Close']
    
    # 1. 定義要測試的參數範圍
    fast_ma_range = np.arange(3, 16)  # 快線：3 到 15 天
    slow_ma_range = np.arange(10, 31) # 慢線：10 到 30 天
    
    # VectorBT MA range requires grid flattening to test all combinations properly
    # (修正原本無法直接傳入 list_of_ranges 的問題)
    fast_grid, slow_grid = np.meshgrid(fast_ma_range, slow_ma_range)
    fast_windows = fast_grid.flatten()
    slow_windows = slow_grid.flatten()

    # 2. 向量化計算所有組合的均線
    fast_mas = vbt.MA.run(close, window=fast_windows)
    slow_mas = vbt.MA.run(close, window=slow_windows)
    
    # 3. 定義進出場邏輯 (多頭排列)
    entries = fast_mas.ma_crossed_above(slow_mas.ma)
    exits = fast_mas.ma_crossed_below(slow_mas.ma)
    
    # 4. 執行批量回測 (考慮台股成本)
    portfolio = vbt.Portfolio.from_signals(
        close, entries, exits, 
        fees=0.0004, 
        freq='1D'
    )
    
    # 5. 提取總報酬率矩陣並轉化為 Heatmap 資料
    # flatten() 返回的一維結果我們需要重塑回 (len(slow_ma_range), len(fast_ma_range))
    total_returns = portfolio.total_return().values.reshape(len(slow_ma_range), len(fast_ma_range))
    
    # 6. 使用 Plotly 繪製熱力圖
    fig = go.Figure(data=go.Heatmap(
        z=total_returns * 100, # 轉為百分比
        x=fast_ma_range,
        y=slow_ma_range,
        colorscale='Viridis',
        colorbar=dict(title='報酬率 (%)'),
        hovertemplate='快線: %{x}天<br>慢線: %{y}天<br>報酬率: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title='不同均線組合的總報酬率分佈',
        xaxis_title='快速均線天數',
        yaxis_title='慢速均線天數',
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
    
    # 找出最優參數
    best_idx = np.unravel_index(np.argmax(total_returns), total_returns.shape)
    best_fast = fast_ma_range[best_idx[1]]
    best_slow = slow_ma_range[best_idx[0]]
    best_return = total_returns[best_idx]
    
    st.success(f"✅ 最佳組合找到囉！ 快線: **{best_fast}** 天, 慢線: **{best_slow}** 天")
    st.write(f"在該組合下，預期總報酬率為: **{best_return*100:.2f}%**")