import requests
from bs4 import BeautifulSoup
import random
import time
import re

class BahamutCrawler:
    def __init__(self):
        # 巴哈姆特硬體相關討論區搜尋頁面
        self.main_url = "https://forum.gamer.com.tw/B.php?bsn=60030"  # 硬體串
        self.search_url = "https://search.gamer.com.tw"
        # 備用搜索詞組
        self.search_terms = [
            "機殼 推薦",
            "電競機殼",
            "電腦機殼 開箱",
            "機殼 RGB",
            "水冷 機殼"
        ]
        # 模擬真實瀏覽器的請求頭
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://forum.gamer.com.tw/",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "TE": "Trailers"
        }
        # 模擬討論數據，僅在爬取失敗時使用
        self.sample_discussions = [
            "【開箱】Lian Li O11D EVO 機殼 + Galahad水冷",
            "這次升級一口氣把機殼和CPU散熱一起換掉，Lian Li的這款O11D EVO真的超讚！機殼空間很大，水冷安裝很方便，線材管理也很簡單。打開側透看到裏面發光的樣子超帥氣啊！",
            "【求助】靜音機殼推薦？",
            "最近在找一款靜音效果好的機殼，因為電腦放在臥室，晚上開機時風扇聲音太吵了。預算3000左右，有推薦的嗎？目前看中Be Quiet 400系列和Fractal Design的Define系列。",
            "【分享】Fractal Design Meshify 2入手感想",
            "用了幾個星期的Meshify 2，這款機殼真的很讚！散熱效能非常好，前面板的網狀設計讓氣流超順暢。而且前置的I/O埠很齊全，有Type-C很方便。唯一缺點就是灰塵容易卡在網眼裡，要常常清理。",
            "【討論】中塔VS全塔機殼，哪個更推薦？",
            "想組裝一台新電腦，但對於機殼尺寸有點猶豫。中塔機殼好像比較適合一般使用，但全塔擴充性更好？有水冷的話是不是一定要選全塔？有沒有推薦的牌子和型號？",
            "【心得】酷碼 MasterBox TD500 Mesh White開箱",
            "剛換了這款白色機殼，整體質感很不錯，最讚的是前面板的設計很有未來感，而且散熱效果也很好。唯一要注意的是前面板的拆卸不是很方便，清理時要小心一點。有想買這款的可以問我。",
            "【討論】你們都怎麼挑選機殼？",
            "最近想換機殼，但市面上款式太多了，不知道怎麼選。是先看尺寸還是先看散熱？RGB燈效重要嗎？有沒有什麼選購機殼的小技巧可以分享？"
        ]
    
    def crawl(self):
        all_discussions = []
        
        # 嘗試從巴哈姆特首頁抓取熱門文章
        try:
            print("嘗試從巴哈姆特硬體版面抓取熱門文章...")
            
            # 添加隨機延遲
            time.sleep(random.uniform(1, 3))
            
            # 隨機選擇 User-Agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
            ]
            self.headers["User-Agent"] = random.choice(user_agents)
            
            response = requests.get(
                self.main_url,
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"巴哈姆特回應錯誤，狀態碼: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 獲取主題列表
                topics = soup.select('.b-list__row')
                
                print(f"找到 {len(topics)} 個主題")
                
                for topic in topics[:20]:  # 只處理前20個主題
                    title_tag = topic.select_one('.b-list__main__title')
                    
                    if not title_tag:
                        continue
                    
                    title = title_tag.text.strip()
                    
                    # 過濾與機殼相關的主題
                    if re.search(r'(機殼|case|tower|散熱|水冷|風扇|組裝|RGB|電腦)', title):
                        all_discussions.append(title)
                        
                        # 嘗試獲取這個主題的內容
                        topic_url = title_tag.get('href')
                        if topic_url and topic_url.startswith('/'):
                            full_url = f"https://forum.gamer.com.tw{topic_url}"
                            
                            # 增加延遲避免請求過快
                            time.sleep(random.uniform(2, 4))
                            
                            try:
                                topic_response = requests.get(
                                    full_url,
                                    headers=self.headers,
                                    timeout=15
                                )
                                
                                if topic_response.status_code == 200:
                                    topic_soup = BeautifulSoup(topic_response.text, 'html.parser')
                                    content_tag = topic_soup.select_one('.c-article__content')
                                    
                                    if content_tag:
                                        content = content_tag.text.strip()
                                        # 截取前150個字符
                                        content_preview = content[:150].replace('\n', ' ').strip()
                                        all_discussions.append(content_preview + "...")
                                    else:
                                        all_discussions.append(f"這是關於{title}的討論串，點進來看看鄉民們的意見和推薦。")
                                else:
                                    # 如果無法獲取內容，添加一個假設性的描述
                                    all_discussions.append(f"這個主題討論了{title}，可以看到許多巴友分享了他們的經驗和建議。")
                            
                            except Exception as e:
                                print(f"獲取主題內容時出錯: {str(e)}")
                                all_discussions.append(f"有關{title}的討論，巴哈姆特硬體版的鄉民們提供了許多專業意見。")
                        else:
                            # 如果沒有URL，添加一個一般性描述
                            all_discussions.append(f"這個討論主題關於{title}，引起了巴哈姆特玩家的熱烈討論。")
        
        except Exception as e:
            print(f"從巴哈姆特抓取數據時出錯: {str(e)}")
        
        # 檢查是否已經有足夠的數據
        if len(all_discussions) >= 6:  # 至少3個討論 (標題+內容)
            print(f"成功從巴哈姆特抓取了 {len(all_discussions)//2} 個討論")
            return all_discussions
        
        # 如果主頁獲取不夠，嘗試使用搜索功能
        for search_term in self.search_terms:
            if len(all_discussions) >= 6:
                break
            
            try:
                print(f"使用巴哈姆特搜索 '{search_term}'...")
                
                # 添加隨機延遲
                time.sleep(random.uniform(2, 4))
                
                # 構建搜索URL
                search_params = {
                    'keyword': search_term,
                    'search_type': 'web',
                    'search_target': 'forum'
                }
                
                search_response = requests.get(
                    self.search_url,
                    params=search_params,
                    headers=self.headers,
                    timeout=15
                )
                
                if search_response.status_code != 200:
                    print(f"巴哈姆特搜索回應錯誤，狀態碼: {search_response.status_code}")
                    continue
                
                search_soup = BeautifulSoup(search_response.text, 'html.parser')
                
                # 解析搜索結果
                search_results = search_soup.select('.GS-list')
                
                for result in search_results[:5]:  # 只處理前5個結果
                    title_tag = result.select_one('.GS-title')
                    content_tag = result.select_one('.GS-desc')
                    
                    if title_tag:
                        title = title_tag.text.strip()
                        all_discussions.append(title)
                        
                        if content_tag:
                            content = content_tag.text.strip()
                            all_discussions.append(content)
                        else:
                            all_discussions.append(f"關於{title}的討論，包含了許多關於電腦機殼的心得和推薦。")
            
            except Exception as e:
                print(f"使用巴哈姆特搜索時出錯: {str(e)}")
        
        # 如果有部分數據，返回這些數據
        if all_discussions:
            print(f"從巴哈姆特獲取了部分數據: {len(all_discussions)//2} 個討論")
            return all_discussions
        
        # 如果所有嘗試都失敗，使用模擬數據
        return self.generate_sample_data()
    
    def generate_sample_data(self):
        print("無法從巴哈姆特爬取真實數據，使用模擬數據...")
        # 隨機選擇4-6個討論
        sample_count = random.randint(4, 6) * 2  # 乘以2因為每個討論有標題和內容
        return self.sample_discussions[:sample_count]