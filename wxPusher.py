import requests

def send_wxpusher_message(content, uids, app_token, topicIds):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "uids": uids,  # 关键修复：字段名从 "uid" 改为 "uids"
        "topicIds": topicIds,
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
        print("获取失败:", result["msg"])
        return []