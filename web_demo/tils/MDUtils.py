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

    # 去掉三重加粗/斜体（***text*** 或 ___text___）
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)
    text = re.sub(r'___(.*?)___', r'\1', text)

    # 去掉加粗语法 **text** 或 __text__，兼容句尾标点
    text = re.sub(r'\*\*(.+?)\*\*(?=[\u4e00-\u9fa5\w\s]*[，。！？,.!?:;」」））”"\']*)', r'\1', text)
    text = re.sub(r'__(.+?)__(?=[\u4e00-\u9fa5\w\s]*[，。！？,.!?:;」」））”"\']*)', r'\1', text)

    # 去掉斜体 *text* 和 _text_，避免破坏乘号 *
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)_(?!_)', r'\1', text)

    # 删除线语法 ~~text~~
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # 去掉标题符号 #
    text = re.sub(r'^\s{0,3}#{1,6}\s*(.*)', r'\1', text, flags=re.MULTILINE)

    # 去掉引用符号 >
    text = re.sub(r'^\s{0,3}>\s?', '', text, flags=re.MULTILINE)

    # 去掉列表符号（无序和有序）
    text = re.sub(r'^\s*[\*\-\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # 去掉表格线和竖线
    text = re.sub(r'\|', ' ', text)
    text = re.sub(r'^\s*[-:| ]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 清理单独星号（非强调）
    text = re.sub(r'(?<!\S)\*(?!\S)', '', text)

    # 合并空行，去除多余空白
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()

    return text
