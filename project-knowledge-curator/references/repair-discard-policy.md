# Repair / Discard 策略

## 默认策略

错知识默认采用：

1. 从业务域 README 和默认 `Knowledge Pack` 中移除
2. 降级为 `D.stale/legacy`
3. 归档到 `archive/legacy/`，或保留原地但不再被索引
4. 在 authoritative 文档补上替代真源
5. 重新生成 `Knowledge Pack`

## 允许直接删除的内容

- 纯重复副本
- 无任何追溯价值的 AI 草稿
- 未被索引且未被任何文档引用的临时中间文件

## Knowledge Repair Record 模板

```markdown
## Knowledge Repair Record

### knowledge_id
- ...

### 业务域
- ...

### 功能点
- [[功能点]]

### 错误原因
- ...

### 被移除入口
- ...

### 替代真源
- ...

### 受影响节点
- ...

### 重新调研范围
- ...
```

## Closeout

只有在以下条件都满足时，才算 repair 完成：

- 旧知识已退出 README 默认索引
- 旧知识已退出默认 `Knowledge Pack`
- 替代真源已写回
- 新 `Knowledge Pack` 已生成
