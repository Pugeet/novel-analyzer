"""
主题分析 — 核心主题、象征意义、社会背景
"""
from analyzer.llm import NovelLLM

THEME_PROMPT = """你是一位专业文学研究者。请分析以下小说的主题与深层含义。

请从以下维度分析：

1. **核心主题**：用一句话概括小说的核心主题
2. **主题层次**：
   - 表层主题：故事直接表达的内容
   - 深层主题：作品的社会/哲学/人性思考
3. **象征与隐喻**：作品中是否存在象征性元素？重复出现的意象？
4. **社会背景**：作品反映了什么样的时代或社会背景？
5. **价值取向**：作者通过故事传达了什么样的价值观？
6. **主题评分**：给主题深度一个综合评分(1-10)

请用 Markdown 格式输出。"""


def analyze_theme(text: str, model: str = "claude") -> str:
    """分析主题"""
    llm = NovelLLM(model)
    sample = text[:8000]
    return llm.invoke(THEME_PROMPT, f"请分析以下小说的主题：\n\n{sample}")
