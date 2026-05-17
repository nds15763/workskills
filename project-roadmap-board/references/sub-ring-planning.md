# 子环规划 / 建板视图 vs 执行视图（v2 补充）

> **公理**：这份文档是对 `rules.md` 规则 3 / 规则 6 / 规则 0K 的**补充层**，不替换它们。
>
> **触发来源**：2026-05-17 narnia/66bian 项目实战教训 — 用户拍 "就一层?"，对 grey WB 没展开 runtime 表示不满。

## TL;DR

| 视图 | 适用场景 | 灰节点 runtime 子环 | 黄节点 runtime 子环 |
|---|---|---|---|
| **建板视图** (planning) | PRD/OpenSpec 已就绪、用户想看完整施工蓝图 | **允许预画**（结构可见）| 必须有 |
| **执行视图** (execution) | 工作流真实推进中 | 禁止有（per rule 6）| 必须有 |

**关键判定**：用户问"为什么 WB2 是空的？"或者"就一层吗？" → 是建板视图诉求 → 允许预画 grey runtime 子环。

---

## 1. 视图区分

### 建板视图 (Planning View)

**目标**：把"完成这件事必须闭合哪些可验收工作块"全景一次性展示给 reviewer。

**形态**：
- 所有 WB（含 grey/yellow）都展开 runtime 子环
- 每个 runtime 节点严格按 **实现 / 验证 / 证据** 三件套排
- 每个 runtime 节点 link to **`details/T#.md` 详细设计**（详见 §3 IO/Gate 三件套）
- 父 WB 颜色用 **yellow** 标"结构已知 + 等待执行 或 执行中"语义
- 灰 runtime 子节点表示"未派工"

**为什么 yellow 不仅是"in progress"**：
- 当 WB 处于"已规划 + 结构可见 + 等待派工"时，semantic 上跟"executing in progress"一致——结构已就位，差最后一步 trigger
- 灰色严格保留给"未规划 / 未触及 / 不知道里面是什么"的真正未触地节点
- 这跟 rule 6 不冲突——rule 6 保护的是"不要预先猜结构"，但建板视图是"用户已经讨论清楚结构了，只是还没派工"

**示例**：本次 `66bian_roadmap.canvas` (8 WB 全展开)
- WB0 设计就绪 (7 节点, 全 green)
- WB1 起手 (9 节点, 3 green + 4 grey, parent yellow)
- WB2 双流并行 (24 节点, 全 grey, parent yellow ← 已规划)
- ...
- WB5 Phase D (16 节点, 全 grey, parent yellow ← 已规划)

总 88 个施工节点 / 0 P0 违反。

### 执行视图 (Execution View)

**目标**：每天看进度，知道当前真在哪。

**形态**：
- 只 yellow WB 有展开的 runtime 子环
- grey WB 是单 box（rule 6 严格生效）
- 派工 trigger 时 grey → yellow + 展开 runtime（规则 3 触发）

**示例**：rules.md 规则 3 + 规则 6 描述的经典形态。

### 何时用哪种视图？

| 决策点 | 用哪种 |
|---|---|
| PRD/OpenSpec 设计阶段，用户要看全景 | 建板视图 |
| 设计完，开始落代码，进度跟踪 | 执行视图 |
| `/goal status` 调用 | 当前在哪个 phase 就用哪个 |
| 用户问"为什么只有一层？" | 切到建板视图 |

**主 Agent 自检**：grey + runtime children → 先问"用户是要建板还是执行视图？" 不要直接走 rule 6 拒绝。

---

## 2. Runtime 节点 三件套（实现 / 验证 / 证据）

**每个施工 task 在 runtime 子环里至少要有 3 类节点**（不一定 3 个，可以 N 个）：

| 类 | 内容 | 颜色 |
|---|---|---|
| **实现** | 写代码 / 跑 DDL / 配 CI | 灰 (未派工) → 黄 (worker 在做) → 绿 |
| **验证** | 单测 / build pass / SHOW CREATE | 同上 |
| **证据** | 提交 commit hash / DB 状态 / 飞书 sync rev | 同上 |

**为什么需要三件套？**
- 单纯写"实现 T2 insert.go"不知道怎么 close —— 单测有没有过？code review 谁批的？
- 三件套强制让闭环成立：worker 跑完 → 验证 pass → 证据落地 → runtime 全绿 → 父 WB 转黄候选
- 跟规则 12（代码型 Worker 必须拿 Knowledge Pack）+ 规则 19（回写顺序不可颠倒）+ 规则 20（变绿要 docs 证据）匹配

**实战例子**（来自 66bian roadmap WB1）：

```
WB1 (parent yellow)
  ├─ 调查 火山 product_esm DB 现状 (实现+验证+证据合一; 用户已跑 → green)
  ├─ T1.a 实现 game_rounds DDL ALTER on staging (green)
  ├─ T1.b 实现 game_round_members DDL ALTER on staging (green)
  ├─ T4 实现 round/contract.go (grey, 待派)
  ├─ T4 验证 go build + interface signature locked (grey)
  ├─ T1 证据 SHOW CREATE TABLE 对齐 spec ③ §7 (grey)
  └─ T4 证据 contract_test.go pass + spec mirror (grey)
```

**反模式**：
- ❌ "完成 T4" 单节点（缺验证 + 证据；不知道怎么 close）
- ❌ "T4 实现 / T4 验证 / T4 上线" （上线≠证据，太具体；证据应该是"docs writeback + commit hash"）
- ❌ 全合并成 "T4 实现+验证+证据"（太粗，无法跟踪 partial progress）

---

## 3. IO / Gate 三件套（input / output / Gate）

**每个 runtime 节点对应一份 details/T#.md 详细设计**，§2 必须明确写：

| 维度 | 内容 |
|---|---|
| **输入** | 上游 task 产物 + spec / IDL / DB schema / 配置等所有 prerequisites |
| **输出** | 本 task 交付的具体文件 / 接口 / DB schema / proto / config |
| **Gate（校验契约）** | 自动化测试 + 验收标准 + spec 对齐性检查 |

**为什么需要 IO/Gate 三件套？**
- 单纯"实现 T2 insert.go"没有约束 — worker 可能写出跟其它 task 冲突的产物
- IO 三件套强制 task 之间形成显式 dependency 链 (上游 output = 下游 input)
- Gate 三件套强制每个 task 的"完成"是可机器验证的，不靠主观判断

**示例**（来自 details/T4-round-contract.md §2）：

```markdown
## §2 输入 / 输出 / Gate

| 维度 | 内容 |
| **输入** | (1) ③ §6.X 7 方法签名表; (2) ③ §6.Y Context lifecycle 字段表; (3) idl gen/go/narnia/games/game_round.pb.go; (4) idl gen/go/narnia/gsc/v1/gsc.pb.go; (5) services/gsc 现有目录树 |
| **输出** | (1) services/gsc/internal/narnia/gsc/round/contract.go (~200 行); (2) round/doc.go (~30 行); (3) round/contract_test.go (~50 行) |
| **Gate** | (1) go build exit 0; (2) go vet 无 warn; (3) 7 方法签名 vs ③ §6.X 一对一 match; (4) Context 字段 vs §6.Y 一对一; (5) import 无 cycle; (6) 没有 method body |
```

**反模式**：
- ❌ 输入只写"详细设计 spec" — 太抽象，worker 不知道具体读哪节
- ❌ 输出只写"实现完毕" — 不知道交付什么文件
- ❌ Gate 只写"测试通过" — 不知道测什么场景

---

## 4. details/ 子目录约定

**位置**：`openspec/changes/<change>/details/`

**文件命名**：
- `_io_chain.md` (master IO 拓扑图，第一个读)
- `T1-<short-name>.md`, `T2-<short-name>.md`, ... (平台/工具层)
- `B1-<short-name>.md`, `B2-<short-name>.md`, ... (业务层)
- `D1-<short-name>.md`, ... (deferred / migration)

**每份 details/T#.md 严格 9 节模板**：

| § | 内容 |
|---|---|
| 1 | 任务概述 (what + why + spec source) |
| **2** | **输入 / 输出 / Gate 表**（**§3 强制要求，单独成节**） |
| 3 | 文件清单（新建 / 改动 / 路径） |
| 4 | 接口 / 结构定义（**产品级 Go 代码 / SQL DDL / proto，不是伪码**） |
| 5 | 实现细节（算法伪码 + SQL 模板 + 错误处理 + 日志结构） |
| 6 | 上下游关联（依赖链 + 解锁链 by KP gate） |
| 7 | 测试方案（unit + integration + E2E 场景表 + 断言点） |
| 8 | 验收标准（gate 全过 + spec 对照） |
| 9 | 风险 + 缓解（边界 + 命名冲突 + 性能） |
| 10 | 落地步骤（按序执行） |
| 11 | 派工建议（worker skill + 估时 + allowed/forbidden write） |

**`_io_chain.md` 总图**：
- 列出所有 task 的依赖关系（顶端 task = 起点，底端 task = 终点）
- 用 ASCII 图或 mermaid 表达 IO 拓扑
- 跟 spec.json runtime 顺序一致

**示例**（来自 66bian 项目）：

```
openspec/changes/add-gsc-runtime-domain-and-rounds/details/
  _io_chain.md (总图 — 13 task IO 闭环)
  T1-game-rounds-ddl.md
  T2-idempotent-insert.md
  T3-insert-retry-fallback.md
  T4-round-contract.md
  T5-round-projector-registry.md
  T6-status-state-machine.md
  T7-monitoring.md

openspec/changes/add-morph66-game/details/
  B1-morph66-round-struct.md
  B2-morph66-reducer.md
  B3-morph66-projector.md
  B4-audience-interaction-client.md
  B5-fused-image-award-gate.md
  B6-morph66-e2e.md
```

---

## 5. spec.json runtime 节点 link to details/

**约定**：spec.json 中每个 runtime 节点的 `materials` 数组应该 link to 对应的 `details/T#.md` 路径，让主 Agent 在派工时能自动加载完整 Worker Pack。

**示例**：

```json
{
  "id": "WB1 Phase A 起手",
  "state": "yellow",
  "runtime": [
    {"id": "T4 实现 round/contract.go", "state": "grey"},
    {"id": "T4 验证 go build + interface signature locked", "state": "grey"},
    {"id": "T4 证据 contract_test.go pass + spec mirror", "state": "grey"}
  ],
  "materials": [
    {"id": "说明 详细设计 details/T4-round-contract.md"}
  ]
}
```

主 Agent `/goal advance WB1.T4` 时自动 read `details/T4-round-contract.md` + 注入 Worker Pack。

---

## 6. 复检 / 一致性审计 pattern

**触发**：用户问"我们之前对话所描述的事实和逻辑链，是否对应？"或者"路书 task 是否如规划的？"

**步骤**：
1. read canvas 实际节点（python 解析 json.load）
2. read spec.json 实际定义
3. read details/_io_chain.md 拓扑
4. 对比 details/T#.md §2 IO/Gate 跟 canvas runtime 是否对齐
5. 列出 4 维一致性表（spec source / spec.json / canvas / details）
6. 找 mismatch → 修正
7. 重新生成 canvas + audit

**示例**：本次会话末段做的"复查"实战。

---

## 7. 实战案例索引

完整落地路径（学习模板）：

| 资源 | 路径 |
|---|---|
| Roadmap canvas | `narnia-docs-kim/GSC/66bian_roadmap.canvas` |
| Spec.json | `narnia-docs-kim/GSC/66bian_roadmap.spec.json` |
| Details 集合 | `narnia/dev/openspec/changes/add-gsc-runtime-domain-and-rounds/details/` |
| IO 总图 | `details/_io_chain.md` |
| Kickoff prompt | `narnia-docs-kim/GSC/66bian_goal_kickoff_prompt.md` |
| 决策卡 canvas | `narnia-docs-kim/GSC/GSC morph66 改动.canvas` (box0032-box0045) |
