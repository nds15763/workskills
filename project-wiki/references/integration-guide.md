# Curator / Roadmap 集成指南

project-wiki 不是独立工具——它嵌入三角协作的执行循环中。

## 三角协作角色

| 角色 | Skill | 职责 |
|------|-------|------|
| 主 Agent | — | 读路书、派 Worker、回写路书 |
| Curator | project-knowledge-curator | 知识治理（三色/authority/Repair Loop） |
| Worker | — | 执行任务（只读 Knowledge Pack） |
| **project-wiki** | **本 skill** | **底层工具（Obsidian CLI 封装 + 元数据增强）** |

**project-wiki 补的是底层工具，不替换上层治理。** Curator 的规则定义"什么是对的"，project-wiki 的工具实现"怎么做到"。

## Curator 子能力映射

### knowledge-hit-detect → search.py hit-detect

```bash
python3 scripts/search.py hit-detect "<当前任务关键词>"
```

返回：
- `no_hit` — 无匹配，可能需要新域/新功能点
- `hit_readonly` — 命中有效知识，可直接消费
- `hit_writeback_required` — 灰知识需确权或过期知识需修复

### knowledge-curate → Ingest 操作 + lint.py

Curator 执行 Ingest 工作流（详见 `ingest-workflow.md`），lint.py 做写后验证：

```bash
# 写后验证
python3 scripts/lint.py --domain <业务域> --json
```

### knowledge-link-audit → lint.py

```bash
# 域级审计
python3 scripts/lint.py --domain <业务域>

# 全 vault 审计
python3 scripts/lint.py --json

# 只检查特定项
python3 scripts/lint.py --domain <域> --check links metadata
```

输出格式兼容 Curator 的 `link_health` 接口。

## Curator 读取顺序

```
1. search.py（Obsidian CLI + 元数据增强）  ← 首选
2. MCP fallback                            ← 备用
```

**不要在 Obsidian 不运行时静默降级到 rg/grep。** search.py 会明确报错。

## Gate 系统映射

### 完整执行循环

```
Step 1: 主 Agent 读路书
        → 识别要推进的节点
        → 如涉及代码/设计/排障，先检查业务域

Step 2: Curator 先工作
    ┌────────────────────────────────────────────────────┐
    │  2a. search.py hit-detect "当前任务"                 │
    │      → no_hit / hit_readonly / hit_writeback_required│
    │  2b. search.py search "query" --domain <域>          │
    │      → 排序的搜索结果 + 知识元数据                     │
    │  2c. search.py knowledge-pack --domain --feature-point│
    │      → 完整 Knowledge Pack                           │
    │  2d. lint.py --domain <域>                           │
    │      → 链接健康检查，发现断链先修复                     │
    │  2e. 如发现错知识 → Repair Loop                       │
    │      → 降权 + 归档 + 重新索引 + 新 Knowledge Pack      │
    └────────────────────────────────────────────────────┘

Step 3: 主 Agent 派 Worker
        → 只有 KP-00~KP-03 通过后才可派工
        → Worker Pack = Knowledge Pack 的子集

Step 4: Worker 执行 → 上报 → 主 Agent 回写路书

Step 5: Curator 回写 docs（Wiki 层）
    ┌────────────────────────────────────────────────────┐
    │  5a. 更新业务域 README + [[功能点]] + 叶子文档          │
    │  5b. 三色知识沉淀（新结论 → gray → 确权后 → white）     │
    │  5c. 更新 index.md + log.md                          │
    │  5d. lint.py 写后验证                                 │
    └────────────────────────────────────────────────────┘

Step 6: Closeout
        → KP-04~KP-06 全通过 → 节点转绿
```

### Gate 对应表

| Gate | 名称 | project-wiki 工具 | 通过条件 |
|------|------|-------------------|----------|
| KP-00 | Domain Locked | `search.py hit-detect` | 业务域已确认 |
| KP-01 | Sources Locked | `search.py knowledge-pack` | authoritative sources 已锁定 |
| KP-02 | Conflict Verdict | `lint.py` | 矛盾已裁决或无矛盾 |
| KP-03 | Worker Pack Ready | `search.py knowledge-pack` 输出 | Knowledge Pack 可裁剪为 Worker Pack |
| KP-04 | Docs Writeback Done | Curator ingest + `lint.py` | 文档回写完成且链接健康 |
| KP-05 | Knowledge Repair Closed | `lint.py` | 旧知识退出索引 + 替代真源就位 |
| KP-06 | Node Can Turn Green | 所有上述 | 全部 gate 通过 |

## 引用的 Curator 模板（不复制）

project-wiki 引用但不复制以下 Curator references：

| 模板 | 路径 | 用途 |
|------|------|------|
| Knowledge Pack 模板 | `project-knowledge-curator/references/knowledge-pack-template.md` | `search.py knowledge-pack` 输出格式 |
| 三色沉淀模板 | `project-knowledge-curator/references/tricolor-knowledge-settlement-template.md` | Ingest 时的知识分类 |
| 读写合同 | `project-knowledge-curator/references/read-write-contract.md` | Wiki 读写规则 |
| Conflict Verdict | `project-knowledge-curator/references/conflict-verdict-template.md` | 矛盾裁决 |
| Repair/Discard | `project-knowledge-curator/references/repair-discard-policy.md` | 错知识降权归档 |

## 与 Roadmap 的关系

| | project-wiki | knowledge-curator | roadmap-board |
|---|---|---|---|
| 职责 | Obsidian CLI 封装 + 元数据增强 | 知识治理规则 | 进度管理 |
| 改 vault | Wiki 层（通过 Curator） | 读写（按合同） | 不改（只改 .canvas） |
| 引用关系 | 引用 curator 模板 | 调用 wiki 工具 | 消费 Knowledge Pack |

## 多项目 Vault 配置

| Vault | 路径 |
|-------|------|
| narnia | `/Users/kim/code/narnia/narnia-docs-kim` |
| withvideo | `/Users/kim/code/WithVideo/with_video_obsidian` |
| mewt | `/Users/kim/code/Mewt/docs` |

所有 CLI 通过 `--vault` 参数选择 vault。未来可加 `--project` 参数 + 注册表配置文件。
