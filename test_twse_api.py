import requests
import urllib3
from datetime import datetime

# 關閉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 測試證交所 API
date_str = '20260212'  # 最近的交易日
url = f'https://www.twse.com.tw/rwd/zh/fund/T86?date={date_str}&selectType=ALLBUT0999&response=json'

try:
    response = requests.get(url, verify=False, timeout=10, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print(f'狀態碼: {response.status_code}')
    
    if response.status_code == 200:
        data = response.json()
        print(f'資料筆數: {len(data.get("data", []))}')
       
        # 找 2330
        if 'data' in data and data['data']:
            for row in data['data']:
                if row[0].strip() == '2330':
                    print(f'\n找到 2330:')
                    print(f'  外資買賣超 (第4欄): {row[4]}')
                    print(f'  自營商買賣超 (第7欄): {row[7]}')
                    print(f'  投信買賣超 (第10欄): {row[10]}')
                    break
            else:
                print('未找到 2330')
                print(f'前3筆代號: {[row[0] for row in data["data"][:3]]}')
        else:
            print('無資料或格式錯誤')
            print(f'回應內容: {data}')
    else:
        print(f'請求失敗: {response.text[:200]}')
        
except Exception as e:
    print(f'錯誤: {e}')
    import traceback
    traceback.print_exc()
