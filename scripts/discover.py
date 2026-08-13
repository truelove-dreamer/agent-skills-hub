"""Search GitHub for candidate skill repositories (suggestions only)."""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

GITHUB_SEARCH = "https://api.github.com/search/repositories"


def search_candidates(query: str, token: str = "") -> list:
    url = f"{GITHUB_SEARCH}?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=20"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "agent-skills-hub", "Accept": "application/vnd.github+json"},
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return [
        {
            "name": item["full_name"],
            "url": item["html_url"],
            "stars": item["stargazers_count"],
            "description": item["description"],
        }
        for item in payload.get("items", [])
    ]


def main() -> int:
    queries = [
        "filename:SKILL.md stars:>100",
        "topic:agent-skills stars:>100",
        "topic:skills stars:>100",
    ]
    args = sys.argv[1:]
    token = args[args.index("--token") + 1] if "--token" in args else ""
    root = Path(__file__).resolve().parent.parent
    results = {}
    for query in queries:
        try:
            results[query] = search_candidates(query, token)
            print(f"OK {query}: {len(results[query])} candidates")
        except Exception as exc:
            results[query] = []
            print(f"FAIL {query}: {exc}")
    (root / "data" / "candidates.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
