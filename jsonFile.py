import logging
import json
from datetime import datetime

# 配置日志记录器
logging.basicConfig(filename='xwlb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_json(structured_text, date, filename="news_data.json"):
    # 读取现有数据（如果文件存在）
    try:
        with open(filename, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    
    # 将新数据合并到当前日期下
    existing_data[date] = structured_text
    
    # 写回文件
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

def load_from_json(date, filename="news_data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if date in data:
                # 格式化输出
                if isinstance(data[date], list):
                    return "\n".join(json.dumps(item, ensure_ascii=False, indent=2) for item in data[date])
                else:
                    return json.dumps(data[date], ensure_ascii=False, indent=2)
            else:
                logging.info("未找到该日期的数据")
                return "未找到该日期的数据"
    except FileNotFoundError:
        logging.error("数据文件不存在")
        return "数据文件不存在"