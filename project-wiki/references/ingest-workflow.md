# Ingest 工作流

> 一个源素材可能触及 10-15 个 wiki 页面。

## 触发条件

- 人类把新素材放入 `_sources/`
- 用户要求处理新文档/会议记录/设计文档
- 用户要求沉淀当前会话产物

## 完整流程

### Step 1: 读取素材

Curator 读取 `_sources/` 中的新素材，理解内容。

### Step 2: 与用户讨论

Curator 与用户确认：
- 这份素材的核心价值是什么？
- 涉及哪些业务域？
- 有哪些值得沉淀的结论？
- 是否与已有知识存在矛盾？

### Step 3: 知识命中检测

```bash
python3 scripts/search.py hit-detect "<素材关键词>"
```

根据返回结果决定策略：
- `no_hit` → 新域/新功能点，需要创建新页面
- `hit_readonly` → 已有知识仍然有效，需要更新和扩充
- `hit_writeback_required` → 发现灰知识或过期知识，需要确权/修复

### Step 4: 写入 Wiki（Curator 执行）

按以下顺序写入：

1. **写 summary page**：为新素材创建摘要页（如果值得独立成页）
2. **更新域 README.md**：添加新功能点、新实体链接
3. **更新/创建实体页和概念页**：优先更新已有 note，不平铺创建新 note
4. **更新 knowledge/README.md**：三色知识索引
5. **标注矛盾**：新数据与旧知识的冲突必须在写入时就标记

#### 写入规则

- 所有文档使用中文，Obsidian 友好 Markdown
- 每条新知识必须带 frontmatter：
  ```yaml
  ---
  knowledge_kind: prd | constraint | architecture
  knowledge_color: gray    # 新知识默认 gray
  authority_level: <根据来源判断>
  ---
  ```
- 新知识默认进入 `gray`（待确权）
- 只有用户明确确认后才可升级为 `white`
- 优先合并到已有页面，不创建重复页面
- 主动压缩和整理知识结构，不等用户要求
- 文档副标题需携带业务域标签，如 `#masquerade`
- 功能点条目必须携带代码位置，格式：`[[功能点]] 简述 Handler @file#L{start}-L{end}`
- 工具函数不用记录，只记录业务功能点

#### 什么不要做

- 不要逐轮对话转录——优先沉淀最终成立的结论
- 不要把整份长文档复制到 wiki——摘要 + 路径引用
- 不要修改 `_sources/` 中的原始素材
- 不要把 gray knowledge 直接写成 locked facts

### Step 5: 更新索引

- **index.md**：添加新页面条目（一行摘要）
- **log.md**：追加操作日志

```markdown
## [YYYY-MM-DD] ingest | <素材标题>
- 新增: <新建页面路径>
- 更新: <更新页面路径>（变更摘要）
- 冲突: <冲突描述> → Conflict Verdict 已出 / 待裁决
```

### Step 6: 写后验证

```bash
python3 scripts/lint.py --domain <业务域> --json
```

验证：
- 新建链接是否有效（无断链）
- 新页面是否在域 README 中被引用
- frontmatter 元数据是否完整

## 三色知识沉淀规则

会话产物默认收敛成三色知识：

| 颜色 | 条件 | 沉淀位置 |
|------|------|----------|
| 白 white | 用户已确认、有权威来源支持 | knowledge/README.md 白知识区 |
| 灰 gray | 有价值但未确权 | knowledge/README.md 灰知识区 |
| 黑 black | 已明确弃用或隔离 | knowledge/README.md 黑知识区 |

每条知识必须先归类到 `prd | constraint | architecture` 之一，再标注颜色。

## 矛盾处理

当新素材与已有知识冲突时：

1. 在相关页面标注冲突
2. 生成 Conflict Verdict（参考 `project-knowledge-curator/references/conflict-verdict-template.md`）
3. 如果无法自动裁决，显式建议进入 Exception
4. 在 log.md 记录冲突

## Repair Loop

当发现错知识时（参考 `project-knowledge-curator/references/repair-discard-policy.md`）：

1. 从域 README 和默认 Knowledge Pack 中移除
2. 降级为 `D.stale/legacy`
3. 归档到 `archive/legacy/` 或保留原地但不再被索引
4. 在 authoritative 文档补上替代真源
5. 重新生成 Knowledge Pack
6. `lint.py` 验证修复完成

只有以下条件全满足，repair 才算完成：
- 旧知识已退出 README 默认索引
- 旧知识已退出默认 Knowledge Pack
- 替代真源已写回
- 新 Knowledge Pack 已生成
