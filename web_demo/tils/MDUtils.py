import re

def clean_markdown(text: str) -> str:
    # 去除代码块（```代码```）
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 去除内联代码（`code`）
    text = re.sub(r'`([^`]*)`', r'\1', text)

    # 去除图片语法 ![alt](url)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 转换链接语法 [text](url) => text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # 去掉加粗语法 **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

    # 去掉斜体语法 *text* 或 _text_
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', text)  # 单星斜体
    text = re.sub(r'_(.*?)_', r'\1', text)

    # 删除线语法 ~~text~~
    text = re.sub(r'~~(.*?)~~', r'\1', text)

    # 去掉标题符号 #，保留内容
    text = re.sub(r'#+\s*(.*)', r'\1', text)

    # 去掉引用符号 >
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)

    # 去掉无序列表符号 *, -, +
    text = re.sub(r'^[\*\-\+]\s+', '', text, flags=re.MULTILINE)

    # 去掉多余空行和前后空白
    text = re.sub(r'\n{2,}', '\n', text)
    text = text.strip()

    return text