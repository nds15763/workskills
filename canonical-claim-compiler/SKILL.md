---
name: canonical-claim-compiler
description: >-
  Use when PRD、设计稿、用户表述、LLM 总结、Obsidian/OpenSpec 同步、
  术语漂移或“已有知识检索不到”需要先归一成 stable concept_id、
  claim_id、canonical term、pending 项、claim_ref 或 drift 分类。
---

# Canonical Claim Compiler

本 skill 是 PRD / 问题进入 Obsidian、OpenSpec、路书和快问快答之前的前置编译器。

它解决的不是“怎么写文档”，而是：

> 同一个对象、同一条断言，在人、PRD、LLM 和 Obsidian 里如何保持同一身份？

Obsidian 的优势是 lexical retrieval：`[[词元]]`、`#标签`、精确文本和文件路径。PRD 与 LLM 的优势是 semantic generation：同一概念可以被多种自然语言复述。两者直接同步会制造同义词碎片：搜“献毒”找不到“投毒”，LLM 上次写“诅咒者”这次写“女巫”，OpenSpec 又复述成第三种说法。

本 skill 的产物是 canonical identity layer：把自然语言先编译成稳定身份和可检验命题，再交给下游 skill。

## 先用场景

遇到以下输入，先用本 skill，再决定下游：

- 拿到 PRD、OpenSpec 草稿、产品说明、会议纪要、长对话总结。
- 用户说“已有知识检索不到”“LLM 每次换词”“Obsidian 同步”“术语不统一”。
- 要把 PRD 写入 Obsidian、OpenSpec、roadmap 或 Knowledge Pack。
- 要判断两个说法是不是同一个对象、同一条规则、同一条 claim。
- 要校准“分歧到底是真分歧，还是同一个 claim 的版本 drift”。

不要在这里直接写代码、直接改 OpenSpec、直接画路书、直接写 vault。这里输出的是身份、命题、pending、drift 和 claim_ref 草案；执行交给下游。

## 核心区分

| 层 | 问题 | 产物 |
|---|---|---|
| lexical | 这句话用了什么词？ | `canonical` / `aliases` / `not_same_as` |
| concept | 这是不是同一个对象？ | `concept_id` + `identity_condition` |
| proposition | 这条断言什么情况下为真？ | `claim_id` + `truth_condition` |
| status | 产品认不认、工程做到哪？ | `semantic_status` / `delivery_status` / `implementation_lifecycle` |
| source | 原始权威在哪、是否漂移？ | `source_ref` + revision / hash |

不要把 concept 和 claim 混在一张卡里。对象是命题的构成元素；命题是关于对象的断言。

## 现象到概念

用户最先给出的常常不是概念，而是现象：看见了什么、期待什么、哪里不对、哪些东西“应该相关”。这些现象可以启动编译，但不能直接当 canonical identity。

| 输入层 | 要做什么 | 不能做什么 |
|---|---|---|
| 用户现象 | 保留原话和可见例子，标出期待/困惑/反例 | 直接翻成实现名词或固定架构 |
| 共通概念 | 写 `identity_condition`、`not_same_as`、典型现象和反例 | 只用某个文件、字段、接口或工具名定义概念 |
| claim | 写 `truth_condition`、成立条件、失败方式 | 把“看起来相关”当成已经因果成立 |
| 证据投影 | 记录哪些权威源、运行结果或实现位置可验证 claim | 让证据投影反过来替代 concept/claim |

实现侧词汇只能进入 `source_ref`、`verified_by`、`delivery_depends_on` 或下游证据计划。它可以证明某个 claim 当前如何被交付，不能成为“人机共通概念”的第一身份。

## 三套枚举的关系

`kind`、`claim_type`、`knowledge_kind` 是三个正交轴，不互相替代：

| 字段 | 回答的问题 | 归属 |
|---|---|---|
| `kind` | 这个 concept / claim 的结构类型是什么 | canonical identity layer |
| `claim_type` | 这条知识在认识论上是什么：fact / rule / inference / value / taste / vision / decision | Curator 治理层 |
| `knowledge_kind` | 这条知识属于 PRD、约束还是架构 | Curator / Wiki 索引层 |

示例：

```yaml
kind: rule
claim_type: rule
knowledge_kind: prd
```

含义是：这是一条规则型 claim，它的认识论性质也是业务规则，并且来源/归属在 PRD 知识区。不要用 `claim_type=rule` 替代 `kind=rule`，也不要用 `knowledge_kind=prd` 判断它是否为真。

## 工作流 A：拿到 PRD

```text
source lock
  -> hit detect
  -> extract candidates
  -> canonicalize
  -> pending isolation
  -> human legislation
  -> accepted concept/claim set
  -> downstream write
```

1. **锁来源**：记录 PRD path、anchor、revision。没有 revision 的来源只能进 pending，不能进 accepted claim。
2. **查已有**：先用 Obsidian / project-wiki 查业务域、`[[功能点]]`、已有 concept / claim。不要凭相似词直接新建。
3. **抓候选**：从 PRD 句子里抽对象、动作、状态、关系、规则、事件、指标。只抽短句，不保留修饰性长句。
4. **分 concept / claim**：
   - concept：女巫、献毒、房间、ROUND_STARTED、扣血量。
   - claim：女巫每轮最多献毒一次、献毒目标必须是存活玩家。
5. **canonicalize**：已有就引用已有 `concept_id` / `claim_id`；找不到就进 pending，不直接落 accepted。
6. **人裁决**：accept / merge / reject / rename / supersede 只能由人或 owner 拍板。LLM 只提议。
7. **输出 accepted set**：下游只消费 accepted concept / claim；pending 不进 OpenSpec、路书锚点或白知识。

## 工作流 B：遇到问题或分歧

先把问题改写成 drift 分类，不要直接争对错：

| drift 类型 | 典型症状 | 下一步 |
|---|---|---|
| lexical drift | 同一个对象换词导致搜不到 | 补 alias，正文改 canonical |
| concept identity drift | 两个对象被混成一个，或一个对象被拆成多个 | 出 pending concept，交人裁决 |
| proposition drift | 同一 claim 的 truth condition 变了 | 更新 hash，触发下游 review |
| source drift | PRD revision 变了，claim 还指旧来源 | source_ref 失效检测 |
| status drift | accepted / implemented / verified 被混成一个状态 | 拆 semantic / delivery / lifecycle |
| implementation drift | 实现仍跑旧规则，但语义已 superseded | 标 implementation_lifecycle |
| phenomenon drift | 用户看到的现象、期待或失败信号变了 | 回到用户现象层，重新 claimize；不要只改实现投影 |

“他说的和我说的有没有分歧”要先 claimize：把双方断言列成 claim 表，再比较 claim_id、hash 和 asserted/unclaimed 状态。未表态是 `unclaimed`，不能当真，也不能当反对。

## 工作流 C：实现 task 反查 claim

收到实现任务时，不要只问“改哪个文件”。先问这次实现依赖哪些 accepted claims：

1. 把 task 拆成动作、对象、状态变化和验收口径。
2. 查已有 `claim_id` / `concept_id`，找不到的进 pending，不进入 Worker Pack baseline。
3. 为每个实现点列出 `claim_ref`：`id + local_truth_hash + closure_truth_hash`。
4. 如果 task 依赖 pending / disputed / superseded claim，先交 Curator 裁决；不能直接实现。
5. 只有 accepted claim + Knowledge Pack 都齐时，才交给 roadmap / Worker / OpenSpec。

输出：

```yaml
task_claim_refs:
  - {id: morph66.claim.witch.poison_once_per_round, local_truth_hash: sha256:..., closure_truth_hash: sha256:...}
blocked_by_pending:
  - morph66.claim.poison_target_scope
```

## 工作流 D：分歧校准

当两段话看起来冲突时，按 4 步做，不要直接选边：

1. **claimize**：把双方话语拆成最小 claim。
2. **type**：标注 `asserted / unclaimed / denied / superseded`；未说出的只能是 `unclaimed`。
3. **hash compare**：同 `claim_id` 比 `local_truth_hash` 与 `closure_truth_hash`；不同 id 先比 concept_refs 和 truth_condition。
4. **classify**：输出 lexical / concept identity / proposition / source / status / implementation drift。

只有 classification 出来后，才决定是补 alias、开 pending、更新 claim、修 OpenSpec、还是改实现。

## 工作流 E：design review 反向追 claim

review OpenSpec、tech design、proto 或方案文档时，从设计反推 claim：

1. 扫所有规则性自然语言，要求每段绑定 `claim_ref`。
2. 对每个 `claim_ref` 校验 `local_truth_hash` 和 `closure_truth_hash` 是否匹配当前 accepted claim。
3. 若自然语言与 `truth_condition` 不一致，标 semantic lint，输出差异理由，交人 review。
4. 若设计新增了 PRD 没有的对象/规则，生成 pending concept / pending claim。
5. 若 claim 已 superseded，但设计仍引用旧 hash，标 implementation / design drift。

设计文档可以写自然语言，但自然语言不能替代 claim_ref。

## Schema

## 命名规则

id 默认格式：

```text
<domain>.<kind>.<name>[.<qualifier>]
```

| 段 | 含义 |
|---|---|
| `domain` | 业务域或产品域，如 `morph66`、`gsc` |
| `kind` | 封闭枚举：`concept | state | action | rule | relation | event | metric` |
| `name` | 主对象或主断言名，使用稳定英文 token |
| `qualifier` | 可选限定词，如 `host`、`target`、`per_round` |

不要用实现服务名、文件名、页面名或 PRD 标题当第一身份。服务名可以进 `source_ref` 或 `delivery_depends_on`，不能替代业务 identity。

### concept 卡

```yaml
concept_id: morph66.action.poison
kind: action
canonical: 献毒
aliases:
  - 投毒
  - 下毒
  - poison
identity_condition: 女巫对目标玩家执行一次扣血动作
not_same_as:
  - {ref: morph66.state.poisoned, reason: kind=state}
  - {ref: morph66.event.damage_settlement, reason: kind=event}
semantic_status: accepted
source_ref:
  prd:
    - {path: prd/morph66/glossary.md, anchor: "#L10-L20", revision: d3a8c91}
concept_identity_hash: sha256:...
```

规则：

- `concept_id` 一旦 accepted，不改名；需要换身份时 deprecate + new id。
- `canonical` 是默认显示名，可以改，但要有 owner 签字和 migration record。
- `aliases` 吸收同义词；accepted 正文、OpenSpec 和路书里只用 canonical 或 id。
- `not_same_as` 必须带 reason，用来记录“长得像但不是同一个”的负空间。
- `kind` 必须封闭枚举：`concept | state | action | rule | relation | event | metric`。超出枚举先进 pending。

### claim 卡

```yaml
claim_id: morph66.claim.witch.poison_once_per_round
kind: rule
canonical: 女巫每轮最多献毒一次
truth_condition: 同一轮内，女巫最多只能成功执行一次献毒

concept_refs:
  - {id: morph66.role.witch, identity_hash: sha256:...}
  - {id: morph66.action.poison, identity_hash: sha256:...}

depends_on:
  - {id: morph66.claim.role.witch_exists, closure_truth_hash: sha256:...}
  - {id: morph66.claim.action.poison_defined, closure_truth_hash: sha256:...}

semantic_status: accepted
delivery_status: speced
implementation_lifecycle: active

supersedes: []
superseded_by: null

source_ref:
  prd:
    - {path: prd/morph66/rules.md, anchor: "#L42-L58", revision: d3a8c91}

verified_by: []
local_truth_hash: sha256:...
closure_truth_hash: sha256:...
```

规则：

- `concept_refs` 是这条 claim 提到了哪些对象，只能指 concept。
- `depends_on` 是这条 claim 的真成立依赖哪些其他 claim，只能指 claim。
- 工程依赖不要塞进 `depends_on`；另写 `delivery_depends_on`。
- `semantic_status`: `proposed | accepted | disputed | superseded`。
- `delivery_status`: `not_speced | speced | implemented | verified`。
- `implementation_lifecycle`: `active | deprecated | removed`。
- `superseded` 必须有 `superseded_by`；继任 claim 可写 `supersedes`。
- `proposed` 可以改 id；`accepted` 之后 id 不改，只能 supersede。

## Hash 规则

hash 只锁同一性和真值条件，不锁项目管理元数据。

```yaml
concept_identity_hash: sha256(canonical_serialize({
  kind,
  identity_condition,
  not_same_as: [{ref, reason}, ...]
}))

local_truth_hash: sha256(canonical_serialize({
  kind,
  truth_condition,
  concept_refs: [{id, identity_hash}, ...]
}))

closure_truth_hash: sha256(canonical_serialize({
  local_truth_hash,
  depends_on: [{id, closure_truth_hash}, ...]
}))
```

要求：

- `concept_refs` 必须带对应 concept 的 `identity_hash`，否则 concept 重新定义时 claim 不会漂移。
- `depends_on` 必须带被依赖 claim 的 `closure_truth_hash`，否则底层前提变更时上游 claim 不会漂移。
- `canonical / aliases / source_ref / status / lifecycle / verified_by` 不进 truth hash。
- pending / proposed 阶段不冻结 hash，可用 `pending:<draft_id>`；生产 OpenSpec 不允许引用 pending claim。
- 序列化必须 deterministic，优先用 RFC 8785 JCS 或等价 canonical JSON。
- claim dependency 必须是 DAG；出现环时先拆 claim，不要用工程兜底绕过。

## Concept Evolution Layer

前面 schema 是静态身份快照。这一层把 concept/claim 变成**有时间厚度的演进实体**——记版本、记双向费曼融合、记硬核/保护带、记 drift 累积、记决策反向索引、记推论角色。

### 为什么需要这一层

静态 concept 卡解决"是不是同一个对象"。演进层解决"两周后为什么还在原点"——同一概念反复被讨论但没收敛。根因是概念没有被当成**随时间演进的实体**，每次对话都从零对齐。

### 哲学资源对应

| 字段/层 | 哲学资源 | 解决什么 |
|---|---|---|
| 时间厚度（retention/primal/protention） | Husserl 内时间意识 + Heidegger 此在时间性 | 知道概念"经过迭代" |
| fusion_record | Gadamer 视域融合 | 双向费曼记录——双方都可能变，不是单向对齐 |
| hard_core / protective_belt | Lakatos 研究纲领 | fork 判据——硬核变才是 fork |
| drift_state + crisis 阈值 | Kuhn 反常/危机/范式革命 | 什么时候真要 fork，避免每次 drift 都打断 |
| sense.inferential_role | Brandom 推论主义（主轴）| 飘移判定——推论角色公开可观察，不循环论证 |
| landing | 操作主义 | 客观落地层，机器 grep 即可 |
| affects_decisions | Quine 整体论 | 决策反向回溯——单个概念不能单独判，放信念网里 |
| stability_score | 综合 | 演进曲线 y 轴，随时间收敛的双曲线 |

### 时间厚度（Husserl + Heidegger）

每个 concept/claim 必须版本化：

```
concepts/<claim_id>/
  v1.md
  v2.md
  ...
  lineage.md  # 谱系图：v1→v2→v3→(v3a, v3b)
```

每次对话提到 concept，主 agent 必须做三件事，不直接说"我懂"：

| 时间层 | 含义 | 字段 |
|---|---|---|
| retention | 继承自哪 | `parent_version` / `based_on_transcript` |
| primal | 当前用法属于哪版 | `matches_version` / `drift_signal` |
| protention | 预期下次怎么用 | `expected_usage` / `open_questions` |

### 视域融合（Gadamer）

版本 bump 不记"谁纠正谁"，记**融合产物**——双向费曼的本质是视域融合，产出双方之前都没有的新视域：

```yaml
fusion_record:
  user_horizon: "用户脑中的逻辑图像（原话片段）"
  ai_horizon: "AI 脑中的逻辑图像（原话片段）"
  fused_horizon: "融合后的新视域（新版本定义）"
  fusion_type: mutual | user_refines_ai | ai_refines_user | external
```

`mutual` 最常见；承认双方都可能变。只有 `user_refines_ai` 或 `ai_refines_user` 时才是单向纠正。

### 硬核 vs 保护带（Lakatos）

每个 concept 版本必须声明两部分：

```yaml
hard_core:  # 不可变，变了就是 fork
  - "属于 viewpoint 维度"
  - "基于 headPose.pitch"

protective_belt:  # 可调，变了是版本演进
  - "pitch 阈值 30°（可调）"
  - "命名 head_up（可调）"
```

判 fork 判据：`hard_core` 变了 = fork（split / merge / supersede / reject）；`protective_belt` 变了 = 版本演进。不靠感觉。

### Drift 累积与危机阈值（Kuhn）

drift 不是错误，是反常信号。累积到危机才需要范式检讨：

```yaml
drift_state:
  anomaly_count: 0
  crisis_threshold: 3
  state: normal | anomaly | crisis | revolution
  anomalies:
    - {ts, session_id, drift_type, signal, transcript_ref}
  last_action: null  # crisis 时填 paradigm_review / fork / redefine / reject
```

| state | anomaly_count | 动作 |
|---|---|---|
| normal | 0 | 无 |
| anomaly | 1 ~ crisis_threshold-1 | 记下来，不处理 |
| crisis | >= crisis_threshold | 触发 problem-review-mapper 范式检讨 |
| revolution | crisis 后 | 决定 fork / redefine / reject |

裁决后 `anomaly_count` 清零，state 回 normal。这避免每次 drift 都打断对话——反常是正常的，累积到危机才处理。

### 推论角色（Brandom 主轴）

判飘移最硬的层，因为推论角色是**公开可观察的**（决策是公开的），不依赖 AI 主观语义判断（循环论证风险）。

每个 concept/claim 版本的 sense 必须声明推论角色：

```yaml
sense:
  sign: "head_up"  # 指称（Frege signifier）
  referent: "headPose.pitch > 30°"  # 事物（Frege reference）
  inferential_role:  # 逻辑（Frege sense / Brandom 推论角色）
    upstream_inferences:
      - "headPose.pitch 测量值 > 30° → head_up 成立"
    downstream_inferences:
      - "head_up 成立 → 样本进 viewpoint bucket"
      - "head_up 成立 → 不计入 action bucket"
```

判飘移 = 重跑推论链。不需要 AI 凭语义判断"用法是否一致"，只需把旧决策拿出来按新版本 `upstream_inferences` / `downstream_inferences` 重跑一遍，看结论变不变。

### 客观落地（机器可验证）

```yaml
landing:
  code_landed: false
  code_refs: []
  doc_landed: true
  doc_refs: ["docs/viewpoint.md#head-up"]
  spec_refs: []
```

主 agent 跑 grep 即可判定，不需要 AI 判断。`code_landed=false` 就是没收敛的客观证据。

### 决策反向索引（Quine 整体论）

每个 concept 版本必须带 `affects_decisions`，反向索引到引用它的决策（gate green / commit / spec）：

```yaml
affects_decisions:
  - decision_id: G3_unknown_cat_recording
    verdict_at_decision: green
    sense_used: v3a
    needs_recheck: false  # concept 版本变化时由 workskills-router Step C 重跑推论链更新
```

概念版本变化时，扫描所有引用旧版本的决策，按新 sense 重跑推论链：
- 旧决策在新版本下还成立 → `ok`
- 不成立 → `needs_recheck`
- 判不了 → `ambiguous`（必须人工复检）

**不自动降级 green → yellow，只标 needs_recheck**。因为概念变不等于旧决策错——可能旧决策其实用的是新 sense，只是当时没区分清楚。必须重跑逻辑链才能确定。

### Stability Score

```text
stability_score = f(landing, drift_state, decisions_valid) ∈ [0, 1]

- code_landed + doc_landed + spec_refs 都齐 → +0.4
- drift_state.state == normal 且 anomaly_count == 0 → +0.3
- 所有 affects_decisions.needs_recheck == false → +0.3
```

精准 = 1.0；过程态在 [0, 1)。这是演进曲线的 y 轴，随时间收敛的双曲线。

### 演进版完整 schema

在原 concept 卡基础上扩展（向后兼容）：

```yaml
concept_id: mewt.viewpoint.head_up
version: v3a
parent: v3
fork_type: split  # split | merge | supersede | reject

# 时间厚度
created_at: 2026-07-09
based_on_transcript: session_X
retention_from: v3

# 指称/事物/逻辑三元 + 推论角色
sense:
  sign: "head_up"
  referent: "headPose.pitch > 30°"
  inferential_role:
    upstream_inferences: ["headPose.pitch > 30° → head_up"]
    downstream_inferences: ["head_up → 样本进 viewpoint bucket"]

# 硬核 vs 保护带
hard_core:
  - "属于 viewpoint 维度"
  - "基于 headPose.pitch"
protective_belt:
  - "pitch 阈值 30°（可调）"
  - "命名 head_up（可调）"

# 视域融合
fusion_record:
  user_horizon: "用户原话片段"
  ai_horizon: "AI 原话片段"
  fused_horizon: "融合后定义"
  fusion_type: mutual

# 漂移状态
drift_state:
  anomaly_count: 0
  crisis_threshold: 3
  state: normal
  anomalies: []
  last_action: null

# 客观落地
landing:
  code_landed: false
  code_refs: []
  doc_landed: true
  doc_refs: ["docs/viewpoint.md#head-up"]
  spec_refs: []

# 决策反向索引
affects_decisions:
  - decision_id: G3_unknown_cat_recording
    verdict_at_decision: green
    sense_used: v3a
    needs_recheck: false

# 综合分数
stability_score: 0.45
```

### 哲学外因的诚实局限

| 哲学资源 | 软在哪 |
|---|---|
| Gadamer 视域融合 | 依赖对话双方诚实记录，无法强校验 fusion_record 内容真实性 |
| Kuhn crisis 阈值 | 默认 3 是经验值，需调；不同概念可能阈值不同 |
| Brandom 推论角色 | 重跑推论链有成本；复杂决策链可能跑不动 |
| Quine 整体论 | 决策网络越大，回溯扫描越贵 |

**硬在哪**：landing（机器 grep）、inferential_role（公开决策）、hard_core（明确 fork 判据）这三层不依赖主观判断。

### 反模式（演进层专属）

- 用 LLM 凭语义判"用法是否一致"——循环论证，AI 是当事人
- 每次 drift 都立刻 fork 或 redefine——Kuhn 反常是正常的，累积到危机才处理
- 概念版本变了自动降级所有引用旧版本的决策 green → yellow——必须重跑推论链，可能旧决策其实用的是新 sense
- fusion_record 只记 `user_refines_ai`——双向费曼是视域融合，承认双方都可能变
- 把 discriminator 写成纯文本而不带 `upstream_inferences` / `downstream_inferences`——推论角色是判飘主轴，必须结构化
- stability_score = 1.0 但 code_landed = false——客观落地是硬指标，没落地不能满分

## Scripts / CLI

随本 skill 提供 `scripts/claim-hash.py`，是 hash 算法的参考实现，也是 drift 检测器的底座。

### 用法

```bash
# Dry-run: 算单个文件 hash，print 到 stdout（不写回）
python3 scripts/claim-hash.py <vault>/_glossary/concepts/morph66.action.poison.yml

# 写回单个文件
python3 scripts/claim-hash.py <vault>/_glossary/concepts/morph66.action.poison.yml --update

# 批量算所有：先 concepts/, 再 claims/（拓扑顺序）
python3 scripts/claim-hash.py --all <vault>/_glossary --update

# 校验所有 hash 是否 drift（CI 用）
python3 scripts/claim-hash.py --all <vault>/_glossary --verify
# exit 0 = 全部 clean
# exit 1 = 至少一处 drift
# exit 2 = schema 缺字段
# exit 3 = I/O 错误
```

### 行为

- 自动跳过 `semantic_status: proposed` 或 `pending`（hash 不冻结）
- claim 的 `concept_refs` 必须带 `identity_hash`（缺则 ERR）—— 先跑 concept hash
- claim 的 `depends_on` 必须带 `closure_truth_hash`（缺则 ERR）—— 拓扑顺序：被依赖 claim 先算
- 出现环 → 报错 `DAG required: no cycles`
- 算法近似 RFC 8785 JCS：sorted keys / no whitespace / utf-8 / sha256

### CI 集成

最小用法（在 narnia-docs-kim 仓库的 CI 里）：

```yaml
- name: claim-hash drift check
  run: |
    python3 path/to/claim-hash.py --all _glossary --verify
```

drift 时 CI 失败，触发 review PR 由人裁决"实现还成不成立"。

## OpenSpec 输出

OpenSpec 可以保留自然语言，但必须绑定 claim_ref：

```yaml
claim_ref:
  id: morph66.claim.witch.poison_once_per_round
  local_truth_hash: sha256:...
  closure_truth_hash: sha256:...
```

自然语言用于人读，`claim_ref` 用于机器锁定。两者不一致时，LLM semantic lint 只能 block review 并输出差异理由；不能作为 hard CI 的唯一判死依据。hard lint 只处理确定性规则：schema、引用存在、hash mismatch、pending 引用、DAG、accepted id 改名。

## 输出物

按任务需要输出最小集合：

- `pending_terms`: 找不到 canonical 或疑似同义/近义的词。
- `pending_claims`: LLM 从 PRD 抽出但未被人 accepted 的 claim。
- `accepted_concepts`: 可写入 Obsidian / OpenSpec / roadmap 的 concept。
- `accepted_claims`: 可作为 white candidate / OpenSpec claim_ref / roadmap 锚点的 claim。
- `drift_report`: drift 类型、触发字段、影响下游、需要谁裁决。
- `claim_ref_skeleton`: OpenSpec 可引用的 `id + local_truth_hash + closure_truth_hash`。
- `writeback_checklist`: 需要交给 project-wiki / curator / roadmap / OpenSpec 的下游动作。

## 下游路由

| 下一步 | 交给 |
|---|---|
| 搜已有、写 Obsidian、SourceCheck | `project-wiki` |
| accept / merge / reject / supersede、三色治理 | `project-knowledge-curator` |
| 把 accepted claims 编译成闭环工作块 | `project-roadmap-board` |
| 写 OpenSpec / 技术设计 | `dq-be-core:dq-be-tech-design`（plugin）/ 项目 `openspec/AGENTS.md` / `openspec-workflow` |
| 把裁决压成人话卡 | `knowledge-card-qa` |
| 逻辑成句、真值条件、价值边界 | `logical-grammar` / `truth-condition-checker` / `say-show-boundary` |

## 反模式

- 直接把 PRD 里的自然语言写成 Obsidian 正文或 OpenSpec 规则，跳过 concept / claim。
- 把 alias 当 canonical 使用，或允许 LLM 在 accepted 正文里随意换词。
- 把 `path + line` 当知识身份；它只是物理定位。
- 把 SourceCheck `ok` 当成 claim 为真；它只证明引用对得上。
- 把 `accepted`、`implemented`、`verified` 塞进一个 status。
- 把 `concept_refs` 和 `depends_on` 写成同一批 id。
- 把工程依赖、测试文件、实现目录塞进 truth hash。
- 把 `unclaimed` 当 `true`、`false` 或“默认同意”。
- 用 LLM 自动决定两个 concept / claim 是不是同一个。

## 入口口诀

```text
拿到 PRD，先锁来源；
看到名词，先找身份；
看到句子，拆成 claim；
找不到的，进 pending；
能不能同一，只能人裁；
accepted 以后，再写 wiki / openspec / roadmap；
遇到分歧，先看 hash，再谈观点。
```
