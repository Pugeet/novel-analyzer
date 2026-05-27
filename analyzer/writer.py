"""
小说仿写引擎 — 输入想法 + 分析结果 -> 一键生成全书
字数自动匹配输入小说
"""
from analyzer.llm import NovelLLM


def generate_outline(analyses: dict, user_idea: str, model: str = "claude") -> str:
    """基于小说分析和用户想法，生成故事大纲"""
    llm = NovelLLM(model)
    analysis_summary = _build_summary(analyses)
    prompt = _outline_prompt(analysis_summary, user_idea)
    return llm.invoke(prompt, "")


def write_full_novel(
    analyses: dict,
    outline: str,
    user_idea: str,
    target_words: int,
    model: str = "claude",
    progress_callback=None,
) -> str:
    """
    一键生成全书，字数匹配输入小说。

    策略：分章节生成，每章目标字数 = target_words / 10
    所有章节连续输出，前文自动作为后文上下文。
    """
    llm = NovelLLM(model)

    # 从大纲中提取章数
    import re
    chapter_titles = re.findall(
        r'(?:第\d+章[^:\n]*|Chapter\s*\d+[^\n]*)', outline
    )
    if not chapter_titles:
        # 自己规划章节
        chapter_titles = [f"第{i+1}章" for i in range(10)]

    total_chapters = len(chapter_titles)
    words_per_chapter = max(500, target_words // total_chapters)

    analysis_summary = _build_summary(analyses)

    full_text = _title_page(analyses, user_idea, outline)
    previous = ""

    for i, ch_title in enumerate(chapter_titles):
        if progress_callback:
            progress_callback(i + 1, total_chapters, ch_title)

        chapter = _write_one_chapter(
            llm, analysis_summary, outline, user_idea,
            i + 1, ch_title, words_per_chapter, previous, model
        )
        full_text += f"\n\n# {ch_title}\n\n{chapter}"
        previous += f"\n## {ch_title}\n{chapter[:1000]}"
        # 只保留最近几章作为上下文
        prev_parts = previous.split("## ")
        if len(prev_parts) > 4:
            previous = "## " + "## ".join(prev_parts[-4:])

    return full_text


def polish_novel(full_text: str, style_analysis: str, model: str = "claude") -> str:
    """全文润色，统一风格"""
    llm = NovelLLM(model)
    # 分段润色，每段5000字
    chunks = []
    for i in range(0, len(full_text), 5000):
        chunk = full_text[i:i + 5000]
        if len(chunk) < 500:
            chunks.append(chunk)
            continue

        prompt = f"""你是小说润色编辑。请根据风格要求润色以下文本。

== 目标风格 ==
{style_analysis[:800]}

== 润色原则 ==
1. 保持情节和人物不变
2. 优化句式节奏（长短句搭配）
3. 增强描写细节
4. 对话更自然

直接输出润色后的文本：

{chunk}"""
        polished = llm.invoke(prompt, "")
        chunks.append(polished)

    return "\n".join(chunks)


# ===== 内部函数 =====

def _build_summary(analyses: dict) -> str:
    parts = []
    dims = {
        "style": "写作风格", "narrative": "叙事结构",
        "conflict": "冲突与高潮", "characters": "人物分析",
        "theme": "主题深度",
    }
    for key, label in dims.items():
        if key in analyses:
            parts.append(f"### {label}\n{analyses[key][:500]}")
    return "\n\n".join(parts)


def _outline_prompt(analysis_summary: str, user_idea: str) -> str:
    return f"""你是专业小说策划编辑。根据参考小说的风格分析，为一个全新的原创故事设计大纲。

== 参考小说分析（学习技巧，内容必须完全原创）==

{analysis_summary}

== 用户的想法 ==

{user_idea}

== 要求 ==
- 故事必须完全原创，不能抄袭参考小说的任何情节、人物、背景
- 学习参考小说的写作技巧（叙事节奏、冲突设计、人物塑造手法）
- 用参考小说的风格来写全新内容

请输出：

## 故事标题

## 一句话简介

## 故事类型

## 主角设定
- 姓名/年龄/职业
- 性格（3-5个关键词）
- 核心动机

## 第1章 章名
一句话梗概

## 第2章 章名
一句话梗概

（以此类推，共10-15章）"""


def _write_one_chapter(llm, analysis_summary, outline, user_idea,
                       ch_index, ch_title, target_words,
                       previous_context, model) -> str:
    prompt = f"""你是专业小说作家。根据以下设定创作一章小说。

== 参考风格（学习但不能抄袭）==

{analysis_summary[:1500]}

== 故事大纲 ==

{outline[:1500]}

== 用户想法 ==

{user_idea[:500]}

== 前面章节摘要 ==

{previous_context[:800] if previous_context else "（这是第一章）"}

== 本章 ==

标题：{ch_title}
类型：第{ch_index}章
目标字数：约{target_words}字

== 写作要求 ==
1. 学习参考小说的风格和节奏，但故事完全原创
2. 字数：{target_words}字左右
3. 本章要有独立起承转合，同时推进整体故事
4. 适当穿插对话、描写、内心独白
5. 开头吸引人，结尾留悬念或自然过渡

直接输出本章正文，无需任何标记："""

    return llm.invoke(prompt, "")


def _title_page(analyses, user_idea, outline):
    """生成卷首信息"""
    import re
    title = "仿写作品"
    match = re.search(r'## 故事标题\s*\n(.+)', outline)
    if match:
        title = match.group(1).strip()

    return f"""# {title}

> 基于 AI 文学分析后的风格仿写
> 想法：{user_idea[:100]}
> 本作品为原创内容

"""
