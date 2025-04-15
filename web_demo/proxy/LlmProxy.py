import logging
import httpx

logger = logging.getLogger(__name__)

async def fetch_llm_stream_async(message: str):
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
        logging.info("fetch_llm_stream")

        timeout = httpx.Timeout(300.0, connect=30.0)
        async with httpx.AsyncClient(timeout = timeout) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    logger.error(f"[错误] 状态码：{response.status_code}")
                    raise Exception(f"[错误] 状态码：{response.status_code}")

                async for line in response.aiter_lines():
                    if line:
                        yield line
    except Exception as e:
        logger.error(f"请求异常：{e}")
        raise e
