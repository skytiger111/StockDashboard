# 🇹🇼 台股全方位戰情室 (Stock Dashboard)

這是一個為專業投資者打造的台股即時分析儀表板，基於 **Streamlit** 開發。它不只是顯示股價，更結合了**自動化健康診斷**與**盤後全市場掃描**技術，幫助你快速過濾雜訊，找出爆發前的關鍵標的。

## 🌟 核心功能

### 🏥 1. 持股健康度 (Health Check)
- **多維度評分**: 整合 RSI、季線乖離度、均線排列等多項指標，自動產出 0-10 分的健康分。
- **矩陣式分析**: 透過「位階矩陣氣泡圖」直觀呈現持股是否存在過熱（高 RSI）或超跌（低乖離）狀態。
- **自動標籤化**: 即時產出「建議：續抱/觀望/減碼」與詳細原因分析。

### 📈 2. 專業技術圖表 (Technical Pro)
- **整合顯示**: K 線圖、由布林通道 (Bollinger Bands) 構成的波動範圍。
- **動能指標**: 獨立 MACD 與 Signal 曲線分析，洞察多空趨勢轉換點。
- **中文化呈現**: 完美整合股票簡稱，再也不用背代碼（支援 2330.TW 自動顯示為台積電）。

### 💎 3. 潛力尋寶區 (Gem Scanner)
- **壓縮待變掃描**: 自動篩選符合「均線糾結 (Squeeze)」、「量能急凍 (Dry-up)」與「波動率創低」的壓縮股。
- **全市場掃描**: 內建 0-100、中型 100 及關鍵科技股池（約 160 檔），一鍵偵測全市場潛力黑馬。
- **極速分析**: 結合資料快取技術，20 秒內完成百檔個股深度掃描。

## 🚀 快速啟動

### 環境準備
本專案已針對最新版 **Python 3.14** 進行優化，移除了過時的指標套件，改採自研高效能計算引擎。

1. **安裝依賴**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **啟動戰情室**:
   ```powershell
   python -m streamlit run app.py
   ```

## 🛠️ 技術架構
- **Frontend**: Streamlit (Dark Mode UI)
- **Data Source**: Yahoo Finance API (yfinance)
- **Charts**: Plotly (Interactive Charts)
- **Logic**: Pandas-integrated technical indicator engine

---
Developed with ❤️ by Skytiger & **Google Deepmind Antigravity Team**
