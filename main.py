import logging
import xwlb
import contextBrief
import jsonFile
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import wxPusher

# 配置日志记录器
logging.basicConfig(filename='xwlb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

start_day = "20250301"
end_day = "current"
# 配置参数
APP_TOKEN = "AT_yqnyoG262pwdmA6esDdvyp804v74jsrK"  # xwlb专用 APP_TOKEN
USER_UIDS = ["UID_wKraNNh5OPgSq2kP0neChHsNC3Sd"]
APP_KEY = 96458
# 创建一个锁对象
lock = threading.Lock()


def join_list_with_newline(items):
    """
    将列表中的每个元素拼接成一个字符串，每个元素之间由换行符连接。
    如果元素是列表，则递归处理。
    
    :param items: 包含字符串或列表的列表
    :return: 拼接后的字符串
    """
    result = []
    for item in items:
        if isinstance(item, list):
            result.append(join_list_with_newline(item))
        else:
            result.append(item)
    return "\n".join(result)


def process_xwlb(date_str):
    # 获取新闻联播的 URL
    url = xwlb.get_xwlb_url_byDate(date_str)
    if url:
        # 获取新闻联播的内容摘要
        result = xwlb.get_xwlb_contextBrief(url)
        
        # 解析结构化文本
        structured_text = contextBrief.parse_structured_text(result)
        
        # 保存到 JSON 文件时加锁
        with lock:
            jsonFile.save_to_json(structured_text, date_str)
    else:
        logging.info(f"无法获取新闻联播URL，日期: {date_str}")

if __name__ == "__main__":
    # 记录程序开始时间
    start_time = datetime.now()
    logging.info(f"程序开始时间: {start_time}")
    
    # 将开始日期和结束日期转换为 datetime 对象
    start_date = datetime.strptime(start_day, "%Y%m%d")
    if end_day == "current":
        current_hour = datetime.now().hour
        if current_hour > 22:
            end_day = datetime.now().strftime("%Y%m%d")
        else:
            end_day = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    end_date = datetime.strptime(end_day, "%Y%m%d")
    
    current_date = start_date
    
    dates = []
    while current_date <= end_date:
        # 将当前日期转换为字符串格式 "YYYYMMDD"
        date_str = current_date.strftime("%Y%m%d")
        dates.append(date_str)
        # 递增一天
        current_date += timedelta(days=1)
    
    # 使用线程池来并行处理每个日期
    with ThreadPoolExecutor() as executor:
        future_to_date = {executor.submit(process_xwlb, date_str): date_str for date_str in dates}
        for future in as_completed(future_to_date):
            date_str = future_to_date[future]
            try:
                future.result()
            except Exception as exc:
                logging.error(f'{date_str} generated an exception: {exc}')
    
    # 记录程序结束时间
    end_time = datetime.now()
    logging.info(f"程序结束时间: {end_time}")
    
    # 计算并打印程序运行时间
    elapsed_time = end_time - start_time
    logging.info(f"程序运行总时间: {elapsed_time}")

    readNews = jsonFile.load_from_json(end_day)
    # 新增：将readNews列表中的每个元素拼接成一个字符串
    readNews_str = join_list_with_newline(readNews)
    userUids = wxPusher.get_subscribed_uids(APP_TOKEN, APP_KEY)
    result = wxPusher.send_wxpusher_message(readNews_str, userUids, APP_TOKEN, [38685], end_day + "新闻联播内容")
    logging.info("推送结果: %s", result)

    