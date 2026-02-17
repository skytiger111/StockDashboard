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
- **三大法人籌碼**: 外資、投信、自營商買賣超堆疊柱狀圖，即時掌握主力動向（使用 **FinMind API**）。
- **中文化呈現**: 完美整合股票簡稱，再也不用背代碼（支援 2330.TW 自動顯示為台積電）。
- **側邊欄整合**: 全新的全局選擇器，切換股票後各頁面同步更新，操作流暢不跳轉。

### 💎 3. 潛力尋寶區 (Gem Scanner)
- **壓縮待變掃描**: 自動篩選符合「均線糾結 (Squeeze)」、「量能急凍 (Dry-up)」與「波動率創低」的壓縮股。
- **全市場掃描**: 內建 0-100、中型 100 及關鍵科技股池（約 160 檔），一鍵偵測全市場潛力黑馬。
- **極速分析**: 結合資料快取技術，20 秒內完成百檔個股深度掃描。

### 🎬 4. AI 解盤腳本生成器 (AI Script Generator)
- **Gemini 驅動**: 串接 Google Gemini API，根據即時技術數據自動產出腳本。
- **籌碼整合**: 自動分析三大法人買賣超，當投信連續買超 > 3 天會特別強調「大哥已經進場卡位了！」。
- **創作者風格**: 內建「台股專業且幽默短影音創作者」人格，生成的內容適合直接錄製 Reels/TikTok。
- **一鍵導出**: 生成後可直接複製腳本，大幅縮短盤後分析與自媒體影音製作時間。

## 🚀 快速啟動

### 環境準備
本專案建議使用 **Python 3.12+** 或最新實驗性版本。

1. **建立虛擬環境與安裝依賴**:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r StockDashboard/requirements.txt
   ```

2. **設定環境變數**:
   在專案根目錄或 `StockDashboard` 目錄下建立 `.env` 檔案：
   ```env
   GEMINI_API_KEY=你的_API_KEY
   ```

3. **啟動戰情室**:
   ```powershell
   streamlit run StockDashboard/app.py
   ```

## 🛠️ 技術優化紀錄
- **絕對路徑管理**: 修正了數據存檔路徑問題，確保在哪裡啟動都能讀取正確的 `stock_list.json`。
- **UI 結構重組**: 
    - 導入左側導覽選單 (Sidebar Navigation)，解決了 Streamlit Tabs 在某些版本中產生的畫面重置 (Jumping) 問題。
    - 重新編排側邊欄順序，將「AI 設定」置底，並加入「全局分析對象」選單。
- **錯誤防禦**: 增加了數據目錄自動建立機制，避免 `FileNotFoundError`。
- **FinMind API 整合**: 
    - 整合台灣金融資料開源專案 FinMind，穩定取得三大法人買賣超資料。
    - 克服證交所 API 反爬蟲限制，確保資料抓取穩定性。
    - 法人資料快取 1 小時，減少 API 呼叫次數。

```
.\.venv\Scripts\streamlit run StockDashboard\app.py
```
---
Developed with ❤️ by Skytiger & **Google Deepmind Antigravity Team**
