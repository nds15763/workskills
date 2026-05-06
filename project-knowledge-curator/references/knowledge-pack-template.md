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
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `white`
  authority_level: `A | B | C | D`
  business_domain: ...
  feature_point: ...

### advisory sources
- path: ...
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `gray`
  authority_level: `A | B | C | D`
  business_domain: ...
  feature_point: ...

### blocked sources
- path: ...
  knowledge_kind: `prd | constraint | architecture`
  knowledge_color: `black`
  authority_level: `A | B | C | D`
  business_domain: ...
  feature_point: ...

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
- `gray` 只能出现在 `advisory sources`
- `black` 只能出现在 `blocked sources`
