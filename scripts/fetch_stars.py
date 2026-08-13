"""Fetch current star counts for curated repos and write daily snapshots."""
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

GITHUB_API = "https://api.github.com/repos"
STAR_HISTORY_URL = "https://api.star-history.com/svg"


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


def backfill_from_star_history(date_str: str, slugs: list) -> None:
    """Best-effort historical backfill; upstream is currently degraded."""
    try:
        repos = ",".join(slugs)
        url = f"{STAR_HISTORY_URL}?repos={urllib.parse.quote(repos)}"
        request = urllib.request.Request(url, headers={"User-Agent": "agent-skills-hub"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(2000).decode("utf-8", errors="ignore")
        if "restricted access" in body.lower():
            print("WARN: star-history 服务当前受 GitHub 数据限制影响，跳过回填")
            return
        print(f"INFO: star-history 返回数据（{len(body)} 字节），本版暂不解析历史序列")
    except Exception as exc:
        print(f"WARN: star-history 回填失败，跳过: {exc}")


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
        backfill_from_star_history(date_str, list(stars.keys()))
    if errors:
        (root / "data" / "errors.json").write_text(
            json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    return 0 if stars else 1


if __name__ == "__main__":
    sys.exit(main())
