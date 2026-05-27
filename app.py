"""
小说分析+仿写系统
流程：上传小说 -> 多维分析 -> 输入你的故事想法 -> 一键生成全书
"""
import streamlit as st
import os

from analyzer import (
    parse_document, split_by_chapter,
    analyze_style, analyze_narrative, analyze_conflict,
    analyze_characters, analyze_theme,
)
from analyzer.writer import generate_outline, write_full_novel
from analyzer.project import ProjectManager
from obsidian import export_to_obsidian

st.set_page_config(page_title="小说分析+仿写", page_icon="[BOOK]", layout="wide")
st.title("[BOOK] 小说分析 + 仿写系统")
st.caption("上传参考小说 -> AI 分析写作技巧 -> 输入你的创作想法 -> 一键生成全新小说")

# ===== session 初始化 =====
for k, v in {
    "novel_text": "", "novel_name": "", "chapters": [],
    "analyses": {}, "outline": "", "full_novel": "", "novel_words": 0,
    "model": "claude", "user_idea": "", "target_words": 0,
    "completed_chapters": 0, "chapter_titles": [],
    "total_chapters": 0, "words_per_chapter": 0,
    "previous_context": "", "project_loaded": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ===== 项目恢复（检测未完成项目） =====
if not st.session_state.project_loaded:
    projects = ProjectManager.list_projects()
    if projects:
        st.info("检测到之前的写作项目。您可以恢复进度继续写作，或开始全新项目。")
        col_a, col_b = st.columns([2, 1])
        with col_a:
            resume_choice = st.selectbox(
                "选择项目",
                ["-- 开始新项目 --"] + projects,
                key="resume_select",
            )
        with col_b:
            st.write("")
            if st.button("确认", type="primary", use_container_width=True):
                if resume_choice == "-- 开始新项目 --":
                    st.session_state.project_loaded = True
                    st.rerun()
                else:
                    pm = ProjectManager(resume_choice)
                    data = pm.load_project()
                    if data:
                        for k in ["novel_text", "novel_name", "chapters",
                                   "analyses", "outline", "full_novel",
                                   "novel_words", "model", "user_idea",
                                   "target_words", "completed_chapters",
                                   "chapter_titles", "total_chapters",
                                   "words_per_chapter", "previous_context"]:
                            if k in data:
                                st.session_state[k] = data[k]
                        st.session_state.project_loaded = True
                        st.success(f"已恢复项目: {resume_choice}（已完成 {data.get('completed_chapters', 0)}/{data.get('total_chapters', '?')} 章）")
                        st.rerun()
        st.stop()
    else:
        st.session_state.project_loaded = True
        st.rerun()

# ===== 侧边栏 =====
with st.sidebar:
    st.header("[GEAR] 模型配置")
    model_idx = 0 if st.session_state.get("model", "claude") == "claude" else 1
    model = st.selectbox(
        "选择模型",
        ["claude", "deepseek"],
        format_func=lambda x: "Claude (Sonnet 4.6)" if x == "claude" else "DeepSeek (Chat)",
        index=model_idx,
    )
    st.session_state.model = model
    if model == "deepseek" and not os.environ.get("DEEPSEEK_API_KEY"):
        key = st.text_input("DeepSeek API Key", type="password")
        if key:
            os.environ["DEEPSEEK_API_KEY"] = key

    st.divider()
    st.header("[FILE] 步骤1: 上传小说")
    uploaded = st.file_uploader("参考小说（学习其写作风格）", type=["txt", "pdf", "docx"])
    if uploaded:
        try:
            text, fname = parse_document(uploaded)
            # 检测是否是新文件
            if st.session_state.novel_name != fname.rsplit(".", 1)[0]:
                st.session_state.novel_text = text
                st.session_state.novel_name = fname.rsplit(".", 1)[0]
                st.session_state.chapters = split_by_chapter(text)
                st.session_state.analyses = {}
                st.session_state.outline = ""
                st.session_state.full_novel = ""
                st.session_state.novel_words = len(text)
            st.success(f"[OK] {fname}  ({len(text):,} 字, {len(st.session_state.chapters)} 章)")
        except Exception as e:
            st.error(f"解析失败: {e}")

    if st.session_state.novel_name:
        st.caption(f"参考小说: {st.session_state.novel_name}")
        st.metric("目标仿写字数", f"{st.session_state.novel_words:,}")

    st.divider()
    st.header("[FOLDER] Obsidian 导出")
    vault_path = st.text_input("Vault 路径", placeholder="D:/Obsidian/我的小说库")
    if st.button("导出分析", use_container_width=True):
        if vault_path and st.session_state.analyses:
            d = export_to_obsidian(vault_path, st.session_state.novel_name,
                                   st.session_state.analyses, st.session_state.chapters)
            st.success(f"导出到 {d}")

# ===== 主区域 =====
if not st.session_state.novel_text:
    st.info("[INFO] 在左侧上传一本参考小说，AI 会分析它的写作技巧，然后帮你创作全新作品")
    st.stop()

# ===== 步骤2: 自动分析 =====
st.subheader("[MAGNIFIER] 步骤2: 分析参考小说")

if not st.session_state.analyses:
    if st.button("[ROCKET] 开始分析（5个维度，约需1-2分钟）", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()
        analyzers = [
            ("style", analyze_style, "写作风格"),
            ("narrative", analyze_narrative, "叙事结构"),
            ("conflict", analyze_conflict, "冲突与高潮"),
            ("characters", analyze_characters, "人物分析"),
            ("theme", analyze_theme, "主题深度"),
        ]
        for i, (key, fn, label) in enumerate(analyzers):
            status.info(f"分析: {label}...")
            try:
                st.session_state.analyses[key] = fn(st.session_state.novel_text, model)
            except Exception as e:
                st.session_state.analyses[key] = f"失败: {e}"
            progress.progress((i + 1) / len(analyzers))
        status.success("[OK] 分析完成！")
        progress.empty()

    # 分析完成后自动保存
    if st.session_state.analyses and st.session_state.novel_name:
        pm = ProjectManager(st.session_state.novel_name)
        pm.save_analysis(
            novel_text=st.session_state.novel_text,
            novel_name=st.session_state.novel_name,
            chapters=st.session_state.chapters,
            analyses=st.session_state.analyses,
            novel_words=st.session_state.novel_words,
            model=st.session_state.model,
            user_idea=st.session_state.user_idea,
        )

if st.session_state.analyses:
    dim_names = {"style": "风格", "narrative": "叙事", "conflict": "冲突",
                 "characters": "人物", "theme": "主题"}
    with st.expander("查看分析结果", expanded=False):
        tabs = st.tabs(list(dim_names.values()))
        for tab, key in zip(tabs, dim_names.keys()):
            with tab:
                if key in st.session_state.analyses:
                    st.markdown(st.session_state.analyses[key])

# ===== 步骤3: 创作 =====
st.divider()
st.subheader("[WRITE] 步骤3: 创作你的小说")

if not st.session_state.analyses:
    st.caption("请先完成步骤2的分析")
else:
    # --- 3a: 输入故事想法 ---
    st.markdown("#### 3a. 描述你的故事")
    user_idea = st.text_area(
        "你想写一个什么样的故事？（情节、人物、背景，越详细越好）",
        value=st.session_state.user_idea,
        placeholder="例：一个都市悬疑故事。主角是外卖小哥陈然，某天送餐时无意间撞见一桩凶案，"
                    "凶手发现了他，开始追杀。陈然只能靠自己送外卖时积累的对城市每个角落的了解，"
                    "在城市的缝隙中求生，同时一步步揭开凶手背后的秘密组织...",
        height=80,
    )
    st.session_state.user_idea = user_idea

    target = st.session_state.novel_words
    st.session_state.target_words = target
    st.caption(f"目标字数: {target:,} 字（与参考小说一致）")

    col_a, col_b = st.columns([1, 2])
    with col_a:
        gen_btn = st.button("[BULB] 生成大纲", type="primary", use_container_width=True)
    with col_b:
        st.caption("AI 基于分析结果 + 你的想法，生成故事大纲和章节规划")

    if gen_btn:
        if not user_idea:
            st.warning("请先输入你的故事想法")
        else:
            with st.status("构思大纲..."):
                st.session_state.outline = generate_outline(
                    st.session_state.analyses, user_idea, model
                )
            # 保存大纲及章节元数据
            pm = ProjectManager(st.session_state.novel_name)
            meta = pm.save_outline(st.session_state.outline, target)
            st.session_state.chapter_titles = meta["chapter_titles"]
            st.session_state.total_chapters = meta["total_chapters"]
            st.session_state.words_per_chapter = meta["words_per_chapter"]
            st.success("大纲已生成，请审阅修改")

    # --- 3b: 审阅修改大纲 ---
    if st.session_state.outline:
        st.divider()
        st.markdown("#### 3b. 审阅并修改大纲")

        edited_outline = st.text_area(
            "确认或修改大纲（你可以自由调整章节、情节、人物设定）",
            value=st.session_state.outline,
            height=300,
        )
        # 同步修改到 session
        st.session_state.outline = edited_outline

        # --- 3c: 确认后开始写作 ---
        st.divider()
        st.markdown("#### 3c. 确认大纲，开始写作")

        col1, col2 = st.columns([2, 1])
        with col1:
            write_btn = st.button(
                f"[ROCKET] 确认大纲，开始写作（约{target:,}字，需3-8分钟）",
                type="primary", use_container_width=True,
            )
        with col2:
            target_override = st.number_input(
                "自定义字数", value=target, step=1000, format="%d"
            )

        if write_btn:
            final_target = target_override or target
            pm = ProjectManager(st.session_state.novel_name)

            # 显示部分下载按钮（如有之前保存的进度）
            partial_text = pm.get_partial_novel_text()
            if partial_text:
                st.download_button(
                    "[DOWNLOAD] 下载当前进度 (TXT)",
                    partial_text,
                    file_name=f"{st.session_state.novel_name}_草稿.txt",
                )

            st.subheader("写作中...")
            progress = st.progress(0)
            chapter_status = st.empty()

            def update_progress(i, total, title):
                progress.progress(i / total)
                chapter_status.info(f"正在写: {title} ({i}/{total})")

            # 断点续写参数
            start_ch = st.session_state.completed_chapters
            initial_text = st.session_state.full_novel if start_ch > 0 else ""
            initial_ctx = st.session_state.previous_context

            def on_chapter_done(ch_index, ch_title, ch_text,
                                full_so_far, prev_ctx):
                pm.save_checkpoint(ch_index, full_so_far, prev_ctx)
                st.session_state.full_novel = full_so_far
                st.session_state.completed_chapters = ch_index
                st.session_state.previous_context = prev_ctx

            with st.spinner(f"创作中 (目标 {final_target:,} 字)..."):
                full = write_full_novel(
                    st.session_state.analyses,
                    st.session_state.outline,
                    user_idea,
                    final_target,
                    model,
                    update_progress,
                    checkpoint_callback=on_chapter_done,
                    start_chapter=start_ch,
                    initial_full_text=initial_text,
                    initial_previous_context=initial_ctx,
                )
                st.session_state.full_novel = full
                st.session_state.completed_chapters = st.session_state.total_chapters

            progress.progress(1.0)
            chapter_status.success(f"[OK] 全书生成完毕！ {len(full):,} 字")

    # 显示生成结果
    if st.session_state.full_novel:
        st.divider()
        st.subheader("[PAGE] 你的小说")

        novel = st.session_state.full_novel

        st.download_button(
            "[DOWNLOAD] 下载全书 (TXT)",
            novel,
            file_name=f"{st.session_state.novel_name}_仿写.txt",
        )

        st.metric("总字数", f"{len(novel):,}")
        st.text_area("预览", novel, height=500)

# ===== 页脚 =====
st.divider()
c1, c2 = st.columns(2)
with c1:
    if st.button("[REFRESH] 重新分析"):
        st.session_state.analyses = {}
        st.session_state.outline = ""
        st.session_state.full_novel = ""
        st.session_state.completed_chapters = 0
        st.session_state.chapter_titles = []
        st.session_state.total_chapters = 0
        st.session_state.words_per_chapter = 0
        st.session_state.previous_context = ""
        st.rerun()
with c2:
    if st.button("[NEW] 换一本参考小说"):
        defaults = {
            "novel_text": "", "novel_name": "", "chapters": [],
            "analyses": {}, "outline": "", "full_novel": "",
            "novel_words": 0, "model": "claude", "user_idea": "",
            "target_words": 0, "completed_chapters": 0,
            "chapter_titles": [], "total_chapters": 0,
            "words_per_chapter": 0, "previous_context": "",
        }
        for k, v in defaults.items():
            st.session_state[k] = v
        st.rerun()
