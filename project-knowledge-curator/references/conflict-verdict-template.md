# Conflict Verdict 模板

```markdown
## Conflict Verdict

### 业务域
- ...

### 功能点
- [[功能点]]

### 状态
- aligned | missing | conflicting | stale | superseded

### 当前事实
- ...

### 冲突来源
- docs:
- code:
- prd/spec:

### 当前建议
- ...

### 是否需要进入 Exception
- yes / no
```

使用规则：

- 不能只说“有冲突”，必须写清冲突来自哪里
- 如果无法自动裁决，显式建议进入 `Exception.md`
