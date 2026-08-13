import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_rankings import render_readme


RANKINGS = {
    "updated_at": "2026-08-13",
    "weekly": [
        {"rank": 1, "name": "b/beta", "repo": "https://github.com/b/beta", "delta": 15, "description": "B"}
    ],
    "monthly": [],
    "yearly": [
        {"rank": 1, "name": "b/beta", "repo": "https://github.com/b/beta", "stars": 120, "delta": None, "description": "B"}
    ],
}


def test_render_readme_contains_boards_and_meta():
    markdown = render_readme(RANKINGS, [])
    assert "## 周榜 Top 5" in markdown
    assert "## 月榜 Top 5" in markdown
    assert "## 年榜 Top 5" in markdown
    assert "b/beta" in markdown
    assert "2026-08-13" in markdown


def test_render_readme_limits_to_top5():
    rows = [{"rank": i, "name": f"r{i}", "repo": "https://github.com/x/y", "delta": i, "description": "d"} for i in range(1, 8)]
    markdown = render_readme({"updated_at": "2026-08-13", "weekly": rows, "monthly": [], "yearly": []}, [])
    assert "r6" not in markdown
    assert "r7" not in markdown
