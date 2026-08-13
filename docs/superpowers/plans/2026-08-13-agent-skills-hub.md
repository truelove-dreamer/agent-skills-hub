# Agent Skills Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 agent-skills-hub：一个数据驱动的 GitHub 项目，收录热门 SKILL.md 技能包，提供周/月/年榜、按人群分类的静态站，以及每周自动更新的数据管道。

**Architecture:** `data/skills.json` 是唯一事实源（人工策展）；`scripts/fetch_stars.py` 每周抓取星标写快照，`scripts/generate_rankings.py` 计算三个榜单并渲染 README 与站点 JSON；纯静态站（无构建步骤）读取 JSON 渲染；GitHub Actions 每周定时跑完整管道并部署 Pages。

**Tech Stack:** Python 3.10+（仅标准库，`urllib`）、pytest、纯 HTML/CSS/JS、GitHub Actions + GitHub Pages。

**执行环境说明：**

- 本机为 Windows + PowerShell，Python 3.14（`python` 可用），pytest 需先安装。
- 仓库根目录即当前工作区（本地目录名 `suitable-skill`，GitHub 仓库名 `agent-skills-hub`）。
- 所有文件路径相对仓库根目录。
- 初版种子数据为 12 条已核验条目；扩充到 30+ 在管道上线后通过 PR 与 `discover.py` 候选清单逐步完成（设计文档里程碑 6）。
- star-history 回填为“尽力而为”：该服务当前受 GitHub 星标数据限制影响，不可用时自动跳过，周/月榜靠快照积累，另支持手动导入历史快照。

---

## 文件结构总览

```text
.gitignore
requirements-dev.txt
README.md（由 generate_rankings.py 生成）
CONTRIBUTING.md
docs/methodology.md
docs/candidates.md
data/categories.json
data/skills.json
data/snapshots/*.json（脚本生成）
scripts/fetch_stars.py
scripts/generate_rankings.py
scripts/validate_data.py
scripts/discover.py
site/index.html
site/rankings.html
site/categories.html
site/about.html
site/assets/style.css
site/assets/app.js
site/data/*.json（脚本生成）
tests/test_schema.py
tests/test_fetch_stars.py
tests/test_rankings.py
tests/test_readme.py
tests/test_site.py
.github/workflows/update-rankings.yml
```

---

### Task 1: 脚手架与种子数据

**Files:**
- Create: `.gitignore`
- Create: `requirements-dev.txt`
- Create: `data/categories.json`
- Create: `data/skills.json`

- [ ] **Step 1: 创建 `.gitignore`**

```text
__pycache__/
.pytest_cache/
data/errors.json
data/candidates.json
```

- [ ] **Step 2: 创建 `requirements-dev.txt`**

```text
pytest>=7
```

- [ ] **Step 3: 创建 `data/categories.json`**

```json
{
  "categories": [
    {"key": "developer", "name": "开发", "audience": "程序员：代码、调试、重构、测试"},
    {"key": "data-analyst", "name": "数据分析", "audience": "数据分析师/研究者：SQL、统计、可视化"},
    {"key": "designer", "name": "设计", "audience": "设计师：UI/UX、图片、视频、3D"},
    {"key": "writer", "name": "写作/文档", "audience": "技术写作、文档、翻译"},
    {"key": "product", "name": "产品/管理", "audience": "产品经理、项目经理：PRD、需求分析"},
    {"key": "devops", "name": "运维", "audience": "运维/DevOps：部署、监控、安全"},
    {"key": "marketing", "name": "营销/内容", "audience": "运营、市场：内容创作、SEO、社媒"},
    {"key": "research", "name": "研究/学习", "audience": "学生、研究者：文献、学习辅助"},
    {"key": "productivity", "name": "通用效率", "audience": "所有人：日常办公、自动化"}
  ]
}
```

- [ ] **Step 4: 创建 `data/skills.json`（12 条已核验种子数据，entry 全部 pin 到 2026-08-13 的 commit SHA）**

```json
{
  "schema_version": 1,
  "updated_at": "2026-08-13",
  "skills": [
    {
      "id": "anthropics-skills",
      "name": "anthropics/skills",
      "repo": "https://github.com/anthropics/skills",
      "entry": "https://github.com/anthropics/skills/blob/f17010c9bb483898c1d9c9f42dde2b3a98889434/README.md",
      "description": "Anthropic 官方技能集合，覆盖文档、创意与研发场景，含 docx/pdf/pptx/xlsx 文档技能",
      "categories": ["developer", "writer", "productivity"],
      "platforms": ["claude-code"],
      "license": "Apache-2.0",
      "verified_at": "2026-08-13",
      "tags": ["document", "official"],
      "added_at": "2026-08-13"
    },
    {
      "id": "agentskills-spec",
      "name": "agentskills/agentskills",
      "repo": "https://github.com/agentskills/agentskills",
      "entry": "https://github.com/agentskills/agentskills/blob/69ef37e9424c0a7ea9dd2293b559e43ec8176379/README.md",
      "description": "Agent Skills 官方规范与文档仓库，定义 SKILL.md 标准与最佳实践",
      "categories": ["developer", "productivity"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["spec", "official"],
      "added_at": "2026-08-13"
    },
    {
      "id": "openai-skills",
      "name": "openai/skills",
      "repo": "https://github.com/openai/skills",
      "entry": "https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/README.md",
      "description": "OpenAI 官方 Codex 技能目录，提供面向 Codex 的 SKILL.md 技能集合",
      "categories": ["developer"],
      "platforms": ["codex"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["coding", "official"],
      "added_at": "2026-08-13"
    },
    {
      "id": "vercel-labs-skills",
      "name": "vercel-labs/skills",
      "repo": "https://github.com/vercel-labs/skills",
      "entry": "https://github.com/vercel-labs/skills/blob/c6f69c631292444cc541ac6d91e2226b0ff247da/README.md",
      "description": "开源技能工具链，用 npx skills 一键搜索、安装和管理 Agent Skills",
      "categories": ["developer", "devops"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["tooling", "installer"],
      "added_at": "2026-08-13"
    },
    {
      "id": "microsoft-skills",
      "name": "microsoft/skills",
      "repo": "https://github.com/microsoft/skills",
      "entry": "https://github.com/microsoft/skills/blob/e58528db9a006528a5fb0a2c029790fa6a9a7c0e/README.md",
      "description": "微软官方技能与 MCP 集合，为编码 Agent 提供 SDK 相关领域知识",
      "categories": ["developer", "devops"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["coding", "official"],
      "added_at": "2026-08-13"
    },
    {
      "id": "trailofbits-skills",
      "name": "trailofbits/skills",
      "repo": "https://github.com/trailofbits/skills",
      "entry": "https://github.com/trailofbits/skills/blob/304c81a8cefb6e3c029ebd0d12940ccf0713eccb/README.md",
      "description": "安全研究专用技能，覆盖漏洞检测、代码审计与渗透测试工作流",
      "categories": ["developer", "devops"],
      "platforms": ["claude-code"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["security", "audit"],
      "added_at": "2026-08-13"
    },
    {
      "id": "claude-scientific-skills",
      "name": "K-Dense-AI/claude-scientific-skills",
      "repo": "https://github.com/K-Dense-AI/claude-scientific-skills",
      "entry": "https://github.com/K-Dense-AI/claude-scientific-skills/blob/5ad4aae76bc40257b914367afacc6fd686a282d5/README.md",
      "description": "科研全流程技能库，从选题、实验设计到论文写作，社区广泛使用的科研技能集合",
      "categories": ["research", "data-analyst"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["science", "research"],
      "added_at": "2026-08-13"
    },
    {
      "id": "web-quality-skills",
      "name": "addyosmani/web-quality-skills",
      "repo": "https://github.com/addyosmani/web-quality-skills",
      "entry": "https://github.com/addyosmani/web-quality-skills/blob/95d6e255afe1596b557d7a8498517884438f5b3a/README.md",
      "description": "基于 Lighthouse 与 Core Web Vitals 的 Web 质量优化技能",
      "categories": ["developer"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["web", "performance"],
      "added_at": "2026-08-13"
    },
    {
      "id": "voltagent-awesome-agent-skills",
      "name": "VoltAgent/awesome-agent-skills",
      "repo": "https://github.com/VoltAgent/awesome-agent-skills",
      "entry": "https://github.com/VoltAgent/awesome-agent-skills/blob/bb272b65c8162bed7e1f92d72e9323744ecdb6f5/README.md",
      "description": "社区策展的 1000+ Agent Skills 目录，兼容 Claude Code、Codex、Cursor 等平台",
      "categories": ["developer", "productivity"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["directory", "community"],
      "added_at": "2026-08-13"
    },
    {
      "id": "heilcheng-awesome-agent-skills",
      "name": "heilcheng/awesome-agent-skills",
      "repo": "https://github.com/heilcheng/awesome-agent-skills",
      "entry": "https://github.com/heilcheng/awesome-agent-skills/blob/de9056857eb0e96da833469d2ee3ac392058225d/README.md",
      "description": "面向工程团队的 Agent Skills 精选目录，含教程与实战指南",
      "categories": ["developer", "productivity"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["directory", "tutorial"],
      "added_at": "2026-08-13"
    },
    {
      "id": "awesome-academic-skills",
      "name": "cosen1024/awesome-academic-skills",
      "repo": "https://github.com/cosen1024/awesome-academic-skills",
      "entry": "https://github.com/cosen1024/awesome-academic-skills/blob/bcc3e92e88cd42536f7351839437e7de4d75ae1a/README.md",
      "description": "可机器校验的科研 Agent Skills 清单，按科研工作流组织 13 个环节",
      "categories": ["research"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["research", "directory"],
      "added_at": "2026-08-13"
    },
    {
      "id": "skills-top-stars",
      "name": "wind8ai/skills-top-stars",
      "repo": "https://github.com/wind8ai/skills-top-stars",
      "entry": "https://github.com/wind8ai/skills-top-stars/blob/4f27da6c459de6b565a060b448266288581128d1/README.md",
      "description": "GitHub 高星 Skills 项目精选，按星标与更新时间整理",
      "categories": ["developer", "productivity"],
      "platforms": ["multi"],
      "license": "",
      "verified_at": "2026-08-13",
      "tags": ["ranking", "directory"],
      "added_at": "2026-08-13"
    }
  ]
}
```

- [ ] **Step 5: 验证 JSON 可解析**

Run: `python -c "import json; json.load(open('data/skills.json', encoding='utf-8')); json.load(open('data/categories.json', encoding='utf-8')); print('JSON OK')"`

Expected: `JSON OK`

- [ ] **Step 6: 提交**

```bash
git add .gitignore requirements-dev.txt data/categories.json data/skills.json
git commit -m "feat: 初始化数据文件与种子技能列表"
```

---

### Task 2: 数据校验脚本 `validate_data.py`（TDD）

**Files:**
- Create: `tests/test_schema.py`
- Create: `scripts/validate_data.py`

- [ ] **Step 1: 安装 pytest**

Run: `python -m pip install -r requirements-dev.txt`

Expected: pytest 安装成功。

- [ ] **Step 2: 编写失败测试 `tests/test_schema.py`**

```python
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
```

- [ ] **Step 3: 运行测试确认失败**

Run: `python -m pytest tests/test_schema.py -q`

Expected: FAIL，报 `ModuleNotFoundError: No module named 'validate_data'`。

- [ ] **Step 4: 实现 `scripts/validate_data.py`**

```python
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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `python -m pytest tests/test_schema.py -q`

Expected: `8 passed`

- [ ] **Step 6: 提交**

```bash
git add tests/test_schema.py scripts/validate_data.py
git commit -m "feat: 添加数据校验脚本与 schema 测试"
```

---

### Task 3: 星标抓取 `fetch_stars.py`（TDD）

**Files:**
- Create: `tests/test_fetch_stars.py`
- Create: `scripts/fetch_stars.py`

- [ ] **Step 1: 编写失败测试 `tests/test_fetch_stars.py`**

```python
import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest

from fetch_stars import (
    backfill_from_star_history,
    fetch_current_stars,
    repo_slug,
    write_snapshot,
)


def test_repo_slug():
    assert repo_slug("https://github.com/anthropics/skills") == "anthropics/skills"


def test_fetch_current_stars():
    response = mock.MagicMock()
    response.read.return_value = json.dumps({"stargazers_count": 4242}).encode()
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value = response
        assert fetch_current_stars("a/b") == 4242


def test_fetch_current_stars_uses_token():
    response = mock.MagicMock()
    response.read.return_value = json.dumps({"stargazers_count": 1}).encode()
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value = response
        fetch_current_stars("a/b", token="secret-token")
    request = urlopen.call_args.args[0]
    assert request.get_header("Authorization") == "Bearer secret-token"


def test_fetch_error_propagates():
    with mock.patch("urllib.request.urlopen", side_effect=Exception("boom")):
        with pytest.raises(Exception):
            fetch_current_stars("a/b")


def test_write_snapshot_overwrites_same_day(tmp_path):
    first = write_snapshot(tmp_path, "2026-08-13", {"a/b": 1})
    second = write_snapshot(tmp_path, "2026-08-13", {"a/b": 2})
    assert first == second
    data = json.loads(second.read_text(encoding="utf-8"))
    assert data["repos"]["a/b"] == 2


def test_backfill_gracefully_skips_when_service_degraded(capsys):
    body = b"<text>GitHub restricted access to star data</text>"
    with mock.patch("urllib.request.urlopen") as urlopen:
        urlopen.return_value.__enter__.return_value.read.return_value = body
        backfill_from_star_history("2026-08-13", ["a/b"])
    assert "跳过回填" in capsys.readouterr().out


def test_backfill_ignores_network_errors(capsys):
    with mock.patch("urllib.request.urlopen", side_effect=Exception("boom")):
        backfill_from_star_history("2026-08-13", ["a/b"])
    assert "跳过" in capsys.readouterr().out
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_fetch_stars.py -q`

Expected: FAIL，报 `ModuleNotFoundError: No module named 'fetch_stars'`。

- [ ] **Step 3: 实现 `scripts/fetch_stars.py`**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_fetch_stars.py -q`

Expected: `7 passed`

- [ ] **Step 5: 提交**

```bash
git add tests/test_fetch_stars.py scripts/fetch_stars.py
git commit -m "feat: 添加星标抓取与快照写入脚本"
```

---

### Task 4: 榜单计算 `generate_rankings.py`（TDD）

**Files:**
- Create: `tests/test_rankings.py`
- Create: `scripts/generate_rankings.py`

- [ ] **Step 1: 编写失败测试 `tests/test_rankings.py`**

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from generate_rankings import build_rankings, delta_stars

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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_rankings.py -q`

Expected: FAIL，报 `ModuleNotFoundError: No module named 'generate_rankings'`。

- [ ] **Step 3: 实现 `scripts/generate_rankings.py`**

```python
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


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skills = json.loads((root / "data" / "skills.json").read_text(encoding="utf-8"))["skills"]
    snapshots = load_snapshots(root / "data" / "snapshots")
    rankings = build_rankings(skills, snapshots)
    write_site_data(rankings, skills, root / "site" / "data")
    print(json.dumps({key: len(value) for key, value in rankings.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_rankings.py -q`

Expected: `7 passed`

- [ ] **Step 5: 提交**

```bash
git add tests/test_rankings.py scripts/generate_rankings.py
git commit -m "feat: 添加榜单计算与站点数据生成脚本"
```

---

### Task 5: README 渲染、协作文档与方法论文档

**Files:**
- Modify: `scripts/generate_rankings.py`
- Create: `tests/test_readme.py`
- Create: `CONTRIBUTING.md`
- Create: `docs/methodology.md`
- Create: `docs/candidates.md`

- [ ] **Step 1: 编写失败测试 `tests/test_readme.py`**

```python
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
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_readme.py -q`

Expected: FAIL，报 `ImportError: cannot import name 'render_readme'`。

- [ ] **Step 3: 在 `scripts/generate_rankings.py` 末尾追加 `render_readme` 并让 `main()` 写 README.md**

在 `write_site_data` 函数之后追加：

```python
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
```

把 `main()` 中 `write_site_data(...)` 之后追加：

```python
    (root / "README.md").write_text(render_readme(rankings, skills), encoding="utf-8")
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_readme.py -q`

Expected: `2 passed`

- [ ] **Step 5: 创建 `CONTRIBUTING.md`**

```markdown
# 贡献指南

欢迎通过 PR 或 Issue 参与维护。

## 新增或更新一个 skill

1. 修改 `data/skills.json`，新增或更新条目。
2. 运行 `python scripts/validate_data.py`，确保输出 `OK: ...`。
3. 运行 `python -m pytest -q`，确保测试全部通过。
4. 提交 PR，说明简介、分类与核验情况。

## 条目字段

| 字段 | 说明 |
| --- | --- |
| `id` | 唯一 ID，小写连字符 |
| `name` | 仓库名（owner/repo） |
| `repo` | GitHub 仓库链接 |
| `entry` | 固定 commit 的 SKILL.md 或套件入口链接 |
| `description` | 一句话中文功能说明 |
| `categories` | 分类 key（见 `data/categories.json`），至少 1 个 |
| `platforms` | 兼容平台：`claude-code`、`codex`、`cursor`、`gemini-cli`、`copilot`、`windsurf`、`opencode`、`multi` |
| `license` | 许可证（可选，核验后补） |
| `verified_at` | 人工核验日期 YYYY-MM-DD |
| `tags` | 标签数组 |
| `added_at` | 收录日期 YYYY-MM-DD |

## 收录边界

- 只收公开 GitHub 仓库，且能定位到 `SKILL.md`、插件入口或 Skill 套件入口。
- 不收仅 MCP 的仓库、纯宣传页、无法审阅源码的产品。
- 失效或归档仓库请提出 Issue 移除。

## 安全提示

核验日期仅表示链接与描述经过人工检查，不构成对技能内容、安全性或质量的背书。安装任何第三方技能前，请阅读其 README、许可证、权限与数据上传说明。
```

- [ ] **Step 6: 创建 `docs/methodology.md`**

```markdown
# 方法与口径

## 榜单口径

- 周榜：近 7 天涨星（当前快照 − 7 天前快照）
- 月榜：近 30 天涨星（当前快照 − 30 天前快照）
- 年榜：总星标数
- 周榜/月榜剔除涨星为 0 或负数的条目；并列时按总星标再排序。
- 快照存于 `data/snapshots/YYYY-MM-DD.json`，每周追加，同日覆盖。

## 冷启动与回填

- 新项目没有历史快照，周榜/月榜在积累 1–4 周后逐步可用，年榜（总星标）始终可用。
- `fetch_stars.py` 会尝试调用 star-history 接口回填历史；该服务当前受 GitHub 星标数据限制影响，不可用时自动跳过，不影响主流程。
- 如需手动导入历史数据，可直接添加一个 `data/snapshots/YYYY-MM-DD.json` 文件（格式见已有快照）。

## 收录边界

只收录公开 GitHub 源码且能定位到 SKILL.md / 插件入口 / 套件入口的项目。排除：仅 MCP、纯宣传页、无法审阅源码的产品、失效仓库。

## 更新流程

GitHub Actions 每周日 UTC 0 点自动运行：抓取星标 → 生成榜单与站点数据 → 校验 → 测试 → 提交 → 部署 Pages。也可在 Actions 页面手动触发。

## 数据来源

- 当前星标：GitHub REST API（`GET /repos/{owner}/{repo}`）
- 历史回填：star-history（尽力而为，受上游限制影响）
```

- [ ] **Step 7: 创建 `docs/candidates.md`**

```markdown
# 候选与核验记录

## 待审核

运行 `python scripts/discover.py` 后会生成 `data/candidates.json`（不入库）。将值得收录的候选整理到下表并提交 PR：

| 仓库 | 说明 | 建议分类 | 核验人 |
| --- | --- | --- | --- |
| （示例）owner/repo | 一句话说明 | developer | 待核验 |

## 已核验

首批 12 条（见 `data/skills.json`）已于 2026-08-13 核验：仓库存在、入口链接指向固定 commit、描述与分类人工确认。

## 排除记录

| 仓库 | 排除原因 | 日期 |
| --- | --- | --- |
| （示例）owner/repo | 仅提供 MCP，无 SKILL.md 入口 | 2026-08-13 |
```

- [ ] **Step 8: 全量测试并提交**

Run: `python -m pytest -q`

Expected: 全部通过（当前应为 `8 passed`（schema）+ `7 passed`（fetch）+ `7 passed`（rankings）+ `2 passed`（readme）= 24 passed）。

```bash
git add scripts/generate_rankings.py tests/test_readme.py CONTRIBUTING.md docs/methodology.md docs/candidates.md
git commit -m "feat: 添加 README 渲染、贡献指南与方法论文档"
```

---

### Task 6: 静态站页面与资源

**Files:**
- Create: `tests/test_site.py`
- Create: `site/index.html`
- Create: `site/rankings.html`
- Create: `site/categories.html`
- Create: `site/about.html`
- Create: `site/assets/style.css`
- Create: `site/assets/app.js`
- Create: `site/data/.gitkeep`

- [ ] **Step 1: 编写失败测试 `tests/test_site.py`**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
PAGES = ["index.html", "rankings.html", "categories.html", "about.html"]


def test_pages_exist():
    for page in PAGES:
        assert (SITE / page).exists(), f"缺少 {page}"


def test_pages_use_app_js():
    for page in PAGES:
        html = (SITE / page).read_text(encoding="utf-8")
        assert "assets/app.js" in html


def test_assets_exist():
    assert (SITE / "assets" / "app.js").exists()
    assert (SITE / "assets" / "style.css").exists()


def test_about_covers_boundaries():
    html = (SITE / "about.html").read_text(encoding="utf-8")
    assert "收录边界" in html
    assert "核验" in html
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_site.py -q`

Expected: FAIL，报 `AssertionError: 缺少 index.html`。

- [ ] **Step 3: 创建 `site/assets/style.css`**

```css
:root {
  --bg: #f6f7f9;
  --card: #ffffff;
  --text: #1f2328;
  --muted: #656d76;
  --accent: #0969da;
  --border: #d0d7de;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
}
header {
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
}
header h1 { margin: 0; font-size: 20px; }
nav { margin-top: 8px; }
nav a { color: var(--accent); text-decoration: none; margin-right: 16px; }
nav a:hover { text-decoration: underline; }
main { max-width: 960px; margin: 24px auto; padding: 0 16px; }
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}
.muted { color: var(--muted); }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 8px; border-bottom: 1px solid var(--border); }
th { color: var(--muted); font-weight: 600; }
a { color: var(--accent); }
.tab-button {
  padding: 8px 16px;
  border: 1px solid var(--border);
  background: var(--card);
  cursor: pointer;
  border-radius: 6px 6px 0 0;
}
.tab-button.active { background: var(--accent); color: #fff; border-color: var(--accent); }
.category-card { cursor: pointer; }
.category-card h3 { margin: 0 0 4px; }
.category-card .count { color: var(--muted); font-size: 13px; }
#skill-list .skill-item { padding: 10px 0; border-bottom: 1px solid var(--border); }
```

- [ ] **Step 4: 创建 `site/assets/app.js`**

```js
async function fetchJSON(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path}: HTTP ${response.status}`);
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function metricValue(row) {
  return row.delta == null ? row.stars : row.delta;
}

function boardRows(rows) {
  return rows
    .map(
      (row) => `<tr>
        <td>${row.rank}</td>
        <td><a href="${escapeHtml(row.repo)}" target="_blank" rel="noopener">${escapeHtml(row.name)}</a></td>
        <td>${metricValue(row)}</td>
        <td>${row.categories.map(escapeHtml).join(", ")}</td>
        <td>${escapeHtml(row.description)}</td>
      </tr>`
    )
    .join("");
}

function renderBoard(rows, tableId) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  tbody.innerHTML = boardRows(rows);
}

async function initHome() {
  const rankings = await fetchJSON("data/rankings.json");
  renderBoard(rankings.weekly.slice(0, 10), "weekly-table");
  document.querySelector("#updated-at").textContent = rankings.updated_at || "暂无";
}

async function initRankings() {
  const rankings = await fetchJSON("data/rankings.json");
  renderBoard(rankings.weekly, "weekly-table");
  renderBoard(rankings.monthly, "monthly-table");
  renderBoard(rankings.yearly, "yearly-table");
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((b) => b.classList.remove("active"));
      button.classList.add("active");
      document.querySelectorAll(".board").forEach((board) => (board.style.display = "none"));
      document.querySelector(`#${button.dataset.target}`).style.display = "";
    });
  });
}

async function initCategories() {
  const [categories, skills] = await Promise.all([
    fetchJSON("data/categories.json"),
    fetchJSON("data/skills.json"),
  ]);
  const container = document.querySelector("#category-cards");
  container.innerHTML = categories.categories
    .map((category) => {
      const count = skills.skills.filter((s) => s.categories.includes(category.key)).length;
      return `<div class="card category-card" data-key="${escapeHtml(category.key)}">
        <h3>${escapeHtml(category.name)}</h3>
        <p class="muted">${escapeHtml(category.audience)}</p>
        <span class="count">${count} 个技能</span>
      </div>`;
    })
    .join("");
  container.querySelectorAll(".category-card").forEach((card) => {
    card.addEventListener("click", () => {
      const key = card.dataset.key;
      const filtered = skills.skills.filter((s) => s.categories.includes(key));
      document.querySelector("#skill-list").innerHTML = filtered
        .map(
          (s) => `<div class="skill-item">
            <a href="${escapeHtml(s.entry)}" target="_blank" rel="noopener">${escapeHtml(s.name)}</a>
            <span class="muted"> — ${escapeHtml(s.description)}</span>
          </div>`
        )
        .join("");
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.body.dataset.page === "home") {
    initHome().catch((error) => console.error(error));
  } else if (document.body.dataset.page === "rankings") {
    initRankings().catch((error) => console.error(error));
  } else if (document.body.dataset.page === "categories") {
    initCategories().catch((error) => console.error(error));
  }
});
```

- [ ] **Step 5: 创建四个 HTML 页面**

`site/index.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Skills Hub - 首页</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="home">
  <header>
    <h1>Agent Skills Hub</h1>
    <nav>
      <a href="index.html">首页</a>
      <a href="rankings.html">榜单</a>
      <a href="categories.html">分类</a>
      <a href="about.html">关于</a>
    </nav>
  </header>
  <main>
    <div class="card">
      <h2>GitHub 热门 Agent Skills 排行</h2>
      <p class="muted">数据更新时间：<span id="updated-at">加载中…</span></p>
    </div>
    <div class="card">
      <h2>周榜 Top 10（近 7 天涨星）</h2>
      <table>
        <thead><tr><th>排名</th><th>名称</th><th>涨星</th><th>分类</th><th>简介</th></tr></thead>
        <tbody id="weekly-table"></tbody>
      </table>
    </div>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
```

`site/rankings.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Skills Hub - 榜单</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="rankings">
  <header>
    <h1>Agent Skills Hub</h1>
    <nav>
      <a href="index.html">首页</a>
      <a href="rankings.html">榜单</a>
      <a href="categories.html">分类</a>
      <a href="about.html">关于</a>
    </nav>
  </header>
  <main>
    <div class="card">
      <button class="tab-button active" data-target="weekly-board">周榜（近 7 天涨星）</button>
      <button class="tab-button" data-target="monthly-board">月榜（近 30 天涨星）</button>
      <button class="tab-button" data-target="yearly-board">年榜（总星标）</button>
    </div>
    <div class="card board" id="weekly-board">
      <h2>周榜</h2>
      <table><thead><tr><th>排名</th><th>名称</th><th>涨星</th><th>分类</th><th>简介</th></tr></thead><tbody id="weekly-table"></tbody></table>
    </div>
    <div class="card board" id="monthly-board" style="display:none">
      <h2>月榜</h2>
      <table><thead><tr><th>排名</th><th>名称</th><th>涨星</th><th>分类</th><th>简介</th></tr></thead><tbody id="monthly-table"></tbody></table>
    </div>
    <div class="card board" id="yearly-board" style="display:none">
      <h2>年榜</h2>
      <table><thead><tr><th>排名</th><th>名称</th><th>总星</th><th>分类</th><th>简介</th></tr></thead><tbody id="yearly-table"></tbody></table>
    </div>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
```

`site/categories.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Skills Hub - 分类</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body data-page="categories">
  <header>
    <h1>Agent Skills Hub</h1>
    <nav>
      <a href="index.html">首页</a>
      <a href="rankings.html">榜单</a>
      <a href="categories.html">分类</a>
      <a href="about.html">关于</a>
    </nav>
  </header>
  <main>
    <div class="card">
      <h2>按人群选择</h2>
      <p class="muted">点击卡片查看这类人适合的 skill。</p>
      <div id="category-cards"></div>
    </div>
    <div class="card">
      <h2>推荐技能</h2>
      <div id="skill-list"></div>
    </div>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
```

`site/about.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Agent Skills Hub - 关于</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header>
    <h1>Agent Skills Hub</h1>
    <nav>
      <a href="index.html">首页</a>
      <a href="rankings.html">榜单</a>
      <a href="categories.html">分类</a>
      <a href="about.html">关于</a>
    </nav>
  </header>
  <main>
    <div class="card">
      <h2>这个项目是什么</h2>
      <p>收录 GitHub 热门的 SKILL.md 智能体技能包，提供周榜（近 7 天涨星）、月榜（近 30 天涨星）、年榜（总星标），并按人群分类。</p>
    </div>
    <div class="card">
      <h2>数据来源与更新</h2>
      <p>星标数据来自 GitHub REST API，每周由 GitHub Actions 自动更新；完整口径见仓库内的 <code>docs/methodology.md</code>。</p>
    </div>
    <div class="card">
      <h2>收录边界</h2>
      <p>只收录公开 GitHub 源码且能定位到 SKILL.md、插件入口或套件入口的项目；排除仅 MCP、纯宣传页、无法审阅源码的产品。</p>
    </div>
    <div class="card">
      <h2>核验与安全声明</h2>
      <p>每个条目带有核验日期，仅表示链接与描述经过人工检查，不构成对技能内容、安全性或质量的背书。安装第三方技能前请阅读其 README、许可证与权限说明。</p>
    </div>
  </main>
  <script src="assets/app.js"></script>
</body>
</html>
```

`site/data/.gitkeep`：空文件。

- [ ] **Step 6: 运行测试确认通过**

Run: `python -m pytest tests/test_site.py -q`

Expected: `4 passed`

- [ ] **Step 7: 提交**

```bash
git add tests/test_site.py site/
git commit -m "feat: 添加静态站页面与前端资源"
```

---

### Task 7: 候选发现 `discover.py`

**Files:**
- Create: `scripts/discover.py`

- [ ] **Step 1: 实现 `scripts/discover.py`**

```python
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
```

- [ ] **Step 2: 运行验证**

Run: `python scripts/discover.py`

Expected: 三条查询各打印 `OK ... candidates`，`data/candidates.json` 生成（已被 .gitignore 排除）。

- [ ] **Step 3: 提交**

```bash
git add scripts/discover.py
git commit -m "feat: 添加候选技能发现脚本"
```

---

### Task 8: GitHub Actions 自动更新

**Files:**
- Create: `.github/workflows/update-rankings.yml`

- [ ] **Step 1: 创建 `.github/workflows/update-rankings.yml`**

```yaml
name: update-rankings

on:
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Fetch stars
        run: python scripts/fetch_stars.py --token ${{ secrets.GITHUB_TOKEN }}
      - name: Generate rankings and README
        run: python scripts/generate_rankings.py
      - name: Validate data
        run: python scripts/validate_data.py --check
      - name: Run tests
        run: python -m pytest -q
      - name: Commit data updates
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/snapshots site/data README.md
          git commit -m "chore: 更新榜单数据 $(date -u +%Y-%m-%d)" || echo "无变更"
          git push
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: 检查 YAML 关键点**

确认：`cron` 为每周日 UTC 0 点；`permissions` 含 `contents: write` 和 `pages: write`；`fetch_stars.py` 传入 `--token`；deploy job 使用 `deploy-pages@v4`。

- [ ] **Step 3: 提交**

```bash
git add .github/workflows/update-rankings.yml
git commit -m "ci: 添加每周自动更新与 Pages 部署工作流"
```

---

### Task 9: 端到端验证

**Files:** 无新增（会生成 `data/snapshots/*.json`、`site/data/*.json`、`README.md`）

- [ ] **Step 1: 全量测试**

Run: `python -m pytest -q`

Expected: 全部通过（28 passed）。

- [ ] **Step 2: 校验数据**

Run: `python scripts/validate_data.py`

Expected: `OK: 12 skills validated`

- [ ] **Step 3: 抓取真实星标（匿名调用 GitHub API）**

Run: `python scripts/fetch_stars.py`

Expected: 每个仓库打印 `OK owner/repo: <数字>`，生成 `data/snapshots/2026-08-13.json`（以运行当天日期命名）。

- [ ] **Step 4: 生成榜单与 README**

Run: `python scripts/generate_rankings.py`

Expected: 打印类似 `{"updated_at": "2026-08-13", "weekly": 5, "monthly": 8, "yearly": 12}`；生成 `site/data/rankings.json`、`site/data/skills.json`、`README.md`。

- [ ] **Step 5: 再次全量测试**

Run: `python -m pytest -q`

Expected: 全部通过。

- [ ] **Step 6: 本地起服务验证页面**

PowerShell 执行：

```powershell
$server = Start-Process -FilePath python -ArgumentList '-m','http.server','8000' -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 2
Invoke-WebRequest -Uri 'http://localhost:8000/site/index.html' -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest -Uri 'http://localhost:8000/site/rankings.html' -UseBasicParsing | Select-Object StatusCode
Invoke-WebRequest -Uri 'http://localhost:8000/site/data/rankings.json' -UseBasicParsing | Select-Object StatusCode
Stop-Process -Id $server.Id
```

Expected: 三个请求都返回 `200`。

- [ ] **Step 7: 查看生成内容并提交**

Run: `git status`

Expected: 出现 `data/snapshots/2026-08-13.json`（运行当天日期）、`site/data/rankings.json`、`site/data/skills.json`、`README.md`（`data/errors.json`、`data/candidates.json` 被忽略）。

```bash
git add data/snapshots site/data README.md
git commit -m "chore: 初始化榜单数据与站点内容"
```

---

## 完成后检查单

- [ ] `python -m pytest -q` 全部通过
- [ ] `python scripts/validate_data.py` 输出 OK
- [ ] 本地 `http://localhost:8000/site/index.html` 三个页面 + JSON 均 200
- [ ] GitHub Pages 部署说明写入 `docs/methodology.md`（已包含）
- [ ] 后续扩充条目按 `CONTRIBUTING.md` 流程（改 `data/skills.json` → validate → 测试 → PR）
