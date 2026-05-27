"""
Project manager: persist novel generation state to disk so progress
survives browser disconnects and server restarts.
"""
import json
import os
import shutil

from .writer import extract_chapter_titles

PROJECTS_DIR = "projects"


def _safe_name(name: str) -> str:
    """Sanitize a novel name into a safe directory name."""
    safe = name.strip().replace(" ", "_")
    for ch in r'\/:*?"<>|':
        safe = safe.replace(ch, "_")
    return safe[:80]


class ProjectManager:
    """Manages a single novel project on disk."""

    def __init__(self, novel_name: str):
        safe = _safe_name(novel_name)
        self.project_dir = os.path.join(PROJECTS_DIR, safe)
        os.makedirs(self.project_dir, exist_ok=True)
        self.project_file = os.path.join(self.project_dir, "project.json")
        self.ref_file = os.path.join(self.project_dir, "novel_ref.txt")
        self.output_file = os.path.join(self.project_dir, "novel_output.txt")

    # ---- save phases ----

    def save_analysis(self, novel_text: str, novel_name: str, chapters: list,
                      analyses: dict, novel_words: int, model: str,
                      user_idea: str = "") -> None:
        """Save everything after Step 2 (analysis) completes."""
        with open(self.ref_file, "w", encoding="utf-8") as f:
            f.write(novel_text)

        data = {
            "novel_name": novel_name,
            "novel_words": novel_words,
            "model": model,
            "user_idea": user_idea,
            "target_words": novel_words,
            "outline": "",
            "analyses": analyses,
            "chapters": chapters,
            "chapter_titles": [],
            "completed_chapters": 0,
            "total_chapters": 0,
            "words_per_chapter": 0,
            "previous_context": "",
        }
        with open(self.project_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("")

    def save_outline(self, outline: str, target_words: int) -> dict:
        """Save outline after Step 3a. Returns computed chapter metadata."""
        titles = extract_chapter_titles(outline)
        total = len(titles)
        wpc = max(500, target_words // total)

        with open(self.project_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["outline"] = outline
        data["target_words"] = target_words
        data["chapter_titles"] = titles
        data["total_chapters"] = total
        data["words_per_chapter"] = wpc
        with open(self.project_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return {"chapter_titles": titles, "total_chapters": total,
                "words_per_chapter": wpc}

    def save_checkpoint(self, completed_chapters: int, full_text_so_far: str,
                        previous_context: str) -> None:
        """Save after each chapter is written."""
        with open(self.project_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["completed_chapters"] = completed_chapters
        data["previous_context"] = previous_context
        with open(self.project_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(full_text_so_far)

    # ---- load ----

    def load_project(self) -> dict | None:
        """Load all project state. Returns None if project doesn't exist."""
        if not os.path.exists(self.project_file):
            return None

        with open(self.project_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        novel_text = ""
        if os.path.exists(self.ref_file):
            with open(self.ref_file, "r", encoding="utf-8") as f:
                novel_text = f.read()

        full_novel = ""
        if os.path.exists(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                full_novel = f.read()

        data["novel_text"] = novel_text
        data["full_novel"] = full_novel
        return data

    def get_partial_novel_text(self) -> str:
        """Read the generated novel so far (for partial download)."""
        if os.path.exists(self.output_file):
            with open(self.output_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    # ---- static utilities ----

    @staticmethod
    def list_projects() -> list[str]:
        """Scan projects/ for subdirectories containing a project.json."""
        result = []
        if not os.path.exists(PROJECTS_DIR):
            return result
        for entry in os.listdir(PROJECTS_DIR):
            proj_dir = os.path.join(PROJECTS_DIR, entry)
            pj_file = os.path.join(proj_dir, "project.json")
            if os.path.isdir(proj_dir) and os.path.exists(pj_file):
                try:
                    with open(pj_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    result.append(data.get("novel_name", entry))
                except (json.JSONDecodeError, KeyError):
                    pass
        return result

    @staticmethod
    def delete_project(novel_name: str) -> None:
        """Remove a project directory entirely."""
        safe = _safe_name(novel_name)
        proj_dir = os.path.join(PROJECTS_DIR, safe)
        if os.path.exists(proj_dir):
            shutil.rmtree(proj_dir)
