---
name: project-knowledge-curator
description: >-
  管理业务域 Obsidian 文档的读取、authority 分级、Knowledge Pack 输出、
  Conflict Verdict、Knowledge Repair Record、README 索引维护、
  obsidian-cli 优先读取和错知识降权/归档。
  当用户提到业务域、知识库、Obsidian、文档驱动、知识校准、
  README 索引、双链、补文档、修知识、错知识收敛时使用。
---

> **公理继承 / Axiom Inheritance**
> 本 skill 服从顶层公理 `typed evidence gates action`——
> 未经类型化（三色 + authority + kind）的上下文不允许驱动行动。
> 在该公理下，本 skill 的职能：给业务域知识打类型（三色 + authority + kind），错知识降权归档

# Project Knowledge Curator

执行位置：仓库根目录。

## 核心目标

这不是一个“帮忙写几篇文档”的 skill，而是一个**知识校准器**：

- 所有 Code 必须先由 Docs 驱动
- 先确认业务域，再读 docs
- 先索引，再放进默认上下文
- 先做 authority 分级，再给 Worker 用
- 发现错知识时，让它退出默认上下文

## Canonical Paths
- Obsidian仓库： `/Users/kim/code/narnia/narnia-docs-kim`
- Skill 入口：`skills/project-knowledge-curator/SKILL.md`
- 读写合同：`skills/project-knowledge-curator/references/read-write-contract.md`
- Knowledge Pack 模板：`skills/project-knowledge-curator/references/knowledge-pack-template.md`
- 三色知识沉淀模板：`skills/project-knowledge-curator/references/tricolor-knowledge-settlement-template.md`
- Conflict Verdict 模板：`skills/project-knowledge-curator/references/conflict-verdict-template.md`
- Repair / Discard 策略：`skills/project-knowledge-curator/references/repair-discard-policy.md`
- 配套主 skill：`skills/project-roadmap-board/SKILL.md`

## 运行时输入

每次使用本 skill 都必须先明确：

- `docs_root`
- `vault` 或等价知识库入口
- `business_domain`
- `feature_point`
- `authoritative_roots`

如果用户没有明确给出 `business_domain`，先问用户，不要直接开始大规模读码。

如果当前任务没有相关 `[[功能点]]` 或业务域文档，先和用户确认是否需要补收集业务域知识，再进入设计或代码执行。

## 读取顺序

固定顺序：

1. `rg/grep` 业务域 README 与 `[[功能点]]`
2. `obsidian-cli`
3. MCP 兜底

只要前一步已经拿到足够事实，就不要继续扩大上下文。

## 可插拔子能力

`Knowledge Curator` 不是只在“明确写 docs”时才运行。它默认包含 3 个可插拔子能力：

- `knowledge-hit-detect`
  - 判断当前对话、设计、实现、排障是否命中已有知识
  - 输出：
    - `no_hit`
    - `hit_readonly`
    - `hit_writeback_required`
- `knowledge-curate`
  - 真正做知识分类、三色收敛、索引吸收、叶子 note 合并和 writeback
- `knowledge-link-audit`
  - 检查 `README.md`、`knowledge/README.md`、`[[功能点]]` 和叶子知识 note 的双链是否断裂
  - 输出：
    - `ok`
    - `missing_wikilink`
    - `missing_index`
    - `orphan_note`

固定触发规则：

- 进入设计、实现、排障前，先触发一次 `knowledge-hit-detect`
- 对话形成 durable knowledge、代码变更完成、spec 变化、Exception 产生后，再触发一次 `knowledge-hit-detect`
- 若结果是 `hit_writeback_required`，必须进入 `knowledge-curate`
- 每次 Curator writeback 前后都要跑 `knowledge-link-audit`
- 发现断链时，即使没有新知识，也必须先修复索引或双链

## Docs-Driven 规则

- 所有代码工作都必须先经过 `Docs Read`
- 没有相关业务域和 `[[功能点]]` 时，不能直接把假设写成方案或代码
- 业务域必须以文档库中的文件夹形式组织
- 每个业务域目录下固定建立 `knowledge/` 子文件夹，业务知识默认写入 `<business_domain>/knowledge/`
- 每个业务域的 `knowledge/README.md` 必须吸收所有 durable knowledge 的索引入口，不等待用户提醒
- 业务域文档标题或副标题必须带有可检索的业务域标签，例如 `#用户`
- 功能新增、功能修改、或首次进入一个从未治理过的业务域时，必须补 `[[功能点]]` 双链
- 文档写回必须保证后续可以通过业务域标签和 `[[功能点]]` 搜到
- Knowledge Curator 必须主动判断是否应该压缩、合并、整理已有知识，不要等用户提醒
- 当已有 note、README、双链足够承载新结论时，优先更新和合并，避免继续平铺新 note

## authority 分级

- `A.authoritative`
- `B.supporting`
- `C.evidence`
- `D.stale/legacy`

默认 `Knowledge Pack` 只收：

- 所有 `A`
- 与当前功能点直接相关的 `B`

`C` 只能被引用，不能整份塞进上下文。`D` 默认不进入上下文。

## 三色知识分层

authority 分级描述“证据强度”，三色分层描述“默认使用策略”。两者并存，不能互相替代。

- `white knowledge`
  - 已确认有效的默认基线
  - 可以进入默认 `Knowledge Pack`
  - 允许沉淀为 `locked facts`
- `gray knowledge`
  - 待确权或经验性知识
  - 只能按需进入 `Knowledge Pack`
  - 可以参考，但不能直接提升为 `locked facts`
- `black knowledge`
  - 已弃用、已归档或明确不应继续暴露的知识
  - 默认不进入执行上下文
  - 不能被 Worker 或 Runner 当作可用依据

固定规则：

- 新产生的知识默认进入 `gray knowledge`
- `gray knowledge` 只有在当前任务、双链、反链或人工明确点名命中时，才允许进入 advisory 上下文
- `black knowledge` 不删除，只隔离；恢复时必须先回到 `gray knowledge`，不能直接恢复为 `white knowledge`
- `white knowledge` 是默认基线，但不代表它永远正确；发生冲突时仍要走 `Conflict Verdict` 和 `Repair Loop`

## 知识双轴模型

三色描述“默认使用策略”，知识类别描述“这条知识是什么”。两者正交，必须同时存在。

- `knowledge_kind`
  - `prd`
    - 功能目标、业务规则、用户流、验收口径
  - `constraint`
    - 必须遵守的规则、门闩、流程限制、禁止事项、环境约束
  - `architecture`
    - 模块边界、数据流、对象模型、控制面和集成关系
- `knowledge_color`
  - `white`
  - `gray`
  - `black`
- `authority_level`
  - `A.authoritative`
  - `B.supporting`
  - `C.evidence`
  - `D.stale/legacy`

固定规则：

- 每条 durable knowledge 都必须同时带有 `knowledge_kind`、`knowledge_color` 和 `authority_level`
- `knowledge_kind` 不是目录结构；业务域仍然是第一层目录
- `knowledge/README.md` 必须固定分为 `PRD知识`、`约束知识`、`架构知识`
- 每个知识类别内部再按 `白知识`、`灰知识`、`黑知识` 组织索引
- `main-phase` 的 PRD / OpenSpec 若仍为当前有效真源，优先作为 `white knowledge` 的 canonical source 被索引

## 输出物

### Knowledge Pack

给主 Agent 和 Worker 的最小知识上下文，字段固定为：

- 业务域
- 功能点
- authoritative sources
- baseline sources（白知识）
- advisory sources（按需命中的灰知识）
- blocked sources（黑知识或本轮禁用知识）
- locked facts
- open conflicts
- stale sources to ignore
- writeback targets

### Knowledge Hit Detection

给 Main Agent 和 Worker 的知识命中判断结果，字段固定为：

- `knowledge_hit_status`
  - `no_hit`
  - `hit_readonly`
  - `hit_writeback_required`
- `matched_business_domain`
- `matched_feature_points`
- `matched_sources`
  - `path`
  - `knowledge_kind`
  - `knowledge_color`
  - `authority_level`
  - `business_domain`
  - `feature_point`
- `selected_knowledge_color`（white / gray / black；`no_hit` 时为空）
- `selected_authority_level`（A / B / C / D；`no_hit` 时为空）
- `writeback_reason`

### Knowledge Link Audit

用于检查业务域知识结构是否健康，字段固定为：

- `link_health`
  - `ok`
  - `missing_wikilink`
  - `missing_index`
  - `orphan_note`
- `findings`
- `repair_targets`

`baseline/advisory/blocked` 中的每一条 source 都必须带：

- `path`
- `knowledge_kind`
- `knowledge_color`
- `authority_level`
- `feature_point`
- `business_domain`

### Conflict Verdict

状态固定为：

- `aligned`
- `missing`
- `conflicting`
- `stale`
- `superseded`

### Knowledge Repair Record

用于记录错知识如何退出默认上下文，以及谁接替成为真源。

### Tri-Color Knowledge Settlement

用于把一次会话、一次执行或一次争议收敛成白 / 灰 / 黑知识，而不是直接保存原始对话转录。

## 回写规则

- 所有文档使用中文
- 使用 Obsidian 友好 Markdown
- 当文件名已经承担标题作用时，正文不要再重复写同名 `# H1`
- 业务域以文件夹组织
- 每个业务域必须有一个 `README.md` 根索引
- 每个业务域必须有一个 `knowledge/README.md` 知识索引
- `knowledge/README.md` 固定只维护三类一级索引：
  - `PRD知识`
  - `约束知识`
  - `架构知识`
- 每个一级索引内部固定维护三类颜色分区：
  - `白知识`
  - `灰知识`
  - `黑知识`
- 功能新增或修改时，补 `[[功能点]]`
- 业务域文档需要带有对应的 `#业务域` 标签
- 代码落点格式固定为：
  - `功能名 符号名 @filename#L{start}-L{end}`
- 工具函数默认不作为业务知识落点记录，除非用户明确要求
- 写回时优先更新业务域 README 与 `[[功能点]]` 叶子文档，再补充关联结论
- 若已有真源文档能够承载结论，优先在 `knowledge/README.md` 中索引该真源，不重复抄写正文
- 若发现 `[[功能点]]`、`knowledge/README.md` 或叶子知识 note 未被互相索引，必须优先修复双链

## Repair Loop

发现错知识时，固定执行：

1. 标记 `conflicting` 或 `stale`
2. 从业务域 README 和默认 `Knowledge Pack` 中移除
3. 降级为 `D.stale/legacy`
4. 写回替代真源
5. 生成 `Knowledge Repair Record`
6. 从 README 根节点重新组织调研路径
7. 产出新的 `Knowledge Pack`

默认策略是“降权 + 归档 + 重新索引”。

如果采用三色知识分层，再附加以下动作：

8. 白知识失效时，退出 `white knowledge`
9. 废弃或禁止复用的内容进入 `black knowledge`
10. 黑知识若需要重新讨论，先恢复到 `gray knowledge`，再决定是否返白

## 不要做的事

- 不要在没有业务域的情况下直接给代码方案
- 不要把整份 HAR、整份长日志塞进默认 `Knowledge Pack`
- 不要让错知识继续留在业务域 README 的默认索引里
- 不要让 Worker 私自回写业务知识结论
- 不要把 `gray knowledge` 直接写成 `locked facts`
- 不要让 `black knowledge` 进入 Worker 或 Runner 的默认知识包
- 不要无限创建新的知识分类文件夹；优先压缩到既有业务域目录及其 `knowledge/` 子目录
- 不要把 `PRD / 约束 / 架构` 做成新的并列目录树；它们只存在于 `knowledge/README.md` 的索引结构和知识项元数据里
- 不要等用户提醒才做知识压缩、命中判断和断链修复；这属于 Curator 的默认职责
