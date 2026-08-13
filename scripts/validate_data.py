"""Validate data/skills.json against schema and the category dictionary."""
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REPO_URL_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")
PINNED_ENTRY_RE = re.compile(r"/blob/[0-9a-f]{40}/")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ALLOWED_PLATFORMS = {
    "claude-code", "codex", "cursor", "gemini-cli", "copilot",
    "windsurf", "opencode", "multi",
}


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def validate_skills(skills: list, categories: dict) -> list:
    errors = []
    category_keys = {c["key"] for c in categories.get("categories", [])}
    seen_ids = set()
    for index, skill in enumerate(skills):
        label = f"skills[{index}]"
        skill_id = skill.get("id", "")
        if not ID_RE.fullmatch(skill_id):
            errors.append(f"{label}: id 必须是小写连字符格式，当前: {skill_id!r}")
        if skill_id in seen_ids:
            errors.append(f"{label}: id 重复: {skill_id}")
        seen_ids.add(skill_id)
        if not skill.get("name"):
            errors.append(f"{label}: name 不能为空")
        if not REPO_URL_RE.fullmatch(skill.get("repo", "")):
            errors.append(f"{label}: repo 必须是 https://github.com/<owner>/<repo>")
        if not PINNED_ENTRY_RE.search(skill.get("entry", "")):
            errors.append(f"{label}: entry 必须指向 /blob/<40位commit>/ 下的固定版本链接")
        if not skill.get("description", "").strip():
            errors.append(f"{label}: description 不能为空")
        categories_field = skill.get("categories", [])
        if not categories_field:
            errors.append(f"{label}: categories 至少 1 个")
        for category in categories_field:
            if category not in category_keys:
                errors.append(f"{label}: 未知分类 {category!r}")
        platforms = skill.get("platforms", [])
        if not platforms:
            errors.append(f"{label}: platforms 至少 1 个")
        for platform in platforms:
            if platform not in ALLOWED_PLATFORMS:
                errors.append(f"{label}: 未知平台 {platform!r}")
        for field in ("verified_at", "added_at"):
            if not DATE_RE.fullmatch(skill.get(field, "")):
                errors.append(f"{label}: {field} 必须是 YYYY-MM-DD")
        if not isinstance(skill.get("tags", []), list):
            errors.append(f"{label}: tags 必须是数组")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skills = load_json(root / "data" / "skills.json")
    categories = load_json(root / "data" / "categories.json")
    errors = validate_skills(skills["skills"], categories)
    if "--check" in sys.argv[1:]:
        pass  # CI 兼容，行为与默认一致
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        return 1
    print(f"OK: {len(skills['skills'])} skills validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
