"""
小说智能分章 — 按章节/场景拆分文本
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re


def split_by_chapter(text: str) -> list[dict]:
    """
    尝试按常见章节标记拆分（"第X章"、"Chapter X"等）
    返回 [{"title": "第1章 xxx", "content": "..."}, ...]
    """
    chapter_patterns = [
        r'(第[一二三四五六七八九十百千0-9]+章[^\n]*)',
        r'(Chapter\s+\d+[^\n]*)',
        r'(第[一二三四五六七八九十百千0-9]+节[^\n]*)',
    ]

    for pat in chapter_patterns:
        parts = re.split(pat, text)
        if len(parts) > 2:  # 成功匹配到章节
            chapters = []
            # parts[0] 是前言，parts[1] 是第一章标题，parts[2] 是第一章内容...
            if parts[0].strip():
                chapters.append({"title": "前言", "content": parts[0].strip()})
            for i in range(1, len(parts), 2):
                title = parts[i].strip()
                content = parts[i + 1].strip() if i + 1 < len(parts) else ""
                chapters.append({"title": title, "content": content})
            return chapters

    # 没找到章节标记，按段落长度大致拆分
    return _fallback_split(text)


def split_to_chunks(text: str, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """将文本切分为固定大小的块（用于向量存储）"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )
    return splitter.split_text(text)


def _fallback_split(text: str, target_chapters: int = 10) -> list[dict]:
    """无法识别章节时，按字符数均分"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    total = len(paragraphs)
    per_chapter = max(1, total // target_chapters)

    chapters = []
    for i in range(0, total, per_chapter):
        chunk = paragraphs[i:i + per_chapter]
        chapters.append({
            "title": f"段落 {i//per_chapter + 1}",
            "content": "\n\n".join(chunk),
        })
    return chapters
