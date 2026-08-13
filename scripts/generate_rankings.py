"""Compute weekly/monthly/yearly rankings from snapshots and write site data."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fetch_stars import repo_slug


def load_snapshots(snapshots_dir: Path) -> list:
    snapshots = []
    for path in sorted(snapshots_dir.glob("*.json")):
        snapshots.append(json.loads(path.read_text(encoding="utf-8")))
    return snapshots


def delta_stars(snapshots: list, days: int) -> dict:
    """Stars gained in the last `days`, falling back to the earliest snapshot."""
    if not snapshots:
        return {}
    current = snapshots[-1]["repos"]
    target_date = date.fromisoformat(snapshots[-1]["date"]) - timedelta(days=days)
    baseline = None
    for snapshot in reversed(snapshots[:-1]):
        if date.fromisoformat(snapshot["date"]) <= target_date:
            baseline = snapshot["repos"]
            break
    if baseline is None:
        baseline = snapshots[0]["repos"]
    return {repo: current[repo] - baseline.get(repo, 0) for repo in current}


def build_rankings(skills: list, snapshots: list) -> dict:
    stars = snapshots[-1]["repos"] if snapshots else {}
    weekly = delta_stars(snapshots, 7)
    monthly = delta_stars(snapshots, 30)
    skills_by_slug = {repo_slug(skill["repo"]): skill for skill in skills}

    def row(repo: str, rank: int, delta):
        skill = skills_by_slug.get(repo)
        if skill is None:
            return None
        return {
            "rank": rank,
            "id": skill["id"],
            "name": skill["name"],
            "repo": skill["repo"],
            "entry": skill["entry"],
            "description": skill["description"],
            "categories": skill["categories"],
            "platforms": skill["platforms"],
            "stars": stars.get(repo, 0),
            "delta": delta,
        }

    def board(deltas: dict, exclude_nonpositive: bool = True) -> list:
        entries = [(repo, delta) for repo, delta in deltas.items()
                   if not exclude_nonpositive or delta > 0]
        entries.sort(key=lambda item: (-item[1], -stars.get(item[0], 0)))
        result = []
        for rank, (repo, delta) in enumerate(entries, start=1):
            built = row(repo, rank, delta)
            if built:
                result.append(built)
        return result

    yearly_sorted = sorted(stars.items(), key=lambda item: -item[1])
    yearly = []
    for rank, (repo, star_count) in enumerate(yearly_sorted, start=1):
        built = row(repo, rank, None)
        if built:
            yearly.append(built)

    return {
        "updated_at": snapshots[-1]["date"] if snapshots else "",
        "weekly": board(weekly),
        "monthly": board(monthly),
        "yearly": yearly,
    }


def write_site_data(rankings: dict, skills: list, site_data_dir: Path) -> None:
    site_data_dir.mkdir(parents=True, exist_ok=True)
    (site_data_dir / "rankings.json").write_text(
        json.dumps(rankings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    pruned = [
        {
            "id": skill["id"],
            "name": skill["name"],
            "repo": skill["repo"],
            "entry": skill["entry"],
            "description": skill["description"],
            "categories": skill["categories"],
            "platforms": skill["platforms"],
            "tags": skill.get("tags", []),
        }
        for skill in skills
    ]
    (site_data_dir / "skills.json").write_text(
        json.dumps({"updated_at": rankings["updated_at"], "skills": pruned}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def render_readme(rankings: dict, skills: list) -> str:
    lines = [
        "# Agent Skills Hub",
        "",
        "> 收录 GitHub 热门的 SKILL.md 智能体技能包，提供周榜 / 月榜 / 年榜与按人群分类。",
        "",
        f"- 收录技能：{len(skills)} 个",
        f"- 数据更新时间：{rankings.get('updated_at', '暂无')}",
        "- 在线榜单：GitHub Pages 部署后可用（见 [docs/methodology.md](docs/methodology.md)）",
        "",
    ]
    boards = [
        ("周榜 Top 5（近 7 天涨星）", "delta", rankings["weekly"]),
        ("月榜 Top 5（近 30 天涨星）", "delta", rankings["monthly"]),
        ("年榜 Top 5（总星标）", "stars", rankings["yearly"]),
    ]
    for title, metric, rows in boards:
        lines.append(f"## {title}")
        lines.append("")
        lines.append(f"| 排名 | 名称 | {metric} | 简介 |")
        lines.append("| --- | --- | --- | --- |")
        for row in rows[:5]:
            lines.append(f"| {row['rank']} | [{row['name']}]({row['repo']}) | {row[metric]} | {row['description']} |")
        lines.append("")
    lines.append("## 如何贡献")
    lines.append("")
    lines.append("新增或更新技能请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)；完整榜单与分类见站点页面。")
    return "\n".join(lines)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skills = json.loads((root / "data" / "skills.json").read_text(encoding="utf-8"))["skills"]
    snapshots = load_snapshots(root / "data" / "snapshots")
    rankings = build_rankings(skills, snapshots)
    write_site_data(rankings, skills, root / "site" / "data")
    (root / "README.md").write_text(render_readme(rankings, skills), encoding="utf-8")
    print(json.dumps({key: len(value) for key, value in rankings.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
