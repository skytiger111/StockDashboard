# 專案規格書：Streamlit 台股全方位戰情室 (All-in-One Stock Dashboard)

## 1. 專案概述 (Overview)
建立一個針對個人投資者設計的 Web 儀表板，整合「持股防守」與「潛力進攻」兩大核心功能。
系統需以高互動性、深色模式 (Dark Mode) 呈現，將複雜的技術指標轉化為直觀的「分數」與「訊號」。

## 2. 功能模組 (Modules)
1.  **持股診斷模組 (Health Monitor):** 針對庫存名單進行評分 (0-10分)，輔助判斷續抱或停損。
2.  **潛力掃描模組 (Gem Scanner):** 針對觀察名單，篩選出符合「均線糾結 + 窒息量 + 低波動」的左側交易標的。

## 3. 技術堆疊 (Tech Stack)
* **Frontend:** `Streamlit` (UI), `Streamlit-extras`
* **Data Processing:** `Pandas`, `NumPy`
* **Data Source:** `yfinance` (台股代號需加 .TW)
* **Visualization:** `Plotly` (互動式圖表), `Matplotlib` (簡易 Sparkline)
* **Storage:** 本地 `JSON` 檔 (初期測試用) 或 `Google Sheets` (正式用)

## 4. UI/UX 設計規範 (UI Specifications)
* **Theme:** Dark Mode (`#0E1117`)，強調專業感。
* **Layout:** 左側 Sidebar 為控制項，右側 Main Area 分為三個 Tabs。

### 4.1 頁面結構
* **Sidebar:**
    * 股票清單輸入/選擇。
    * 參數設定 (如 RSI 週期，預設 14)。
    * 按鈕：「🔄 更新數據」。

* **Tab 1: 🏥 持股健康度 (Health Check)**
    * **KPI Cards:** [總持股數]、[平均健康分]、[今日最強股]。
    * **Chart:** 位階矩陣氣泡圖 (X軸=RSI, Y軸=季線乖離率, 顏色=健康分)。
    * **Table:** 詳細評分表 (含 Sparkline 走勢圖、建議動作)。

* **Tab 2: 📈 技術分析 (Technical Analysis)**
    * 下拉選單選擇個股。
    * 顯示 K 線圖 + 布林通道 (Bollinger Bands) + 成交量 Bar。
    * 副圖顯示 KD 或 MACD 指標。

* **Tab 3: 💎 尋寶區 (Gem Scanner)**
    * **Concept:** 尋找「壓縮待變」的股票。
    * **Chart:** 散佈圖 (X軸=均線糾結度, Y軸=波動率)。目標為左下角股票。
    * **Table:** 篩選出的潛力股清單，標註符合條件 (如：量能急凍、均線黏合)。

## 5. 核心演算法 (Core Logic)

### 5.1 健康度評分 (Health Score) - 總分 10 分
需實作於 `utils/scorer.py`：
* **趨勢面 (40%):** 收盤 > 月線 (+2), 收盤 > 季線 (+2)。
* **動能面 (30%):** RSI > 50 (+1.5), 今日量 > 5日均量 (+1.5)。
* **型態面 (30%):** MACD > 0 (+1.5), 收盤 > 布林中軌 (+1.5)。
* **扣分項:** 收盤 < 月線 且 跌幅 > 3% (扣 2 分)。
* **輸出:** 分數 (Float) 與 評級 (健康/中立/危險)。

### 5.2 潛力股篩選 (Scanner Logic)
需實作於 `utils/scanner.py`，篩選符合以下條件者：
1.  **均線糾結 (Squeeze):** `abs(SMA20 - SMA60) / SMA60 < 0.05` (差距 < 5%)。
2.  **量能急凍 (Dry-up):** `Current_Vol < 0.7 * SMA20_Vol`。
3.  **低波動 (Low Volatility):** 20日標準差處於低檔區。

## 6. 檔案結構 (File Structure)
```text
stock_dashboard/
├── .streamlit/config.toml  # Theme 設定
├── data/stock_list.json    # 測試用股票代號 (e.g., ["2330.TW", "2303.TW"])
├── utils/
│   ├── fetcher.py          # 處理 yfinance 資料抓取
│   ├── technical.py        # 計算 RSI, MACD, MA, Bollinger
│   ├── scorer.py           # 實作健康度評分
│   └── scanner.py          # 實作潛力股篩選
├── app.py                  # Streamlit 主程式
├── requirements.txt
└── README.md


