"""Fetch current star counts for curated repos and write daily snapshots."""
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

GITHUB_API = "https://api.github.com/repos"
STAR_HISTORY_API = "https://star-history.dera.page"


def repo_slug(repo_url: str) -> str:
    """'https://github.com/a/b' -> 'a/b'."""
    return repo_url.rstrip("/").split("github.com/", 1)[1]


def fetch_current_stars(repo: str, token: str = "") -> int:
    """Return current stargazers_count for an owner/repo slug."""
    request = urllib.request.Request(
        f"{GITHUB_API}/{repo}",
        headers={"User-Agent": "agent-skills-hub", "Accept": "application/vnd.github+json"},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return int(payload["stargazers_count"])


def write_snapshot(snapshots_dir: Path, date_str: str, stars: dict) -> Path:
    """Write one snapshot file per date; same-day reruns overwrite."""
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    target = snapshots_dir / f"{date_str}.json"
    target.write_text(
        json.dumps({"date": date_str, "repos": stars}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return target


def fetch_star_history(slugs: list) -> dict:
    """Return {owner/repo: {date: cumulative stars}} via star-history.dera.page."""
    url = f"{STAR_HISTORY_API}/repo-data?repos={','.join(slugs)}"
    request = urllib.request.Request(url, headers={"User-Agent": "agent-skills-hub"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    result = {}
    for item in payload.get("data", []):
        result[item["repo"]] = {
            row["date"]: int(row["count"]) for row in item["starRecords"]
        }
    return result


def fetch_star_history_adaptive(slugs: list) -> dict:
    """Fetch history, splitting requests on rate limits (best effort)."""
    try:
        return fetch_star_history(slugs)
    except Exception as exc:
        if len(slugs) <= 1:
            print(f"WARN: 历史回填失败 {slugs}: {exc}")
            return {}
        mid = len(slugs) // 2
        result = fetch_star_history_adaptive(slugs[:mid])
        result.update(fetch_star_history_adaptive(slugs[mid:]))
        return result


def backfill_from_star_history(snapshots_dir: Path, date_str: str, slugs: list) -> None:
    """Best-effort backfill of 7/30-day baseline snapshots via star-history.dera.page."""
    current = date.fromisoformat(date_str)
    targets = [(current - timedelta(days=days)).isoformat() for days in (7, 30)]
    existing = {path.stem for path in snapshots_dir.glob("*.json")}
    missing = [target for target in targets if target not in existing]
    if not missing:
        return
    history = fetch_star_history_adaptive(slugs)
    if not history:
        return
    baselines = {target: {} for target in missing}
    for target in missing:
        for slug, series in history.items():
            stars_at = series.get(target)
            if stars_at is None:
                earlier = [day for day in series if day <= target]
                if not earlier:
                    continue
                stars_at = series[max(earlier)]
            baselines[target][slug] = stars_at
    for target, baseline in baselines.items():
        if baseline:
            write_snapshot(snapshots_dir, target, baseline)
    print(f"INFO: 历史快照回填完成: {missing}")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skills = json.loads((root / "data" / "skills.json").read_text(encoding="utf-8"))["skills"]
    snapshots_dir = root / "data" / "snapshots"
    args = sys.argv[1:]
    token = args[args.index("--token") + 1] if "--token" in args else ""
    date_str = datetime.now().date().isoformat()

    stars = {}
    errors = []
    for skill in skills:
        slug = repo_slug(skill["repo"])
        try:
            stars[slug] = fetch_current_stars(slug, token)
            print(f"OK {slug}: {stars[slug]}")
        except Exception as exc:
            errors.append({"repo": slug, "error": str(exc)})
            print(f"FAIL {slug}: {exc}")

    if stars:
        write_snapshot(snapshots_dir, date_str, stars)
        backfill_from_star_history(snapshots_dir, date_str, list(stars.keys()))
    if errors:
        (root / "data" / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return 0 if stars else 1


if __name__ == "__main__":
    sys.exit(main())
