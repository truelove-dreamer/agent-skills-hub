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
