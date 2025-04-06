import requests
import re


def fetch_chat_response(message: str) -> str:
    """
    向本地 HTTP 接口发送聊天请求，并返回 textResponse 中 <think> 标签之后的正文内容。

    参数:
        message (str): 聊天内容

    返回:
        str: 去除 <think> 思考部分后的真实回答文本
    """
    url = "http://localhost:8000/ask"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "question": message
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("answer")
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"请求异常：{e}"
