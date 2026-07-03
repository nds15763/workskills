# Workskills

本仓库是一组本地协作 skills。真正给 Codex 使用的统一入口是：

- `workskills-router`
- 安装位置：`/Users/kim/.codex/skills/workskills-router`
- 源目录：`/Users/kim/code/workskills/workskills-router`

根 README 只给人快速浏览；不要把它当成 skill 入口。Codex 需要路由时应加载 `workskills-router/SKILL.md`，再由它按需加载下游 skill。

## 方法链

整体实践不是一个 E2E skill：`problem-statement-card` 定问题，`canonical-claim-compiler` 对齐概念/claim，`stage-evidence-gate` 做跨语言证据门，`problem-review-mapper` 做多猜想裁决，`truth-condition-checker` / `say-show-boundary` 拆真值和边界，`knowledge-card-qa` 做人话沉淀。

## 路由速查

| 场景 | 入口 |
|---|---|
| 不知道该用哪个 skill | `workskills-router` |
| 问题模糊、方案太多、需要先定义问题 | `problem-statement-card` |
| 在多个方案里挑/排序、"哪个更好/先做哪个/我喜欢/X好做" | `decision-tripwire` |
| 思路乱了/想法太多/对话记录要收敛成一版范围、砍方案、各执一词 | `three-rulers` |
| review、排查、复盘、归因、真因、多猜想竞争、画证据态势图 | `problem-review-mapper` |
| 多步链路或 E2E 结果需要说明“到底证明了什么”，用户表象语言要对齐到共通概念和本轮证据面 | `stage-evidence-gate` |
| PRD/设计稿/LLM总结 需要先统一术语、concept、claim、drift | `canonical-claim-compiler` |
| Obsidian、业务域、`#业务`、`[[功能点]]`、知识写回 | `project-wiki` |
| 黑白灰、authority、Knowledge Pack、错知识退出 | `project-knowledge-curator` |
| 路书、canvas、长任务 Loop、子环、状态颜色同步 | `project-roadmap-board` |
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

## 关键图型

| 图型 | 用在什么时候 | 入口 |
|---|---|---|
| 证据态势图 | 原因不明、多猜想竞争、需要看证据如何更新判断 | `problem-review-mapper` |
| 流程放射图 | 材料很多但主要问题是顺序、阶段和细节挂载 | `problem-review-mapper` |
| 真值依赖图 | 单条 claim / gate / decision 是否成立、需要反向证伪 | `truth-condition-checker` |
| roadmap runtime group | 长任务、挂起调研、执行闭环和状态颜色推进 | `project-roadmap-board` |

## 目录

```text
workskills-router/             # 统一入口和智能路由
problem-statement-card/        # 问题定义
decision-tripwire/             # 决策起跳点警报器:物本位 vs 目的本位,逼出"赢的标准"
three-rulers/                  # 三把尺:批量候选收敛,摊牌→立尺→过筛→停车场
problem-review-mapper/         # 图优先 review / 排查 / 复盘；判断态势用证据态势图，讲顺序用流程放射图
stage-evidence-gate/           # 多步链路证据门：用户现象->共通概念/claim->本轮证据面，区分目标证据、代理证据和缺口
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
