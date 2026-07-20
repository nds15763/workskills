# Workskills

本仓库是一组本地协作 skills。真正给 agent 使用的统一入口是：

- `workskills-router`
- 安装位置：`/Users/kim/.codex/skills/workskills-router`（软链到本仓库）
- 源目录：`/Users/kim/code/workskills/workskills-router`

根 README 只给人快速浏览；不要把它当成 skill 入口。agent 需要路由时应加载 `workskills-router/SKILL.md`，再由它按需加载下游 skill。

## 方法链

整体实践不是一个 E2E skill：`clarification-tripwire` 处理会改变结果的语义歧义并独占中断协议，`problem-statement-card` 定问题，`canonical-claim-compiler` 对齐概念/claim，`stage-evidence-gate` 做跨语言证据门，`problem-review-mapper` 做多猜想裁决；仅在时序 / 系统指标或依赖图诊断需要候选因果结构、混杂校准、区分性 probe 或有界排查优先级时，才由它下游调用 `causal-evidence-rca` 产出专项证据。`truth-condition-checker` / `say-show-boundary` 拆真值和边界，`knowledge-card-qa` 做人话沉淀。

## Clarification Tripwire 中断协议

`clarification-tripwire` 是 STOP / 恢复协议的唯一权威；`workskills-router` 与 calibration hooks 只负责检测、调用并服从它，不复制协议。

本机 `/Users/kim/.codex/AGENTS.md` 另有全局强制入口：发现 material semantic ambiguity 时必须加载并服从该 skill。它只保证调用不会被跳过，不取代仓库中的协议真源。

- **打断时刻**：两个合理解释会实质改变候选、标准、worker scope、写入/外部影响或最终结论时，在第一次语义承诺前打断；不得先淘汰候选、调用工具、fanout、写入或给出单一结论。
- **STOP 动作**：冻结上述动作，只问一个会改变决策的最小问题，然后结束当前回合并等待。
- **恢复条件**：只有用户选择某个解释、明确授权双轴/分支输出，或明确把选择权委托给 agent，才恢复执行；恢复后的语义契约必须进入直接执行和 worker prompts。
- **查询边界**：STOP 前只允许有限只读查询来消除事实指代；查询和贝叶斯置信度不能替用户决定意图、价值、权限或优化目标。

## 概念收敛

防止"两周后还在原点"——同一概念反复被讨论但不收敛。概念演进由 `canonical-claim-compiler` 承载，router 只负责在需要时路由：

- `canonical-claim-compiler` 的 **Concept Evolution Layer** 负责演进版 schema：版本化 + 时间厚度（Husserl）+ 视域融合（Gadamer）+ 硬核/保护带（Lakatos）+ drift 累积（Kuhn）+ 推论角色（Brandom 主轴）+ 客观落地 + 决策反向索引（Quine）+ stability_score

演进曲线作为人的主观视角：漂的就是风险点，收敛的就是稳定点，不用读卡内容。

## 路由速查

| 场景 | 入口 |
|---|---|
| 不知道该用哪个 skill | `workskills-router` |
| 语义歧义会改变结果、结论、候选或行动；需要 STOP / 提问 / 恢复 | `clarification-tripwire` |
| 问题模糊、方案太多、需要先定义问题 | `problem-statement-card` |
| 在多个方案里挑/排序、"哪个更好/先做哪个/我喜欢/X好做" | `decision-tripwire` |
| 思路乱了/想法太多/对话记录要收敛成一版范围、砍方案、各执一词 | `three-rulers` |
| review、排查、复盘、归因、真因、多猜想竞争、画证据态势图 | `problem-review-mapper` |
| 时序 / 系统指标或依赖图诊断，需要候选因果结构、混杂校准、区分性 probe 或有界排查优先级 | `problem-review-mapper` → `causal-evidence-rca`（专项证据；不单独确认根因） |
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
clarification-tripwire/        # 语义歧义断路器；独占 STOP / 冻结 / 提问 / 恢复协议
problem-statement-card/        # 问题定义
decision-tripwire/             # 决策起跳点警报器:物本位 vs 目的本位,逼出"赢的标准"
three-rulers/                  # 三把尺:批量候选收敛,摊牌→立尺→过筛→停车场
problem-review-mapper/         # 图优先 review / 排查 / 复盘；判断态势用证据态势图，讲顺序用流程放射图
causal-evidence-rca/           # problem-review-mapper 的可选下游专项证据生产器：时序 / 系统指标或依赖图的因果 RCA；不定义 Router 或项目证据政策
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
ln -s /Users/kim/code/workskills/clarification-tripwire /Users/kim/.codex/skills/clarification-tripwire
```

其他 skill 也可按同样方式链接到 `/Users/kim/.codex/skills/<skill-name>`。新增或修改 skill 后，重启或新开 Codex 会话最稳。
