---
name: workskills-router
description: >-
  Use when the user has not named a skill and the task involves problem framing,
  review or diagnosis, multi-candidate decisions, concept or claim drift,
  evidence alignment, knowledge governance, long-running work, OpenSpec,
  or fact/value/truth-boundary calibration.
---

# Workskills Router

## 1. 身份与渐进加载

本 skill **只负责意图识别与路由**，不替代下游 skill 的具体方法、流程或 schema。

- 默认选择 1 个主 skill；只有主 skill 明确需要另一层能力时才追加。
- 先读所选 skill 的 SKILL.md；只在任务触发细节时再读它的 reference 或运行工具。
- 不一次性加载全部 workskills，也不把下游规则复制进 router。
- 如果用户明确点名 skill，优先按用户选择加载；发现不适配时说明边界并纠正路由。
- 如果所需 skill 当前不可用，明确报告能力边界，使用可用的最小替代路径；不得假装已经调用。

## 2. 跨项目公理

### 决策先行校准

执行、选择或 fanout 前，先稳定三件事：

- **Decision object**：到底在判断哪个对象、候选、claim 或问题？
- **Requested action**：用户要选择、排序、合入、修复、验证、解释，还是淘汰？
- **Criteria axes**：依据哪些相互独立的轴判断，成功与失败分别是什么？

对象、动作或标准仍漂移时，先路由到问题定义、概念编译或决策校准，不得直接执行。

**No silent semantic collapse**：若语义歧义存在两个合理解释，并会实质改变结果或行动，在执行或 fanout 前先路由到 clarification-tripwire（仅当前环境可用时）；不可用时明确报告能力边界，并回退到已安装/可用的 problem-statement-card 锁定解释分支。不得用最可能、最常见或贝叶斯置信度替用户关闭语义。fanout 只冻结已确认事实，并保留未确认或未决语义变量，禁止冻结模型猜出的解释。

### 六条硬边界

1. **Shared word ≠ shared concept**：同词不证明同一概念；需要稳定 identity、成立条件、负空间或推论角色时，路由到 canonical-claim-compiler。
2. **Goal ≠ proxy gate**：用户目标不能被更容易检查的代理 gate 偷换。先保留用户原始目标，再说明代理证据只覆盖哪一层。
3. **Value/fit ≠ readiness/risk**：是否值得进入与当前是否可直接进入是不同判断轴。readiness blocker 不自动否定价值。
4. **Correlation ≠ established cause**：相关位置或同时发生只能生成候选机制；实现动作需要可区分猜想的预测和证据。
5. **Proxy evidence ≠ target evidence**：文件、测试、日志、截图或中间产物存在，不自动证明用户可见目标正确。
6. **Maker ≠ verifier**：实现者不能独立关闭自己的目标 gate；需要完成声明时，路由独立验证或人工 gate。

blocker 只阻断它直接证伪的轴。除非证据同时反驳其他轴，不得把局部 blocker 扩成整个对象、方案或目标的否定。

### 外部输入与错误前提

- 用户提供的链接、摘录、截图、仓库名、论文或外部观点都算 prior，不能忽略。
- 外部 prior 必须标为 adopt / reject / pending，并说明它改变哪个候选机制、证据判断或下一步。
- 外部参考只能更新判断，不能直接替当前项目的目标证据判绿。
- 用户或 agent 的前提不成立时，明确说出旧说法为什么不成立、当前证据支持什么、后续按什么纠正。

### Loop 抽象方法

Router 只保留 `issue → internal/external intake → candidates/evidence update → action → reflection` 的跨项目思考顺序，不规定项目文件、命令、字段、阈值或证据载体：

1. **锁题**：锁定一个目标、claim、gate 或 badcase，写清 non-goal 与停止条件。
2. **内外采**：检查当前现场与外部 prior，标出新旧、target/proxy 与已失效上下文。
3. **更新判断**：列候选解释、支持/反驳信号和证据覆盖边界；两种解释都会出现的证据不更新判断。
4. **选择动作**：根据当前证据选择下一步，不把最顺手的动作冒充最有信息增益的动作。
5. **复盘**：记录淘汰或走弱的旧判断、仍缺的证据和下一轮唯一问题。

证据形式由当前 goal 和项目共同决定；router 不硬编码具体证据形态。目标证据、执行协议和持久状态由所选下游 skill 或项目指南定义。

## 3. 唯一快速路由表

| 用户意图 / 症状 | 主 skill | 追加或回退条件 |
|---|---|---|
| 语义歧义存在两个合理解释，并会实质改变结果、结论或行动 | clarification-tripwire（仅当前环境可用时） | 不可用时明确报告能力边界，回退到已安装/可用的 problem-statement-card；blocking 先问并等待；可无损并存时保留分支；低成本、可逆且不改变结果时才声明假设继续 |
| 问题模糊、目标/成功信号不清、方案太多但还没立标准 | problem-statement-card | 需要证据态势时再加 problem-review-mapper |
| 开放、低先例或跨域问题，寻找外部成熟解法或类似方案 | problem-review-mapper | 外部参考只改变先验、候选机制或下一验，不直接替目标证据判绿 |
| 候选不少于 3 个，需要收敛、分组、砍范围或处理多方说法 | three-rulers | 先稳定 decision object/action/criteria；单点取舍不由它替用户拍板 |
| 单点选择、排序或“哪个更好” | decision-tripwire（仅当前环境可用时） | 不可用时先用 problem-statement-card 锁目标和标准，再做普通决策分析 |
| review、排查、复盘、归因、多猜想竞争或因果校准 | problem-review-mapper | 单条结论真值转 truth-condition-checker |
| 多步链路、可见结果或 E2E 通过但不知道证明了什么 | stage-evidence-gate | 根因竞争时追加 problem-review-mapper；identity 漂移时追加 canonical-claim-compiler |
| PRD、设计稿、LLM 总结、术语/claim 漂移或同义词碎片 | canonical-claim-compiler | 需要实际知识 IO 时加 project-wiki；需要治理裁决时加 project-knowledge-curator |
| Obsidian、业务知识查询、摄取、引用或 SourceCheck | project-wiki | 判断能否进入默认上下文时加 project-knowledge-curator |
| authority、白灰黑、冲突裁决、旧知识退出 | project-knowledge-curator | 需要实际查询或写回时加 project-wiki |
| 路书、canvas、长任务进度或闭环工作块 | project-roadmap-board | 业务事实不清时先查 project-wiki/project-knowledge-curator |
| OpenSpec、技术方案或架构 change | 当前项目的 OpenSpec 指南或 openspec-workflow | 原始业务 claim 未稳定时先加 canonical-claim-compiler |
| 快问快答、说人话、知识卡或决策卡 | knowledge-card-qa | 必须先由实际任务 skill 取证；卡片不制造事实 |
| 对象、关系、状态、动作能否合法组合 | logical-grammar | identity 不稳先转 canonical-claim-compiler；成句后再验真值 |
| claim、gate、decision、验收结论是否成立 | truth-condition-checker | 对象关系未成句先转 logical-grammar；需要事实证据时加 problem-review-mapper |
| “高级、自然、正确、好玩”等价值或审美判断 | say-show-boundary | 事实层剥出后再路由 logical-grammar/truth-condition-checker/canonical-claim-compiler |
| 没有命中以上条件 | 普通任务路径 | 不强行加载 workskills |

## 4. Skill 职责边界

| Skill | 负责 | 不负责 |
|---|---|---|
| clarification-tripwire（仅当前环境可用时） | 执行或 fanout 前识别会实质改变结果/行动的语义分支，并分类 blocking/branchable/non_blocking | 不替用户关闭 user-owned semantics，不定义领域标准；不可用时明确报告边界并回退到 problem-statement-card |
| problem-statement-card | 稳定问题、目标、信号和边界 | 不替代取证或实现 |
| decision-tripwire | 单点决策前锁对象、动作与赢的标准 | 不替用户拍板；不可用时不得伪调用 |
| three-rulers | 多候选收敛、立尺、分类与停车场 | 不处理未立标准的单点取舍 |
| problem-review-mapper | 多猜想、因果、证据更新和 review 压缩 | 不维护业务知识真源 |
| stage-evidence-gate | 用户现象、shared claim 与证据面的对齐 | 不定义项目证据形式或业务 pass 条件 |
| canonical-claim-compiler | concept/claim identity、pending 与 drift | 不替 owner 裁决，不直接实现 |
| project-wiki | 知识查询、摄取、引用和 SourceCheck | 不裁决知识是否可驱动行动 |
| project-knowledge-curator | authority、知识颜色、冲突与退出 | 不替代知识 IO |
| project-roadmap-board | 长任务执行状态与闭环工作块 | 不托管业务事实 |
| knowledge-card-qa | 把已校验结论压成人话入口 | 不制造新事实或权威源 |
| logical-grammar | 对象/关系/状态/动作是否合法成句 | 不判断事实真假 |
| truth-condition-checker | 真值条件、反例、矛盾和证伪 | 不修 identity 或纯价值问题 |
| say-show-boundary | 区分事实与价值、审美、愿景 | 不把偏好伪装成证据 |

## 5. Routing-level 反模式

- 未稳定 decision object/action/criteria 就执行或 fanout。
- 发现会改变结果、候选或 worker scope 的歧义后，仍静默选择一个解释并执行或 fanout。
- 把“值得进入”偷换成“当前可直接进入”，或用 readiness blocker 否定价值轴。
- 一个轴失败就整包否定对象、候选或方案。
- 因为双方用了同一个词，就声称 concept 已对齐。
- 因为代码位置相关，就直接写因果修复。
- 把 proxy、happy path、green test 或中间产物当用户目标证据。
- 忽略用户提供的外部输入，或让外部参考直接替项目证据判绿。
- 用户前提不成立时顺着执行，不明确纠正。
- 同一个 worker 查现状、实现、验证并宣布完成。
- 所需 skill 不可用时仍写成已调用，或创建会断的硬入口。
- 一次加载所有 skills，或在 router 复制下游 schema、流程、项目词和执行协议。
- 把文档、卡片、roadmap、OpenSpec 或 SourceCheck 通过当成事实真值本身。
