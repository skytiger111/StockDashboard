import google.generativeai as genai

def generate_stock_script(api_key, stock_name, stock_data, institutional_data=None):
    """
    根據股票數據及法人數據生成 AI 短影音腳本
    
    Args:
        api_key: Gemini API Key
        stock_name: 股票名稱
        stock_data: 股票技術面數據
        institutional_data: 三大法人買賣超資料 (DataFrame, optional)
    """
    if not api_key:
        return "⚠️ 請提供 Gemini API Key 以使用此功能。"
    
    try:
        genai.configure(api_key=api_key)
        # 根據主人偏好使用 gemini-2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash') 
        
        # 分析法人數據
        institutional_analysis = ""
        if institutional_data is not None and not institutional_data.empty:
            # 檢查投信連續買超天數
            invest_trust_data = institutional_data['投信買賣超'].values
            consecutive_buy = 0
            for value in reversed(invest_trust_data):
                if value > 0:
                    consecutive_buy += 1
                else:
                    break
            
            if consecutive_buy > 3:
                institutional_analysis = f"\n⚠️ 重點：投信已連續買超 {consecutive_buy} 天！大哥(投信)已經進場卡位了！"
            elif consecutive_buy > 0:
                institutional_analysis = f"\n📊 法人動態：投信連續買超 {consecutive_buy} 天"
            
            # 計算外資總買賣超
            foreign_total = institutional_data['外資買賣超'].sum()
            institutional_analysis += f"\n外資累計買賣超: {foreign_total:.0f} 張"
        
        system_prompt = (
            "你是一位住在宜蘭、53 歲的『理性冒險家』。你熱愛溯溪、登山，並將這種冒險精神融入股市分析。"
            "你的講話風格精準、務實、帶點野性，但非常有長者的沉穩感。你像是一位在溪邊烤肉時，順便跟後輩分享投資心得的老大哥。"
            "你不說空話，追求效率，說話溫暖但充滿邏輯。你的目標是產出約 30 秒（約 140 字）的短影音解盤腳本。"
        )
        
        user_prompt = f"""
        請根據以下股票數據，為「{stock_name} ({stock_data.get('代碼', '')})」撰寫一份 30 秒的短影音解盤腳本。
        
        股票數據：
        - 均線糾結度：{stock_data.get('均線糾結%', '未知')}%
        - 量能比 (今日/20日均)：{stock_data.get('量能比', '未知')}
        - 波動度：{stock_data.get('原始波動度', '未知')}
        - 潛力理由：{stock_data.get('理由', '技術面整理盤整中')}
        {institutional_analysis}
        
        腳本結構（請嚴格執行）：
        1. 【Hook (0-5秒)】：用一句反直覺、有梗的話開場，讓人停下來。
        2. 【數據證據 (5-15秒)】：用譬喻解釋技術面數據，不要用教科書句型。
        3. 【情境預判 (15-25秒)】：描述接下來可能的噴發劇本，搭配反問句增加對話感。
           {f"特別注意：若投信連續買超 > 3 天，務必在此段強調「大哥(投信)已經進場卡位了！」" if "大哥(投信)" in institutional_analysis else ""}
        4. 【結尾 CTA (25-30秒)】：給出一句有記憶點的具體行動建議。
        
        風格指導原則：
        - 宜蘭溫度：對話使用繁體中文，保持像老朋友聊天般的自然語氣。
        - 拒絕說教：改用「你看這走勢...」、「就像我在宜蘭登山時...」。
        - 善用冒險譬喻：
          · 均線糾結 → 「像是在山區紮營後的裝備整理」「暴風雨前的寧靜」
          · 量縮 → 「像是在溯溪時遇到的深潭」「水流變緩，是在蓄力」
          · 突破 → 「像是攻頂前的最後衝刺」「翻過這座山就是平原」
          · 投信買超 → 「大哥(投信)已經進場紮營了」「有經驗的嚮導帶路」
        - 沉穩幽默：適度使用「這有點東西喔」「這數據，我看很有戲」「跟我當年...有點像」等語氣。
        
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
