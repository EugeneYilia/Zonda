import re

def clean_markdown(text: str) -> str:
    # 去除代码块（```代码```）
    text = re.sub(r'```[\s\S]*?```', '', text)

    # 去除内联代码（`code`）
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # 去除图片语法 ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 转换链接语法 [text](url) => text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 去掉加粗/斜体组合语法 ***text*** 或 ___text___
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
    text = re.sub(r'___(.*?)___', r'\1', text)

    # 去掉加粗语法 **text** 或 __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)

    # 去掉斜体语法 *text* 或 _text_
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.*?)_(?!_)', r'\1', text)

    # 删除线语法 ~~text~~
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # 去掉标题符号 #，保留内容
    text = re.sub(r'^\s{0,3}#{1,6}\s*(.*)', r'\1', text, flags=re.MULTILINE)

    # 去掉引用符号 >
    text = re.sub(r'^\s{0,3}>\s?', '', text, flags=re.MULTILINE)

    # 去掉无序列表符号 *, -, +
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)

    # 去掉有序列表符号 1. 2. 3.
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # 去掉表格分隔线 | 和 ---
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'^\s*[-:| ]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 去掉所有孤立的星号（非强调用途）
    text = re.sub(r'(?<!\S)\*(?!\S)', '', text)

    # 合并多余空行，去除首尾空白
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()

    return text
