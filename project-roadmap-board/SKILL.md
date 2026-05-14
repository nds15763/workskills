---
name: project-roadmap-board
version: 2
description: >-
  管理 Obsidian Canvas 格式的项目进度路书。路书第一语义是
  “完成某件事的闭环”：从开始到结束必须闭合哪些可验收工作块、
  每个工作块如何推进、验证、裁决和回退。覆盖两条主线：
  建板（PRD/OpenSpec 材料池 → 事实卡 → 闭环工作块 → runtime group 细节 → 锚点）
  执行（竖向首环主干"开始在下、结束在上自下而上推进"、
  横向运行时 group "P + 全部 runtime / 子链递归被 canvas.group 圈住"、
  灰黄红绿四色传播、未决点演化、错知识反路径、
  主 Agent / Knowledge Curator / Worker 三角协作、KP-00~KP-06 gate）。
  当用户提到路书、项目板、进度板、联调路书、canvas 状态管理、节点推进、
  节点闭环、扇出工作、SubAgent 协作、知识校准、文档驱动时使用。
---

> **公理继承 / Axiom Inheritance**
> 本 skill 服从顶层公理 `typed evidence gates action`——
> 未经类型化（三色 + authority + kind）的上下文不允许驱动行动。
> 在该公理下，本 skill 的职能：把类型化知识编译成 Canvas 路书的合法执行单元（工作块 + 锚点 + KP gate）

# Project Roadmap Board

执行位置：仓库根目录。

## 强制前置

**在执行任何路书相关操作之前，必须先完整读取本 SKILL.md。**

路书 `.canvas` 文件是唯一的进度真源。所有进度变更必须直接修改 `.canvas` 文件。

**禁止**用 `.md` 文件（如 `orchestration.md`）替代 `.canvas` 来记录或管理进度状态。`.md` 文件只能作为路书的配套摘要，不能成为进度的主载体。

如果任务包含代码、设计、排障或方案裁决，必须同时加载 `project-knowledge-curator` skill；没有业务域时，先问用户业务域，不能直接派 Worker。

## Canonical Paths

本仓库 skill 通过 git submodule 挂载在 `submodules/skills/`。从仓库根访问时使用以下路径；如果 host 仓库挂载位置不同，自行替换前缀。

- Skill 入口：`submodules/skills/project-roadmap-board/SKILL.md`
- 详细规则：`submodules/skills/project-roadmap-board/rules.md`
- 标准范例：`submodules/skills/project-roadmap-board/examples.md`
- 共享常量与几何工具：`submodules/skills/project-roadmap-board/geometry.py`
- 自动校验脚本：`submodules/skills/project-roadmap-board/audit.py`
- 正向布局生成脚本（JSON spec → .canvas）：`submodules/skills/project-roadmap-board/layout.py`
- 配套知识 skill：`submodules/skills/project-knowledge-curator/SKILL.md`
- Canvas 技术规范：参考 `json-canvas` skill

## 两条主线

本 skill 覆盖路书的两条独立主线，混着用会出错：

| 主线 | 干什么 | 主要章节 |
|---|---|---|
| **建板** | 从 PRD/OpenSpec 材料池抽事实卡，再收敛成“完成某件事”的闭环工作块 + 锚点 | 「路书第一语义」「建板六步法」「锚点写法速查」+ rules.md 0B–0H |
| **执行** | 围绕首环闭环推进 runtime group，传播颜色、处理未决点/错知识/子环、回写文档 | 「执行循环」「未决点演化速查」「错知识反路径速查」+ rules.md 1–20 |

新建/重构路书时走「建板」；推进现有路书时走「执行」。

## 核心原则

### 路书第一语义：完成闭环

- 路书的核心不是复述 PRD/OpenSpec，也不是展开 Agent 执行计划，而是表达：**为了完成这件事，必须闭合哪些可验收工作块，以及这些工作块如何从开始走到结束**。
- OpenSpec / PRD / 原型 / 截图 / tasks.md 都是材料池。它们提供动作、边界、UI 细节、证据要求和未决点；路书只吸收会影响闭环推进、验证、裁决、回退或子环展开的内容。
- 首环主干回答“这件事从开始到完成要闭合哪几个核心工作块”。runtime group 回答“当前工作块怎么推进到可验证闭合”。Agent / Worker / Gate 是执行投影和门禁，不是路书本体。
- 一个 runtime 节点如果在执行中长出独立入口、出口、状态推进、证据要求或阻塞面，**先在同一 group 内派生横向子环**；只有它跨多个工作块、需要独立 gate / Worker Pack、或阻塞主干闭环时，才提升成新的 spine 工作块。

### 与 Context Compiler 的关系

本 skill 是闭环执行真源，不是业务事实真源。

路书只消费已经类型化的知识：

- `white / baseline` 可以进入锚点、Worker Pack 和转绿依据。
- `gray / advisory` 只能作为风险、未决点或调查输入；不能直接让节点转绿。
- `black / blocked` 必须被隔离；不能升首环、不能进 Worker Pack、不能作为锚点依据。

`.canvas` 记录进度、门禁、执行闭环和状态传播；业务事实仍由 Curator/Wiki 维护。收到新 Knowledge Pack、Conflict Verdict 或 Repair Record 后，主 Agent 必须先审计 `.canvas` 锚点是否需要改写，再推进颜色。

### 建板原则

- **可执行首环 = PRD 事实卡 + Obsidian 已有知识 + Curator 三色裁决**。首环不是"PRD 段落 + 直觉"，必须经过知识校准（规则 0CC）。
- 路书只托管**进度状态**，不托管业务事实。
- 新建/重构路书必须走完 `PRD/OpenSpec → 事实卡 → 功能候选 → 名词消歧 → 首环工作块 → runtime group 细节` 收敛链；禁止把 PRD 标题、页面名、表格行或段落机械直转成首环。
- **首环主干竖向排列**：`开始（最下）→ 工作块1 → 工作块2 → ... → 结束（最上）→ 根（弧线回环）`。**开始在下、结束在上，自下而上推进**（贴用户图 3）。首环只表达顶层顺序和状态，不承载运行时细节。
- 首环规模默认控制在 **3-7 个工作块**：超过 7 再收敛一层主干，少于 3 检查是否糊死多个交付面。
- 首环节点是工作块，不是资料摘抄；每个首环节点保留 **2-5 条带来源的纲要事实锚点**，用来说明该工作块为何存在、必须交付什么、边界是什么。
- 锚点是宪法条款不是 PRD 摘要——**每条 1-2 行写不清就下沉到 runtime group**。
- **首环锚点是 Knowledge Pack 在路书上的"使用面"**：每次 Curator 出新 KP，必须 grep `.canvas` 审计锚点是否过期（规则 0J）。

### 执行原则

- 路书是**单棵树**：从唯一根节点出发，所有业务节点必须连通可达（rules.md 规则 0）。
- 路书必须展开到**可验收闭环粒度**：tasks.md checkbox 用来校验 runtime group 是否足够可执行，但不能反向决定首环结构，也不能把每个 checkbox 提升成主干节点（规则 0A）。
- **灰→黄必须立即创建对应 `工作块:` group 节点 + 横向 runtime 链**（规则 3 + 0K，整个系统最关键的触发规则）：group 必须**完全包含 P 自身 + P 的所有 runtime 节点 + 子链递归到底**。
- **运行时处理一律横向展开**：事实卡、调查、实现、验证、证据、未决点、Exception 都放在所属 runtime group 内；禁止把运行时细节插回竖向首环主干。
- **嵌套 group 允许完全包含、禁止部分相交**（规则 0K）：子工作块的 group 可以套在父工作块的 group 里，但两个 group 矩形不能部分相交。
- **gate 节点必须封到独立 `Gate:` group**（规则 0L）：gate 必须串在 spine 主干上，连接在前任务之后、后任务之前；Gate group 与所有 `工作块:` group 完全分离。
- 业务事实、功能点索引、冲突裁决、错知识修正由 Knowledge Curator 负责。
- 没有 `Knowledge Pack`，不允许派代码型 Worker；Worker Pack 是当前闭环工作块的最小执行包，不是把 OpenSpec / tasks / 长日志整体转交给 Worker。
- `Knowledge Pack` 必须明确区分 `baseline / advisory / blocked sources`；白知识默认进上下文，灰知识按需，黑知识隔离。
- 主 Agent 收到任何回报后，**第一件落地动作永远是回写 `.canvas`**；若本次收到新 KP / Repair Loop / 未决点驱散，回写前先做规则 0J 锚点审计。
- **回写前必须跑一次 `audit.py`，exit 0 才能提交**（默认 P0 阻断 / P1 警告；`--strict` 让 P1 也阻断）。`audit.py` 现在合一校验拓扑、颜色、几何（spine 方向 / runtime 方向 / group 包含 P + 状态后缀 + color 镜像 + 嵌套合法性 / Gate group）；审计清单里 `[人工]` / `[半自动]` 项仍必须主 Agent 自己核（rules.md 末尾）。
- 错知识一旦确认失效，必须退出默认上下文；同时**主 Agent 必须 grep `.canvas` 审计相关首环锚点是否需要改写**（规则 0J）。

## Canvas 颜色映射

| 状态 | Canvas `color` | 含义 |
|---|---|---|
| 未开始 | 不设 color | 灰色（默认） |
| 进行中 | `"3"` | 黄色 |
| 阻塞/异常 | `"1"` | 红色 |
| 已完成 | `"4"` | 绿色 |
| 护栏/房间 | `"6"` | 紫色，不参与传播 |
| 分支路径 | `"5"` | 青色，不参与传播 |

**红色不是未开始。** 未开始只能是灰色（无 `color`）。

## 材料 / 说明节点规则

Canvas 可以放材料/说明节点来让人看清上下文，但它们不是业务节点：

- 可视化内容：OpenSpec drift、原型 UI 细节、截图说明、方案分歧、决策点、颜色图例、审计规则、弃用/旁路材料摘要。
- 位置：放在业务节点区域左上角外侧，或用 `装饰:` / `区域:` group 框住；不要塞进 spine 主干，也不要混入 runtime 链。
- 边：材料/说明节点**不能接业务 edge**，不能成为 `开始 → 工作块 → 结束` 或 `父 → runtime → 父` 的一部分；最多只用无状态视觉引用或文本 source 指针。
- 状态：材料/说明节点不参与红黄绿传播，不作为 gate，不触发 Worker Pack，也不能让父节点变色。
- 转换：一旦某个材料点实际影响闭环推进、验证、裁决、回退或子环展开，必须把它转成对应 `runtime` 节点、首环锚点、Gate 或 Exception；保留原材料节点只作为来源说明。

## 建板六步法（建板主线核心）

拿到 PRD/OpenSpec 时按以下六步收敛，对应 rules.md 0B–0H。核心链路是：**OpenSpec/PRD 材料池 → 事实卡 → 闭环工作块 → runtime group 可验收叶子**。**禁止跳步**。

### 第 1 步：抓动词（事实卡）

像淘金一样去掉 PRD 修饰语，只留下 7 个字段：`source / 对象 / 动作 / 目标行为 / 入口出口 / 边界 / 证据 / 未决点`。事实卡不进 `.canvas`，只用于后续收敛。

### 第 2 步：归类成功能候选

按以下优先级合并事实卡（规则 0C）：

1. 同一用户旅程 / 状态机阶段 / 时间顺序
2. 同一业务能力或用户可感知结果
3. 同一数据契约、配置源、资源链路或验证证据
4. 同一 owner / 代码写域 / 可并行派工边界

**禁止**按 PRD 文件名 / 页面字段 / 表格行 / 截图 / 文案 / 参数直接拆首环。

### 第 3 步：名词消歧（知识补全关口）

事实卡里的业务名词必须先消歧再升首环。否则容易把"已是独立数据模型的名词"误判成"runtime 细节"。

不是看到名词就查（会爆炸）。名词命中以下 5 类之一才必须问 Curator（规则 0CC）：

| 触发条件 | 例子（morph72 PRD） |
|---|---|
| 影响首环资格 | "冠军贴纸" 是否已是独立数据模型 |
| 影响锚点边界 | "AI 锐评得分" 由哪些 input 决定 |
| 影响派工边界 | "服务端自动 Ready" 是 GSC / room-service / 前端态 |
| 影响红黄绿状态 | "prompt 未定" 是 A/B/C 哪类未决点 |
| 影响验收证据 | round_rank / 公聊 / OS 真实运行链路 |

调用 curator skill 的 `knowledge-hit-detect`。`hit_readonly` 必须按三色分支处理，**black 不允许升首环也不进 Worker Pack**：

- `no_hit` → Curator 走 `knowledge-curate` 补完知识；如影响首环资格，等补完再升首环
- `hit_readonly` + **white** → 进 `baseline sources`，可升首环、可挂锚点、可进 Worker Pack
- `hit_readonly` + **gray** → 仅进 `advisory sources`；要升首环必须 Curator 显式提级；不进默认 baseline
- `hit_readonly` + **black** → 进 `blocked sources`；**不允许升首环**；**不允许进 Worker Pack**；指向已弃用方案时事实卡作废或归 exception.md
- `hit_writeback_required` → 触发 `knowledge-curate` writeback，writeback 完再升首环

详细判定见 rules.md 0CC。

### 第 4 步：升首环（5 选 1 资格）

候选项满足以下任一才允许升首环（规则 0D）。这里升的是“完成某件事必须闭合的工作块”，不是 OpenSpec 章节、tasks checkbox 或 Worker 分工：

- 有独立用户可感知结果或业务阶段结果
- 有独立入口/出口、状态推进或验收边界
- 派生多个调查/实现/验证叶子任务
- 阻塞下游阶段，需独立红黄绿跟踪
- 需要独立 Knowledge Pack / Worker Pack 才能安全执行

首环命名建议：`能力/阶段 + 闭合结果`，例如 `集体亮相社交体验闭环`、`故事反馈探索裁决`。

### 第 5 步：挂纲要事实锚点（2-5 条）

每个首环挂 2-5 条锚点，按 5 类类型词分类（规则 0E、0H）：

| 类型词 | 干什么 |
|---|---|
| `非目标` | 全局红线，约束多 Worker 不踩的边界 |
| `入口/出口` | 时序边界、状态切换点、阶段分界 |
| `时序` | 顺序约束（按 X 顺序展示、先 A 后 B） |
| `未决点` | 待拍方案 / 暂定值 / 待裁冲突，必须带 owner 和阻塞面 |
| `来源` | authoritative source 指针 |

每条 1-2 行；超过即下沉到 runtime group 或 Knowledge Pack。**PRD 一句话夹两层（动作+UI形态、时序+参数值）时必须先拆**，约束面广的进锚点，约束面窄的下沉 runtime group（规则 0H 句子拆分）。

### 第 6 步：下沉到 runtime group

零散点默认下沉到所属节点右侧 runtime group（规则 0F）：UI 局部、文案池、参数、动效、贴纸、按钮文案、排序规则、分值表、倒计时、兜底、"如果/是否/当..."条件分支、调查未决项、单阶段实现细节、验证证据。

runtime group 内继续按 `事实卡 / 调查 / 实现 / 验证 / 证据 / 未决点` 拆叶子，叶子要可追溯覆盖 tasks.md checkbox 或等价验收点，但不是把 checkbox 机械复制成路书节点。

## 锚点写法速查

锚点 vs runtime 细节的差别**不是字数，是约束面**：

- 约束面广（≥2 个工作块、跨 Worker、跨阶段）→ 锚点
- 约束面窄（只指导一处实现的具体形态）→ runtime group

锚点格式（每条 1-2 行）：
```
非目标：贴纸属社交表达，禁止进入得分链路
入口/出口：阶段一 10s，贴纸仅自己可见；切换后揭晓
时序：个人 C 位按座位 1→4 顺序展示
未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工
来源：v1.4.2 PRD §方案详情·亮相
```

详细判定表与正反例见 rules.md 0H。

## canvas.group 速查

路书 v2 引入 JSON Canvas `type:"group"` 节点作为工作块的视觉容器。规则速记：

**两类 group**：

| 类型 | label 模式 | color | 圈住什么 |
|---|---|---|---|
| 工作块 group | `工作块:<spine节点 id>:[处理中｜已完成｜阻塞]` | `5` 处理中 / `4` 已完成 / `1` 阻塞（镜像 P 颜色） | **P 节点自身 + P 的所有 runtime 节点 + 子链递归到底** |
| Gate group | `Gate:<gate id>:<gate 名>` | `6`（紫，护栏） | 单个 gate 节点 |

**核心规则（详见 rules.md 0K / 0L）**：

- 黄/红/绿 spine 节点**必须**有对应的 `工作块:` group；灰节点禁止有 group
- group label 状态后缀必须与 P 颜色配对：黄↔处理中 / 绿↔已完成 / 红↔阻塞
- 嵌套 group：**允许完全包含**（子工作块在父工作块内），**禁止部分相交**
- spine 链 edge 跨过 `工作块:` group 是合法的（spine 是总主干）
- runtime 链 edge 不能跨 group（同 group 内闭合）
- gate 节点必须封到 `Gate:` group，且 Gate 必须在 spine 主干上有前驱和后继；Gate group 与所有 `工作块:` group 完全分离

**生命周期（与 P 颜色联动）**：

```
   [无 group]
       │ P 灰→黄
       ↓
  [处理中 color=5] ──P 黄→红──→ [阻塞 color=1] ──P 红→黄──→ [处理中]
       │                              │
       │ P 黄→绿                      │ P 红→绿（直接闭合）
       ↓                              ↓
  [已完成 color=4] ←──────────────────┘
       │ P 绿→红（假绿撤回，规则 0J）
       ↓
   [阻塞 color=1]
```

黄→绿后保留 group（作为历史证据，规则 0J 锚点 grep 审计需要）。

## 工具脚本

- **`audit.py`**：拓扑 + 几何 + group 校验合一脚本。回写 .canvas 前必跑，exit 0 才能提交（默认 P0 阻断 / P1 警告，`--strict` 让 P1 也阻断）
- **`layout.py`**：JSON spec → .canvas 正向生成器。把抽象路书描述（spine + runtime + gates，无坐标）转成完整 .canvas（坐标、edges、groups 自动生成）
- **`geometry.py`**：常量 + 工具函数共享模块。audit / layout 必须从这里 import，禁止本地定义常量

典型工作流：

```bash
# 起新路书：写 spec.json → 跑 layout.py 生成 → 自动 validate
python3 layout.py spec.json -o roadmap.canvas --validate

# 改完路书：跑 audit
python3 audit.py roadmap.canvas --root v14-root
```

## 角色分工

### 主 Agent

- 唯一可写 `.canvas`
- 负责：读路书、选父节点、锁 checkpoint、派 Curator/Worker、处理回报、回写路书、写 `exception.md`、**锚点版本审计**（规则 0J）
- 不直接写业务代码

### Knowledge Curator

- 负责：确认业务域、读取 docs、authority 分级、输出 `Knowledge Pack`、产出 `Conflict Verdict`、执行 `Repair Loop`、回写业务域 README 与叶子文档
- 不改 `.canvas`
- 不直接判定节点转绿；只给主 Agent 提供知识裁决与 writeback 结果

### Worker

- 负责：代码实现、测试、排障、证据采集
- 不改 `.canvas`
- 不直接修改业务域知识结论
- 发现知识冲突时只能上报，不能私自覆盖知识库

## 真源与读写权限

| 真源类型 | 主 Agent | Curator | Worker |
|---|---|---|---|
| 路书 `.canvas` | 读写 | 只读 | 只读 |
| 核心 OpenSpec / 主规格 | 读写 | 读写 | 只读 |
| 业务域 docs / Obsidian 知识库 | 读写 | 读写 | 只读 |
| `exception.md` | 读写 | 建议内容 | 只读 |
| 扇出 OpenSpec（`agent-*`） | 读写 | 读写摘要/任务 | 仅自己的写域 |
| 证据产物（HAR / 日志 / 截图 / rerun） | 读写 | 读写摘要 | 读写 |

## Gate

- `KP-00 Domain Locked`
- `KP-01 Sources Locked`
- `KP-02 Conflict Verdict Issued`
- `KP-02A Knowledge Compliance Checked`
- `KP-03 Worker Pack Ready`
- `KP-04 Docs Writeback Done`
- `KP-05 Knowledge Repair Closed`
- `KP-06 Node Can Turn Green`

任何一个 gate 未通过，主 Agent 都不能把对应节点转绿。

Gate 是闭环门禁，不能画成主干外侧的说明节点。它必须以 `前置工作块 → Gate → 后续工作块` 的形式阻挡和放行具体进度；gate 未过，后续闭环不能合法推进或转绿。

## 执行循环

```
Step 0: 建板 / 重构路书
        → 锁定 PRD/OpenSpec/任务清单来源，并把它们视为材料池
        → 走「建板六步法」：OpenSpec/PRD 材料池 → 抓动词事实卡 → 归类候选 → 名词消歧 → 升 3-7 个闭环工作块 → 挂 2-5 条锚点 → 首环竖向排布（开始最下、结束最上）
        → 首环主干只按“完成这件事要闭合什么”组织；OpenSpec 章节、组件名、Agent 分工、tasks checkbox 不能直接决定主干
        → 推荐先写 spec.json 跑 layout.py 自动生成 .canvas，避免手画方向出错
        → 详细规则 rules.md 0B-0H（含 0CC 知识补全关口）

Step 1: 主 Agent 读路书
        → 识别灰/黄/红父节点
        → 锁定当前要推进的父节点/runtime group
        → 若任务涉及代码/设计/排障，先检查业务域是否已锁定

Step 2: Curator 先工作
        → 确认业务域与功能点
        → 读取业务域 README + [[功能点]]
        → 输出 Knowledge Pack / Conflict Verdict / Knowledge Compliance
        → 如发现错知识，执行 Repair Loop（细则见「错知识反路径速查」）

Step 3: 主 Agent 派 Worker
        → 只有 KP-00~KP-03 通过后才可派工
        → spine 节点灰→黄：**同时**做三件事：(a) 把节点 color 改黄；(b) 在节点右侧建 runtime 链（开始→...→结束）；(c) 建 `工作块:<P>:[处理中]` group 包住 P + runtime（规则 0K）
        → 立即回写 .canvas
        → 生成 Worker Pack（只包含当前节点需要的最小上下文 + 当前 runtime group ID）

Step 4: Worker 执行
        → 按所属 runtime group 的横向链条顺序推进
        → 每次状态变化立即上报
        → 发现知识冲突立即上报，不私自裁决
        → 运行时发现新问题，默认先在同一 runtime group 插入灰节点；开始处理时在同 group 派生横向子环；只有跨工作块/独立 gate/独立 Worker Pack/阻塞主干闭环时，主 Agent 才评估升 spine

Step 5: 主 Agent 先回写路书
        → 若本次收到新 Knowledge Pack / Repair Loop 结果 / 未决点驱散，先按规则 0J 对当前 .canvas 做锚点 grep 审计，确定锚点改写/删除和节点回退
        → 第一件事：把状态变化、锚点审计结果和必要回退写入 .canvas（spine 节点颜色变化必须同步更新 group label 状态后缀和 group color）
        → 改完跑 audit.py，exit 0 才算脚本通过；同时主 Agent 必须人工 review 审计清单的 [人工] / [半自动] 项
        → 第二件事：如有阻塞，写 exception.md

Step 6: Curator 回写 docs
        → 更新业务域 README
        → 更新叶子文档 / [[功能点]] / 代码落点
        → 必要时把错知识降级到 stale/legacy

Step 7: Closeout
        → KP-04 / KP-05 / KP-06 全通过
        → 节点才允许转绿
```

## 未决点演化速查

PRD 抓事实卡时识别出的"未决点"分三类，路书表现不同（详见 rules.md 0I）：

| 类型 | 例子 | 阻塞面 | 路书表现 |
|---|---|---|---|
| **A. 参数暂定**（方案已定，值待锁） | 「结算页 15s 暂定」 | 不阻塞 | 时序锚点 + 未决点锚点（拆成两条） + runtime 参数节点 |
| **B. 方案未定**（产品/策划没拍） | 「故事反馈策划 prompt 未定」 | 阻塞实现派工 | 锚点 + runtime 全调查节点 |
| **C. 冲突未裁**（多文档/代码不一致） | "PRD 写 15s，Figma 标 20s" | 阻塞整个工作块 | exception.md + 红节点 |

锚点必须带 owner 和阻塞面；A 类一句话夹两层时必须先按规则 0H 句子拆分：
```
未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工
入口/出口：锐评结束 → 结算页 → 全员 Ready 或倒计时结束 → 离开
未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现
```

**调查节点持续黄是合法状态**（"在追"≠"卡死"）。变红阈值任一命中即可：
- owner 跨 sprint 边界仍无进展回报或 ETA
- owner 明确说"我给不了答案"，且没有给出下一任 owner
- 输入超出当前 owner 能力边界，且没有升级路径或 ETA
- 出现"未决套未决"
- 调查耗时 ≥ 该首环总预算 50%

变红判定主体永远是**主 Agent**，Worker / Curator 只能上报事实。

## 错知识反路径速查

错知识 vs 未决点：**错知识从绿撤、未决点从灰爬**——方向相反。

错知识发现链路（规则 0J）：
```
T0  Worker 撞到现状不符 → 上报主 Agent
T1  主 Agent 把当前节点（含已绿的）标红 + exception.md 立条
T2  主 Agent 派 Curator 走 Repair Loop（curator skill 7 步）
T3  Curator 完成 → 主 Agent 拿到新 Knowledge Pack
T4  主 Agent grep .canvas 找所有引用了该 knowledge_id 的首环锚点
T5  改写锚点为新真源；若旧锚点曾让节点变绿，相关节点回退到黄
T6  节点红→黄继续推
```

**T4-T5 是 skill 闭环关键**：不审计锚点，新派工的 Worker 还会基于错锚点干活，Repair Loop 白做。

## Worker Pack 要求

Worker Pack 是闭环门禁的一部分：它证明“当前 runtime group 可以被安全派出去推进”，而不是 Agent 的自由计划书。Worker Pack 必须由主 Agent 基于 Curator 输出生成，只包含：

- 当前路书节点 ID
- 当前 runtime group ID
- 当前 checkpoint
- 当前业务域
- 当前功能点
- authoritative sources
- baseline sources
- advisory sources
- blocked sources
- locked facts
- open conflicts
- stale sources to ignore
- evidence required
- allowed write scope

禁止把整份 PRD、整份 HAR、整份长日志直接塞给 Worker。
禁止把 `blocked sources` 交给 Worker 当成可用依据。

## 上报格式

Worker 每次上报必须包含：

- 节点 ID
- 状态变更
- 代码/测试/运行证据
- 是否触发知识冲突
- 是否建议插入新节点
- 是否建议创建/扩展 runtime group

Curator 每次上报必须包含：

- 业务域
- 功能点
- `Knowledge Pack` 或 `Conflict Verdict`
- `Knowledge Compliance`
- 是否发生 `Repair Loop`
- README / 叶子文档 / 索引是否已回写
- 是否满足 `KP-04` / `KP-05`

## Exception 规则

以下情况必须进入 `exception.md`：

- docs / 代码 / PRD 冲突，Curator 无法自动裁决（未决点 C 类）
- 未决点跨 sprint 边界仍无进展回报或 ETA（未决点 B 类升级）
- 未决点需要外部 owner，但没有明确承接人、升级路径或 ETA（未决点 B 类升级）
- 未决点会让多个首环连锁变红（未决点 B 类升级）
- 调查节点超阈值变红（见「未决点演化速查」）
- docs 根目录、vault、authoritative roots 缺失
- `obsidian-cli` 不可用且 MCP 也拿不到必要信息
- 需要人工确认业务域、功能点归属或正式命名

**exception.md 每条必须指向至少一个红节点**。死信（无对应红节点的 Exception 条目）说明阻塞已解除但回写漏了，必须清理。

## 重要约束

- 路书是进度真源，不是知识真源。
- 业务域 README 是知识入口，不是进度板。
- **锚点必须 1-2 行写得清楚**；写不清等于不是锚点，下沉 runtime group。
- **锚点带 owner**：未决点类锚点必须标 owner 和阻塞面，否则驱散动作漂浮。
- **锚点版本管理**：每次 Curator 出新 Knowledge Pack（不论是 Repair Loop 还是未决点驱散触发），主 Agent 在写回 `.canvas` 前必须 grep `.canvas` 审计所有首环锚点是否引用了已被替代/降级的真源。
- 错知识默认处理是"降权 + 归档 + 重新索引"，不是"原地继续暴露"。
- `obsidian-cli` 是首选 vault 通道，但允许 CLI 不可用时退回 MCP。
- 引用了未授权灰知识或任何黑知识的交付物，不允许过 gate。
