# Knowledge Pack 模板

```markdown
## Knowledge Pack

### 业务域
- ...

### 功能点
- [[功能点]]

### authoritative sources
- ...

### baseline sources
- path: ...
  claim_id: ...
  business_domain: ...
  business_tag: `#业务域`
  feature_point: `[[功能点]]`
  source_ref:
    wikilink: `[[页面#^block-id]]`
    block_id: `^block-id`
    start_line: 1
    end_line: 2
    start_text: ...
    end_text: ...
  relation: `support | refute`
  confidence: `0.0-1.0`
  sourcecheck_status: `ok`
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `white`
  authority_level: `A | B | C | D`

### advisory sources
- path: ...
  claim_id: ...
  business_domain: ...
  business_tag: `#业务域`
  feature_point: `[[功能点]]`
  source_ref:
    wikilink: `[[页面#Heading]]`
    start_line: 1
    end_line: 2
    start_text: ...
    end_text: ...
  relation: `support | refute`
  confidence: `0.0-1.0`
  sourcecheck_status: `ok | source_drift | boundary_not_unique | ...`
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `gray`
  authority_level: `A | B | C | D`

### blocked sources
- path: ...
  claim_id: ...
  business_domain: ...
  business_tag: `#业务域`
  feature_point: `[[功能点]]`
  source_ref:
    wikilink: `[[页面#Heading]]`
  relation: `support | refute`
  confidence: `0.0-1.0`
  sourcecheck_status: `ok | source_drift | ...`
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `black`
  authority_level: `A | B | C | D`

### claim refs
- claim_id: ...
  claim: ...
  business_domain: ...
  business_tag: `#业务域`
  feature_point: `[[功能点]]`
  source_ref:
    path: ...
    wikilink: `[[页面#^block-id]]`
    start_line: 1
    end_line: 2
    start_text: ...
    end_text: ...
  relation: `support | refute`
  confidence: `0.0-1.0`
  sourcecheck_status: `ok`

### locked facts
- ...

### open conflicts
- ...

### stale sources to ignore
- ...

### writeback targets
- 业务域 README
- 业务域 `knowledge/README.md`
- [[功能点]]
```

规则：

- 只放最小必要事实
- 不放整份长文档
- 不放整份 HAR / 日志 / rerun
- 每条 source 都必须带 `knowledge_kind`、`knowledge_color`、`authority_level`
- 支撑 `locked facts`、路书锚点或 Worker Pack 的 Obsidian source 必须带 `claim_id` 和 `source_ref`
- `claim_id` 必须绑定 `business_domain`、`#业务域`、`[[功能点]]`
- `sourcecheck_status != ok` 的 claim 不能进入 `locked facts`
- SourceCheck `ok` 只表示引用对得上，不等于 `white`
- `gray` 只能出现在 `advisory sources`
- `black` 只能出现在 `blocked sources`
