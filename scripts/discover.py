"""Search GitHub for candidate skill repositories.

Normal mode writes the raw candidate list to data/candidates.json (gitignored).
--auto-add mode filters candidates into schema-compliant entries and appends
them to data/skills.json so new skills appear automatically.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

GITHUB_SEARCH = "https://api.github.com/search/repositories"
GITHUB_API = "https://api.github.com/repos"
RAW = "https://raw.githubusercontent.com"

MIN_STARS = 200

SKILL_PATHS = [
    "SKILL.md",
    "skills/SKILL.md",
    ".claude/skills/SKILL.md",
    ".codex/skills/SKILL.md",
    "plugins/skills/SKILL.md",
]

CATEGORY_KEYWORDS = {
    "design": ["designer"],
    "ui": ["designer"],
    "ux": ["designer"],
    "writing": ["writer"],
    "writer": ["writer"],
    "document": ["writer"],
    "research": ["research"],
    "science": ["research"],
    "academic": ["research"],
    "product": ["product"],
    "project management": ["product"],
    "security": ["devops"],
    "audit": ["devops"],
    "devops": ["devops"],
    "deploy": ["devops"],
    "marketing": ["marketing"],
    "seo": ["marketing"],
    "content": ["marketing"],
    "data": ["data-analyst"],
    "sql": ["data-analyst"],
    "analytics": ["data-analyst"],
    "obsidian": ["writer", "productivity"],
    "notes": ["writer", "productivity"],
    "productivity": ["productivity"],
    "workspace": ["productivity"],
    "office": ["productivity"],
}


def _request(url: str, token: str = ""):
    request = urllib.request.Request(
        url, headers={"User-Agent": "agent-skills-hub", "Accept": "application/vnd.github+json"}
    )
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(request, timeout=30)


def search_candidates(query: str, token: str = "") -> list:
    url = f"{GITHUB_SEARCH}?q={urllib.parse.quote(query)}&sort=stars&order=desc&per_page=30"
    with _request(url, token) as response:
        payload = json.load(response)
    return [
        {
            "name": item["full_name"],
            "url": item["html_url"],
            "stars": item["stargazers_count"],
            "description": item["description"] or "",
        }
        for item in payload.get("items", [])
    ]


def branch_head(repo: str, token: str = "") -> tuple:
    """Return (default_branch, head_sha) for an owner/repo slug."""
    with _request(f"{GITHUB_API}/{repo}", token) as response:
        repo_info = json.load(response)
    branch = repo_info["default_branch"]
    with _request(f"{GITHUB_API}/{repo}/commits?per_page=1", token) as response:
        commits = json.load(response)
    return branch, commits[0]["sha"]


def find_skill_path(repo: str, branch: str) -> str:
    """Return the first reachable SKILL.md path, or empty string."""
    for path in SKILL_PATHS:
        url = f"{RAW}/{repo}/{branch}/{path}"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "agent-skills-hub"})
            with urllib.request.urlopen(request, timeout=15) as response:
                if response.status == 200:
                    return path
        except Exception:
            continue
    return ""


def classify(description: str, name: str) -> list:
    """Map repo metadata to category keys; default to developer."""
    text = f"{description} {name}".lower()
    found = []
    for keyword, categories in CATEGORY_KEYWORDS.items():
        if keyword in text:
            for category in categories:
                if category not in found:
                    found.append(category)
    return found or ["developer"]


def slugify(repo: str) -> str:
    owner, name = repo.split("/", 1)
    owner = owner.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f"{owner}-{name}" if name else owner


def build_entry(candidate: dict, token: str = "") -> dict:
    repo = candidate["name"]
    branch, sha = branch_head(repo, token)
    skill_path = find_skill_path(repo, branch)
    if not skill_path:
        return None
    description = (candidate["description"] or "").strip()
    if not description:
        description = "GitHub 高星 Agent 技能仓库（自动收录，描述待完善）"
    return {
        "id": slugify(repo),
        "name": repo,
        "repo": f"https://github.com/{repo}",
        "entry": f"https://github.com/{repo}/blob/{sha}/{skill_path}",
        "description": description,
        "categories": classify(candidate["description"], repo),
        "platforms": ["multi"],
        "license": "",
        "verified_at": date.today().isoformat(),
        "tags": ["auto"],
        "added_at": date.today().isoformat(),
    }


def collect_new_skills(existing: list, token: str = "") -> list:
    """Return schema-compliant entries for new skill repos (deduped)."""
    queries = [
        "topic:agent-skills stars:>200",
        "topic:skills stars:>200",
        "topic:claude-skills stars:>200",
    ]
    existing_ids = {item["id"] for item in existing}
    existing_repos = {item["name"] for item in existing}
    seen = set()
    added = []
    for query in queries:
        try:
            candidates = search_candidates(query, token)
        except Exception as exc:
            print(f"WARN: 搜索失败 {query}: {exc}")
            continue
        for candidate in candidates:
            repo = candidate["name"]
            if repo.lower().startswith("awesome"):
                continue
            if candidate["stars"] < MIN_STARS:
                continue
            if repo in existing_repos or repo in seen:
                continue
            seen.add(repo)
            try:
                entry = build_entry(candidate, token)
            except Exception as exc:
                print(f"WARN: 处理 {repo} 失败: {exc}")
                continue
            if entry is None:
                continue
            if entry["id"] in existing_ids:
                continue
            existing_ids.add(entry["id"])
            added.append(entry)
            print(f"NEW: {repo}（{candidate['stars']}★）-> {entry['categories']}")
    return added


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    args = sys.argv[1:]
    token = args[args.index("--token") + 1] if "--token" in args else ""
    auto_add = "--auto-add" in args

    if not auto_add:
        queries = [
            "filename:SKILL.md stars:>100",
            "topic:agent-skills stars:>100",
            "topic:skills stars:>100",
        ]
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

    skills_path = root / "data" / "skills.json"
    skills = json.loads(skills_path.read_text(encoding="utf-8"))
    added = collect_new_skills(skills["skills"], token)
    if added:
        skills["skills"].extend(added)
        skills["updated_at"] = date.today().isoformat()
        skills_path.write_text(json.dumps(skills, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"INFO: 自动新增 {len(added)} 个技能")
    return 0


if __name__ == "__main__":
    sys.exit(main())
