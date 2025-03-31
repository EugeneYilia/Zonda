import requests
import re

def query_chatbot(message: str) -> str:
    """
    向本地接口发送请求并提取 <think> 标签中的响应内容。

    参数:
        message (str): 要发送的聊天消息内容。

    返回:
        str: 提取的 <think> 标签内容，如果未找到则返回提示信息。
    """
    url = "http://localhost:3001/api/v1/workspace/decfb45a-25f6-4541-b6d4-029172f2fc97/thread/587df2b0-573c-43fd-9265-14df45581b86/chat"
    headers = {
        "Authorization": "Bearer 7NXBQRE-9GDMJFA-P9MA3EC-MQ4K0MQ",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "message": message,
        "mode": "chat"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            text_response = data.get("textResponse", "")
            match = re.search(r"<think>(.*?)</think>", text_response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return "未找到 <think> 标签中的内容。"
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"请求出错：{e}"
