import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_data import load_json, validate_skills

ROOT = Path(__file__).resolve().parent.parent


def _categories():
    return load_json(ROOT / "data" / "categories.json")


def _valid_skill(**overrides):
    skill = {
        "id": "example-skill",
        "name": "example/skill",
        "repo": "https://github.com/example/skill",
        "entry": "https://github.com/example/skill/blob/0123456789abcdef0123456789abcdef01234567/SKILL.md",
        "description": "示例技能",
        "categories": ["developer"],
        "platforms": ["multi"],
        "license": "",
        "verified_at": "2026-08-13",
        "tags": ["demo"],
        "added_at": "2026-08-13",
    }
    skill.update(overrides)
    return skill


def test_valid_skill_passes():
    assert validate_skills([_valid_skill()], _categories()) == []


def test_real_seed_data_passes():
    data = load_json(ROOT / "data" / "skills.json")
    assert validate_skills(data["skills"], _categories()) == []


def test_duplicate_id_rejected():
    skills = [_valid_skill(), _valid_skill(id="example-skill")]
    errors = validate_skills(skills, _categories())
    assert any("重复" in error for error in errors)


def test_unknown_category_rejected():
    skill = _valid_skill(categories=["not-a-category"])
    errors = validate_skills([skill], _categories())
    assert any("未知分类" in error for error in errors)


def test_missing_description_rejected():
    skill = _valid_skill(description="")
    errors = validate_skills([skill], _categories())
    assert any("description" in error for error in errors)


def test_unpinned_entry_rejected():
    skill = _valid_skill(entry="https://github.com/example/skill/blob/main/SKILL.md")
    errors = validate_skills([skill], _categories())
    assert any("固定版本" in error for error in errors)


def test_bad_platform_rejected():
    skill = _valid_skill(platforms=["unknown-agent"])
    errors = validate_skills([skill], _categories())
    assert any("未知平台" in error for error in errors)


def test_bad_date_rejected():
    skill = _valid_skill(verified_at="2026/08/13")
    errors = validate_skills([skill], _categories())
    assert any("verified_at" in error for error in errors)
