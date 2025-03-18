import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def get_xwlb_contextBrief(url):
    # 设置请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': url  # 防盗链需要
    }
    
    # 1. 获取网页内容并提取m3u8链接
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    html = response.text

    brief_pattern = r'本期节目主要内容：(.*?)（《新闻联播'
    brief_match = re.search(brief_pattern, html, re.DOTALL)

    if brief_match:
        print("匹配到的内容:", brief_match.group(1))
        return brief_match.group(1)
    else:
        print("未找到匹配的内容")
        return None
  

def get_xwlb_url_byDate(target_date=None):
    # 1. 生成目标页面URL
    url = f"https://tv.cctv.com/lm/xwlb/day/{target_date}.shtml"

    # 2. 配置浏览器级请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://tv.cctv.com/lm/xwlb/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    try:
        # 3. 发起请求（建议添加代理参数）
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # 4. 精准定位内容区域
        soup = BeautifulSoup(resp.text, 'html.parser')
        content_div = soup.find('div', class_='image')
        if not content_div:
            raise ValueError("无法获取视频链接")

        for element in content_div(['a']):
            videoUrl = element.get('href')
            print(videoUrl)
        
        return videoUrl

    except Exception as e:
        print(f"[ERROR] 抓取失败：{str(e)}")
        # 显示调试信息
        if 'resp' in locals():
            with open(f"debug_{target_date}.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
        return None

# 使用示例（获取当日新闻）
if __name__ == "__main__":
    url = get_xwlb_url_byDate("20250317")
    if url:
        result = get_xwlb_contextBrief(url)
