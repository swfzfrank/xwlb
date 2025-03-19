import re
import logging

# 配置日志记录器
logging.basicConfig(filename='xwlb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_structured_text(text):
    # 主条目分割：优先用换行符，否则用分号
    if '\n' in text:
        main_items = re.split(r'\n(?=\d+[\.。、])', text.strip())  # 前瞻保留编号前缀
    else:
        main_items = re.split(r'；(?=\d+[\.。、])', text.strip())  # 分号后必须跟新编号
    
    # 清理空白项
    main_items = [item.strip().rstrip('；') for item in main_items if item.strip()]
    
    result = []
    for item in main_items:
        item = item.replace('\r\n', '').strip()
        # 提取主条目编号和内容（严格匹配 "数字.内容" 格式）
        header_match = re.match(r'(\d+[\.。、])\s*(.*)', item)
        if not header_match:
            continue
            
        num_mark, content = header_match.groups()
        content = content.strip()
        
        subTextFlag = ("联播快讯" in content)
        if not subTextFlag:
            result.append(f"{num_mark} {content}")
        else:
            title = content.split('：')[0] # 提取主标题（子条目前的部分）
            content = content.split('联播快讯：')[1]
            # 检测子条目（严格匹配 "（数字）内容" 格式）
            sub_pattern = r'(?:；|^)\s*([\(（]\d+[\)）])\s*(.*?)(?=；|$|（\d+）|\(\d+\))'
            sub_matches = re.findall(sub_pattern, content)
            
            sub_list = [sub[1].strip() for sub in sub_matches]
            result.append([f"{title}", sub_list])
            
    
    return result

def printStructuredData(structured_data):
    for item in structured_data:
        if isinstance(item, list):
            logging.info(f"{item[0]}")
            for j, sub in enumerate(item[1], 1):
                logging.info(f"  └─({j}) {sub}")
        else:
            logging.info(item)