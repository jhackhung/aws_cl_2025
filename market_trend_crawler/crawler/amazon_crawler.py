import requests
from bs4 import BeautifulSoup
import random
import time
import re

class AmazonCrawler:
    def __init__(self):
        self.url = "https://www.amazon.com/s?k=gaming+computer+case"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "TE": "Trailers"
        }
        
        self.sample_products = [
            "Corsair iCUE 7000X RGB 全塔式電競機殼",
            "超大全塔設計可支援多個水冷排安裝，搭載原廠RGB風扇，前置USB Type-C接口，具備無與倫比的擴展性。",
            "Lian Li O11 Dynamic EVO 白色機殼",
            "模組化設計使擴充性無限，雙層結構便於線材管理，多個玻璃側板使組件展示效果出眾，支援垂直GPU安裝。",
            "NZXT H9 Flow 簡約風格ATX機殼",
            "乾淨簡約的設計風格，優化的氣流設計讓散熱效能大幅提升，可同時安裝多個水冷排。",
            "Cooler Master HAF 700 EVO 旗艦電競機殼",
            "旗艦級全塔機殼，前面板帶有多種ARGB燈效模式，頂部3.9吋顯示幕可顯示系統狀態，頂級的硬體相容性。",
            "Phanteks Enthoo Pro 2 大型機殼",
            "支援雙系統安裝的大型機殼，內部空間極為充裕，一次可安裝多達十五顆風扇，適合專業玩家與水冷愛好者。"
        ]
    
    def crawl(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"嘗試從 Amazon 爬取數據，第 {attempt+1} 次...")
                time.sleep(random.uniform(1, 3))
                
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
                ]
                
                self.headers["User-Agent"] = random.choice(user_agents)
                response = requests.get(
                    self.url, 
                    headers=self.headers, 
                    timeout=15
                )
                
                if response.status_code != 200:
                    print(f"Amazon 響應錯誤，狀態碼: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if "captcha" in response.text.lower() or "sign in" in response.text.lower():
                    print("Amazon 請求被阻擋，可能需要驗證碼")
                    continue
                
                data = []
                
                product_items = soup.select('.s-result-item[data-component-type="s-search-result"]')
                print(f"找到 {len(product_items)} 個產品項目")
                
                for item in product_items:
                    name_elem = item.select_one('.a-size-medium.a-color-base.a-text-normal')
                    if not name_elem:
                        name_elem = item.select_one('.a-size-base-plus.a-color-base.a-text-normal')

                    price_elem = item.select_one('.a-price .a-offscreen')

                    rating_elem = item.select_one('.a-icon-star-small .a-icon-alt')

                    reviews_elem = item.select_one('.a-size-base.s-underline-text')
                    
                    if name_elem:
                        product_name = name_elem.text.strip()
                        if re.search(r'(case|tower|chassis|atx|mid|full|tempered glass|rgb)', product_name.lower()):
                            data.append(product_name)
                            
                            description_parts = []
                            if price_elem:
                                description_parts.append(f"價格: {price_elem.text.strip()}")
                            if rating_elem:
                                description_parts.append(f"評分: {rating_elem.text.strip()}")
                            if reviews_elem:
                                description_parts.append(f"評論數: {reviews_elem.text.strip()}")
                            
                            # 添加特性描述
                            if "RGB" in product_name or "rgb" in product_name:
                                description_parts.append("RGB燈效設計")
                            if "Glass" in product_name or "glass" in product_name:
                                description_parts.append("強化玻璃側板")
                            if "ATX" in product_name or "atx" in product_name:
                                description_parts.append("支援ATX主板")
                            if "Mesh" in product_name or "mesh" in product_name:
                                description_parts.append("網格前面板設計，提供優異散熱效能")
                            
                            description = "，".join(description_parts)
                            data.append(description)
                
                if len(data) >= 4:  # 確保至少有2個產品
                    print(f"成功從 Amazon 爬取了 {len(data)//2} 個產品資訊")
                    return data
                else:
                    print("從 Amazon 爬取的數據不足，可能需要調整選擇器")
            
            except Exception as e:
                print(f"爬取 Amazon 時發生錯誤: {str(e)}")
                time.sleep(2)  # 發生錯誤後等待一段時間再重試
        
        # 如果所有嘗試都失敗，使用模擬數據
        return self.generate_sample_data()
    
    def generate_sample_data(self):
        print("無法從 Amazon 爬取真實數據，使用模擬數據...")
        return self.sample_products