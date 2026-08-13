# Agent Skills Hub 设计文档

- 日期：2026-08-13
- 状态：已确认（等待用户审阅）
- 仓库名：`agent-skills-hub`
- 目录：当前工作区 `suitable-skill`（本地目录名保持不变，GitHub 仓库名使用 `agent-skills-hub`）

## 1. 背景与目标

GitHub 上出现了越来越多以 `SKILL.md` 为入口的 AI 智能体技能包（供 Codex、Claude、ChatGPT 等 Agent 使用），但缺少一个集中的、带热度排行的整理入口。本项目旨在：

1. 收录 GitHub 上热门的 SKILL.md 技能包，提供跳转链接和一句话功能说明。
2. 提供周榜（近 7 天涨星）、月榜（近 30 天涨星）、年榜（总星标）三种排行。
3. 按“什么样的人需要什么样的 skill”进行领域/人群分类。
4. 通过静态站 + 定时数据管道实现低维护、自动更新的展示。
5. 吸收现有同类项目的优秀做法，做出定位清晰、可机器校验、可持续维护的差异化项目。

## 2. 范围

### 包含

- 人工策展的候选 skill 列表（`data/skills.json`）。
- 收录边界与核验规则（见第 5 节），以及自动校验脚本。
- 自动抓取星标数据并计算榜单的 Python 脚本。
- 纯静态展示站点（GitHub Pages 托管）。
- GitHub Actions 每周定时更新。
- 社区协作入口（`CONTRIBUTING.md`）+ 方法论文档。

### 不包含（初版）

- 用户账号、收藏、评论等后端功能。
- 对 skill 内容的深度评测（仅一句话功能说明）。
- 自动把任意 GitHub 仓库纳入榜单（收录需人工审核，脚本只做候选推荐）。
- 仅提供 MCP、无 `SKILL.md`/Skill 入口、或无法审阅源码的产品（见收录边界）。

## 3. 竞品分析与经验借鉴

调研了现存同类项目，提炼出以下值得借鉴的做法：

| 项目 | 值得借鉴的做法 | 本项目如何吸收 |
| --- | --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | 官方 SKILL.md 规范：frontmatter 只需 `name` + `description` | 校验时以 frontmatter 合法性作为收录硬门槛之一 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | “手选而非 AI 生成”、徽章（技能数/最后更新）、标注平台兼容 | README 加徽章；条目增加 `platforms` 字段 |
| [cosen1024/awesome-academic-skills](https://github.com/cosen1024/awesome-academic-skills) | 单一数据源 + 脚本渲染/校验；固定版本链接；核验日期；方法论文档；明确收录边界 | `skills.json` 唯一事实源；条目增加 `entry`/`verified_at`/`license`；增加 `docs/methodology.md` 与 `docs/candidates.md` |
| [wind8ai/skills-top-stars](https://github.com/wind8ai/skills-top-stars) | 按星标做高星精选，附星数/Fork/更新时间 | 榜单页展示星标、涨星、更新时间等元数据 |
| [philipbankier/awesome-agent-skills](https://github.com/philipbankier/awesome-agent-skills) | 跨平台目录组织（Agent Skills / MCP / Rules 分层） | 分类与平台兼容分开维护，避免混在一起 |

### 采用的核心原则

1. **数据驱动展示**：README 表格和站点数据都由脚本从 `data/skills.json` 生成，贡献者不手改展示层。
2. **可追溯**：每个条目提供固定版本（pin commit SHA）的 Skill 入口链接，避免 `main` 分支内容漂移。
3. **可核验**：每条目记录 `verified_at` 核验日期，README/关于页声明“核验≠安全背书”。
4. **边界明确**：只收公开 GitHub 源码且能定位到 `SKILL.md` 或 Skill 套件入口的项目；排除仅 MCP、纯宣传页、无法审阅源码的产品。
5. **安全提示**：安装前提示阅读许可证、权限与数据上传说明。
6. **透明口径**：榜单快照与计算方法公开在 `docs/methodology.md` 和关于页。

## 4. 技术选型

| 项 | 选择 | 理由 |
| --- | --- | --- |
| 站点 | 纯 HTML/CSS/JS，无构建步骤 | 零依赖、Pages 友好、易维护 |
| 数据管道 | Python 3 + 标准库 + `requests` | 脚本简单，易在 Actions 中运行 |
| 星标数据 | GitHub REST API + star-history 回填 | GitHub API 拿当前星标；star-history 回填历史，解决冷启动 |
| 定时更新 | GitHub Actions（cron，每周日 UTC 0 点） | 免费、仓库内闭环 |
| 托管 | GitHub Pages（从 `site/` 发布） | 免费、和仓库同源 |
| 测试 | pytest + JSON schema 校验 | 榜单计算与数据质量可回归验证 |

## 5. 收录边界

### 可收录

- 公开 GitHub 仓库，能从源码定位到 `SKILL.md`（含 `name`/`description` frontmatter）、插件入口或 Skill 套件入口。
- 有明确功能描述，能写出中文一句话说明。
- 官方团队发布或社区维护、有实际使用价值的技能包。

### 不可收录

- 仅提供 MCP server、无 Skill 入口的仓库。
- 无法审阅源码的产品/宣传页。
- 普通工具库或教程（不含 `SKILL.md`）。
- 失效、归档、长期无维护且无法核验的仓库。

核验动作与排除理由记录在 `docs/candidates.md`。

## 6. 仓库结构

```text
agent-skills-hub/
├── README.md                    # 项目说明 + 徽章 + 最新榜单摘要（脚本生成）
├── CONTRIBUTING.md              # 如何新增/更新 skill + 安全提示
├── docs/
│   ├── methodology.md           # 榜单口径、收录边界、更新流程
│   └── candidates.md            # 待审核候选与排除项记录
├── data/
│   ├── skills.json              # 主数据：skill 元数据（人工策展，唯一事实源）
│   ├── categories.json          # 分类字典
│   └── snapshots/               # 每周星标快照（脚本生成）
├── scripts/
│   ├── fetch_stars.py           # 拉取当前星标 + 写快照 + 回填历史
│   ├── generate_rankings.py     # 计算周/月/年榜，生成站点 JSON 与 README 表格
│   ├── validate_data.py         # 校验 schema、分类取值、收录边界
│   └── discover.py              # 辅助：GitHub 搜索候选 skill（人工审核）
├── site/
│   ├── index.html               # 首页：总览 + 周榜 Top 10
│   ├── rankings.html            # 榜单页（周/月/年 tab）
│   ├── categories.html          # 分类页（“我是谁 → 推荐”）
│   ├── about.html               # 关于/口径/数据来源
│   ├── assets/                  # CSS/JS
│   └── data/                    # 脚本生成的 rankings.json / skills.json（站点数据）
├── tests/
│   ├── test_rankings.py         # 榜单计算与排序测试
│   └── test_schema.py           # skills.json schema 校验
└── .github/workflows/
    └── update-rankings.yml      # 每周定时更新 + 部署 Pages
```

## 7. 数据模型

### 7.1 `data/skills.json`（人工维护）

```json
{
  "schema_version": 1,
  "updated_at": "2026-08-13",
  "skills": [
    {
      "id": "anthropics-skills",
      "name": "anthropics/skills",
      "repo": "https://github.com/anthropics/skills",
      "entry": "https://github.com/anthropics/skills/blob/<commit-sha>/skills/docx/SKILL.md",
      "description": "Anthropic 官方技能集合，覆盖文档撰写、代码分析等场景",
      "categories": ["developer", "writer"],
      "platforms": ["claude-code", "codex", "cursor"],
      "license": "Apache-2.0",
      "verified_at": "2026-08-13",
      "tags": ["document", "coding"],
      "added_at": "2026-08-13",
      "note": "（可选）人工补充的备注"
    }
  ]
}
```

字段约束：

- `id`：唯一，小写连字符。
- `repo`：GitHub 仓库完整 URL，作为跳转链接和 API 查询依据。
- `entry`：固定版本（pin commit SHA）的 SKILL.md / Skill 套件入口链接，保证可追溯。
- `categories`：至少 1 个，取值限定在分类字典内（见第 9 节）。
- `platforms`：兼容的 Agent 平台列表（枚举：`claude-code`、`codex`、`cursor`、`gemini-cli`、`copilot`、`windsurf`、`opencode` 等）。
- `license`：仓库许可证（人工填或脚本核验后补）。
- `verified_at`：人工核验日期；核验动作记录到 `docs/candidates.md`。
- `description`：一句话中文功能说明。
- 星标、涨星等动态数据**不**写入此文件，由脚本按快照计算。

### 7.2 星标快照 `data/snapshots/YYYY-MM-DD.json`

```json
{
  "date": "2026-08-13",
  "repos": {
    "anthropics/skills": 12345,
    "...": 0
  }
}
```

脚本每次运行追加一个快照文件，作为周/月涨星计算的依据，也便于审计。

## 8. 榜单口径

- 周榜：按最近 7 天涨星数降序（当前快照 − 最近可用的 7 天前快照）。
- 月榜：按最近 30 天涨星数降序（当前快照 − 最近可用的 30 天前快照）。
- 年榜：按总星标数降序。
- 涨星为 0 或负数的条目：周榜/月榜不展示，年榜正常展示。
- 快照不足 7 天时，用最早可用快照近似；完全无历史时该榜暂缺，年榜始终可用。
- 口径说明同步写入 `docs/methodology.md` 与站点关于页。

## 9. 分类体系

初版 9 个分类，每个分类对应“什么样的人需要”：

| 分类 key | 中文名 | 面向人群 |
| --- | --- | --- |
| `developer` | 开发 | 程序员：代码、调试、重构、测试 |
| `data-analyst` | 数据分析 | 数据分析师/研究者：SQL、统计、可视化 |
| `designer` | 设计 | 设计师：UI/UX、图片、视频、3D |
| `writer` | 写作/文档 | 技术写作、文档、翻译 |
| `product` | 产品/管理 | 产品经理、项目经理：PRD、需求分析 |
| `devops` | 运维 | 运维/DevOps：部署、监控、安全 |
| `marketing` | 营销/内容 | 运营、市场：内容创作、SEO、社媒 |
| `research` | 研究/学习 | 学生、研究者：文献、学习辅助 |
| `productivity` | 通用效率 | 所有人：日常办公、自动化 |

分类字典统一维护在 `data/categories.json`（脚本生成站点时引用），避免各条目自造分类。

## 10. 静态站设计

- 纯静态，无框架；页面通过 `fetch('data/rankings.json')` 和 `data/skills.json` 渲染。
- 中文界面，skill 名称保留英文原名，跳转链接指向原仓库（榜单链接优先指向固定版本 `entry`）。
- 页面：
  - 首页：项目简介、周榜 Top 10 表格、技能总数与最后更新徽章、最新更新时间。
  - 榜单页：周/月/年三个 tab，显示排名、名称、类别、涨星数/总星、平台兼容标签、简介、链接。
  - 分类页：先选“我是谁”（9 类之一或多选），再展示该类 skill 卡片列表。
  - 关于页：说明数据来源、更新频率、榜单口径、收录边界与如何贡献；含“核验≠安全背书”声明。
- 排名名次并列时按总星数再排序；分页或展示上限（如每榜 Top 50）由 `generate_rankings.py` 配置。

## 11. 自动数据管道

### 11.1 `fetch_stars.py`

1. 读取 `data/skills.json`，得到仓库列表（`owner/repo`）。
2. 优先用 `GITHUB_TOKEN`/`GH_TOKEN` 调 GitHub REST API（`GET /repos/{owner}/{repo}`）取当前星标；未配置 token 时降级为匿名调用（限流 60 次/小时）。
3. 将当前星标写入当日快照 `data/snapshots/YYYY-MM-DD.json`。
4. 冷启动回填：当历史快照不足时，调用 star-history 接口拉取历史星标序列，回填缺失日期（只用于计算 7/30 天增量，不逐日写文件）。
5. 单仓库失败（404/改名/限流）只记录到 `data/errors.json`，不中断整体运行。

### 11.2 `generate_rankings.py`

1. 读取最新快照与历史快照，按第 8 节口径计算三个榜单。
2. 合并 `skills.json` 的元数据（名称、简介、链接、分类、平台）。
3. 输出 `site/data/rankings.json`（含三个榜单 + 更新时间）和 `site/data/skills.json`（站点用精简版）。
4. 渲染 README 榜单摘要与徽章（数据驱动，不手改生成表格）。

### 11.3 `validate_data.py`

- 校验 `skills.json` 的 schema、分类取值、id 唯一性、`entry` 是否指向固定 commit。
- 抽查 `SKILL.md` 可达性（网络可用时），输出核验报告到 `docs/candidates.md`。
- 供本地和 Actions 在提交/合并前运行（`--check` 模式）。

### 11.4 `discover.py`（辅助）

- 用 GitHub 搜索 API 按 `filename:SKILL.md`、`topic:skills`、`topic:agent-skills` 等条件搜候选仓库，输出“待审核”清单。
- 只产生建议，不自动收录；收录动作是人工修改 `data/skills.json` 并提交 PR。

### 11.5 GitHub Actions（`update-rankings.yml`）

- 触发：`schedule: cron 0 0 * * 0`（每周日 UTC 0 点）+ 手动触发（workflow_dispatch）。
- 步骤：检出 → 装 Python 依赖 → 运行 `fetch_stars.py` + `generate_rankings.py` + `validate_data.py --check` → 跑测试 → 提交数据变更 → 部署 Pages。
- 使用仓库自带 `GITHUB_TOKEN` 调 API（限流 1000 次/小时，满足百级仓库规模）。

## 12. 数据流

```text
data/skills.json（人工，唯一事实源） ─┐
GitHub API / star-history ────────────┤→ fetch_stars.py → 快照 → generate_rankings.py → site/data/*.json → 静态站
                                     └───────────────────────────────────────────────────────┘
validate_data.py 把关数据质量；GitHub Actions 每周自动执行；README 与 Pages 同步更新
```

## 13. 错误处理

- API 限流：检测 `403`/`429`，指数退避；token 缺失时提示并提供降级。
- 单仓库失败：写入 `data/errors.json`，榜单跳过该条目，下次运行重试。
- 脚本幂等：重复运行不产生重复快照（同日快照覆盖）；数据文件不因中途失败被清空。
- Actions 失败：保留上次成功数据，站点继续可用；失败时在 commit message 或 issue 中留痕。

## 14. 测试

- `tests/test_rankings.py`：构造快照序列，验证 7/30 天增量、年榜排序、并列处理、负增长剔除。
- `tests/test_schema.py`：校验 `skills.json` 字段、分类取值、id 唯一性、`entry` 格式。
- 本地验证：直接打开 `site/index.html` 检查渲染；脚本以 `--dry-run` 支持不落盘试跑。

## 15. 协作流程

- `CONTRIBUTING.md` 说明：新增 skill = 修改 `data/skills.json`（附简介、分类、入口、核验日期）并运行 `validate_data.py` 后提交 PR；分类调整需先改分类字典。
- 数据文件与生成表格分开：贡献者只改 `data/skills.json`，README/站点表格由脚本重新生成，避免手工编辑冲突。
- 候选与排除记录在 `docs/candidates.md`，口径疑问看 `docs/methodology.md`。
- README 提供链接跳转 GitHub Issue，便于不会改代码的人提交建议。
- 安全提示：README/CONTRIBUTING 声明“核验≠安全背书”，安装第三方 skill 前阅读许可证、权限与数据上传说明。

## 16. 部署

- 仓库设置中启用 GitHub Pages，发布源选择 GitHub Actions（由 workflow 部署 `site/`）。
- 域名：初版用默认 `https://<owner>.github.io/agent-skills-hub/`，后续可配自定义域名。

## 17. 初版里程碑

1. 脚手架：目录结构、`skills.json` 样例（首批约 30 个技能）、`categories.json`、空站点骨架。
2. 校验与渲染：`validate_data.py` + README 生成逻辑 + 测试通过。
3. 管道：`fetch_stars.py` + `generate_rankings.py` + 测试通过。
4. 站点：四个页面完成渲染，本地可打开。
5. 自动化：Actions workflow 跑通，Pages 上线。
6. 内容：收录边界与分类定稿，首批技能逐条补齐简介并核验。
