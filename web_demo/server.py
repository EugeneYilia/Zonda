import base64
import json
import re
import asyncio
import time

from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from web_demo import SystemConfig
from web_demo.proxy.LlmProxy import fetch_llm_stream_async
from web_demo.tils.MDUtils import clean_markdown
import colorama
colorama.just_fix_windows_console()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ 启动前执行
    logger.info("FastAPI 启动：is_use_gpu: %s", SystemConfig.is_use_gpu)
    logger.info("FastAPI 启动：is_dev_mode: %s", SystemConfig.is_dev_mode)

    yield  # 🟢 应用运行中

    # ✅ 关闭前执行（可选）
    logger.info("FastAPI 即将关闭")
app = FastAPI(lifespan=lifespan)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="web_demo/static"), name="static")

import logging
logger = logging.getLogger(__name__)

# async def get_audio_by_edge_tts(text_cache, voice_speed, voice_id):
#     import edge_tts
#     import tempfile
#     import os
#     from pydub import AudioSegment
#
#     if voice_speed is None or voice_speed == "":
#         rate = "+0%"  # rate = "-50%"
#     elif int(voice_speed) >= 0:
#         rate = f"+{int(voice_speed)}%"
#     else:
#         rate = f"{int(voice_speed)}%"
#
#     if voice_id == "female":
#         voice = "zh-CN-XiaoxiaoNeural"
#     else:
#         voice = "zh-TW-YunJheNeural"
#
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_mp3:
#         mp3_path = tmp_mp3.name
#     wav_path = mp3_path.replace(".mp3", ".wav")
#
#     communicate = edge_tts.Communicate(text_cache, voice=voice, rate=rate)
#     await communicate.save(mp3_path)
#
#     # 转换为 WAV
#     sound = AudioSegment.from_file(mp3_path, format="mp3")
#     sound = sound.set_frame_rate(16000).set_channels(1)
#     sound.export(wav_path, format="wav")
#
#     with open(wav_path, "rb") as audio_file:
#         audio_value = audio_file.read()
#
#     os.remove(mp3_path)
#     os.remove(wav_path)
#
#     return base64.b64encode(audio_value).decode("utf-8")

async def get_audio(text, voice_speed, voice_id):
    logger.info(f"text: {text} voice_speed: {voice_speed}  voice_id: {voice_id}")
    url = "http://127.0.0.1:8189/synthesize"
    payload = {
        "text": text,
        "voice_id": voice_id
    }

    timeout = httpx.Timeout(300.0, connect=30.0)

    async with httpx.AsyncClient(timeout = timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()  # 抛出非 2xx 异常
        data = response.json()
        base64_audio = data["audio"]
        logger.info(f"Received base64 audio string {text}.")

        return base64_audio

def split_sentence(sentence, min_length=10):
    # 定义包括小括号在内的主要标点符号
    punctuations = r'[。？！；…，、()（）]'
    # 使用正则表达式切分句子，保留标点符号
    parts = re.split(f'({punctuations})', sentence)
    parts = [p for p in parts if p]  # 移除空字符串
    sentences = []
    current = ''
    for part in parts:
        if current:
            # 如果当前片段加上新片段长度超过最小长度，则将当前片段添加到结果中
            if len(current) + len(part) >= min_length:
                sentences.append(current + part)
                current = ''
            else:
                current += part
        else:
            current = part
    # 将剩余的片段添加到结果中
    if len(current) >= 2:
        sentences.append(current)
    return sentences


# async def gen_stream_old(question, asr=False, voice_speed=None, voice_id=None):
#     logger.info(f"gen_stream   voice_speed: {voice_speed}   voice_id: {voice_id}")
#     if asr:
#         chunk = {"question": question}
#         yield f"{json.dumps(chunk)}\n"  # 使用换行符分隔 JSON 块
#
#     text_cache = llm_answer(question)
#     sentences = split_sentence(text_cache)
#
#     for index_, sub_text in enumerate(sentences):
#         base64_string = await get_audio(clean_markdown(sub_text), voice_speed, voice_id)
#         # 生成 JSON 格式的数据块
#         chunk = {"text": sub_text, "audio": base64_string, "endpoint": index_ == len(sentences) - 1}
#         yield f"{json.dumps(chunk)}\n"  # 使用换行符分隔 JSON 块

async def gen_stream(question, asr=False, voice_speed=None, voice_id=None):
    logger.info(f"gen_stream  question: {question}  voice_speed: {voice_speed}   voice_id: {voice_id}")

    if asr:
        chunk = {"question": question}
        yield f"{json.dumps(chunk)}\n"

    # 并发处理容器
    tasks = []
    idx = 0

    async for llm_response in fetch_llm_stream_async(question):
        logger.info(f"gen_stream   llm_response: {llm_response}")
        is_answer_end = False
        if llm_response.endswith("[Heil Hitler!]"):
            llm_response = llm_response.removesuffix("[Heil Hitler!]")
            is_answer_end = True

        clear_llm_response = clean_markdown(llm_response)
        if clear_llm_response == "":
            continue

        # 为当前响应创建异步音频任务
        task = asyncio.create_task(get_audio(clear_llm_response, voice_speed, voice_id))
        tasks.append((idx, clear_llm_response, task, is_answer_end))
        idx += 1

    # 按顺序 await 音频任务并 yield 到前端
    for idx, text, task, is_end in sorted(tasks, key=lambda x: x[0]):
        try:
            base64_string = await task
        except Exception as e:
            logger.exception(f"get_audio failed at idx={idx}: {e}")
            base64_string = ""
        chunk = {"text": text, "audio": base64_string, "endpoint": is_end}
        yield f"{json.dumps(chunk)}\n"

# 处理 ASR 和 TTS 的端点
@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...)):
    # 模仿调用 ASR API 获取文本
    text = "语音已收到，这里只是模仿，真正对话需要您自己设置ASR服务。"
    # 调用 TTS 生成流式响应
    return StreamingResponse(gen_stream(text, asr=True), media_type="application/json")


async def call_asr_api(audio_data):
    # 调用ASR完成语音识别
    answer = "语音已收到，这里只是模仿，真正对话需要您自己设置ASR服务。"
    return answer


@app.post("/eb_stream")  # 前端调用的path
async def eb_stream(request: Request):
    try:
        body = await request.json()
        input_mode = body.get("input_mode")
        voice_speed = body.get("voice_speed")
        voice_id = body.get("voice_id")

        if input_mode == "audio":
            base64_audio = body.get("audio")
            # 解码 Base64 音频数据
            audio_data = base64.b64decode(base64_audio)
            # 这里可以添加对音频数据的处理逻辑
            question = await call_asr_api(audio_data)  # 假设 call_asr_api 可以处理音频数据
            return StreamingResponse(gen_stream(question, asr=True, voice_speed=voice_speed, voice_id=voice_id),
                                     media_type="application/json")
        elif input_mode == "text":
            question = body.get("question")
            logger.info(f"User text input: {question}")
            return StreamingResponse(gen_stream(question, asr=False, voice_speed=voice_speed, voice_id=voice_id),
                                     media_type="application/json")
        else:
            raise HTTPException(status_code=400, detail="Invalid input mode")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=FileResponse)
async def read_root():
    return FileResponse("web_demo/static/Yuri.html", media_type="text/html")


# 启动Uvicorn服务器
if __name__ == "__main__":
    import uvicorn

    if SystemConfig.is_dev_mode:
        uvicorn.run(
            "web_demo.server:app",
            host="0.0.0.0",
            port=8898,
            reload=SystemConfig.is_dev_mode,
            log_config="web_demo/log_config.yml"
        )
    else:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8898,
            reload=SystemConfig.is_dev_mode,
            log_config="web_demo/log_config.yml"
        )