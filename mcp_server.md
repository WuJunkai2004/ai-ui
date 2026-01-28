# MCP Server functionality

## 1. 全网实时情报能力 (Real-time Information Retrieval)
功能定义: 能够连接互联网搜索引擎，获取最新的新闻、价格、天气、政策变动等。
实现方式: bocha-search-mcp

## 2. 地理空间感知能力 (Geospatial Awareness)
功能定义： 地点检索、距离计算、路径规划、周边探索（POI Search）。
实现方式: amap-maps

## 3. 深度内容读取与浏览能力 (Web Browsing & Content Extraction)
功能定义： 能够像人一样打开网页，提取其中的正文、表格数据、或者特定参数，排除广告干扰。
实现方式: fetcher

## 4. 本地文件操作与交付能力 (Filesystem I/O)
功能定义： 读取用户上传的文件（PDF/Word/Excel），或在本地生成新的文件、修改现有文件。
实现方式: filesystem

## 5. 逻辑计算与代码执行能力 (Code Execution / Calculator)
功能定义： 提供一个 Python 解释器环境，让 AI 可以写代码来计算复杂的费用、统计数据、或者绘图。
实现方式: mcp-run-python