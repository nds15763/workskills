# 评审流程与 change 生命周期

## 4. `design.md` 与 `tech_design.md` 的职责划分

| 文件 | 视角 | 风格 | 长度 |
|---|---|---|---|
| `design.md` | ADR 决策记录 | openspec 原生（Context / Goals·Non-Goals / Decisions / Risks / Migration / Open Questions） | 短（1-2 页） |
| `tech_design.md` | 完整实现设计 | 本 skill §3 的 23 节模板 | 中-长（100-800 行视规模） |

**约定**：
- `design.md` 顶部加跳转：`> 详细后端技术设计见 [tech_design.md](./tech_design.md)`
- 两者信息不重复；冲突时 `tech_design.md` 为**实现权威**，`design.md` 为**决策权威**

## 5. 评审流程（人工确认 + 多次 review）

### 5.1 实施前人工确认要求

只要一个 change 产出了 `tech_design.md`，进入具体实施前必须有**人工明确确认**。

**约定**：
- AI 起草 `tech_design.md` 后，只能协助修改、补充、解释方案；不能自行判断"已通过"并进入实施。
- 人工确认可以来自作者或 reviewer，表达可以是"tech_design 已确认，可以实施"、"首轮 review 通过，继续开发"、"按这个方案做"等明确继续信号。
- 在 `tech_design.md` 仍处于待 review、待确认、待补充问题阶段时，AI 不得通过任何路径进入实施，包括但不限于触发 apply / 开始实施入口、读取 `tasks.md` 执行、使用 `executing-plans` / `subagent-driven-development` 执行计划、拆 `tasks.md`、开始改业务代码。
- 没有明确人工确认时，即使 AI 已完成自审、文档没有收到反对意见，也视为**不能进入实施**。

### 5.2 多次 review 时机

人工评审完全以 `tech_design.md` 为准。一个 change 的生命周期里原则上 2-3 次 review：

| Review | 阶段 | review 目标 | 主检查 |
|---|---|---|---|
| **技术设计阶段** | 初稿完成、动手写代码前 | **对整份 tech_design 的初稿 review**（方案可行性、领域建模、契约） | 必须获得人工明确确认后才能进入实施；AI 不得默认通过 |
| **开发联调阶段** | 代码开发 + 联调 + 自测通过后 | **仅对自首次 review 以来 tech_design 有调整的部分 review**（不是全文重 review） | 看 §23 变更点核心记录自上次本人 review commit_id 之后新增的行；核对实现和调整后的 tech_design 一致；无调整则跳过 |
| **测试阶段**（按需）| QA 测试期间，方案层面有修改时 | **仅对自开发联调 review 以来 tech_design 有调整的部分 review**（不是全文重 review） | 看 §23 变更点核心记录自上次本人 review commit_id 之后新增的行；QA 修复若只是代码 bug（无方案变化）则不触发 |

**关键点**：
- 首轮（技术设计阶段）是对 tech_design **初稿的完整 review**
- 后续轮次（开发联调 / 测试阶段）是**变动部分的聚焦 review**，不是对整份重新 review
- 若上一轮之后 tech_design **完全没动**，可以跳过下一轮
- AI 读 §23 上次登记以来的 diff 自动梳理变动（见 §23 触发机制），reviewer 直接看变更点核心记录最新一行定位变化点

### 5.3 AI Native 操作流程

1. AI 起草 `tech_design.md` 初稿（必填节实写，条件节按触发或写"无改动"）
2. 本人自审（重点校验 §5 领域实体关系 / §6 领域服务能力 / §7 库表设计）
3. 人工 review `tech_design.md` 初稿；如有意见，AI 继续修改文档
4. 作者或 reviewer 明确确认 `tech_design.md` 可以进入实施
5. **作者触发实施入口**进入实施：具体入口按 `dq-be-dev-practice` 的 Agent 入口抽象映射；superpowers + openspec 流程可使用 `executing-plans` / `subagent-driven-development` 执行计划
6. 开发中 tech_design 被 update：小改不必重开 review；**大改动**作者说一句，AI 同步改 §23，并等待人工确认后再继续按新方案实施
7. 开发 + 联调 + 自测完成 → **作者触发"登记变更"**（或同义，如 "变更点核心记录加一条"）→ AI 读 git diff 梳理核心方案变动追加一行 → 触发第二次 review
8. QA 期若方案有变化 → **作者触发"登记变更: <QA 发现的问题简述>"**（同上）→ AI 同上梳理
9. 所有 review 通过、服务发布前 → 执行归档动作（更新 `openspec/current/tech_design.md` 当前态汇总 + `openspec archive` 归档 change）

## 6. 生成时机（openspec 工作流）

**固定顺序**（由 schema `requires` 字段强制）：

```
proposal → design/spec → tech_design → 人工确认 → tasks → 实施 → archive
```

### 6.1 生成步骤

1. `openspec new <change-id>` 创建 change 骨架
2. 填写 `proposal.md`（需求视角：what / why / non-goals / 验收）
3. 填写 `design.md`（ADR 决策：关键技术选择 / trade-off，简短）
4. **填写 `tech_design.md`**（实现视角：本 skill §3 的 23 节展开）
5. 人工明确确认 `tech_design.md` 可以进入实施
6. 基于已确认的 tech_design 拆 `tasks.md`
7. 进入实施 → 开发联调阶段 review → 测试阶段 review（按需）→ QA 测试完成后执行归档动作

### 6.2 change 的使用原则（硬性）

- **一个需求 = 一个 change**：该需求所有改动全部体现在同一 change 中，不拆分
- **例外**：完全独立、可解耦、且明确要分开推进的，可各开独立 change
- **仓库内自闭环**：每个仓库 / 服务都维护自己的 openspec change、archive 和 `openspec/current/tech_design.md`；读者在仓库内必须能理解本仓库当前设计和历史变更
- **跨多仓库**：每个仓库各自独立 change（仓库级变更记录），详见 `dq-be-dev-practice` §3.4
- **公共承载**：跨多端 / 多仓库 / 大领域垂直链路需要统一视图时，公共内容放 `gitlab.daqian369.com/esm/narnia/dev`（详见 `dq-be-dev-practice` §3.5）；该公共承载只做汇总和追溯入口，不替代各仓库自己的 change 与当前态 tech_design
- **change 贯穿整个生命周期**：从 proposal 到最终**服务发布前归档**，期间所有 review（技术设计 / 开发联调 / 测试阶段）和实施都在这一个 change 里
- **必须归档**（硬约束）：
  - 归档时机：代码已合入 + tasks 全勾完 + QA 测试完成
  - 归档动作：更新 `openspec/current/tech_design.md` 当前态汇总，并执行 `openspec archive --change <change-id>`；两者是同一个归档节点的必做动作，缺一不可
  - 人工确认：归档动作整体必须由作者明确确认；AI 不得只更新 current 或只执行 archive，也不得在未确认时先改 current
  - 每个 change 的 `tech_design.md` 随 change 进入 archive，作为历史快照；`openspec/current/tech_design.md` 保留服务当前最新技术设计，作为后续开发和排查的当前态入口
  - 活跃 change（未 archive 的）表示"还在开发中"；如果一个 change 长期不归档，说明进度停滞或遗漏归档，都要处理
  - `openspec status` 可查当前所有活跃 change；review 会议上可一起过一下

### 6.3 AI Native 节奏建议

- AI 可在 proposal 完成后主动起草 design + tech_design 双份草稿
- 提交 review 可以一起（先 design 后 tech_design），主要评审 tech_design
- 实施入口按 `dq-be-dev-practice` 的 Agent 入口抽象映射；openspec-only / superpowers + openspec 的执行序列以 `dq-be-dev-practice` 为准
- 多轮 review 节奏见 §5.2
