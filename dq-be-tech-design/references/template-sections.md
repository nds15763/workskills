# tech_design.md 章节模板

## 2. 文档位置与文件组织

路径随 openspec 走：

```
<repo>/openspec/
├── current/
│   └── tech_design.md             # 当前服务最新技术设计汇总
├── changes/
│   └── <change-id>/
│       ├── proposal.md            # openspec 原生
│       ├── design.md              # openspec 原生（ADR 短风格）
│       ├── tasks.md               # openspec 原生
│       ├── specs/                 # openspec 原生规范片段
│       └── tech_design.md         # ★ 本 skill 新增
└── archive/
    └── <change-id>/               # openspec archive 命令自动归档
        └── ... (同上)
```

**文件组织**：
- **默认**：单文件 `tech_design.md`（23 节用 `## N. 标题` 串联）
- **超长时**：拆 `tech_design/` 子目录（如 `tech_design/data_model.md`），主文件保留作为**总览 + 索引**
- **拆分阈值**：reviewer 判断（经验：>800-1000 行、某节 DDL/proto/图 >300 行）
- **当前态汇总**：`openspec/current/tech_design.md` 保存服务当前最新技术设计；它不是某个 change 的历史记录，归档动作中要用该 change 的最终方案更新它

**当前态汇总规则**：
- 首次归档时若 `openspec/current/tech_design.md` 不存在，先创建目录和文件。
- 内容格式复用本 23 节 `tech_design.md` 骨架，但正文写服务当前状态；不要保留 change 过程叙事、评审过程、临时方案。
- 后续归档只合入本 change 已落地并通过 QA 的最终方案；未落地、已废弃、仅讨论过的方案不进入当前态汇总。
- 多个 active change 并行时，按实际完成归档的顺序合入当前态汇总；若后归档 change 覆盖先前设计，以最新已归档状态为准，并在对应 change 的 `tech_design.md §23` 记录方案变动。

**团队既有 side files**：
- 新 change 库表设计统一在 `tech_design.md` §7；大块 DDL 可外挂 `tech_design/data_model.md`

## 3. `tech_design.md` 23 节骨架

每节**标题必须出现**；触发则实写，不触发则正文写 `无改动` + 一行原因（反向验证作者每节都考虑过）。

**可扩展性**：23 节是**基线骨架**，不是上限。如果 change 性质特殊、需要补充额外章节或图形（如额外的架构视角、性能估算、容量评估、安全威胁建模、第三方合规、A/B 实验方案等），可以在合适位置**动态新增章节**（§24 / §25 …）或在既有章节内加子节，不必强行塞进现有 23 节。原则：**骨架不删、按需扩展**。

**图形约定**：流程图、时序图、架构图等图形内容**优先使用 mermaid 格式**（可 diff、版本管理友好）。

### 必填节（所有档位都要实写）

**1. 目标** — 1-3 段 what + why，技术视角（与 proposal 呼应）

**2. 需要pm或者其它相关方决策和讨论的点** — 需要产品、运营、设计、法务、数据、上下游 owner 等相关方拍板或讨论的问题

**3. 整体架构**
- **必须有：服务调用链路图**
  - 格式：`flowchart TB`
  - **按服务/仓库边界分组**：**每个服务（或仓库）的内部组件用一个 subgraph 框起来**，subgraph 标题写服务名（可带部署端口 / 协议），让读者一眼看出哪些节点属于同一个服务
  - 外层再按逻辑边界分组（如"调用方"/"网关层"/"业务服务层"/"存储层"/"外部依赖"）
  - 调用箭头用编号 ①②③ 标注；图下方配**调用时序表格**（列：# / 调用路径 / 协议·路径 / 动作）
  - 数据库节点用 `[(text)]` 风格，列出本 change 涉及的表
- 按需提供（一个或多个，mermaid 优先）：
  - **用例图**（有多角色 / 新增用户可见能力时）：`flowchart LR`，Actor 用 `([角色])` 圆角，system 边界用 subgraph；回答"谁能做什么"，展示系统边界与角色能力总览
  - **系统分层架构图**（新服务 / 跨多服务时）：`flowchart TB` 上下分层，每层一个 subgraph，从上到下：入口层 → 业务领域层 → 公共领域层 → 基础组件层。**粒度到服务/仓库为止**（每个节点是一个服务或一个仓库；**不展开服务内部组件**——内部结构见 §12 服务目录结构）。回答"各服务在哪层、依赖方向如何"
  - **数据流向图**（消息驱动 / 多写 / ETL 场景）：`flowchart LR`，展示数据在服务间的产生 → 加工 → 流转路径
- 服务清单：表格 `服务 | 职责`，每行 1 句话

**两图职责区分**（避免混淆）：

| 图 | 视角 | 最小元素 | 回答的问题 |
|---|---|---|---|
| 服务调用链路图 | **运行时 / 动态** | 服务内部组件（subgraph 框出服务边界） | 一个请求怎么走 / 调用顺序 |
| 系统分层架构图 | **静态 / 层次** | 服务 / 仓库 | 各服务在哪层 / 依赖方向 |
| §12 服务目录结构 | **服务内部代码** | 文件 / 目录 | 服务内部代码怎么组织 |

### 条件必填节（章节必有，不触发写"无改动"+原因）

**4. 服务职责边界**
- 触发：多服务 / 新服务
- 格式：表格 `组件 | 职责 | 不做什么`

**5. 领域实体关系（DDD）** ← 领域建模视角
- 触发：新聚合 / 新实体 / 改聚合边界
- 格式：mermaid classDiagram 或文字，说明实体 / 值对象 / 聚合根 / 关系（1:N / N:M / 归属）
- **类图 MUST 用 DDD stereotypes 标注**：`<<ValueObject>>` / `<<AggregateRoot>>` / `<<Entity>>`；关系箭头用 `"1" --> "N"`（组合 / 归属）或 `..>`（依赖 / 使用）。示例见 `examples/tech_design_infra_wx.md` §5
- **类图节点必须是代码中真实存在的 struct / interface**，禁止虚构聚合类名（如 `NotificationAggregate`）或把 DTO / 请求结构（如 `SendNotifyReq`）当作聚合成员
- 与 §7 区别：这里是**领域建模视角**（谁聚合谁），§7 是**库表设计视角**（DDL / gorm tag）

**6. 领域服务能力（DDD）** ← 领域能力视角
- 触发：新增或修改 domain_service 方法
- 格式：每项含 能力名 / 输入 / 输出 / 前置条件 / 业务不变量
- **必须用领域能力语义**（"用户注册"/"订单结算"/"直播上架"），**不是 curd**
- 与 §8 区别：这里是**领域能力语义**（做什么业务），§8 是**接入层接口**（怎么调）

**7. 库表设计** ← 持久化视角
- 触发：库表变更
- 格式细分：
  - **新建表**：完整 CREATE TABLE 语句 + 派生状态说明
  - **修改表**：完整 CREATE TABLE 语句（标注变更字段）+ 影响评估（数据迁移见 §16）
  - **跨域临时只读表**：完整 CREATE TABLE 语句 + 标注 `[跨域临时]` + owner 服务 + 本 change 消费字段
- **表归属分类**：
  - **本领域/服务直接管理的表**：本服务 owner，可读写
  - **跨领域/服务的表**（临时直接读）：理论上应调用对应服务接口；当前考虑成本暂时直接读，须标注 `[跨域临时]`，后续纳入技术债偿还

**8. Proto 契约**
- 触发：idl 变更
- **idl 仓库**：所有 proto 和生成产物统一放在 `gitlab.daqian369.com/esm/narnia/idl`；业务服务不放 `api/` / `proto/` 目录，只 import `gitlab.daqian369.com/esm/narnia/idl/...`；详见 `dq-be-idl-convention` skill 和 idl 仓库 README
- 格式：
  1. IDL 仓库路径 + `go_package` 声明（`gitlab.daqian369.com/esm/narnia/idl/gen/go/...`）
  2. 文件清单：每行 `proto 文件（新建/修改）— 变更点一句话`
  3. 每个文件单独一个小节，包含实际 protobuf 代码（message / enum / service RPC 注册 + HTTP 路径绑定）；单文件内容较长时可在小节内分组（先列 message/enum，再列 service），但以文件为单位划定小节
  4. 如有公共约定（分页 cursor 编码、错误码规则等）单独一节说明

**9. 状态机**
- 触发：引入/修改状态机
- 格式：mermaid stateDiagram-v2；列出状态、转换、触发事件、守卫条件；附状态说明表格

**10. 核心流程**
- 触发：新流程 / 流程变更
- 格式：mermaid 时序图 / 流程图 / 伪代码

**11. 服务启动**
- 触发：新服务或启动顺序变更
- 格式：main 初始化顺序 / 依赖关系
- **推荐格式：ASCII 树**（`├─ │ └─`），line-oriented，易 grep / diff；只有复杂依赖（如启动期多 goroutine 生命周期交织、分支并发）才用 mermaid flowchart
- 示例见 `examples/tech_design_infra_wx.md` §11

**12. 服务目录结构**（服务内部代码架构）
- 触发：新服务或结构大调
- **定位**：本节体现**服务内部的代码分层架构**（和 §3 系统分层架构图的服务/仓库粒度对齐，互为层级——§3 看多个服务怎么排，本节看单个服务内部怎么拆）
- 对照 `dq-be-code-structure` 规范
- **展示格式**：清洁树（树内只写短注释：≤10 个汉字当量，英文标识符按 1 个计，混合时目测一行不超过 20 字符；自解释文件名不加注释）+ 树下方"各层职责说明"表格（`路径 | 职责`，完整描述每个文件）；完整类型列表、详细说明等移到表格，避免树内换行
- **最小示范**（完整示例见 `dq-be-code-structure`）：

  ```
  <service>/
  ├── cmd/<service>/main.go
  ├── internal/
  │   ├── handler/                   # gRPC 入口（每 RPC 一文件）
  │   ├── domain_service/            # 业务聚合服务
  │   ├── infra/                     # 进程单例基础设施
  │   └── model/                     # 跨聚合数据类型
  └── ...
  ```

- **定时任务**：周期性后台任务（如 watchdog goroutine 预刷缓存）归 `worker/cron/`（调度接入层：负责"何时触发"）；实际业务逻辑仍在 `domain_service/`（负责"触发后做什么"），两层各司其职；与 gRPC server 同进程运行时无需独立 `cmd/worker/` 二进制
- **不触发的层**（表格或正文注明原因）：
  - `repository/db/`：无 mysql / gorm 持久化需求时跳过（纯无状态服务）
  - `biz_service/`：符合 `dq-be-code-structure` §2.4 判定（单 domain_service 方法 + 无跨域编排 + 无事务）时跳过，注明原因

**13. 错误码规范**
- 触发：新增业务错误码
- 格式：表格 `code | HTTP | 语义`
- **gRPC + BaseResp A 模式服务**（handler 返 `(resp, nil)`，错误经 `BaseResp.status_code` 传递）可省 HTTP 列，改用 `RPC | 错误码常量 | 触发条件` 三列（见 `examples/tech_design_infra_wx.md` §13）
- **命名规范**：遵循 `narnia/idl/error_code.go` 约定
  - 常量名：`Err<Service><Method><ErrorType>[Fatal]`，PascalCase；例：`ErrProgramCreateReservationNotFound`、`ErrInfraWxGetOAuthURLInvalidParameter`
  - 数值：通过 `idl.ComposeErrorCode(product, service, module, method, errorType, fatal)` 组合，统一在 `narnia/idl/error_code.go` 登记
  - 错误类型：`InvalidParameter` / `Unauthorized` / `NotFound` / `Conflict` / `Internal` / `TooManyRequests` / `Unavailable`；致命错误加 `Fatal` 后缀
  - 详细规范见 `narnia/idl/error_code.go` 及 `dq-be-libs` skill

**14. 日志规范**
- 触发：新增关键事件日志
- 格式：event 名 / 字段列表 / 示例
- 日志工具（`logutil.Setup` / `logx` 结构化日志 / ctx 字段自动抽取）使用规范见 `dq-be-libs` §2.3
- 日志 level / 字段脱敏 / 采样策略等细则：本节落地各 change 的具体事件，通用约定在 `dq-be-libs` 补齐

**15. 监控 / 告警**
- 触发：新增指标 / 告警点
- 格式：指标名 / 维度 / 告警阈值

**16. 数据迁移**
- 触发：存量数据处理
- 格式：迁移脚本 / 双写策略 / 校验方案

**17. 兼容性 / 灰度 / 回滚**
- 触发：有线上兼容考量
- 格式：向前/后兼容策略 / 灰度步骤 / 回滚脚本

**18. 部署**
- 触发：新服务 / 新增依赖资源 / 已有资源容量变更 / 明确依赖的环境变量
- 格式：K8s Deployment / 副本数 / 资源预估 / 依赖集群 / 环境变量
- 明确新增依赖资源是否需要部署（如 Redis / MQ / MySQL schema / 对象存储 / 定时任务 / 第三方服务配置等）
- 明确已有依赖资源是否需要扩缩容（如实例规格 / 副本数 / 连接数 / topic 分区 / 存储容量 / QPS 配额等）
- 明确依赖的环境变量是否已配置；若未配置，列出新增 / 修改的变量名、环境范围和配置来源
- 具体详细信息参考：https://gitlab.daqian369.com/esm/narnia/deploy.git

### 必填节（末尾）

**19. 风险 & 兜底** — 即使无重大风险也要写"主要风险评估"一段；格式：表格 `风险 | 应对`

**20. 不在本设计范围** — 显式圈边界，避免 scope creep

### 选填节

**21. 参考 / 相关文档** — PRD / 上下游 tech_design / 外部资料链接

**22. todo事项** — 设计阶段未定的技术点或后续待办（后续 change 或 TODO 跟进）

### 必填节（末尾 · 贯穿生命周期）

**23. 变更点核心记录** — 贯穿整个 change 生命周期，**每次 tech_design 方案层面调整后**记录一行

- 目的：reviewer 看最新几行就能聚焦 tech_design 变动，不用比 diff 全文；commit_id 提供"记录时刻 tech_design 精确状态"的溯源锚点
- 评审时机（技术设计阶段 / 开发联调阶段 / 测试阶段）和详细流程见 §5.2；本节只讲记录机制本身
- 格式：表格 `# | 变更点名 | 时间 | commit_id | 变动摘要 | reviewer`

**触发机制（统一）**

作者一句话触发，例如 **"在 tech_design 里记录一个变更点"** / "登记变更" / "变更点核心记录加一条"（等价同义）。AI 收到后：

1. 读取当前 tech_design 所在 commit：`git log -1 --format=%h -- openspec/changes/<id>/tech_design.md`
2. 读取**自上一条 Log 记录的 commit_id 以来**的 tech_design.md diff（首次则取完整文件）
3. 梳理**方案层面**变动（库表字段 / 流程分支 / 契约调整 / 风险评估；typo / 格式 / 措辞不记）
4. 追加一行：新序号、当前日期、commit_id、变动摘要、reviewer（作者可选提供）

**记录粒度**：只记核心方案变动。

**作用**：
- reviewer 按 §5.2 时机进来 review，看 Log 自上次自己评审的 commit_id 之后新增的所有行聚焦变化
- `git show <commit_id>:path/to/tech_design.md` 可查记录时的快照

示例：

| # | 变更点名 | 时间       | commit_id | 变动摘要                                                      | reviewer   |
|---|---|------------|-----------|---------------------------------------------------------------|------------|
| 1 | 初稿 | 2026-04-25 | abc1234   | 初稿                                                           | @me        |
| 2 | 加 wx_open_id | 2026-05-03 | def5678   | §7 表加 wx_open_id 字段；§10 补幂等判定分支；§19 补并发 race      | @colleague |
| 3 | 加分布式锁 | 2026-05-05 | e9a0b12   | §10 加 redis 分布式锁（QA 发现 CheckReserved race）               | @me        |

### 常见反例与纠正

- **反例 1**：服务调用链路图把多个独立服务挤在一个 subgraph 里（如 `CALLERS` 里塞了 program / bagel / 前端）
  → **纠正**：每个独立服务 / 仓库各占一个 subgraph；外层按逻辑边界（调用方 / 网关 / 业务 / 外部）再分组时，同名 subgraph 只聚合同质节点（如"调用方"只放客户端，不放 gateway）
- **反例 2**：系统分层架构图展开了服务内部组件（handler / domain_service / infra ...）
  → **纠正**：系统分层图粒度到"服务 / 仓库"为止，每个节点是一个服务；服务内部结构放 §12
- **反例 3**：领域实体图用虚构聚合类名（如 `NotificationAggregate`）+ DTO（如 `SendNotifyReq`）当作聚合成员
  → **纠正**：类图节点必须是代码中真实存在的 struct / interface，DDD stereotypes 明确标注类型（见 §5）
- **反例 4**：服务启动用 mermaid flowchart 堆砌 Init 步骤
  → **纠正**：ASCII 树对顺序性步骤更紧凑（见 §11）；mermaid flowchart 只用于有分支 / 并发 goroutine 的复杂启动
