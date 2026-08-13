# 方法与口径

## 榜单口径

- 周榜：近 7 天涨星（当前快照 − 7 天前快照）
- 月榜：近 30 天涨星（当前快照 − 30 天前快照）
- 年榜：总星标数
- 周榜/月榜剔除涨星为 0 或负数的条目；并列时按总星标再排序。
- 快照存于 `data/snapshots/YYYY-MM-DD.json`，每周追加，同日覆盖。

## 冷启动与回填

- 新项目没有历史快照，周榜/月榜在积累 1–4 周后逐步可用，年榜（总星标）始终可用。
- `fetch_stars.py` 会通过开源服务 star-history.dera.page 的 `repo-data` 接口回填 7 天前/30 天前的星标基线，生成对应日期的快照，因此周榜/月榜可在首次运行后即有数据。
- 如需手动导入历史数据，可直接添加一个 `data/snapshots/YYYY-MM-DD.json` 文件（格式见已有快照）。

## 收录边界

只收录公开 GitHub 源码且能定位到 SKILL.md / 插件入口 / 套件入口的项目。排除：仅 MCP、纯宣传页、无法审阅源码的产品、失效仓库。

## 更新流程

GitHub Actions 每周日 UTC 0 点自动运行：自动发现新技能 → 抓取星标 → 生成榜单与站点数据 → 校验 → 测试 → 提交 → 部署 Pages。推送 master 时也会自动部署一次（内容更新即时上线）；也可在 Actions 页面手动触发。

## 自动发现新技能

- 每周自动运行 `scripts/discover.py --auto-add`：按 `topic:agent-skills`、`topic:skills`、`topic:claude-skills` 搜索高星仓库，要求星标 ≥ 200、能定位到 SKILL.md（常见路径探测）、与现有清单去重，自动写入 `data/skills.json`。
- 自动收录的条目带 `auto` 标签；描述使用仓库原始说明，分类由关键词启发式推断，可能不如人工策展精确，欢迎通过 PR 精修。
- 排除 `awesome-` 开头等聚合目录类仓库（人工收录不受此限制）。

## 数据来源

- 当前星标：GitHub REST API（`GET /repos/{owner}/{repo}`）
- 历史回填：[star-history.dera.page](https://star-history.dera.page) 开源服务（`/repo-data?repos=...`），原 star-history 的替代实现
