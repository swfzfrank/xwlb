import json
import jieba.analyse  # 恢复 jieba.analyse 的导入
from collections import defaultdict
import logging
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from textrank4zh import TextRank4Keyword
import spacy  # 确保 spacy 库已导入
import time  # 导入 time 模块
import concurrent.futures  # 添加 concurrent.futures 导入

# 配置日志记录器
logging.basicConfig(filename='xwlb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_keywords_from_text(text, topK=20):
    """
    使用 spacy 提取文本中的关键字，并区分人名、地名和其他关键词
    
    :param text: 输入文本
    :param topK: 提取的关键字数量
    :return: 人名、地名和其他关键词的列表
    """
    nlp = spacy.load("zh_core_web_sm")  # 加载中文模型
    doc = nlp(text)
    
    names = set()
    places = set()
    other_keywords = set()
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.add(ent.text)
        elif ent.label_ == "GPE":
            places.add(ent.text)
    
    for token in doc:
        if token.is_stop != True and token.is_punct != True and token.pos_ == 'NOUN' and len(token.text) >= 2:
            if token.text not in names and token.text not in places:
                other_keywords.add(token.text)
    
    names = list(names)[:topK]
    places = list(places)[:topK]
    other_keywords = list(other_keywords)[:topK]
    
    return names, places, other_keywords

def flatten_list(nested_list):
    """
    将嵌套列表展平为一维字符串列表
    
    :param nested_list: 嵌套列表
    :return: 一维字符串列表
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def analyze_text(date, content, topK=20):
    """
    分析单个日期的文本内容
    
    :param date: 日期
    :param content: 文本内容
    :param topK: 提取的关键字数量
    :return: 人名、地名和其他关键词的列表
    """
    flat_content = flatten_list(content)  # 展平嵌套列表
    text_content = ' '.join(flat_content)  # 将展平后的内容列表转换为字符串
    names, places, keywords = extract_keywords_from_text(text_content, topK)  # 提取关键字
    return date, names, places, keywords

def analyze_json_file(json_file="news_data.json"):
    """
    根据JSON文件中每个日期的内容，提炼出其中的关键字和人名，并统计到“analyze.json”文件中
    
    :param json_file: 输入的JSON文件路径
    """
    start_time = time.time()  # 添加时间打点
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        name_stats = defaultdict(list)
        place_stats = defaultdict(list)
        keyword_stats = defaultdict(list)
        
        # 处理每个日期的内容
        for date, content in data.items():
            try:
                date, names, places, keywords = analyze_text(date, content)
                name_stats[date] = names
                place_stats[date] = places
                keyword_stats[date] = keywords
            except Exception as e:
                logging.error(f"处理日期 {date} 时出错: {e}")
        
        # 合并文件写操作
        with open("key_name.json", 'w', encoding='utf-8') as f_name, \
             open("key_place.json", 'w', encoding='utf-8') as f_place, \
             open("key_words.json", 'w', encoding='utf-8') as f_keyword:
            json.dump(name_stats, f_name, ensure_ascii=False, indent=4)  # 保存人名
            json.dump(place_stats, f_place, ensure_ascii=False, indent=4)  # 保存地名
            json.dump(keyword_stats, f_keyword, ensure_ascii=False, indent=4)  # 保存其他关键词
        
        logging.info(f"关键字和人名分析完成并保存为 key_name.json, key_place.json, key_words.json")
    
    except Exception as e:
        import traceback
        logging.error(f"分析JSON文件时出错: {e}\n{traceback.format_exc()}")
    
    end_time = time.time()  # 添加时间打点
    print(f"analyze_json_file 执行时间: {end_time - start_time} 秒")  # 打印执行时间

def count_keywords_in_period(start_date="20250101", end_date=None, input_file=None):
    """
    统计一段时间内关键词出现的次数
    
    :param start_date: 开始日期，默认为20250101
    :param end_date: 结束日期，默认为当前日期
    :param input_file: 输入的分析结果文件路径，默认为key_words.json
    :return: 关键词及其出现次数的列表
    """
    start_time = time.time()  # 添加时间打点
    try:
        if end_date is None:
            from datetime import datetime
            end_date = datetime.now().strftime("%Y%m%d")
        
        if input_file is None:
            input_file = "key_words.json"  # 修改默认输入文件路径
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keyword_counts = defaultdict(int)
        
        for date, keywords in data.items():
            if start_date <= date <= end_date:
                for keyword in keywords:
                    keyword_counts[keyword] += 1
        
        end_time = time.time()  # 添加时间打点
        print(f"count_keywords_in_period 执行时间: {end_time - start_time} 秒")  # 打印执行时间
        return list(keyword_counts.items())
    
    except Exception as e:
        import traceback
        logging.error(f"统计关键词出现次数时出错: {e}\n{traceback.format_exc()}")

def plot_wordcloud(top_keywords, picName = 'wordcloud.png'):
    """
    绘制词云图，关键字大小和出现次数成正比
    
    :param top_keywords: 关键字及其出现次数的列表
    """
    start_time = time.time()  # 添加时间打点
    try:
        # 检查字体文件是否存在
        import os
        font_path = 'NotoSansSC-VariableFont_wght.ttf'  # 修改为宋体字体文件路径
        if not os.path.exists(font_path):
            logging.warning(f"字体文件 {font_path} 不存在，将使用系统默认字体")
            font_path = None
        
        # 创建词云对象
        wordcloud = WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate_from_frequencies(dict(top_keywords))
        
        # 检查 wordcloud 对象是否正确生成
        if wordcloud is None:
            logging.error("词云对象未正确生成")
            return
        
        # 调试信息：打印词云对象的频率数据
        logging.debug(f"词云对象的频率数据: {wordcloud.words_}")
        
        # 显示词云图
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        #plt.show()
        
        # 保存词云图到文件
        wordcloud.to_file(picName)
        
        logging.info(f"词云图绘制完成并保存为 {picName}")
    
    except Exception as e:
        import traceback
        logging.error(f"绘制词云图时出错: {e}\n{traceback.format_exc()}")
    
    end_time = time.time()  # 添加时间打点
    print(f"plot_wordcloud 执行时间: {end_time - start_time} 秒")  # 打印执行时间

if __name__ == "__main__":
    analyze_json_file()
    # 示例调用
    keyname_counts = count_keywords_in_period(input_file="key_name.json")
    keyplace_counts = count_keywords_in_period(input_file="key_place.json")
    keyword_counts = count_keywords_in_period(input_file="key_words.json")
    plot_wordcloud(keyname_counts, "name_cloud.png")
    plot_wordcloud(keyplace_counts, "place_cloud.png")
    plot_wordcloud(keyword_counts, "word_cloud.png")
