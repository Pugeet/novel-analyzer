"""
Obsidian 导出 — 将分析结果输出为 Obsidian 可读的 Markdown 笔记
"""
import os
import datetime


def export_to_obsidian(
    vault_path: str,
    novel_name: str,
    analyses: dict,  # {"style": "结果", "narrative": "...", ...}
    chapters: list[dict] = None,
) -> str:
    """
    将分析结果导出为 Obsidian vault 中的 Markdown 文件

    Args:
        vault_path: Obsidian vault 路径
        novel_name: 小说名称
        analyses: 各维度分析结果 {"style": "markdown", ...}
        chapters: 章节列表

    Returns:
        导出的文件夹路径
    """
    # 创建小说专属文件夹
    safe_name = novel_name.replace(" ", "_").replace("/", "_")[:50]
    export_dir = os.path.join(vault_path, f"小说分析_{safe_name}")
    os.makedirs(export_dir, exist_ok=True)

    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # === 总览笔记 ===
    overview = f"""---
title: {novel_name} - 分析总览
date: {today}
tags: [小说分析, {novel_name}]
---

# {novel_name} 分析总览

## 快速导航

- [[写作风格分析]]
- [[叙事结构分析]]
- [[人物分析]]
- [[冲突与高潮分析]]
- [[主题分析]]
"""

    if chapters:
        overview += "\n## 章节结构\n\n"
        for ch in chapters[:20]:
            title = ch.get("title", "")[:60]
            length = len(ch.get("content", ""))
            overview += f"- **{title}** ({length} 字)\n"
        overview += f"\n> 共 {len(chapters)} 章"

    _write_md(export_dir, f"{novel_name}_分析总览", overview)

    # === 各维度详细笔记 ===
    category_map = {
        "style": ("写作风格分析", "写作风格", ["#小说风格", "#叙事视角"]),
        "narrative": ("叙事结构分析", "叙事结构", ["#叙事结构", "#情节分析"]),
        "characters": ("人物分析", "人物分析", ["#人物分析", "#角色"]),
        "conflict": ("冲突与高潮分析", "冲突与高潮", ["#冲突", "#高潮"]),
        "theme": ("主题分析", "主题分析", ["#主题", "#象征"]),
    }

    for key, (title, link_name, tags) in category_map.items():
        if key in analyses and analyses[key]:
            content = f"""---
title: {novel_name} - {title}
date: {today}
tags: [{', '.join(tags)}, {novel_name}]
---

# {novel_name} - {title}

> 返回 [[{novel_name}_分析总览|分析总览]]

---

{analyses[key]}
"""
            _write_md(export_dir, f"{novel_name}_{link_name}", content)

    return export_dir


def _write_md(folder: str, filename: str, content: str):
    """写入Markdown文件，处理非法文件名字符"""
    safe = filename.replace("/", "_").replace("\\", "_").replace(":", "_")
    path = os.path.join(folder, f"{safe}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
