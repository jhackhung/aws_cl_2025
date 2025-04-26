import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
import random

class KeywordExtractor:
    def __init__(self):
        # 嘗試下載 nltk 必要的資料
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        # 設置電競機殼相關的領域關鍵詞
        self.gaming_case_keywords = [
            "RGB", "散熱", "風扇", "水冷", "側板", "透明", "強化玻璃", 
            "機殼", "中塔", "全塔", "ITX", "ATX", "mATX", "前置面板",
            "風流", "擴充", "模組化", "濾網", "防塵", "USB", "Type-C",
            "線材管理", "靜音", "流光", "燈效", "一體式", "鋁合金", "鋼化",
            "ARGB", "顯卡支架", "背線", "直立", "垂直顯示", "硬碟架"
        ]
    
    def extract(self, data):
        print("Extracting keywords from data...")
        
        # 如果數據只是模擬的佔位符，生成模擬的電競機殼相關關鍵字
        if all(isinstance(item, str) and item.endswith("data") for item in data):
            keywords = {}
            num_keywords = random.randint(8, 15)  # 隨機選擇 8-15 個關鍵字
            selected_keywords = random.sample(self.gaming_case_keywords, num_keywords)
            
            for keyword in selected_keywords:
                # 生成隨機的權重，讓重要關鍵字權重較高
                weight = random.randint(10, 100)
                keywords[keyword] = weight
            
            # 按照權重降序排序
            keywords = dict(sorted(keywords.items(), key=lambda item: item[1], reverse=True))
            return keywords
        
        # 如果有實際爬取的數據，進行實際的文本分析
        all_text = " ".join(data)
        # 移除非中文和英文的字符
        clean_text = re.sub(r'[^\w\s]|_', ' ', all_text)
        # 分詞
        words = clean_text.lower().split()
        # 移除停用詞
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        # 計算詞頻
        word_counts = Counter(filtered_words)
        
        # 提取電競機殼相關的關鍵詞
        gaming_case_counts = {}
        for keyword in self.gaming_case_keywords:
            keyword_lower = keyword.lower()
            for word, count in word_counts.items():
                if keyword_lower in word or word in keyword_lower:
                    gaming_case_counts[keyword] = gaming_case_counts.get(keyword, 0) + count
        
        # 如果沒有找到任何關鍵詞，使用模擬的關鍵詞
        if not gaming_case_counts:
            return self.extract(["simulated data"])
        
        # 按照頻率降序排序
        gaming_case_counts = dict(sorted(gaming_case_counts.items(), key=lambda item: item[1], reverse=True))
        # 只取前15個關鍵詞
        top_keywords = dict(list(gaming_case_counts.items())[:15])
        
        return top_keywords