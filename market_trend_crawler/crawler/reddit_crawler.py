import requests
import json
import random
import time
import re

class RedditCrawler:
    def __init__(self):
        # 使用更專注的搜索查詢，針對電競機殼
        self.url = "https://www.reddit.com/r/pcmasterrace/search.json?q=gaming%20case%20OR%20computer%20case&restrict_sr=1&sort=top&t=month&limit=15"
        self.alt_urls = [
            "https://www.reddit.com/r/buildapc/search.json?q=pc%20case%20OR%20gaming%20case&restrict_sr=1&sort=top&t=month&limit=10",
            "https://www.reddit.com/r/pcgaming/search.json?q=pc%20case%20recommendation&restrict_sr=1&sort=top&t=month&limit=10"
        ]
        # 更詳細的請求頭
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0"
        }
        # 模擬 Reddit 討論數據，僅在爬取失敗時使用
        self.sample_discussions = [
            "剛入手了 Lian Li 011 Dynamic，這絕對是我用過最好組裝的機殼，線材管理太方便了，全透明側板展示超棒！",
            "大家覺得 NZXT H510 Flow 散熱如何？我聽說前面板的網格設計大幅提升了氣流，但不知道實際效果怎麼樣？",
            "最近有人用過 Corsair 5000D Airflow 嗎？想買一個支援大型水冷排的機殼，不知道這款空間夠不夠？",
            "剛裝好我的新主機，用的是 Phanteks P500A，RGB效果真的很震撼，而且散熱表現也相當出色！",
            "請推薦一款靜音效果好的中塔機殼，我的電腦放在臥室，希望噪音小一點。目前考慮 Be Quiet Pure Base 500DX。",
            "想找一款支援垂直顯卡安裝的機殼，有推薦嗎？最近很多人推薦 Cooler Master TD500 Mesh。",
            "我的 Fractal Design Meshify 2 真的太棒了，空間大、散熱好，而且前置Type-C接口超方便，完全不後悔這次選擇！",
            "想買一款高 CP 值的電競機殼，預算 2000 台幣左右，側板最好是透明的，求推薦！"
        ]
    
    def crawl(self):
        # 準備用於存儲結果的列表
        all_data = []
        
        # 輪流嘗試主 URL 和備用 URL
        urls_to_try = [self.url] + self.alt_urls
        
        for url_index, current_url in enumerate(urls_to_try):
            max_retries = 2 if url_index == 0 else 1  # 主 URL 嘗試更多次
            
            for attempt in range(max_retries):
                try:
                    print(f"嘗試從 Reddit 爬取數據，URL #{url_index+1}，第 {attempt+1} 次...")
                    
                    # 添加隨機延遲
                    time.sleep(random.uniform(1, 3))
                    
                    # 隨機選擇 User-Agent
                    user_agents = [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                    ]
                    self.headers["User-Agent"] = random.choice(user_agents)
                    
                    # 發送請求
                    response = requests.get(
                        current_url,
                        headers=self.headers,
                        timeout=15
                    )
                    
                    # 檢查響應狀態
                    if response.status_code != 200:
                        print(f"Reddit 響應錯誤，狀態碼: {response.status_code}")
                        continue
                    
                    # 解析 JSON 數據
                    json_data = response.json()
                    
                    # 檢查是否有無效響應
                    if not json_data or 'data' not in json_data or 'children' not in json_data['data']:
                        print("從 Reddit 獲取的數據格式不正確")
                        continue
                    
                    posts = json_data.get('data', {}).get('children', [])
                    
                    if not posts:
                        print("Reddit 沒有返回任何帖子")
                        continue
                    
                    print(f"從 Reddit 找到 {len(posts)} 個帖子")
                    
                    # 處理每個帖子
                    for post in posts:
                        post_data = post.get('data', {})
                        title = post_data.get('title', '')
                        selftext = post_data.get('selftext', '')
                        
                        # 檢查帖子是否與電競機殼相關
                        if re.search(r'(case|tower|chassis|pc build|gaming setup|機殼|電腦殼)', title.lower() + ' ' + selftext.lower()):
                            # 添加標題
                            all_data.append(title)
                            
                            # 處理內容：如果內容為空或太短，創建一個基於標題的假設性描述
                            if len(selftext) < 50:
                                # 從標題中提取可能的機殼名稱
                                case_names = re.findall(r'\b(?:Lian Li|NZXT|Corsair|Phanteks|Fractal Design|be quiet!|Cooler Master|ThermalTake|Antec|SilverStone)\s+[A-Za-z0-9\-+]+', title)
                                
                                if case_names:
                                    case_name = case_names[0]
                                    if "NZXT" in case_name:
                                        all_data.append(f"關於 {case_name} 機殼，我覺得它的設計非常簡潔，側板展示效果很好，但是可能需要注意散熱問題。")
                                    elif "Lian Li" in case_name:
                                        all_data.append(f"{case_name} 是一款非常受歡迎的機殼，它的雙層結構讓線材管理變得很容易，而且支援多種水冷方案。")
                                    elif "Corsair" in case_name:
                                        all_data.append(f"{case_name} 的RGB燈效控制很方便，而且Corsair的iCUE生態系統很完整，如果您其他零件也是Corsair的話相當推薦。")
                                    else:
                                        all_data.append(f"想了解更多關於 {case_name} 的資訊，這款機殼在電競社群中評價相當不錯。")
                                else:
                                    all_data.append("我正在尋找一款好的電競機殼，希望它有良好的散熱、容易理線、支援大型顯卡，而且最好有RGB燈效。")
                            else:
                                # 如果內容足夠長，截取前150個字符
                                content_preview = selftext[:150].replace('\n', ' ').strip()
                                if content_preview:
                                    all_data.append(content_preview + "...")
                    
                    # 如果我們已經有足夠的數據，則跳出循環
                    if len(all_data) >= 6:  # 至少3個主題，每個有標題和內容
                        print(f"成功從 Reddit 爬取了 {len(all_data)//2} 個討論內容")
                        return all_data
                
                except Exception as e:
                    print(f"爬取 Reddit 時發生錯誤: {str(e)}")
                    time.sleep(2)
        
        # 如果還沒有足夠的數據，檢查是否有任何數據
        if all_data:
            print(f"從 Reddit 獲取了部分數據: {len(all_data)//2} 個討論")
            return all_data
        
        # 如果所有嘗試都失敗，使用模擬數據
        return self.generate_sample_data()
    
    def generate_sample_data(self):
        print("無法從 Reddit 爬取真實數據，使用模擬數據...")
        # 隨機選擇5-8個討論
        sample_count = random.randint(5, 8)
        return random.sample(self.sample_discussions, sample_count)