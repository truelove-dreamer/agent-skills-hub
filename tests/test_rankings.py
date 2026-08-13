import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_rankings import build_rankings, delta_stars, write_site_data

PIN = "0123456789abcdef0123456789abcdef01234567"


def _skill(skill_id, name, repo_slug, description, categories):
    return {
        "id": skill_id,
        "name": name,
        "repo": f"https://github.com/{repo_slug}",
        "entry": f"https://github.com/{repo_slug}/blob/{PIN}/SKILL.md",
        "description": description,
        "categories": categories,
        "platforms": ["multi"],
        "tags": [],
    }


SKILLS = [
    _skill("alpha", "a/alpha", "a/alpha", "A", ["developer"]),
    _skill("beta", "b/beta", "b/beta", "B", ["research"]),
    _skill("gamma", "c/gamma", "c/gamma", "C", ["designer"]),
]

SNAPSHOTS = [
    {"date": "2026-07-13", "repos": {"a/alpha": 100, "b/beta": 100, "c/gamma": 100}},
    {"date": "2026-08-06", "repos": {"a/alpha": 107, "b/beta": 105, "c/gamma": 100}},
    {"date": "2026-08-13", "repos": {"a/alpha": 110, "b/beta": 120, "c/gamma": 100}},
]


def test_weekly_delta():
    deltas = delta_stars(SNAPSHOTS, 7)
    assert deltas["a/alpha"] == 3
    assert deltas["b/beta"] == 15


def test_monthly_delta():
    deltas = delta_stars(SNAPSHOTS, 30)
    assert deltas["a/alpha"] == 10
    assert deltas["b/beta"] == 20


def test_delta_skips_repos_without_baseline():
    snapshots = [
        {"date": "2026-08-06", "repos": {"a/alpha": 100}},
        {"date": "2026-08-13", "repos": {"a/alpha": 110, "b/beta": 50}},
    ]
    deltas = delta_stars(snapshots, 7)
    assert deltas == {"a/alpha": 10}


def test_weekly_order_and_zero_excluded():
    rankings = build_rankings(SKILLS, SNAPSHOTS)
    weekly = rankings["weekly"]
    assert [row["id"] for row in weekly] == ["beta", "alpha"]
    assert "gamma" not in [row["id"] for row in weekly]
    assert weekly[0]["delta"] == 15
    assert weekly[1]["delta"] == 3


def test_monthly_order():
    rankings = build_rankings(SKILLS, SNAPSHOTS)
    monthly = rankings["monthly"]
    assert [row["id"] for row in monthly] == ["beta", "alpha"]
    assert monthly[0]["delta"] == 20


def test_yearly_by_total_stars():
    rankings = build_rankings(SKILLS, SNAPSHOTS)
    yearly = rankings["yearly"]
    assert [row["id"] for row in yearly] == ["beta", "alpha", "gamma"]
    assert yearly[0]["stars"] == 120
    assert yearly[0]["delta"] is None


def test_tie_break_by_total_stars():
    skills = SKILLS[:2]
    snapshots = [
        {"date": "2026-08-06", "repos": {"a/alpha": 100, "b/beta": 200}},
        {"date": "2026-08-13", "repos": {"a/alpha": 110, "b/beta": 210}},
    ]
    rankings = build_rankings(skills, snapshots)
    assert [row["id"] for row in rankings["weekly"]] == ["beta", "alpha"]


def test_single_snapshot_no_deltas():
    snapshots = [{"date": "2026-08-13", "repos": {"a/alpha": 100}}]
    rankings = build_rankings(SKILLS, snapshots)
    assert rankings["weekly"] == []
    assert rankings["monthly"] == []
    assert rankings["yearly"][0]["id"] == "alpha"


def test_write_site_data_creates_categories_json(tmp_path):
    categories = {"categories": [{"key": "developer", "name": "开发", "audience": "程序员"}]}
    write_site_data({}, [], categories, tmp_path)
    assert (tmp_path / "categories.json").exists()
