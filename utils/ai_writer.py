import google.generativeai as genai

def generate_stock_script(api_key, stock_name, stock_data):
    """
    根據股票數據生成 AI 短影音腳本
    """
    if not api_key:
        return "⚠️ 請提供 Gemini API Key 以使用此功能。"
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        system_prompt = (
            "你是一位講話很有梗、喜歡用譬喻的年輕操盤手。"
            "你不說教，你用畫面感讓人秒懂。你會用反問句製造對話感，讓觀眾覺得你在跟他聊天。"
            "你的目標是產出約 30 秒（約 140 字）的短影音解盤腳本。"
        )
        
        user_prompt = f"""
        請根據以下股票數據，為「{stock_name} ({stock_data.get('代碼', '')})」撰寫一份 30 秒的短影音解盤腳本。
        
        股票數據：
        - 均線糾結度：{stock_data.get('均線糾結%', '未知')}%
        - 量能比 (今日/20日均)：{stock_data.get('量能比', '未知')}
        - 波動度：{stock_data.get('原始波動度', '未知')}
        - 潛力理由：{stock_data.get('理由', '技術面整理盤整中')}
        
        腳本結構（請嚴格執行）：
        1. 【Hook (0-5秒)】：用一句反直覺、有梗的話開場，讓人停下來。
        2. 【數據證據 (5-15秒)】：用譬喻解釋技術面數據，不要用教科書句型。
        3. 【情境預判 (15-25秒)】：描述接下來可能的噴發劇本，搭配反問句增加對話感。
        4. 【結尾 CTA (25-30秒)】：給出一句有記憶點的具體行動建議。
        
        風格指導原則：
        - 拒絕說教：禁止「顯示出...意味著...」這種教科書句型。改用「這根本就是...」、「你看這裡...」。
        - 善用譬喻：
          · 均線糾結 → 「像壓縮到極致的彈簧」「主力在蹲馬步」「暴風雨前的寧靜」
          · 量縮 → 「心電圖快停了」「市場都在屏氣凝神」
          · 突破 → 「像香檳開瓶」「火箭點火」
        - 加入情緒口語：適度使用「太扯了」「鬼故事」「有點東西喔」「這數據絕了」等詞。
        - 對話感：多用反問句，例如「你敢信嗎？」「這你能忍？」。
        
        要求：
        - 繁體中文。
        - 總字數必須在 130 字至 150 字之間。
        - 直接輸出腳本正文，不要有標題、段落標記或其他說明文字。
        """
        
        # 合併提示詞
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"❌ 生成腳本時發生錯誤: {str(e)}"
