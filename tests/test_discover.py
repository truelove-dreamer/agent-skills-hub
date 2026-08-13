import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from discover import build_entry, classify, collect_new_skills, slugify


def test_classify_defaults_to_developer():
    assert classify("some vague description", "some/repo") == ["developer"]


def test_classify_writer():
    assert "writer" in classify("writing assistant for documents", "x/y")


def test_classify_obsidian():
    categories = classify("obsidian notes management", "x/y")
    assert "writer" in categories
    assert "productivity" in categories


def test_slugify():
    assert slugify("SomeOwner/My-Skill_Repo") == "someowner-my-skill-repo"


def test_build_entry_skips_without_skill_md():
    candidate = {"name": "a/b", "description": "desc"}
    with mock.patch("discover.branch_head", return_value=("main", "0123456789abcdef0123456789abcdef01234567")), \
         mock.patch("discover.find_skill_path", return_value=""):
        assert build_entry(candidate) is None


def test_build_entry_pins_entry():
    sha = "0123456789abcdef0123456789abcdef01234567"
    candidate = {"name": "a/b", "description": "data analytics skill"}
    with mock.patch("discover.branch_head", return_value=("main", sha)), \
         mock.patch("discover.find_skill_path", return_value="skills/SKILL.md"):
        entry = build_entry(candidate)
    assert entry["entry"] == f"https://github.com/a/b/blob/{sha}/skills/SKILL.md"
    assert "data-analyst" in entry["categories"]
    assert entry["tags"] == ["auto"]


def test_collect_new_skills_dedupes_and_filters():
    existing = [{"id": "a-b", "name": "a/b"}]
    candidates = [
        {"name": "a/b", "stars": 999, "description": ""},
        {"name": "awesome/x", "stars": 999, "description": ""},
        {"name": "c/d", "stars": 50, "description": ""},
        {"name": "e/f", "stars": 999, "description": "writing"},
    ]

    def fake_build(candidate, token=""):
        return {
            "id": slugify(candidate["name"]),
            "name": candidate["name"],
            "categories": classify(candidate["description"], candidate["name"]),
            "tags": ["auto"],
        }

    with mock.patch("discover.search_candidates", return_value=candidates), \
         mock.patch("discover.build_entry", side_effect=fake_build):
        added = collect_new_skills(existing)
    assert [entry["name"] for entry in added] == ["e/f"]
