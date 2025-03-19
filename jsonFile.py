import json
from datetime import datetime

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
            return data.get(date, "未找到该日期的数据")
    except FileNotFoundError:
        return "数据文件不存在"
