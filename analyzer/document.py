"""
文档处理 — 支持 PDF / Word / TXT 解析
"""
from io import BytesIO


def parse_document(uploaded_file) -> tuple[str, str]:
    """解析上传文件，返回 (纯文本, 文件名)"""
    filename = uploaded_file.name.lower()
    content = uploaded_file.read()

    if filename.endswith(".txt"):
        text = _parse_txt(content)
    elif filename.endswith(".pdf"):
        text = _parse_pdf(content)
    elif filename.endswith(".docx"):
        text = _parse_docx(content)
    else:
        raise ValueError(f"不支持的文件类型: {filename}")

    return text, uploaded_file.name


def _parse_txt(content: bytes) -> str:
    for enc in ["utf-8", "gbk", "gb2312", "latin-1"]:
        try:
            return content.decode(enc)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def _parse_pdf(content: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(content))
    parts = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            parts.append(t)
    return "\n\n".join(parts)


def _parse_docx(content: bytes) -> str:
    from docx import Document
    doc = Document(BytesIO(content))
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    return "\n".join(parts)
