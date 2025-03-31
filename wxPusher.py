import requests
import base64
import logging

# 配置日志记录
logging.basicConfig(filename='xwlb.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_wxpusher_message(content, uids, app_token, topicIds, title=None):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "uids": uids,  # 关键修复：字段名从 "uid" 改为 "uids"
        "topicIds": topicIds,
        "summary": title,  # 关键字段：设置标题（显示在消息通知栏）
        "contentType": 1,
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_subscribed_uids(app_token, app_key, page=1, page_size=100):
    url = "https://wxpusher.zjiecode.com/api/fun/wxuser/v2"
    params = {
        "appToken": app_token,
        "appKey": app_key,
        "page": page,
        "pageSize": page_size
    }
    response = requests.get(url, params=params)
    result = response.json()
    if result["code"] == 1000:
        return [user["uid"] for user in result["data"]["records"]]
    else:
        logging.info(f"获取失败: {result['msg']}")
        return []

def upload_image(image_path):
    upload_url = "https://www.imgurl.org/api/v2/upload"
    
    # 表单参数（替换成你的实际凭证）
    data = {
        "uid": "acabed89e4573e1d04791855e06f6beb",  # 替换为您的UID
        "token": "1153c6e9dac1b68fcd7240e395f59cc2"  # 替换为您的Token
    }
    
    # 文件参数（注意保持name="file"与表单一致）
    with open(image_path, 'rb') as f:
        files = {'file': f}
        
        try:
            response = requests.post(upload_url, data=data, files=files)
            result = response.json()
            
            if result.get('code') == 200:
                return result['data']['url']  # 根据实际返回结构调整字段名
            else:
                logging.info(f"上传失败：{result.get('msg', '未知错误')}")
                return None
        except Exception as e:
            logging.info(f"请求异常：{str(e)}")
            return None

def send_wxpusher_image(image_path, uids, app_token, topicIds, title=None):
    # 上传图片并获取图片URL
    image_url = upload_image(image_path)
    if not image_url:
        logging.info("图片上传失败，无法发送消息。")
        return

    # 使用HTML格式显示图片
    content = f'<img src="{image_url}" alt="Image">'
    
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "uids": uids,
        "topicIds": topicIds,
        "summary": title,
        "contentType": 2,  # HTML类型
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

if __name__ == "__main__":
    APP_TOKEN = "AT_yqnyoG262pwdmA6esDdvyp804v74jsrK"  # xwlb专用 APP_TOKEN
    USER_UIDS = ["UID_wKraNNh5OPgSq2kP0neChHsNC3Sd"]
    send_wxpusher_image("place_cloud.png", USER_UIDS, APP_TOKEN, [39053], "wordcloud")