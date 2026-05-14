# 读写合同

## 读取

- 所有 Code 必须先由 Docs 驱动。
- 先问业务域，再查文档。
- 优先读取业务域 `README.md`，再进入 `[[功能点]]` 叶子文档。
- 读取顺序固定为：`rg/grep -> obsidian-cli -> MCP fallback`。
- `obsidian-cli` 需要 Obsidian app 运行且 CLI 可连通；不可用时明确降级，不要静默失败。
- 如果没有相关业务域或 `[[功能点]]`，先和用户确认是否需要补收集知识，不要直接假设。
- 每次对话、设计、实现、排障前后，都要先判断这次内容是否命中已有知识。
- 命中知识但没有 durable change 时，只读不写；命中且产生 durable change 时，必须进入 writeback。
- 每次 writeback 前后，都要检查 `README.md`、`knowledge/README.md`、`[[功能点]]` 和叶子知识 note 的双链健康。

## 写入

- 所有文档都使用中文。
- 所有文档都保持 Obsidian 友好 Markdown。
- 当文件名已经承担标题作用时，正文不要再重复写同名 `# H1`。
- 业务域以文件夹组织。
- 每个业务域目录下固定建立 `knowledge/` 子文件夹，业务知识默认写入 `<business_domain>/knowledge/`。
- 每个业务域的 `knowledge/README.md` 必须作为 durable knowledge 的统一索引入口。
- 业务域文档需要带 `#业务域` 标签。
- 功能新增或修改时，要在业务域 README 和叶子文档补 `[[功能点]]`。
- 要进入白知识候选、`locked facts`、路书锚点或 Worker Pack 的 Obsidian claim，必须有 `claim_id`，并能通过 `业务域文件夹 + #业务域 + [[功能点]] + Obsidian ref` 指回原文。
- Obsidian ref 优先写 `[[页面#^block-id]]`；同时保留 `start_line/end_line + start_text/end_text` 供程序校验。
- 代码落点格式固定为：`功能名 符号名 @filename#L{start}-L{end}`。
- 工具函数默认不记录到业务文档，除非用户明确要求。
- 会话产物默认要收敛成白 / 灰 / 黑知识，不直接保存为原始对话转录。
- 如果已有 note、README 或双链可以承载新结论，优先合并和整理，不继续平铺创建新 note。
- Curator 需要主动压缩和整理知识结构，不要等用户手动要求。
- 每条 durable knowledge 必须带 `knowledge_kind`、`knowledge_color` 和 `authority_level`。
- 发现 `missing_wikilink`、`missing_index` 或 `orphan_note` 时，优先修复链接，不要把断链状态继续带进默认知识包。

## 索引

- 每个业务域固定一个 `README.md` 根索引。
- 每个业务域固定一个 `knowledge/README.md` 知识索引。
- `knowledge/README.md` 固定分为 `PRD知识`、`约束知识`、`架构知识` 三类。
- 每类固定再按 `白知识`、`灰知识`、`黑知识` 分区。
- 根索引只保留：
  - authoritative 入口
  - `[[功能点]]`
  - 当前冲突/遗留问题索引
- 机器校验用 claim/ref 默认放在 `<业务域>/knowledge/sourcecheck.jsonl`，不塞进根 README。

## authority

- `A.authoritative`
- `B.supporting`
- `C.evidence`
- `D.stale/legacy`

只有 `A + 当前功能点相关的 B` 能进默认 `Knowledge Pack`。

知识类别固定为：

- `prd`
- `constraint`
- `architecture`
