import requests


def fetch_llm_stream(message: str):
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
        "Accept": "text/plain"
    }
    payload = {
        "question": message
    }

    try:
        # stream=True 开启流式响应
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            if response.status_code != 200:
                return f"请求失败，状态码：{response.status_code}"

            for line in response.iter_lines(decode_unicode=True):
                if line:
                    yield line
    except Exception as e:
        return f"请求异常：{e}"
