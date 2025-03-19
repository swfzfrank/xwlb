import xwlb
import contextBrief
import jsonFile
from datetime import datetime, timedelta

start_day = "20250310"
end_day = "20250315"

if __name__ == "__main__":
    # 将开始日期和结束日期转换为 datetime 对象
    start_date = datetime.strptime(start_day, "%Y%m%d")
    if end_day == "current":
        end_day = datetime.now().strftime("%Y-%m-%d")
    end_date = datetime.strptime(end_day, "%Y%m%d")
    
    current_date = start_date
    
    while current_date <= end_date:
        # 将当前日期转换为字符串格式 "YYYYMMDD"
        date_str = current_date.strftime("%Y%m%d")
        
        # 获取新闻联播的 URL
        url = xwlb.get_xwlb_url_byDate(date_str)
        if url:
            # 获取新闻联播的内容摘要
            result = xwlb.get_xwlb_contextBrief(url)
            
            # 解析结构化文本
            structured_text = contextBrief.parse_structured_text(result)
            
            # 保存到 JSON 文件
            jsonFile.save_to_json(structured_text, date_str)
        
        # 递增一天
        current_date += timedelta(days=1)