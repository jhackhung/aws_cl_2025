import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin, urlparse, parse_qs
import re
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import urllib.request
import sys

class CoolerMasterCrawler:
    def __init__(self):
        # 現在使用 en-global 路徑，因為我們想要獲取到新版網站上的內容
        self.base_url = "https://www.coolermaster.com/en-global/catalog/pc-cases/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        self.output_dir = "coolermaster_cases"
        self.create_output_dirs()
        self.cases_data = []
        self.setup_browser()
        
    def setup_browser(self):
        """設置 Selenium 瀏覽器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 無頭模式
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            
            # 建立一個 Chrome 瀏覽器實例
            print("正在初始化瀏覽器...")
            self.driver = webdriver.Chrome(options=chrome_options)
            print("瀏覽器初始化成功")
        except Exception as e:
            print(f"瀏覽器初始化失敗: {str(e)}")
            if "chromedriver" in str(e).lower():
                print("請確認已經安裝了最新版本的 Chrome 瀏覽器和相符的 chromedriver")
            sys.exit(1)
            
    def create_output_dirs(self):
        """建立必要的資料夾"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        if not os.path.exists(os.path.join(self.output_dir, "images")):
            os.makedirs(os.path.join(self.output_dir, "images"))
    
    def save_html_for_debug(self, html_content, filename="debug_page.html"):
        """儲存 HTML 內容到檔案用於除錯"""
        debug_path = os.path.join(self.output_dir, filename)
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"已儲存 HTML 至 {debug_path} 用於除錯")
    
    def get_all_case_links(self):
        """獲取所有機殼產品頁面連結"""
        print("正在訪問 CoolerMaster 機殼產品頁面...")
        
        try:
            # 訪問機殼主頁面
            self.driver.get(self.base_url)
            print("頁面加載中，等待內容渲染...")
            time.sleep(5)  # 給頁面足夠的時間加載
            
            # 保存渲染後的 HTML
            self.save_html_for_debug(self.driver.page_source, "coolermaster_page_full.html")
            
            # 獲取所有產品連結
            product_links = []
            
            # 從頁面中尋找所有機殼產品連結
            try:
                # 尋找所有可能是產品卡片的元素
                product_cards = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/en-global/products/']")
                
                for card in product_cards:
                    href = card.get_attribute("href")
                    if href and "/products/" in href:
                        if href not in product_links:
                            product_links.append(href)
                            print(f"找到產品連結: {href}")
            except Exception as e:
                print(f"尋找產品卡片時出錯: {str(e)}")
            
            # 檢查是否有分頁 (當前頁是否在總頁數之前)
            try:
                # 嘗試找到分頁導航元素
                pagination = self.driver.find_elements(By.CSS_SELECTOR, "nav[aria-label='pagination'], .pagination, .pager")
                
                if pagination:
                    # 檢查是否有"下一頁"按鈕
                    next_button = self.driver.find_elements(By.CSS_SELECTOR, "a[aria-label='next'], .next, .next-page")
                    
                    if next_button and next_button[0].is_enabled():
                        # 有下一頁，需要爬取後續頁面
                        for page in range(2, 6):  # 假設最多有5頁
                            next_page_url = f"{self.base_url}?page={page}"
                            print(f"爬取第 {page} 頁: {next_page_url}")
                            
                            # 訪問下一頁
                            self.driver.get(next_page_url)
                            time.sleep(3)  # 等待頁面加載
                            
                            # 保存頁面 HTML
                            self.save_html_for_debug(self.driver.page_source, f"coolermaster_page_{page}.html")
                            
                            # 獲取當前頁面的產品連結
                            page_cards = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/en-global/products/']")
                            
                            for card in page_cards:
                                href = card.get_attribute("href")
                                if href and "/products/" in href:
                                    if href not in product_links:
                                        product_links.append(href)
                                        print(f"第 {page} 頁找到產品連結: {href}")
            except Exception as e:
                print(f"處理分頁時出錯: {str(e)}")
            
            # 如果找不到產品連結，添加一些已知的產品連結
            if not product_links:
                known_products = [
                    "https://www.coolermaster.com/en-global/products/ncore-100-air/"
                ]
                
                for product in known_products:
                    if product not in product_links:
                        product_links.append(product)
                        print(f"添加已知產品連結: {product}")
            
            print(f"總共找到 {len(product_links)} 個產品連結")
            return product_links
            
        except Exception as e:
            print(f"獲取產品連結時發生錯誤: {str(e)}")
            return []
    
    def extract_storyblok_images(self, product_url, product_name):
        """從產品頁面提取 storyblok 高解析度圖片"""
        print(f"正在從 {product_url} 爬取 storyblok 高解析度圖片...")
        
        try:
            # 使用 Selenium 訪問產品頁面
            self.driver.get(product_url)
            print("產品頁面加載中...")
            time.sleep(5)  # 給頁面足夠的時間加載
            
            # 儲存產品頁面的 HTML
            product_id = product_url.rstrip('/').split('/')[-1]
            debug_filename = f"product_{product_id}.html"
            self.save_html_for_debug(self.driver.page_source, debug_filename)
            
            # 清理產品名稱以用作檔案名稱
            safe_name = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in product_name])
            
            # 提取所有 storyblok 圖片 URL
            images_info = []
            
            # 方法1: 尋找具有 srcset 屬性的圖片
            try:
                # 獲取頁面上所有的圖片元素
                img_elements = self.driver.find_elements(By.TAG_NAME, "img")
                found_storyblok_urls = set()
                
                for i, img in enumerate(img_elements):
                    try:
                        # 獲取 srcset 屬性
                        srcset = img.get_attribute("srcset")
                        
                        if srcset and "storyblok" in srcset:
                            # 使用正則表達式從 srcset 中提取 storyblok URL
                            storyblok_urls = re.findall(r'(https://a\.storyblok\.com/f/\d+/[^,\s]+)', srcset)
                            
                            # 找出最大尺寸的圖片 URL (通常是最後一個)
                            for url in storyblok_urls:
                                if url not in found_storyblok_urls:
                                    found_storyblok_urls.add(url)
                                    
                                    # 從 URL 中提取尺寸信息
                                    dimensions_match = re.search(r'/(\d+)x(\d+)/', url)
                                    dimensions = f"{dimensions_match.group(1)}x{dimensions_match.group(2)}" if dimensions_match else "unknown"
                                    
                                    img_filename = f"{safe_name}_{i}_{dimensions}.jpg"
                                    img_path = os.path.join(self.output_dir, "images", img_filename)
                                    
                                    images_info.append({
                                        "url": url,
                                        "local_path": img_path,
                                        "dimensions": dimensions
                                    })
                                    
                                    print(f"找到 storyblok 圖片: {url}")
                                    
                                    # 下載圖片
                                    try:
                                        urllib.request.urlretrieve(url, img_path)
                                        print(f"已儲存圖片: {os.path.basename(img_path)}")
                                    except Exception as e:
                                        print(f"下載圖片 {url} 時出錯: {str(e)}")
                    except Exception as e:
                        continue
                        
                # 方法2: 從 JavaScript 中提取 storyblok URL
                page_source = self.driver.page_source
                
                # 使用正則表達式從頁面源碼中查找 storyblok URL
                storyblok_js_urls = re.findall(r'(https://a\.storyblok\.com/f/\d+/\d+x\d+/[^"\')\s]+)', page_source)
                
                for j, url in enumerate(storyblok_js_urls):
                    if url not in found_storyblok_urls:
                        found_storyblok_urls.add(url)
                        
                        # 從 URL 中提取尺寸信息
                        dimensions_match = re.search(r'/(\d+)x(\d+)/', url)
                        dimensions = f"{dimensions_match.group(1)}x{dimensions_match.group(2)}" if dimensions_match else "unknown"
                        
                        img_filename = f"{safe_name}_js_{j}_{dimensions}.jpg"
                        img_path = os.path.join(self.output_dir, "images", img_filename)
                        
                        images_info.append({
                            "url": url,
                            "local_path": img_path,
                            "dimensions": dimensions
                        })
                        
                        print(f"在 JavaScript 中找到 storyblok 圖片: {url}")
                        
                        # 下載圖片
                        try:
                            urllib.request.urlretrieve(url, img_path)
                            print(f"已儲存圖片: {os.path.basename(img_path)}")
                        except Exception as e:
                            print(f"下載圖片 {url} 時出錯: {str(e)}")
                
                print(f"總共找到 {len(images_info)} 張 storyblok 圖片")
                return images_info
            except Exception as e:
                print(f"提取 storyblok 圖片時出錯: {str(e)}")
                return []
        except Exception as e:
            print(f"爬取 {product_url} 時發生錯誤: {str(e)}")
            return []
    
    def run(self):
        """執行爬蟲主流程"""
        print("開始爬取 CoolerMaster 機殼產品的高解析度圖片...")
        
        try:
            # 獲取所有產品連結
            product_links = self.get_all_case_links()
            
            if not product_links:
                print("未找到任何產品連結，爬蟲停止")
                return
            
            all_images_data = []
            
            for i, link in enumerate(product_links):
                # 從 URL 中提取產品名稱
                product_name = link.rstrip('/').split('/')[-1].replace('-', ' ').title()
                print(f"處理產品 ({i+1}/{len(product_links)}): {product_name}")
                
                # 提取該產品的 storyblok 高解析度圖片
                product_images = self.extract_storyblok_images(link, product_name)
                
                if product_images:
                    all_images_data.append({
                        "product_name": product_name,
                        "product_url": link,
                        "images": product_images
                    })
                    print(f"成功爬取產品 {product_name} 的 {len(product_images)} 張圖片")
                
                # 爬取間隔，避免請求過於頻繁
                if i < len(product_links) - 1:
                    delay = 0.01
                    print(f"等待 {delay:.2f} 秒後繼續下一個產品...")
                    time.sleep(delay)
            
            # 將所有圖片資訊保存為 JSON
            json_path = os.path.join(self.output_dir, "storyblok_images.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_images_data, f, ensure_ascii=False, indent=2)
            
            print(f"爬蟲完成！總共爬取了 {len(all_images_data)} 個產品的高解析度圖片")
            print(f"圖片資訊已保存至 {json_path}")
            
        except Exception as e:
            print(f"爬蟲執行過程中發生錯誤: {str(e)}")
        finally:
            # 關閉瀏覽器
            if hasattr(self, 'driver'):
                self.driver.quit()
                print("瀏覽器已關閉")

if __name__ == "__main__":
    crawler = CoolerMasterCrawler()
    crawler.run()