---
name: workskills-router
description: >-
  本地 workskills 的统一入口和智能路由。用户没有明确说用哪个 skill，
  但任务涉及问题定义、review/排查/复盘、PRD/自然语言到 concept/claim 编译、
  Obsidian 知识库、黑白灰知识治理、路书/canvas/长任务 Loop、
  OpenSpec 协作、快问快答/知识卡，或逻辑语法、真值条件、
  可说/展示边界校准时使用。
  本 skill 只做渐进式导读：先判断意图，选择并加载最小必要的下游 skill，
  避免一次性读取所有 workskills。
---

# Workskills Router

这是 `/Users/kim/code/workskills` 的唯一入口 skill。它不替代下游 skill，也不复制它们的规则；它只负责把用户请求路由到正确 skill，并控制上下文加载量。

## 核心规则

- 默认只选 **1 个主 skill**。
- 只有当主 skill 明确需要业务知识、路书、OpenSpec、卡片沉淀或引用校验时，才追加第二个 skill。
- 先读下游 skill 的 `SKILL.md`；只有触发到细节，才读 `references/*` 或运行 `scripts/*`。
- 不要一次性读取整个 `/Users/kim/code/workskills`。
- 对于多步链路、可见结果或用户表象需要校准的任务，先走 `stage-evidence-gate` 做跨语言证据门：记录用户现象，编译共通概念/claim，选择本轮证据面和停止条件。router 不硬编码实现侧语言；具体实现词只能在当前项目证据计划或示例里出现。
- 对于开放、不确定、低先例或跨域问题，不能把代码库当成封闭世界。先把外部成熟解法、官方能力边界、论文/开源实现、相邻产品做法编译成先验和候选机制；每条外部参考必须落到 `adopt / reject / pending`，并说明它改变哪个猜想、证据面或下一验。
- 对于任何症状或失败，先把"相关性"和"因果性"分开。大模型可以从许多相关代码里猜一个看似合理的改法，但代码修改必须建立在因果链上：先说明现象的直接机制、可观测预测和能区分猜想的证据面，再决定实现。手机过热时，火焰图只是证明"为什么 CPU/GPU 忙"的一种证据，不是所有性能问题的固定模板。
- 三类逻辑审计先做分流，不在 router 里实现规则：
  - `logical-grammar`：对象 / 关系 / 状态 / 动作能不能合法组合。
  - `truth-condition-checker`：claim / node / gate / decision 什么条件下为真或为假。
  - `say-show-boundary`：事实命题与价值、审美、愿景、偏好边界。
- 当用户前提不成立时，必须提示纠正：说明旧说法为什么不成立、当前证据支持什么、下一步如何改，不要只顺着用户继续执行。
- PRD、设计稿、LLM 总结或用户自然语言要进入 Obsidian / OpenSpec / roadmap 前，先判是否需要 `canonical-claim-compiler`：它负责把 lexical 表达编译成 stable concept / claim / pending / drift，下游只消费 accepted 身份和命题。
- 调度契约（discovery / fanout / subtask exec / pre-finish / skill authoring）见 `references/calibration-hooks.md`。本机 `context-compiler` 是该契约的一种实现，不是契约本身——换机器需重建本机实现，但契约和下游 skill 的"输入前置检查"段始终生效。这是 **router 判 + skill 自检** 双层冗余设计：接受重复，不接受逻辑失效。

## 四方对齐方法链

这套实践不是单个 E2E skill。`stage-evidence-gate` 只负责多步链路的证据门，其他环节分别由下游 skill 承担：

| 方法环节 | 典型问题 | 主 skill |
|---|---|---|
| 问题成形 | 我到底在解决什么、成功/失败信号是什么 | `problem-statement-card` |
| 概念对齐 | 这是不是同一个对象/claim，语义有没有漂移 | `canonical-claim-compiler` |
| 证据门 | 用户现象、共通概念和当前证据面是否互相解释 | `stage-evidence-gate` |
| 多猜想裁决 | 哪个解释领先、走弱、挂起，下一验是什么 | `problem-review-mapper` |
| 真值/边界 | 结论什么条件下为真，哪些只是价值/审美取向 | `truth-condition-checker` / `say-show-boundary` |
| 人话沉淀 | 本轮到底学到了什么，是否需要落卡 | `knowledge-card-qa` |

原则：先把用户现象改写成共通概念和可裁决 claim，再选择证据面；实现侧语言只能作为当前项目的证据投影，不能升级成通用方法准则。

## 快速路由

| 用户在问什么 | 主 skill | 追加条件 |
|---|---|---|
| 问题模糊、方案太多、不踏实、好不好用/好不好看 | `problem-statement-card` | 需要证据校准时加 `problem-review-mapper` |
| 开放/低先例/跨域问题、想看别人怎么做、需要外部参考或类似方案 | `problem-review-mapper`（先验 + 外部类比 + 证据态势图） | 需要沉淀到 Loop / OpenSpec 时按项目指南写 `adopt / reject / pending`；涉及业务知识真伪时加 `project-wiki` + `project-knowledge-curator` |
| 在多个方案里挑/排序、"哪个更好/选哪个/先做哪个/我喜欢哪个"、凭"什么好做"挑东西 | `decision-tripwire` | 标准立完要排序时加 `problem-statement-card`；要落卡时加 `knowledge-card-qa` |
| 甩来对话记录/一堆想法说"思路乱了/想法太多/帮我收敛"、反馈/候选（≥3）要收敛成一版范围、砍方案、（多人或一人不同时刻）各执一词 | `three-rulers` | 锁尺时加 `knowledge-card-qa`；单点取舍转 `decision-tripwire` |
| review、排查、复盘、归因、真因、为什么坏/为什么挂、线上 bug、排错、发热/卡顿/延迟、我感觉不对劲、画图、哪些对/不对 | `problem-review-mapper`（按贝叶斯排查表走） | 先区分相关代码与因果机制；为当前现象选择能区分猜想的证据面（过热可用火焰图/trace）；涉及业务知识真伪时加 `project-wiki` + `project-knowledge-curator` |
| 多步链路、可见结果或 E2E “过了但不知道证明了什么”，需要把用户表象语言翻译成共通概念和本轮证据面 | `stage-evidence-gate` | 根因不明或多猜想竞争时加 `problem-review-mapper`；术语/claim 漂移时先加 `canonical-claim-compiler`；要落 OpenSpec 时再按项目指南 |
| PRD、新需求、设计稿、LLM 总结、术语漂移、Obsidian/OpenSpec 同步、已有知识检索不到 | `canonical-claim-compiler` | 需要实际读写 vault 时加 `project-wiki`；需要 accept/merge/reject 时加 `project-knowledge-curator` |
| Obsidian、知识库、业务域、`#业务`、`[[功能点]]`、补文档、Knowledge Pack | `project-wiki` | 需要判能不能用时加 `project-knowledge-curator` |
| 黑白灰、authority、错知识退出、Conflict Verdict、Repair Loop | `project-knowledge-curator` | 需要实际查/写 vault 时加 `project-wiki` |
| 路书、canvas、进度板、长任务 Loop、子环、状态颜色同步 | `project-roadmap-board` | 涉及业务事实时加 `project-wiki` + `project-knowledge-curator` |
| OpenSpec、后端技术方案、库表/schema、跨服务、架构评审 | `dq-be-core:dq-be-tech-design`（plugin）或项目 `openspec/AGENTS.md` / `openspec-workflow` | 业务事实不清时加 `project-wiki`；执行图需要加 `project-roadmap-board` |
| 快问快答、说人话、知识卡、决策卡、是否落卡 | `knowledge-card-qa` | 先用对应取证 skill 得到证据，再压缩表达 |
| 对象/关系/状态/字段/任务拆分能不能这样连 | `logical-grammar` | 语法合法后再转 `truth-condition-checker` 或领域 skill |
| claim、gate、结论、验收口径是否成立，哪里矛盾，证伪/反向审查/怎么推翻这条链 | `truth-condition-checker` | 需要事实证据时加 `problem-review-mapper` / `project-knowledge-curator` |
| “好/坏/高级/自然/有趣/方向正确”等价值或审美判断 | `say-show-boundary` | 开放问题加 `problem-statement-card`；决策表达加 `knowledge-card-qa` |

## 贝叶斯排查口径（排查/归因类专用）

排查 = 在一堆猜想里用最少验证次数找真因。路由到 `problem-review-mapper` 后按**贝叶斯排查表**走，router 只立口径、不实现表：

- 原因不明 / 多猜想竞争 / 调研推进时，默认要求 `problem-review-mapper` 先画**证据态势图**：同图展示猜想、先验、诊断性证据、混杂、挂起调研和下一验。
- 先验不是只来自代码直觉。开放问题的先验必须显式吸收外部已知解法：官方能力边界、成熟相邻模式、跨域研究/开源实现、竞品/产品范式；外部参考只能改变猜想和实验设计，不能直接把本项目 gate 判绿。
- 材料很多但主要问题是顺序和阶段时，用**流程放射图**；单条 claim / gate / decision 是否成立时，转 `truth-condition-checker` 写真值条件和反向证伪。
- 每个猜想只能处于 `排除 / 走弱 / 挂起 / 领先 / 确认` 五态之一；决断 = 刷状态，不是"选一个答案"。
- 每次刷新状态必须写清「**这条证据只覆盖到哪一层**」——证据打到哪层只能排到哪层，禁止整包排除。
- `领先 ≠ 确认`：单样本 / 跨次方差大的领先不能拿去当根因改实现。
- 两个猜想下都会出现的证据，似然比 ≈ 1，不许更新判断（"查了半天等于没查"）。
- 症状类问题先找因果，不先写修复。相关性只能生成候选猜想，不能授权改代码。比如"手机过热"的第一层 claim 是 CPU/GPU/IO/日志/网络/渲染哪条路径繁忙；"加队列/降频/缓存"只是候选干预，必须等火焰图、trace、日志时间窗或其他可区分实验支持后才能成为实现动作。

图型、表、卡模板和猜想五态定义在 `problem-review-mapper`。

## Loop 方法论

Router 层的 Loop 只是一套**思考方法和协作风格**，不是某个项目的文件模板。它回答的是：用户怎么开始 loop，agent 每轮怎么内采/外采，怎么做决策，决策后怎么继续思考。具体项目里的 `STATE.md`、OpenSpec、E2E、知识卡、设备日志、业务 gate，交给项目 skill 或项目指南内化。

当用户说 loop、循环、长任务、路书、反复 E2E、"每轮怎么决策"、"怎么让 agent 自己持续推进"时，router 先判断这是哪种 loop：

- `开放策略 loop`：问题没现成局部答案，需要外部先验、能力边界、候选机制和 evidence gate。
- `症状排查 loop`：用户或运行结果报告发热、卡顿、延迟、坏图、失败日志等症状，需要先找因果机制。
- `批量探索 loop`：多个独立假设可以并行准备；必须先声明写入边界、共享资源、集成点和 verifier。
- `已知契约 loop`：目标和 gate 已定，只需要按状态文件重跑、验证、回写。

启动 loop 时，不要先派代码任务。先产出或补齐一个方法论入口：

| 项 | 需要写清 |
|---|---|
| Goal | 用户看见的目标现象，用用户语言写。 |
| Non-goals | 本 loop 不证明、不修改、不承诺的范围。 |
| State | 当前可信状态在哪里；具体载体由项目决定，不由 router 规定。 |
| Gates | 哪些 claim 可独立判定，什么条件绿/黄/红。 |
| Badcases | 哪些反例会推翻当前方向。 |
| Evidence | 哪些是 target、proxy、invalid、stale。 |
| Roles | implementer / verifier / human gate 谁能做什么，谁不能自证完成。 |
| Topology | 单线、批量探索、共享稀缺 oracle、还是人工 gate。 |

单轮 loop 按这个顺序走：

1. **锁一个问题**：本轮只处理一个 gate、badcase、claim 或假设，不把多个失败混成"继续优化"。
2. **信息内采**：从当前工作现场取证，包括用户原话、项目文档、代码、日志、测试、历史结论、知识卡、状态文件；标注证据新旧、target/proxy 边界和已失效上下文。
3. **信息外采**：把工作现场之外的材料纳入先验，包括用户在提示词里喂给 agent 的外部内容、官方能力边界、成熟相邻方案、论文、开源实现、竞品或产品范式。外采不等于上网搜索；用户提供的链接、摘录、截图、repo 名称、论文标题也算外部参考。每条外部参考必须落成 `adopt / reject / pending`，并说明它改变哪个先验、候选机制或下一验。
4. **贝叶斯/MoE 决策**：列候选机制、先验、可观测预测、反预测和最有信息增益的证据面；MoE 选择的是下一位专家/工具/worker/验证面，不是直接选一个看起来顺手的补丁。
5. **选择拓扑**：如果多个假设独立，允许批量探索；如果共享真机、生产环境、人工 reviewer、昂贵模型或其它稀缺 oracle，则只能并行准备，oracle 使用必须排队且 WIP 受限。
6. **决定下一动作**：只能是 `report-only update`、`evidence run`、`scoped implementation`、`independent verification`、`human handoff`、`pause/kill` 之一，并写明为什么其他动作暂时不合法。
7. **执行并记录**：每次运行或修改都要有 run_id/session_id/label；执行后分类 artifacts，追加 run log，更新 state。
8. **复盘再思考**：写清本轮淘汰了什么旧猜想、哪个先验变强/变弱、哪个知识卡/文档需要回写、下一轮唯一问题是什么。

可借鉴 `cobusgreyling/loop-engineering` 的运行骨架：L1 report-only 起步、持久状态、run log、readiness/audit、预算/kill switch、maker/checker 分离、必要时隔离工作区。router 只吸收这些作为 loop 方法，不把它们写死成项目模板。具体项目的权威事实、证据 gate、用户可见 claim 和因果链，必须由项目 skill 或项目文档承接。

拓扑选择的通用规则：

- 单线 loop：一个 gate、一个假设、一个证据面；适合回归和已知契约。
- 批量探索 loop：多个 worktree/worker 只能处理独立假设或独立证据面；必须有 owner、写入边界、kill 条件和集成点。
- 共享 oracle loop：当目标证据依赖真机、生产账号、人工评审、昂贵实验、远端环境等稀缺资源时，worktree 只并行做 preflight；oracle 访问必须排队，默认 WIP=1，除非项目 skill 明确记录更多资源。
- verifier lane 可以并行读证据，但不能改它正在验证的实现。
- 并行探索的产物只改变先验和候选机制；目标 gate 仍然只能由项目定义的 target evidence 关闭。

## 路由流程

```mermaid
flowchart TD
  A["用户请求"] --> A0{"是否 PRD/术语/claim/同步/drift?"}
  A0 -- "是" --> A1["加载 canonical-claim-compiler"]
  A1 --> A2["产出 concept/claim/pending/drift 后再选下游"]
  A2 --> B
  A0 -- "否" --> B{"是否模糊开放?"}
  B -- "是" --> C["加载 problem-statement-card"]
  B -- "否" --> B2{"是否多候选 / 想法收敛?"}
  B2 -- "是" --> B3["加载 three-rulers"]
  B2 -- "否" --> D{"是否 review/排查/复盘?"}
  D -- "是" --> E["加载 problem-review-mapper"]
  D -- "否" --> F{"是否知识库/Obsidian?"}
  F -- "是" --> G["加载 project-wiki"]
  G --> H{"是否需要判黑白灰/authority?"}
  H -- "是" --> I["追加 project-knowledge-curator"]
  F -- "否" --> J{"是否路书/长任务/canvas?"}
  J -- "是" --> K["加载 project-roadmap-board"]
  J -- "否" --> L{"是否 OpenSpec/后端设计?"}
  L -- "是" --> M["加载 dq-be-core:dq-be-tech-design 或读项目 OpenSpec 指南"]
  L -- "否" --> N{"是否逻辑校准?"}
  N -- "是" --> N0{"含价值/审美/愿景词?"}
  N0 -- "是" --> Q["加载 say-show-boundary 先剥层"]
  Q --> N1{"剥层后还有事实层?"}
  N1 -- "是" --> O["加载 logical-grammar"]
  N1 -- "否" --> Z["收口为取向/约束/可观察后果"]
  N0 -- "否" --> N2{"对象/关系/状态/字段问题?"}
  N2 -- "是" --> O
  N2 -- "否" --> P["加载 truth-condition-checker"]
  O --> P
  N -- "否" --> R{"是否快问快答/知识卡?"}
  R -- "是" --> S["加载 knowledge-card-qa"]
  R -- "否" --> T["不强行用 workskills，按普通任务处理"]
```

## 组合加载

### 复杂 review / 排查

1. 读 `problem-review-mapper/SKILL.md`
2. 如果图里的 claim 涉及业务知识真伪，读 `project-wiki/SKILL.md`
3. 如果要判白/灰/黑或旧知识退出，读 `project-knowledge-curator/SKILL.md`
4. 用户要“说人话/落卡”时，再读 `knowledge-card-qa/SKILL.md`

### 阶段证据门 / 多步链路验证

1. 读 `stage-evidence-gate/SKILL.md`
2. 先重写 goal：用户看见/期待的现象、共通概念/claim、本轮要校准的关系、停止条件
3. 先把用户表象语言翻译成共通概念，再决定需要哪些证据面；不能直接用实现侧词汇替代用户概念
4. 先说明每一步在方法论里的角色：它承接什么、改变什么、交给谁、什么现象会反驳它
5. 具体证据形式由当前 goal 或项目约定决定；router 不硬编码任何项目名、字段名、工具名或实现侧检查形式
6. 新证据进入前，先写清它会支持/反驳哪个概念或猜想；如果两种解释都会出现同一现象，就不更新判断
7. 原因不明或多猜想竞争复杂时追加 `problem-review-mapper`，用证据态势图刷新五态
8. 例子只能作为 example lens：允许抽取可迁移实践（阶段契约、追溯关系、反例、代理证据 vs 目标证据），禁止把鱼骨、视频帧、贴纸、某个业务链路等具体形状写成通用行为准则
9. 只有当前 goal 选定的证据面能互相解释，且用户可见目标 claim 被覆盖后，才允许说这条链路真的走对；缺失证据面必须标 gap，不能默认通过

### Obsidian 知识导读 / 写回

1. 如果输入是 PRD / 设计稿 / LLM 总结 / 术语漂移，先读 `canonical-claim-compiler/SKILL.md`
2. 读 `project-wiki/SKILL.md`
3. 结构问题才读 `project-wiki/references/vault-structure.md`
4. claim/span 引用校验才读 `project-wiki/references/obsidian-sourcecheck.md`
5. 三色治理才读 `project-knowledge-curator/SKILL.md`
6. Knowledge Pack 模板才读 `project-knowledge-curator/references/knowledge-pack-template.md`

Obsidian 知识身份顺序固定：

```text
业务域文件夹 -> #业务域 -> [[功能点]] -> claim_id/source_ref
```

`path + line` 只能做物理定位，不能当知识身份。

### PRD / identity / claim 编译

1. 读 `canonical-claim-compiler/SKILL.md`
2. 先输出 `pending_terms / pending_claims / accepted_concepts / accepted_claims / drift_report`
3. 需要查已有或写 vault 时追加 `project-wiki`
4. 需要 accept / merge / reject / supersede 时追加 `project-knowledge-curator`
5. 需要把 accepted claims 转成闭环工作块时追加 `project-roadmap-board`
6. 需要写后端 OpenSpec / 技术设计时，转 `dq-be-core:dq-be-tech-design`（plugin）、项目 `openspec/AGENTS.md` 或 `openspec-workflow`
7. 需要给用户做人话裁决时追加 `knowledge-card-qa`

固定边界：

- `canonical-claim-compiler` 不替人裁决 identity；它只提议。
- `project-wiki` 不裁决 claim 真伪；它只做 IO 和 SourceCheck。
- `project-knowledge-curator` 承接人或 owner 的裁决，把 identity / claim 进入三色治理。
- `project-roadmap-board` 只消费 accepted claims 和 Knowledge Pack，不从 raw PRD 直接升首环。

### 长任务 / 路书

1. 如果从 PRD / OpenSpec 材料池建板，先读 `canonical-claim-compiler/SKILL.md`
2. 读 `project-roadmap-board/SKILL.md`
3. 建板、审计、颜色传播细节才读 `project-roadmap-board/rules.md`
4. 需要画法示例才读 `project-roadmap-board/examples.md`
5. 生成/校验 `.canvas` 优先运行 `layout.py` / `audit.py`
6. 涉及业务事实时追加 `project-wiki` + `project-knowledge-curator`

每轮 Loop 必须先回写 `.canvas` 再继续派工；新增任务链先落 runtime group，开始处理再建子环，颜色、edge、group label/color 同批同步。

Loop 的决策门还必须区分两类输入：

- `外部先验门`：开放策略、低先例、跨域实现或 MoE 决策进入实现前，先记录 2-4 条外部参考及 `adopt / reject / pending`，把它们转成候选机制、证据面或下一验。
- `因果取证门`：用户报告任何失败症状时，下一动作先是把相关性候选转成因果假设，选择能区分这些假设的证据面；不能把"可能相关的代码位置"直接升级成修复方案。过热场景下，火焰图/trace 是常见证据面，因为它能回答 CPU/GPU 为什么忙。

### OpenSpec / 后端技术方案

1. 如果 OpenSpec 来自 PRD、设计稿或业务 claim，同步前先读 `canonical-claim-compiler/SKILL.md`
2. 后端 `tech_design.md` / 库表 / 跨服务 / 架构评审优先加载 `dq-be-core:dq-be-tech-design` plugin
3. 同时按当前项目的 `openspec/AGENTS.md` 或项目级 OpenSpec 指南执行；本仓库不再托管 `tech_design.md` 模板
4. 若两者冲突，优先级固定为：`dq-be-core:dq-be-tech-design` plugin → 项目 `openspec/AGENTS.md` → 通用 `openspec-workflow`
5. 业务事实不清时追加 `project-wiki` / `project-knowledge-curator`
6. 如果方案要转执行闭环，再追加 `project-roadmap-board`

OpenSpec / 技术设计是 change 的技术证据，不是业务知识库。

### 快问快答 / 知识卡

1. 先用实际任务 skill 取证、裁决或执行
2. 再读 `knowledge-card-qa/SKILL.md`

卡片不是权威源。Obsidian 知识卡必须能反查业务域、`#业务域`、`[[功能点]]`、`claim_id/source_ref`。

### 三类逻辑审计

1. 读 `logical-grammar/SKILL.md`：如果对象、关系、状态、动作没有成句，先改写，不进入真假验证。
2. 读 `truth-condition-checker/SKILL.md`：如果 claim / gate / decision 要成立，必须列出真值条件、证据、反例和矛盾。
3. 读 `say-show-boundary/SKILL.md`：如果用户或 agent 把价值、审美、愿景当事实说，先改写成取向、约束、可观察后果和代价。
4. 需要表达给用户时，追加 `knowledge-card-qa`；需要画证据链时，追加 `problem-review-mapper`；需要业务事实裁决时，追加 `project-knowledge-curator`。

纠正用户或 agent 前提时，用稳定句式：

```text
这里要纠正一下：<旧说法> 不成立。
当前证据支持的是 <新说法>。
后续按 <纠正动作> 走，<旧动作/旧说法> 不再作为默认上下文。
```

## 职责边界

| Skill | 负责 | 不负责 |
|---|---|---|
| `problem-statement-card` | 把开放问题压成可执行问题陈述 | 不替代取证、实现、知识治理 |
| `decision-tripwire` | 决策前拦一道：查起跳点（物本位 vs 目的本位）、逼出"赢的标准"节点、抓假互斥/串行化 | 不替用户拍板，不立完标准就替他排序 |
| `three-rulers` | 批量候选/想法收敛：原话留源→洞察升维→立尺→强度梯子/座位矩阵→裁决跟尺走→停车场 | 不替用户锁尺；尺锁定后的推导裁决由它填；单点取舍不归它管 |
| `problem-review-mapper` | 图优先 review / 排查 / 复盘 / 多证据收敛 | 不维护业务知识真源 |
| `stage-evidence-gate` | 把多步链路拆成用户现象、共通概念、证据面、反例和不确定性更新 | 不替代业务实现，不把具体例子或 happy path 当正确性证明 |
| `canonical-claim-compiler` | 把 PRD/自然语言编译成 concept_id、claim_id、pending、drift、claim_ref | 不直接实现，不替人裁决 identity，不直接写 vault |
| `project-wiki` | Obsidian Query / Ingest / Lint / SourceCheck 工具层 | 不裁决黑白灰，不替用户拍板 |
| `project-knowledge-curator` | 三色知识、authority、Knowledge Pack、Repair Loop | 不直接实现，不替代 vault IO |
| `project-roadmap-board` | Obsidian Canvas 路书、闭环工作块、Loop 状态事务 | 不托管业务事实 |
| `knowledge-card-qa` | 把已校验结论压成人话卡/决策卡 | 不制造新事实，不替代权威源 |
| `logical-grammar` | 判断对象/关系/状态/动作是否合法组合 | 不判断真假，不替代证据 |
| `truth-condition-checker` | 拆真值条件、找反例、找矛盾 | 不修语法错误，不处理纯价值判断 |
| `say-show-boundary` | 区分事实命题与价值/审美/愿景 | 不把偏好伪装成事实证据 |

## 反模式

- 用户没说业务域时直接写实现方案。
- 一开始把 `project-wiki`、`curator`、`roadmap`、OpenSpec 指南全读进来。
- PRD 还没编译 concept / claim，就直接写 Obsidian、OpenSpec 或 roadmap。
- 让 LLM 用同义词自由复述 accepted 术语，再指望 Obsidian 搜索自动理解。
- 把 Obsidian 的 `path + line` 当成知识身份，跳过业务域、`#业务域`、`[[功能点]]`。
- 把 SourceCheck `ok` 当成白知识。
- 把 roadmap 当 PRD 摘要或 agent Todo。
- 把快问快答卡片当权威文档。
- 发现错知识后只在聊天里修正，不让旧知识退出默认上下文。
- 对象关系还没成句就开始查真假。
- 把未知真值条件默认当真。
- 把价值、审美、愿景包装成“已验证事实”。
- 把代理证据当目标证据（某个测试、文件、链接或中间产物存在 → 当成用户可见结果真实正确）。
- 把粗猜想整包排除（"网络排除了""VLM 排除了""UI 没问题"——证据只打到一个子机制，却记成整包否掉）。
- 把 pending 当 fact（OpenSpec validate / runbook / harness green / fixture pass 只是某一层 ready，不是真值闭合）。
- 把代码库当封闭世界，在开放问题里不看外部成熟解法、官方能力边界或跨域参考，直接在本地参数里打转。
- 把相关性当因果性：用户给出症状后，agent 因为某段代码"看起来相关"就直接加队列、节流、缓存或重构，没有先证明这段机制确实导致现象。
- 把多个 worktree 或多个 agent 当成多个目标 oracle；共享真机、生产环境、人工 reviewer、昂贵实验时，没有队列和 WIP 限制就并行取证。
- 让同一个 worker 查现状 + 改实现 + 跑验证 + 写总结（证据面没有独立性，必然自证完成）。
- 把一个有效例子升级成固定方法，而不是只沉淀其中的可迁移实践。

## 入口口诀

```text
模糊先定问题；
PRD 先编 identity；
遇到分歧先分 drift；
语法不通先改句；
结论要写真值，证伪反着审一趟；
价值审美只 show 不伪装事实；
排查先画证据态势图，先刷猜想五态，说清证据覆盖到哪层；
多步链路先重写 goal：用户现象 -> 共通概念/claim -> 本轮证据面；
例子只抽可迁移实践，不把具体业务形状当通用规则；
具体验证语言由当前项目决定，不写进 router 准则；
讲顺序才用流程放射图；
知识先查 wiki；
能不能用交 curator；
长任务上 roadmap；
OpenSpec 读项目指南；
最后才压快问快答。
```
