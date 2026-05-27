# 小说分析 + 风格仿写系统

基于 **LangChain + Claude + DeepSeek** 的小说智能分析与仿写工具。上传参考小说，AI 自动拆解写作风格、叙事结构、冲突设计、人物塑造、主题深度，再根据你的创作想法，学习参考小说的技法，自动生成一本字数匹配的原创小说。

## 项目亮点

- **五维深度分析**：写作风格 / 叙事结构 / 冲突高潮 / 人物分析 / 主题深度，每个维度由专业文学评论 Prompt 驱动
- **风格仿写引擎**：学习参考小说的技法，不抄袭内容，生成完全原创的故事
- **字数自动匹配**：输出的仿写小说字数自动对齐输入参考小说
- **双模型支持**：Claude (Sonnet 4.6) + DeepSeek，随时切换
- **大纲可编辑**：AI 生成大纲后可在界面中自由修改，确认后再开始写作
- **Obsidian 导出**：分析结果一键导出为 Obsidian 可读的 Markdown 笔记（双向链接、标签）

## 工作流

```
上传参考小说（PDF/Word/TXT）
    -> 五维 AI 分析（风格/叙事/冲突/人物/主题）
    -> 输入你的创作想法
    -> AI 生成故事大纲 + 章节规划
    -> 审阅修改大纲（可自由编辑）
    -> 确认，逐章生成全书
    -> 下载 / 导出
```

## 技术栈

| 组件 | 技术选型 |
|------|---------|
| LLM 框架 | LangChain |
| 大语言模型 | Anthropic Claude + DeepSeek |
| Web 界面 | Streamlit |
| 文档解析 | PyPDF + python-docx |
| 文本切分 | RecursiveCharacterTextSplitter |
| 记忆存储 | LanceDB（可选）/ JSON fallback |
| 笔记导出 | Obsidian Markdown 格式 |

## 项目结构

```
novel-analyzer/
├── app.py                  # Streamlit 主界面
├── analyzer/
│   ├── llm.py              # 多模型统一接口 (Claude + DeepSeek)
│   ├── document.py         # PDF/Word/TXT 文档解析
│   ├── splitter.py         # 小说智能分章
│   ├── style.py            # 写作风格分析
│   ├── narrative.py        # 叙事结构分析
│   ├── conflict.py         # 冲突与高潮分析
│   ├── characters.py       # 人物分析
│   ├── theme.py            # 主题深度分析
│   └── writer.py           # 风格仿写引擎（大纲+全书生成+润色）
├── memory/
│   └── store.py            # LanceDB 向量记忆层
├── obsidian/
│   └── exporter.py         # Obsidian Markdown 笔记导出
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API Key（至少一个）
set ANTHROPIC_API_KEY=your_claude_key
set DEEPSEEK_API_KEY=your_deepseek_key    # 可选，用 DeepSeek 需要

# 3. 启动
python -m streamlit run app.py
# 浏览器打开 http://localhost:8501
```

## 使用说明

### 1. 上传参考小说
侧边栏上传 PDF / Word / TXT 格式的小说文件，系统自动解析并按章节拆分。

### 2. 多维分析
点击"开始分析"，AI 从五个维度解剖参考小说的写作技巧：
- **写作风格**：叙事视角、语言节奏、修辞手法、词汇特征
- **叙事结构**：结构类型、情节点、节奏曲线、叙事线索
- **冲突与高潮**：核心冲突、冲突升级、高潮力度、张力维持
- **人物分析**：性格特点、成长弧线、人物关系、塑造手法
- **主题深度**：核心主题、象征隐喻、社会背景、价值取向

### 3. 输入创作想法
描述你想写的故事——情节、人物、背景，越详细效果越好。

### 4. 审阅大纲
AI 生成故事大纲和章节规划。你可以在界面中直接编辑修改，调整到你满意为止。

### 5. 一键写作
确认大纲后点击"开始写作"，AI 逐章生成全书，自动匹配参考小说的字数。每章写完都会显示进度。

### 6. 导出
- 全文下载为 TXT 文件
- 分析结果导出到 Obsidian vault，生成带双向链接和标签的笔记

## 面试要点

本项目涵盖 AI 应用开发面试核心考点：

- **RAG 架构**：文档加载 -> 文本切分 -> 语义理解 -> 上下文检索
- **多模型集成**：统一的 LLM 接口抽象，支持多种模型后端
- **Prompt Engineering**：多维度专业文学评论 Prompt 设计，结构化输出
- **Agent 模式**：LLM 自主决策写作节奏、章节过渡、风格把控
- **工程化实践**：模块化设计、Session 状态管理、错误处理、进度反馈
