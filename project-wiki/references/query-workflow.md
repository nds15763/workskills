# Query 工作流

> 用户查询 → Obsidian CLI 搜索 → 知识元数据增强 → 结构化输出

## 查询流程

### Step 1: 接收查询

用户提出知识查询请求。常见形式：
- "投毒检测流程是怎样的？"
- "masquerade 域的 authoritative sources 有哪些？"
- "生成关于 X 的 Knowledge Pack"

### Step 2: 选择查询方式

| 场景 | 命令 |
|------|------|
| 通用搜索 | `search.py search "query" [--domain <域>] [-n 5]` |
| 命中检测（Curator 用） | `search.py hit-detect "query"` |
| 生成 Knowledge Pack | `search.py knowledge-pack "query" --domain <域> --feature-point <fp>` |
| 读取特定文件 | `search.py read "file.md" [--meta-only]` |
| 查找反向链接 | `search.py backlinks "file.md"` |

### Step 3: 解读搜索结果

搜索结果按 authority_level 排序（A > B > C > D），每个结果包含：

```
filename        — 文件路径
knowledge_kind  — prd / constraint / architecture
knowledge_color — white / gray / black
authority_level — A.authoritative / B.supporting / C.evidence / D.stale
business_domain — 所属业务域
feature_points  — 关联的 [[功能点]]
```

**解读规则**：
- `white` + `A` = 最可信的基线知识，可直接引用
- `gray` = 有参考价值但需要确权，标注"待确认"
- `black` = 已弃用，不引用到新上下文中
- `D.stale` = 过期知识，可能需要 Repair Loop

### Step 4: 组装输出

根据查询目的选择输出格式：

#### 简单回答

直接基于搜索结果回答用户问题，引用 authoritative 和 baseline sources。

#### Knowledge Pack（Curator 模板格式）

```markdown
## Knowledge Pack

### 业务域
- <domain>

### 功能点
- [[<feature_point>]]

### authoritative sources
- path: <file>
  knowledge_kind: <kind>
  knowledge_color: <color>
  authority_level: A.authoritative
  business_domain: <domain>
  feature_point: <fp>

### baseline sources
（白知识）

### advisory sources
（灰知识，按需引用）

### blocked sources
（黑知识，隔离不用）

### locked facts
（Curator 确认的不可变事实）

### open conflicts
（已发现的矛盾）

### stale sources to ignore
（过期知识）

### writeback targets
（需要回写的位置）
```

## 结果归档规则

> 好的查询结果应该被归档回 Wiki 成为新页面。

### 什么值得归档

- 跨多个来源的综合分析
- 有价值的对比表
- 新发现的关联或矛盾
- 用户确认有持续价值的查询结果

### 什么不归档

- 简单的事实查询（答案已在现有页面中）
- 一次性的临时查询
- 纯代码层面的问题

### 归档流程

1. 将查询结果保存为新 wiki 页面
2. 添加 frontmatter（默认 `gray` + `C.evidence`）
3. 更新 index.md
4. 更新 log.md
5. 建立与已有页面的 wikilink

```markdown
## [YYYY-MM-DD] query | <查询主题>
- 命中: <命中的关键页面>
- 产出: Knowledge Pack for Worker / 综合分析
- 归档: <归档页面路径>（查询结果归档回 wiki）
```

## hit-detect 输出解读

`search.py hit-detect` 返回三种状态：

| status | 含义 | 后续动作 |
|--------|------|----------|
| `no_hit` | 无匹配知识 | 可能是新域/新功能点，需要 Ingest |
| `hit_readonly` | 命中有效知识 | 直接使用，无需修改 |
| `hit_writeback_required` | 命中灰知识或过期知识 | 需要确权/更新/修复 |

## 与 Curator Gate 的映射

| 查询工具 | 支持的 Gate |
|----------|-------------|
| `hit-detect` | KP-00 Domain Locked |
| `knowledge-pack` | KP-01 Sources Locked, KP-03 Worker Pack Ready |
| `search` | 通用查询，辅助所有 Gate |
