# Vault 三层结构规范

## 目录结构

```
<vault_root>/
├── _sources/                    # Layer 1: 原始素材（不可变）
│   ├── prd/                     #   产品文档
│   ├── meeting-notes/           #   会议记录
│   ├── design-docs/             #   设计文档
│   └── code-analysis/           #   代码分析产物
│
├── <业务域>/                     # Layer 2: Wiki（LLM 维护）
│   ├── README.md                #   域索引（authoritative 入口）
│   ├── knowledge/
│   │   └── README.md            #   三色知识索引（3类 × 3色）
│   ├── <实体页>.md               #   实体页（角色、服务、模块）
│   ├── <概念页>.md               #   概念页（模式、原则、决策）
│   └── <对比/综合>.md             #   对比表、综合分析
│
├── _schema/                     # Layer 3: 治理（vault 级覆盖）
│   └── overrides.md             #   vault 专属规则覆盖
│
├── index.md                     # 内容导航（LLM 维护，按类别组织）
└── log.md                       # 时间线变更日志（append-only）
```

## Layer 1: _sources/

### 规则

- **不可变**：LLM 只读不改，人类负责策展
- 子目录按素材类型组织，不按业务域
- 文件名建议：`<简短描述>-<日期>.md`（如 `masquerade-v2-prd-20260401.md`）
- 支持任何格式：.md、.pdf、.txt、图片等
- 不要求 frontmatter（这是原始素材，不是 wiki 页面）

### 子目录

| 目录 | 内容 |
|------|------|
| `prd/` | 产品需求文档、功能规格 |
| `meeting-notes/` | 会议记录、讨论摘要 |
| `design-docs/` | 技术设计文档、架构提案 |
| `code-analysis/` | 代码分析产物、性能报告 |

可按需添加新的子目录。

## Layer 2: 业务域目录

### 域 README.md

每个业务域的入口文件。必须包含：

```markdown
---
knowledge_kind: architecture
knowledge_color: white
authority_level: A.authoritative
---

# <业务域名称>

## 概述
一段话描述这个域的职责和边界。

## 功能点
- [[功能点A]] — 一句话描述
- [[功能点B]] — 一句话描述

## 核心实体
- [[实体页A]] — 角色/服务/模块
- [[实体页B]]

## 核心概念
- [[概念页A]] — 模式/原则/决策
- [[概念页B]]

## 相关域
- [[其他域/README]]
```

### knowledge/README.md（三色知识索引）

按 knowledge_kind × knowledge_color 组织：

```markdown
# <业务域> 知识索引

## PRD知识

### 白知识
- 已确认有效、可进入默认基线的产品目标、业务规则、验收口径

### 灰知识
- 有潜在复用价值，尚未确权的 PRD 结论

### 黑知识
- 已明确弃用或不应进入执行链路的 PRD 内容

## 约束知识

### 白知识
- 已确认有效的门闩、流程限制、禁止事项

### 灰知识
- 待确认的规则、限制或待验证约束

### 黑知识
- 已弃用或已被替代的约束

## 架构知识

### 白知识
- 已确认有效的模块边界、数据流、控制面设计

### 灰知识
- 待进一步确认的架构方案或实现路径

### 黑知识
- 已废弃或已被替代的架构结论
```

### Wiki 页面 Frontmatter

每个 wiki 页面（非 README）必须包含：

```yaml
---
knowledge_kind: prd | constraint | architecture
knowledge_color: white | gray | black
authority_level: A.authoritative | B.supporting | C.evidence | D.stale/legacy
---
```

### 页面类型

| 类型 | 命名建议 | 内容 |
|------|----------|------|
| 实体页 | 名词（角色名、服务名、模块名） | 定义、职责、接口、关联 |
| 概念页 | 名词/短语（模式名、原则名） | 定义、应用场景、权衡 |
| 对比表 | `<A>-vs-<B>` 或 `<主题>-对比` | 多方案对比分析 |
| 综合分析 | `<主题>-综合分析` | 跨多个来源的综合论述 |
| 流程页 | `<主题>-流程` | 步骤、时序、状态转换 |

## Layer 3: _schema/

### 用途

存放 vault 级的规则覆盖。默认规则在 skill 的 references/ 中定义，vault 可通过 `_schema/overrides.md` 覆盖特定规则。

### overrides.md 格式

```markdown
# Vault Schema Overrides

## 覆盖的规则

### 自定义知识类型
- 除 prd/constraint/architecture 外，本 vault 允许 `experiment` 类型

### 自定义目录
- 本 vault 使用 `specs/` 替代 `_sources/prd/`
```

## index.md

### 格式

```markdown
# 知识库索引

## 业务域
- [[masquerade/README]] — 互动娱乐/投毒对决玩法
- [[morph72/README]] — 变形图生成链路
- [[auth/README]] — 认证与授权

## 实体
- [[masquerade/轮次状态机-Phase1到结算]] — 一局游戏的业务相位推进
- ...

## 概念
- [[基础协议/Proto契约模式]] — 服务间契约定义范式
- ...

## 来源
- [[_sources/prd/masquerade-v2-prd]] — Masquerade v2 产品需求文档
- ...
```

### 维护规则

- 按类别组织，不按时间
- 每次 Ingest 后更新（新页面 + 一行摘要）
- 每次 Query 产生可归档结果时更新
- 不包含临时/草稿页面

## log.md

### 格式

```markdown
# 变更日志

## [2026-04-07] ingest | Masquerade v2 PRD
- 新增: masquerade/投毒检测流程.md
- 更新: masquerade/README.md（+2 个功能点）
- 更新: masquerade/knowledge/README.md（+3 条白知识）
- 冲突: 投毒计分规则与 v1 设计冲突 → Conflict Verdict 已出

## [2026-04-07] query | 投毒检测端到端流程
- 命中: masquerade/轮次状态机-Phase1到结算.md
- 产出: Knowledge Pack for Worker
- 归档: masquerade/投毒检测端到端分析.md（查询结果归档回 wiki）

## [2026-04-07] lint | masquerade 域审计
- 发现: 2 broken wikilinks, 1 orphan note
- 修复: masquerade/README.md 补链
```

### 维护规则

- append-only（只追加，不修改历史条目）
- 每条日志以 `## [YYYY-MM-DD] 操作 | 标题` 开头
- 操作类型：ingest / query / lint / repair / archive

## 兼容现有 Vault

对于已有 vault（如 narnia-docs-kim），增量引入：

1. 已有的业务域目录（masquerade/, morph72/, auth/ 等）保持原样
2. 增量添加 `_sources/`、`index.md`、`log.md`
3. 逐步为已有页面补充 frontmatter 元数据
4. 不要求一次性改造——`lint.py` 会报告缺失的元数据，按需补充
