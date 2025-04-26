import os
from datetime import datetime
from crawler.reddit_crawler import RedditCrawler
from crawler.bahamut_crawler import BahamutCrawler
from analyzer.keyword_extractor import KeywordExtractor
from analyzer.visualization import Visualization
# from scheduler.schedule_runner import ScheduleRunner

if __name__ == "__main__":
    # 確保資料夾結構存在
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/md", exist_ok=True)
    os.makedirs("reports/images", exist_ok=True)

    # 初始化爬蟲
    reddit_crawler = RedditCrawler()
    bahamut_crawler = BahamutCrawler()

    # 爬取數據 (從 Reddit 和巴哈姆特爬取)
    print("從 Reddit 和巴哈姆特爬取真實數據中...")
    reddit_data = reddit_crawler.crawl()
    bahamut_data = bahamut_crawler.crawl()

    # 整合數據
    all_data = reddit_data + bahamut_data

    # 關鍵字提取與分析
    print("提取關鍵字中...")
    keyword_extractor = KeywordExtractor()
    keywords = keyword_extractor.extract(all_data)

    # 視覺化
    visualization = Visualization()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/md/market_trends_{timestamp}.md"
    print(f"生成報告中，報告將保存到: {report_path}")
    visualization.generate_report(keywords, report_path)

    # # 啟動定時任務
    # schedule_runner = ScheduleRunner()
    # schedule_runner.run()