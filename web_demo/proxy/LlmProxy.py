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

            # 用正则定位 <think> 标签，获取其后的内容
            match = re.search(r"</think>\s*(.+)", text_response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return "未找到 <think> 之后的回答内容。"
        else:
            return f"请求失败，状态码：{response.status_code}"
    except Exception as e:
        return f"请求异常：{e}"
