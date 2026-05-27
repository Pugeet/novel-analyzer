"""
人物分析 — 角色识别、性格特点、人物关系
"""
from analyzer.llm import NovelLLM

CHARACTER_PROMPT = """你是一位专业文学评论家，擅长分析小说人物。

请从以下维度分析：

1. **主要人物清单**：列出所有重要角色，每个角色一句话介绍
2. **主角深度分析**：
   - 性格特点：用3-5个关键词概括
   - 成长弧线：从开篇到结尾经历了什么变化？
   - 动机与目标：内在动机和外在目标是什么？
3. **人物关系图**：描述主要角色之间的关系（对立/同盟/爱慕/师徒等）
4. **配角功能**：每个配角在故事中承担什么叙事功能？
5. **人物塑造手法**：作者如何让人物"活"起来？（对话/行动/心理描写/侧面烘托）
6. **人物评分**：给人物塑造一个综合评分(1-10)

请用 Markdown 格式输出。"""


def analyze_characters(text: str, model: str = "claude") -> str:
    """分析人物"""
    llm = NovelLLM(model)
    sample = text[:10000]
    return llm.invoke(CHARACTER_PROMPT, f"请分析以下小说的人物：\n\n{sample}")
