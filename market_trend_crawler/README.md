# Market Trend Crawler

## 專案簡介

該工具會從多個來源（如 Amazon、Newegg、Reddit 和巴哈姆特）收集數據，進行分析並生成每日報告(目前成功的只有 Reddit 和巴哈姆特)。

## 專案結構

```
market_trend_crawler/
├── crawler/
│   ├── amazon_crawler.py
│   ├── newegg_crawler.py
│   ├── reddit_crawler.py
│   └── bahamut_crawler.py
├── analyzer/
│   ├── keyword_extractor.py
│   ├── visualization.py
├── reports/
│   └── (每日生成的md報告)
├── scheduler/
│   └── schedule_runner.py
├── main.py
├── requirements.txt
└── README.md
```

## 功能

- **爬取數據**：從多個來源收集市場趨勢數據。
- **數據分析**：提取關鍵字並生成視覺化圖表。
- **報告生成**：每日生成 Markdown 格式的報告。
- **定時執行**：自動化爬取和分析流程。

## 使用方式

1. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
2. 執行主程式：
   ```bash
   python main.py
   ```
3. 查看每日生成的報告：
   前往 `reports/` 資料夾查看最新的報告。

## 目標網站

- [Newegg](https://www.newegg.com/)
- [Amazon](https://www.amazon.com/)
- [Reddit](https://www.reddit.com/)
- [巴哈姆特](https://www.gamer.com.tw/)
