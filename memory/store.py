"""
LanceDB 记忆层 — 持久化存储小说内容、分析结果、对话历史
"""
import lancedb
import pyarrow as pa
import os
import json
from datetime import datetime


class NovelMemory:
    """基于 LanceDB 的小说记忆系统"""

    def __init__(self, db_path: str = "./novel_memory"):
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self._init_tables()

    def _init_tables(self):
        """初始化数据表"""
        # 小说内容表
        if "novel_chunks" not in self.db.table_names():
            self.db.create_table("novel_chunks", [{
                "id": "init",
                "chunk_index": 0,
                "chapter": "",
                "content": "",
                "chunk_size": 0,
                "created_at": datetime.now().isoformat(),
            }])

        # 分析结果表
        if "analysis" not in self.db.table_names():
            self.db.create_table("analysis", [{
                "id": "init",
                "novel_name": "",
                "category": "",       # style/narrative/conflict/characters/theme
                "result": "",
                "model_used": "",
                "created_at": datetime.now().isoformat(),
            }])

        # 对话历史表
        if "chat_history" not in self.db.table_names():
            self.db.create_table("chat_history", [{
                "id": "init",
                "role": "",
                "content": "",
                "novel_name": "",
                "timestamp": datetime.now().isoformat(),
            }])

    def clear_novel(self, novel_name: str):
        """清空指定小说的旧数据"""
        for tbl_name in ["novel_chunks", "analysis", "chat_history"]:
            try:
                tbl = self.db.open_table(tbl_name)
                # LanceDB 不支持 delete，用 overwrite 替代
                remaining = tbl.to_pandas()
                remaining = remaining[remaining.get("novel_name", "") != novel_name] if "novel_name" in remaining.columns else remaining
                remaining = remaining[remaining.get("chapter", "") != ""] if tbl_name == "novel_chunks" else remaining
            except Exception:
                pass

    # === 小说内容 ===
    def save_chapters(self, chapters: list[dict]):
        """保存章节到向量记忆"""
        rows = []
        idx = 0
        for ch in chapters:
            chunks = [ch["content"][i:i+2000] for i in range(0, len(ch["content"]), 2000)]
            for ci, chunk in enumerate(chunks):
                rows.append({
                    "id": f"ch_{idx}",
                    "chunk_index": ci,
                    "chapter": ch.get("title", ""),
                    "content": chunk,
                    "chunk_size": len(chunk),
                    "created_at": datetime.now().isoformat(),
                })
                idx += 1

        if rows:
            self.db.create_table("novel_chunks", rows, mode="overwrite")

    def get_all_chapters(self) -> list[dict]:
        """获取所有章节"""
        try:
            tbl = self.db.open_table("novel_chunks")
            df = tbl.to_pandas()
            return df.to_dict("records")
        except Exception:
            return []

    # === 分析结果 ===
    def save_analysis(self, novel_name: str, category: str, result: str, model: str):
        """保存分析结果"""
        rows = [{
            "id": f"{category}_{datetime.now().timestamp()}",
            "novel_name": novel_name,
            "category": category,
            "result": result,
            "model_used": model,
            "created_at": datetime.now().isoformat(),
        }]
        try:
            tbl = self.db.open_table("analysis")
            tbl.add(rows)
        except Exception:
            self.db.create_table("analysis", rows, mode="overwrite")

    def get_analysis(self, category: str = None) -> list[dict]:
        """获取分析结果"""
        try:
            tbl = self.db.open_table("analysis")
            df = tbl.to_pandas()
            if category:
                df = df[df["category"] == category]
            return df.to_dict("records")
        except Exception:
            return []

    # === 对话历史 ===
    def save_chat(self, role: str, content: str, novel_name: str = ""):
        """保存对话记录"""
        row = [{
            "id": f"chat_{datetime.now().timestamp()}",
            "role": role,
            "content": content,
            "novel_name": novel_name,
            "timestamp": datetime.now().isoformat(),
        }]
        try:
            tbl = self.db.open_table("chat_history")
            tbl.add(row)
        except Exception:
            self.db.create_table("chat_history", row, mode="overwrite")

    def get_chat_history(self, limit: int = 20) -> list[dict]:
        try:
            tbl = self.db.open_table("chat_history")
            df = tbl.to_pandas().tail(limit)
            return df.to_dict("records")
        except Exception:
            return []
