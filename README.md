# Workskills

本仓库是一组本地协作 skills。真正给 Codex 使用的统一入口是：

- `workskills-router`
- 安装位置：`/Users/kim/.codex/skills/workskills-router`
- 源目录：`/Users/kim/code/workskills/workskills-router`

根 README 只给人快速浏览；不要把它当成 skill 入口。Codex 需要路由时应加载 `workskills-router/SKILL.md`，再由它按需加载下游 skill。

## 路由速查

| 场景 | 入口 |
|---|---|
| 不知道该用哪个 skill | `workskills-router` |
| 问题模糊、方案太多、需要先定义问题 | `problem-statement-card` |
| review、排查、复盘、画图、感觉不对劲 | `problem-review-mapper` |
| PRD/设计稿/LLM总结 需要先统一术语、concept、claim、drift | `canonical-claim-compiler` |
| Obsidian、业务域、`#业务`、`[[功能点]]`、知识写回 | `project-wiki` |
| 黑白灰、authority、Knowledge Pack、错知识退出 | `project-knowledge-curator` |
| 路书、canvas、长任务 Loop、子环、状态颜色同步 | `project-roadmap-board` |
| OpenSpec 后端 `tech_design.md`、库表、跨服务、架构评审 | `dq-be-core:dq-be-tech-design`（plugin，不在本仓库） |
| 快问快答、说人话、知识卡、决策卡 | `knowledge-card-qa` |

## 渐进式加载

默认流程：

```text
用户请求
  -> workskills-router
  -> 选择一个主 skill
  -> 只在触发时加载 reference / scripts / 配套 skill
```

不要一开始全读所有 skill。下游规则以各自 `SKILL.md` 为准。

## 目录

```text
workskills-router/             # 统一入口和智能路由
problem-statement-card/        # 问题定义
problem-review-mapper/         # 图优先 review / 排查 / 复盘
canonical-claim-compiler/      # PRD/自然语言 -> concept_id / claim_id / canonical / drift
project-wiki/                  # Obsidian Query / Ingest / Lint / SourceCheck
project-knowledge-curator/     # 黑白灰、authority、Knowledge Pack、Repair Loop
project-roadmap-board/         # Canvas 路书、长任务 Loop、状态事务
knowledge-card-qa/             # 快问快答 / 知识卡
```

## 安装

本机当前采用 symlink 安装，便于直接使用源目录更新：

```bash
ln -s /Users/kim/code/workskills/workskills-router /Users/kim/.codex/skills/workskills-router
```

其他 skill 也可按同样方式链接到 `/Users/kim/.codex/skills/<skill-name>`。新增或修改 skill 后，重启或新开 Codex 会话最稳。
