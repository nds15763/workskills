# Obsidian SourceCheck 协议

## 定位

Obsidian SourceCheck 是 `project-wiki` 的引用校验层。它不替代 Curator，也不直接裁决黑白灰；它只回答一个客观问题：

> 这条 claim 是否能在当前 Obsidian 结构中，精确、唯一、可复核地指回原文？

通过后，claim 才能交给 `project-knowledge-curator` 判 `knowledge_kind / knowledge_color / authority_level`。引用校验通过不等于白知识。

## 主键模型

Obsidian 版 SourceCheck 的主键不是裸 `path + line`，而是：

```text
业务域文件夹 + #业务标签 + [[功能点]] + claim_id + Obsidian ref
```

`path + line + string boundary` 只是最后的物理校验层。

## JSONL Schema

默认存储在 `<业务域>/knowledge/sourcecheck.jsonl`，一行一个 claim。

```json
{
  "claim_id": "morph72.ready.offline-auto-ready",
  "business_domain": "morph72",
  "business_tag": "#morph72",
  "feature_point": "[[Ready推进]]",
  "claim": "离线玩家不阻塞下一轮，服务端会自动 Ready",
  "source_ref": {
    "vault": "narnia",
    "path": "morph72/小局结算与Ready推进.md",
    "wikilink": "[[小局结算与Ready推进#Ready 推进规则]]",
    "heading": "Ready 推进规则",
    "block_id": "^ready-auto-offline",
    "start_line": 42,
    "end_line": 45,
    "start_text": "离线玩家",
    "end_text": "自动 Ready"
  },
  "relation": "support",
  "confidence": 0.86,
  "governance": {
    "knowledge_kind": "constraint",
    "knowledge_color": "white",
    "authority_level": "A.authoritative"
  }
}
```

字段规则：

| 字段 | 规则 |
|---|---|
| `business_domain` | 必须等于 vault 下一级业务域文件夹名 |
| `business_tag` | 页面正文或 frontmatter tags 必须含对应 `#业务域` |
| `feature_point` | 必须是 Obsidian wikilink，且能在业务域 README 或叶子页反查 |
| `claim_id` | 同一业务域内唯一，建议 `<domain>.<feature>.<slug>` |
| `claim` | 人话结论，不能整段复制原文 |
| `source_ref.wikilink` | 给人读的 Obsidian 定位 |
| `source_ref.block_id` | 有长期稳定知识时优先写，格式 `^slug` |
| `start_line/end_line + start_text/end_text` | 给程序做确定性校验 |
| `relation` | `support` 或 `refute` |
| `confidence` | 0 到 1，只表达该 ref 与 claim 的关联强度 |
| `governance` | Curator 判定结果；SourceCheck 只校验引用，不自动生成白知识 |

## 校验顺序

SourceCheck validator 必须按这个顺序做，不允许直接从 line span 开始：

1. `business_domain` 对应的业务域文件夹存在。
2. `source_ref.path` 位于该业务域文件夹内；跨域引用必须显式标 `cross_domain: true` 和目标域。
3. 页面存在，且 frontmatter / 正文包含 `business_tag`。
4. `feature_point` 是合法 `[[功能点]]`，且能从业务域 `README.md` 或叶子文档反查。
5. `source_ref.wikilink` 能解析到页面；如带 heading/block，则 heading/block 存在。
6. `start_line/end_line` 不越界，且顺序合法。
7. `start_text/end_text` 在指定行范围内存在，顺序合法。
8. 边界文本在该范围内能唯一定位；不唯一时要求 agent 重生成更精确 reference。
9. `relation` 必须是 `support/refute`，`confidence` 必须在 0-1。
10. 校验通过后，才进入 Curator 的黑白灰和 authority 判定。

## 定位优先级

| 定位方式 | 用途 |
|---|---|
| `[[页面#^block-id]]` | 最稳定，适合 durable knowledge |
| `[[页面#Heading]]` | 人好读，但 heading 改名会漂移 |
| `line + start_text/end_text` | 程序最容易校验，适合 drift 检测 |
| 仅 `path` | 不够；只能算来源文件，不能算 claim 证据 |

推荐同时写：`wikilink` 给人读，`line/string boundary` 给程序验，`block_id` 给长期稳定。

## 状态输出

validator 输出至少包含：

| status | 含义 |
|---|---|
| `ok` | 引用可解析且边界唯一 |
| `invalid_domain` | 业务域文件夹不存在或 path 不属于该域 |
| `missing_business_tag` | 页面缺 `#业务域` 标签 |
| `missing_feature_point` | `[[功能点]]` 不存在或无法反查 |
| `broken_wikilink` | wikilink 目标不存在 |
| `missing_heading_or_block` | heading / block-id 不存在 |
| `line_out_of_bounds` | 行号越界 |
| `boundary_not_found` | 字符串边界不存在 |
| `boundary_not_unique` | 字符串边界不唯一 |
| `source_drift` | 原文变化导致历史 reference 失效 |

非 `ok` 状态不能进入 `locked facts`，只能作为待修复项或灰知识调查输入。

## 与 Curator 的关系

SourceCheck 和黑白灰分工：

| SourceCheck | Curator |
|---|---|
| 校验 claim 是否能指回 Obsidian 原文 | 判断该 claim 能否驱动行动 |
| 判断引用唯一/越界/漂移 | 判断 white/gray/black 与 authority |
| 表达 support/refute/confidence | 输出 Conflict Verdict / Repair Loop |
| 失败时要求 agent 重生成 reference | 失败时降权、隔离或更新 Knowledge Pack |

通过 SourceCheck 的低权威来源仍可能是灰知识；没通过 SourceCheck 的内容不能成为白知识。

## 写回规则

- 不默认创建 vault 顶层 `_sourcecheck/`。默认写入 `<业务域>/knowledge/sourcecheck.jsonl`。
- `knowledge/README.md` 只索引人可读结论，不塞大量机器字段。
- 真正的 claim/ref 机器字段放 `sourcecheck.jsonl`。
- 若 claim 是跨域知识，源业务域和目标业务域都要能通过 README / `[[功能点]]` 找到它。
- Repair Loop 改写原文或迁移功能点时，必须同步更新 `sourcecheck.jsonl`，否则相关白知识回退为灰。
