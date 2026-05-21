---
name: project-wiki
description: >-
  在写代码前查找和确认业务域知识，在写完代码后回写文档。
  当需要搜索 Obsidian vault、确认功能点是否有现成知识、
  生成 Knowledge Pack、审计文档健康、或摄取新素材时使用。
---

> **公理继承 / Axiom Inheritance**
> 本 skill 服从顶层公理 `typed evidence gates action`——
> 未经类型化（三色 + authority + kind）的上下文不允许驱动行动。
> 在该公理下，本 skill 的职能：执行 Vault 的 Query / Ingest / Lint，是 Curator 的工具层

# project-wiki

基于 Obsidian CLI 的项目知识 IO 系统——**知识只编译一次并保持更新，而不是在每次查询时重新推导。**

## 核心哲学

Obsidian 是 IDE，LLM 是程序员，Wiki 是源代码。

- 人类负责：策展素材、引导分析、提出好问题
- LLM 负责：摘要、交叉引用、归档、记账——让知识库长期有效的所有繁杂工作
- 知识在 Wiki 层持续积累产生复利，不消失在聊天历史中

## 与 Context Compiler 的关系

project-wiki 是知识 IO 层：负责把原始资料读进来、搜出来、写回去、索引起来。

注意：Docs 是 source，不是自动真理。任何文档、会议、代码分析或聊天总结，只有经过 Curator 的 `knowledge_color`、`authority_level`、`knowledge_kind`、`claim_type` 裁决后，才能成为默认行动依据。

如果输入来自 PRD、设计稿、LLM 总结或用户自然语言，并且涉及新术语、同义词、规则句、OpenSpec 同步或“已有知识检索不到”，先交给 `canonical-claim-compiler` 把 raw wording 编译成 `concept_id / claim_id / pending / drift`。Wiki 不负责判断两个词是不是同一个对象，也不负责判断两条自然语言是不是同一条 claim；Wiki 只消费 accepted 身份和命题。

Wiki 只负责 IO 和引用校验；三类逻辑校准不在 Wiki 层定案：

- `logical-grammar`：SourceCheck 可证明引用对得上，但对象/关系/状态是否合法要另判。
- `truth-condition-checker`：SourceCheck 不证明 claim 为真，只证明可回指原文。
- `say-show-boundary`：SourceCheck 不证明价值、审美、愿景应被采纳；摄取时必须标 `claim_type`。

## Agent 行为规则

> [!important]
> 所有 Code 必须由经过知识校准的 Docs / Knowledge 驱动。

如果当前任务没有对应的 `功能点` 和 `业务域`，**不能直接写代码**。必须先：
1. 询问用户需要哪个业务域的知识
2. 确认功能点是否已存在于该业务域
3. 如果是全新业务域/功能点，与用户沟通后先收集知识再执行

写代码前不是“找到一篇文档就够了”，而是必须确认这份资料在当前任务里属于 baseline、advisory 还是 blocked。

## Obsidian SourceCheck

SourceCheck 是 Obsidian 知识进入黑白灰治理之前的引用校验层。它不另建知识库，只校验 claim 是否能按现有 Obsidian 结构精确指回原文。

SourceCheck 不是 canonical identity layer。`claim_id` 可以来自 `canonical-claim-compiler`，但 SourceCheck 只证明这个 claim 能指回 Obsidian ref；它不证明 claim 为真，也不证明两个 alias 指向同一个 concept。

主键必须是：

```text
业务域文件夹 + #业务标签 + [[功能点]] + claim_id + Obsidian ref
```

不是：

```text
path + line
```

`path + line + start_text/end_text` 只能做物理定位；业务域、`#业务`、`[[功能点]]` 才是知识身份。

默认存储位置：

```text
<业务域>/knowledge/sourcecheck.jsonl
```

每条 SourceCheck claim 必须先通过：

1. 业务域文件夹存在，且引用页面属于该业务域；跨域引用必须显式标注
2. 页面有对应 `#业务域` 标签
3. claim 绑定合法 `[[功能点]]`
4. `[[功能点]]` 能从业务域 README 或叶子文档反查
5. Obsidian ref 能解析到页面 / heading / block
6. 行号不越界，字符串边界存在且唯一

通过 SourceCheck 只说明“引用对得上”，不说明“可以驱动行动”。后者仍必须交给 Curator 判 `knowledge_kind / knowledge_color / authority_level / claim_type`。详细协议见 `references/obsidian-sourcecheck.md`。

## 长任务知识门禁

project-wiki 不负责执行长任务 Loop；它负责保证每一轮 Loop 的行动依据没有被聊天、旧总结或未确权资料污染。

长任务必须先形成 `Goal Knowledge Pack`：

| 字段 | 要求 |
|---|---|
| 目标 | 用户到底要闭合什么，不是要读哪些文档 |
| 业务域 / 功能点 | 能映射到 vault 目录和 `[[功能点]]` |
| baseline sources | 可直接驱动行动的白知识 |
| advisory sources | 只能作为风险、补知识输入或待裁依据的灰知识 |
| blocked sources | 明确不能进入 Worker Pack 的黑知识 / 旧方案 |
| open conflicts | 需要 Curator 出 Conflict Verdict 的冲突 |
| evidence needed | 节点转绿所需代码、测试、日志、文档证据 |

每一轮 Loop 回报后，主 Agent 要问三件事：

1. 本轮是否引入新名词、新来源、新证据或旧知识冲突？
2. 这些内容是否会改变 roadmap 锚点、Worker Pack、验收证据或转绿条件？
3. 若会改变，是否已经通过 Curator 写回 wiki / 降权旧知识 / 更新 Knowledge Pack？

如果答案为“会改变但未写回”，该 roadmap 节点不能转绿，只能保持黄或红。Wiki 更新完成后，再由主 Agent 回写 `.canvas` 状态事务。

### 对话入口协议

每次对话开始时：
1. 确认业务域（= vault 中的文件夹，地址 `/Users/kim/code/narnia/narnia-docs-kim`）
2. `search.py hit-detect` 检测是否命中已有知识
3. 如未命中，询问用户是否需要新建业务域

如果本轮输入是 PRD / 设计稿 / LLM 总结 / 术语对齐问题，入口顺序改为：

```text
canonical-claim-compiler
  -> project-wiki Query / SourceCheck
  -> project-knowledge-curator accept / merge / reject / 三色治理
```

不要把 PRD 原句直接 Ingest 成 Obsidian 正文。先把它拆成 concept / claim；找不到身份的内容进 pending。

### 文档读取顺序

1. `search.py search --domain <域>`（Obsidian CLI + 元数据增强）
2. grep 业务域关键词查文档
3. Obsidian MCP fallback

### 文档写入格式

功能点条目必须携带代码位置：

```
[[功能点名称]] 功能简述 HandlerName @filename#L{start}-L{end}
```

示例：
```
[[邀请新用户]] 邀请新用户 NewUserInviteHandler @invite.go#L42-L87
```

- 文档副标题需携带业务域标签，如 `#masquerade`
- 新增/修改功能时，在业务域文件夹中添加 `[[功能点]]` 双链
- 工具函数不用记录

## 三层架构

```
Layer 1: Raw Sources（_sources/，不可变，人类策展）
    PRD、会议记录、设计文档、论文、代码分析
    LLM 只读不改。这是事实之源。

Layer 2: Wiki（<业务域>/，LLM 生成并维护）
    域索引、实体页、概念页、知识沉淀、对比表、综合分析
    LLM 完全拥有这一层：创建、更新、维护链接
    ┌─ Curator 治理层（叠加在 Wiki 之上）──────────────┐
    │  · 三色知识（白/灰/黑）= 默认使用策略              │
    │  · Authority 分级（A/B/C/D）= 证据强度             │
    │  · 知识类别（prd/constraint/architecture）         │
    │  · claim_type（fact/rule/value/taste/vision 等）   │
    │  · 每条 durable knowledge 必须同时带这四个维度      │
    └────────────────────────────────────────────────────┘

Layer 3: Schema（_schema/，治理规则）
    命名规范、页面模板、读写合同、三色沉淀规则
    你和 LLM 共同演进这一层
```

详见 → `references/vault-structure.md`

## 三色知识 × Authority 分级

| 维度 | 值 | 含义 |
|------|----|------|
| knowledge_color | white | 已确认有效，进入默认基线 |
| knowledge_color | gray | 有复用价值，尚未确权 |
| knowledge_color | black | 已弃用/隔离，不进入执行链路 |
| authority_level | A.authoritative | 权威来源（PRD、正式设计文档） |
| authority_level | B.supporting | 支持性来源（讨论记录、分析） |
| authority_level | C.evidence | 证据级（代码分析、日志推断） |
| authority_level | D.stale/legacy | 过期/遗留 |
| knowledge_kind | prd | 产品目标、业务规则、验收口径 |
| knowledge_kind | constraint | 门闩、流程限制、禁止事项 |
| knowledge_kind | architecture | 模块边界、数据流、控制面设计 |
| claim_type | fact/rule | 可验证事实或规则，才可能进入白知识 |
| claim_type | value/taste/vision/decision | 取向、审美、愿景或决策，不得单独驱动行动 |

## 三个核心操作

### 操作 1: Query（查询）

用户查询 → Obsidian CLI 搜索 → 知识元数据增强 → 结构化输出

```bash
# 搜索 + 元数据增强
python3 scripts/search.py search "投毒检测" --domain masquerade -n 5

# 知识命中检测（Curator 子能力）
python3 scripts/search.py hit-detect "投毒检测"

# 生成 Knowledge Pack（匹配 Curator 模板）
python3 scripts/search.py knowledge-pack "投毒" --domain masquerade --feature-point "投毒检测"

# 读取文件 + 元数据
python3 scripts/search.py read "masquerade/README.md" --meta-only

# 反向链接
python3 scripts/search.py backlinks "masquerade/轮次状态机.md"
```

**重要**：好的查询结果应归档回 Wiki 成为新页面——你的探索也在知识库中产生复利。

详见 → `references/query-workflow.md`

### 操作 2: Ingest（摄取）

一个源素材可能触及 10-15 个 wiki 页面。Curator 执行完整 Ingest 流程：

1. 人类把新素材放入 `_sources/`
2. PRD / 设计稿 / LLM 总结先经过 `canonical-claim-compiler`，输出 accepted / pending concept 和 claim
3. Curator 读取素材，与用户讨论重点
4. Curator 写入/更新 wiki 页面：
   - 写 summary page → 更新 index.md → 更新实体页/概念页
   - 标注新数据与旧知识的矛盾
   - 每条新知识必须带 knowledge_kind + knowledge_color + authority_level + claim_type
   - 摄取时区分事实、规则、推断、价值、审美、愿景和决策；价值/审美/愿景只能作为取向或约束，不得写成白知识事实
   - 新知识默认进入 gray knowledge（待确权）
5. 更新 log.md（追加条目）
6. `lint.py` 验证链接健康

**写入规则**：
- 所有文档使用中文，Obsidian 友好 Markdown
- 优先更新已有 note，不平铺创建新 note
- 主动压缩和整理知识结构，不等用户要求
- 会话产物默认收敛成白/灰/黑知识，不保存原始对话转录

详见 → `references/ingest-workflow.md`

### 操作 3: Lint（审计）

```bash
# 审计指定业务域
python3 scripts/lint.py --domain masquerade

# 审计全 vault，JSON 输出
python3 scripts/lint.py --json
```

**检查项**：
- `missing_wikilink` — 断链（wikilink 目标不存在）
- `orphan_note` — 孤儿页（无入链）
- `missing_index` — 页面不在域 README 中
- `missing_metadata` — 缺少 knowledge_kind / knowledge_color / authority_level
- 矛盾检测 → 触发 Curator 的 Conflict Verdict
- 过期检测 → 触发 Curator 的 Repair Loop

**LLM 额外能力**：Lint 不只检查问题——LLM 擅长建议新的问题去调查和新的素材去寻找。

### 操作 4: SourceCheck（引用校验）

用户查询 / Ingest / Knowledge Pack 生成过程中，如果某条结论要作为 `locked facts`、白知识候选、路书锚点或 Worker Pack 依据，必须有可校验的 claim reference。

SourceCheck 检查：

- 业务域文件夹、`#业务域` 标签、`[[功能点]]` 双链是否匹配
- `wikilink / heading / block_id` 是否可解析
- `start_line/end_line` 是否越界
- `start_text/end_text` 是否存在且唯一
- `relation` 是否为 `support/refute`，`confidence` 是否在 0-1

输出非 `ok` 时，该 claim 不允许进入 `locked facts`；只能作为待修复项、灰知识或 Conflict Verdict 输入。

## 操作路由

| 触发词 | 操作 | 调用 |
|--------|------|------|
| 搜索/查找/查询/知识包 | Query | `search.py search \| hit-detect \| knowledge-pack` |
| 审计/检查/断链/孤儿页 | Lint | `lint.py [--domain] [--json]` |
| PRD/设计稿/LLM总结/术语漂移 | Canonical Compile | 先读 `canonical-claim-compiler/SKILL.md` |
| 摄取/导入/处理新素材 | Ingest | 先 canonical compile，再读 `references/ingest-workflow.md`，Curator 执行 |
| 引用/来源/claim/ref/SourceCheck | SourceCheck | `references/obsidian-sourcecheck.md` |
| wiki 结构/规范/模板 | Schema | 读 `references/vault-structure.md` |

## index.md + log.md

### index.md — 内容导航（空间维度）

按类别组织（业务域 / 实体 / 概念 / 来源），非按时间。
LLM 在每次 Ingest 时更新。查询时先读 index.md 定位相关页面。
在中等规模（~100 素材）下，比向量数据库更有效。

### log.md — 变更日志（时间维度）

每条日志格式：`## [YYYY-MM-DD] 操作 | 标题`

```markdown
## [2026-04-07] ingest | Masquerade v2 PRD
- 新增: masquerade/投毒检测流程.md
- 更新: masquerade/README.md（+2 个功能点）
- 冲突: 投毒计分规则与 v1 设计冲突 → Conflict Verdict 已出

## [2026-04-07] query | 投毒检测端到端流程
- 命中: masquerade/轮次状态机-Phase1到结算.md
- 归档: masquerade/投毒检测端到端分析.md（查询结果归档回 wiki）
```

**维护规则**：
- 每次 Ingest 后更新 index.md 和 log.md
- 每次 Query 产生可归档结果时更新 index.md
- 不要等用户提醒才做维护

## 与 Curator 的集成

project-wiki 是工具层，Curator 是治理层。

| Curator 子能力 | project-wiki 工具 |
|----------------|-------------------|
| knowledge-hit-detect | `search.py hit-detect` |
| knowledge-curate | Ingest 操作 + `lint.py` 写后验证 |
| knowledge-link-audit | `lint.py` |
| claim-source-check | `sourcecheck.jsonl` + `references/obsidian-sourcecheck.md` |

**Curator 读取顺序**：`search.py (Obsidian CLI + 元数据增强) → MCP fallback`

**Knowledge Pack 格式**：严格匹配 `project-knowledge-curator/references/knowledge-pack-template.md`

详见 → `references/integration-guide.md`

## 与 Roadmap 的集成

| Gate | project-wiki 如何支持 |
|------|----------------------|
| KP-00 Domain Locked | `search.py hit-detect` 确认业务域 |
| KP-01 Sources Locked | `search.py knowledge-pack` 锁定 authoritative sources |
| KP-02 Conflict Verdict | `lint.py` 发现矛盾 → Curator 出 Conflict Verdict |
| KP-03 Worker Pack Ready | `knowledge-pack` 输出 → 主 Agent 裁剪为 Worker Pack |
| KP-04 Docs Writeback Done | Curator ingest 回写 → `lint.py` 验证 |
| KP-05 Knowledge Repair Closed | `lint.py` 确认旧知识已退出索引 + 替代真源已就位 |
| KP-06 Node Can Turn Green | 所有上述 gate 通过 |

Roadmap 每次 Loop Delta 中的 `knowledge_delta` 都要落到这里判定：

- `无新知识`：只需在 `.canvas` 记录证据索引。
- `新来源 / 新名词 / 新证据`：先 Query / Ingest，再由 Curator 判色。
- `旧知识冲突`：触发 Conflict Verdict 或 Repair Loop；旧知识未退出默认上下文前，roadmap 相关节点不能绿。
- `锚点变更`：主 Agent 先改 `.canvas` 锚点，再让 Curator 回写 wiki 索引，最后重跑 roadmap audit。

## 多项目支持

所有 CLI 用 `--vault` 参数。已知 vault：

| Vault | 路径 |
|-------|------|
| narnia | `/Users/kim/code/narnia/narnia-docs-kim` |
| withvideo | `/Users/kim/code/WithVideo/with_video_obsidian` |
| mewt | `/Users/kim/code/Mewt/docs` |

## 不要做的事

- 不要修改 `_sources/` 中的原始素材（不可变层）
- 不要在 Obsidian 不运行时静默降级到 rg/grep（明确报错）
- 不要把整份长文档塞进 Knowledge Pack（只放路径和摘要）
- 不要把 PRD 原句或 LLM 同义词直接写入 accepted wiki 正文；先 canonical compile
- 不要把只有 `path`、没有业务域 / `#业务域` / `[[功能点]]` / span 的来源当成 claim 证据
- 不要把 SourceCheck 通过当成白知识；它只证明引用对得上
- 不要把 gray knowledge 直接写成 locked facts
- 不要让 black knowledge 进入默认上下文
- 不要等用户提醒才做知识压缩、索引维护和断链修复
- 不要逐轮对话转录——优先沉淀最终成立的结论
- 不要在没有业务域和功能点的情况下直接写代码

## 前置条件

- Obsidian 应用运行中
- Obsidian CLI 已注册（Settings → General → CLI）
- Python 3.x（无外部依赖）
