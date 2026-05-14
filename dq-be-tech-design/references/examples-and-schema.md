# 示例文档与 openspec schema 集成

## 7. 示例文档

**示例 1** `examples/tech_design_reservation_memorabilia.md` — 有库表变更、多领域 DDD、跨域临时直读场景：

- §3 架构图分层（服务调用链路图必须 + 系统架构图按需）
- §5 DDD 实体建模（mermaid classDiagram，聚合根 / 值对象 / 外部只读实体）
- §6 领域服务能力（领域能力语义而非 CRUD 命名）
- §7 库表归属分类（新建表 / 修改表 / 跨域临时直读标注）
- §10 核心流程（mermaid sequenceDiagram，含幂等判断分支）
- "无改动 + 原因"写法示范（§11 / §14 / §15 / §17 / §18）

**示例 2** `examples/tech_design_infra_wx.md` — 无数据库、进程内缓存、外部 HTTP 调用、完整 OAuth2 流程场景：
- §7 库表设计"无改动"写法（纯无状态服务）
- §8 全量 IDL：6 个 RPC + 核心 enum + HTTP 绑定
- §10 flowchart 展示 token 失效兜底重试 + OAuth2 完整流程 + JS-SDK 签名
- §11 服务启动组件有向图（依赖顺序 + watchdog goroutine 生命周期）
- §12 服务目录结构：清洁树 + 短注释 + 职责说明表格写法；`worker/cron/` 承载 jsapi_ticket watchdog 调度
- §15 监控告警具体指标和阈值示范

## 8. openspec schema 集成

把 `tech_design` 注册为 **openspec 原生 artifact**（通过 schema fork），使 openspec 所有命令自动感知。

### source of truth

本 skill 目录下：
```
plugins/dq-be-core/skills/dq-be-tech-design/
├── SKILL.md
└── openspec-schema/
    ├── schema.yaml                   # 完整 schema（spec-driven + tech_design artifact）
    ├── templates/
    │   └── tech_design.md            # 23 节骨架模板
    └── install.sh                    # 业务服务同步脚本
```

### `schema.yaml` 的关键变化（对比 `spec-driven`）

1. **新增 `tech_design` artifact**（插在 design 之后、tasks 之前），`requires: [proposal, design]` 强制顺序
2. **改 `tasks` artifact 的 requires** 加上 `tech_design`

### `install.sh` 用法

在业务服务仓库根（如 `narnia/program/`）执行：
```bash
bash <path-to-tech-spec>/plugins/dq-be-core/skills/dq-be-tech-design/openspec-schema/install.sh
```

动作（幂等）：
1. 检查 `openspec/` 目录存在；若 `openspec/config.yaml` 缺失则兜底生成 `schema: spec-driven`（非交互 init 场景下有用）
2. 若 `openspec/schemas/backend/` 不存在，运行 `openspec schema fork spec-driven backend`
3. 把本 source of truth 的 `schema.yaml` 和 `templates/tech_design.md` 覆盖到 `openspec/schemas/backend/`（通过 `git archive --remote` 从 GitLab 拉取最新）
4. 修改 `openspec/config.yaml` 的 `schema:` 为 `backend`（已是则跳过）
5. 运行 `openspec schema validate backend`
6. 扫 `openspec/changes/*/.openspec.yaml`，列出仍指向非 backend schema 的存量 change（仅提醒，不自动改；若要走 backend 流程手动改 schema 字段）
7. 输出结果

### 工具原生感知效果

| openspec 命令 | 集成后行为 |
|---|---|
| `openspec new <change>` | 自动生成 `tech_design.md` 空模板（23 节骨架） |
| `openspec instructions tech_design --change <id>` | 输出完整 23 节填写指引给 AI |
| `openspec validate` | 校验 `tech_design.md` 存在 + requires 齐 |
| `openspec status` | 跟踪 `tech_design.md` 完成度 |
| `openspec archive` | 归档前 validate；命令本身负责让 `tech_design.md` 随 change 入 archive。后端归档动作还要求同时更新 `openspec/current/tech_design.md` 当前态汇总 |

### 升级路径

`tech-spec` 仓库 schema 更新后：
1. 各业务服务重跑 `install.sh` 同步
2. 新 `openspec new <change>` 自动用新模板
3. 已有进行中的 change 不受影响（文件已存在，不覆盖）
