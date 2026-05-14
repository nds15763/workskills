# 路书规则详解

## 节点分类

### 业务节点

参与状态传播的节点。必须遵守闭环规则。

| 子类型 | 命名模式 | 角色 |
|---|---|---|
| 首环主干节点 | `开始`、`集体亮相社交体验闭环`、`结束` | 竖向主干节点，只表达顶层顺序和状态 |
| runtime 父节点 | `后端跑通`、`结算 Ready 推进` | 派生右侧 runtime group 的起点，接收运行时状态传播 |
| 开始节点 | `开始处理:后端跑通`、`开始调查:Ready 链路` | runtime group 横向链的第一个节点 |
| 结束节点 | `结束处理:后端跑通`、`结束验证:Ready 链路` | runtime group 横向链的最后一个节点，edge 指回 runtime 父节点 |
| 中间节点 | `车坏了需要修车`、`酱油是不是需要补充` | 执行中遇到的问题/任务，插入所属 runtime group 横向链 |
| 调查节点 | `调查: <问题描述> [✅/⚠️/❌]` | 一个设问点，可以是中间节点也可以成为 runtime 父节点 |
| 实现节点 | `实现: <工作描述> [✅/⚠️/❌]` | 一项需要落地的开发工作 |
| 验证节点 | `验证: <验证描述> [✅/⚠️/❌]` | 一项需要拿到证据的验收工作 |
| group 节点 | `工作块:<P>:[处理中|已完成|阻塞]`、`Gate:<gate_id>:<名称>` | JSON Canvas `type:"group"`，圈住一个父节点的运行时工作台，不参与状态传播 |

### 说明节点

不参与状态传播。用于展示规则、颜色索引等元信息。无颜色要求。

### 材料 / 说明节点

材料/说明节点用于把 OpenSpec drift、原型 UI 细节、截图说明、方案分歧、决策点、颜色图例、审计规则、弃用/旁路材料摘要可视化在 canvas 上。它们帮助读图，但不是闭环本体。

强制规则：

- **不参与状态传播**：不能因为材料节点变色、存在或消失而让业务节点红黄绿变化。
- **不能接业务边**：不得接入 `开始 → 工作块 → 结束` spine，也不得接入 `父 → runtime → 父` runtime 链；不得作为 gate 的前驱/后继。
- **不能承载业务完成状态**：不能标记为“已完成/处理中/阻塞”来代表一个工作块，也不能触发 Worker Pack。
- **不能替代 runtime 节点**：如果材料点会影响闭环推进、验证、裁决、回退或子环展开，必须转成 runtime 节点、首环锚点、Gate 或 Exception；材料节点只保留来源说明。
- **布局上外置**：默认放在业务节点区域左上角外侧，或放进 `装饰:` / `区域:` group；不要混入 spine 主干或 runtime group 的执行链。

允许的可视化方式：

- 文本节点：`说明: OpenSpec drift 摘要`、`材料: Figma 交互差异`、`决策点: A/B 方案待拍`
- 装饰 group：`装饰: UI drift 参考`、`区域: 旁路材料`
- 业务节点里的短 source 指针：例如 `来源: openspec/.../design.md §Ready`

禁止的可视化方式：

- `工作块 → 材料: UI 细节 → 下一个工作块`
- `父 → OpenSpec 章节 A → OpenSpec 章节 B → 父`
- `Gate:KP-03 → 说明: Worker Pack 已准备 → 实现节点`

判断口诀：**材料节点可以解释为什么这么做，不能表示这件事做到了哪一步。真正影响闭环的内容，必须转成 runtime 节点。**

### 两种图形语义

路书只有两种可执行图形语义，不能混用：

| 图形语义 | 方向 | 承载内容 | 约束 |
|---|---|---|---|
| **首环主干** | 竖向 | 顶层开始、gate、工作块、结束 | 只表达首环顺序和红黄绿状态；不放运行时事实、证据、异常细节 |
| **runtime group** | 横向 | 某个首环/gate 外部 owner 的事实卡、调查、实现、验证、证据、未决点、Exception | 必须用 JSON Canvas `type:"group"` 包住；内部 runtime 节点可继续横向生子链 |

一句话：**竖向主干是路线图；横向 runtime group 是每个节点的运行时工作台。**

### 路书第一语义：完成某件事的闭环

路书不是第二份 PRD/OpenSpec，也不是 Agent 分工图。路书的第一语义是：

```
为了完成这件事，必须闭合哪些可验收工作块；
每个工作块如何从开始进入、经过处理、拿到证据、最终回到完成态。
```

因此：

- PRD / OpenSpec / 原型 / 截图 / tasks.md 都只是材料池；它们提供动作、状态、UI 细节、边界、证据和未决点。
- 首环主干只能按“完成这件事需要闭合的核心工作块”组织，不能按 OpenSpec 章节、页面、组件、截图、checkbox 或 Agent 分工直接组织。
- runtime group 是闭环推进记录：记录当前工作块内部的事实卡、调查、实现、验证、证据、阻塞和回退。
- 多 Agent 协作、Worker Pack、KP gate、agent-* OpenSpec 都是执行投影和门禁；没有 SubAgent 时，roadmap 仍必须能独立表达这个目标闭环。
- runtime 横向状态遇到新风险时，先在同一 group 内插入新灰节点；开始处理后在同一 group 派生横向子环。只有当子问题具备独立入口/出口、独立验收证据、跨工作块阻塞、独立 gate / Worker Pack，或会改变主干闭环顺序时，才提升为新的 spine 工作块。

## PRD 建板与首环生成规则

### 规则 0B：先抽事实卡，不先画环

拿到 PRD、飞书文档、OpenSpec 或长篇产品说明时，先把它们当作“材料池”，不能先按目录、页面名、表格行、截图顺序直接画首环。必须先像画流程图一样抓动作，形成事实卡，再围绕“完成这件事的闭环”收敛成工作块，最后把细节下沉到 runtime group。

建板主链固定为：

```
OpenSpec/PRD/原型/tasks 材料池 → 事实卡 → 功能候选 → 知识消歧 → 闭环工作块 → runtime group 可验收叶子
```

每条事实卡至少包含：

- `source`：来源文件、标题、段落或行号
- `对象`：页面、阶段、状态机节点、角色、数据对象或配置项
- `动作`：新增、调整、删除、展示、隐藏、排序、触发、等待、同步、兜底、探索、禁止等
- `目标行为`：用户或系统最终应该看到什么变化
- `入口/出口`：从哪里进入、何时离开、依赖什么上游、影响什么下游
- `边界/非目标`：明确不做什么、不能破坏什么、哪些材料只是探索或弃用
- `证据要求`：需要代码、配置、截图、日志、E2E、人工验收中的哪类证据
- `未决点`：缺设计、缺策划、缺命名、缺接口、缺素材、需要人工确认的地方

事实卡不是 `.canvas` 节点，不直接进入路书。它们先用于收敛功能候选、生成 Knowledge Pack 和首环纲要事实锚点。

### 规则 0C：功能候选按交付语义归类，不按文档外观归类

PRD 通常不会明说“这是一个功能点”，而是描述“要做什么”。主 Agent / Curator 必须把这些描述先整理成功能候选。

默认归类优先级：

1. 同一用户旅程 / 状态机阶段 / 时间顺序
2. 同一业务能力或用户可感知结果
3. 同一数据契约、配置源、资源链路或验证证据
4. 同一 owner / 代码写域 / 可并行派工边界

禁止的归类方式：

- 按 PRD 文件名直接拆首环
- 按“页面”字段直接拆首环
- 按表格每一行直接拆首环
- 按 OpenSpec 章节、组件名、原型截图、tasks checkbox 直接拆首环
- 按 SubAgent / Worker / owner 分工直接拆首环
- 把截图、文案、素材、参数单独提升为首环
- 把“探索中 / 不用看 / 弃用方案”当成默认执行功能点

如果一个材料只是边界、弃用方案或未决探索，它应该进入对应工作块的 runtime group、Knowledge Pack 的 advisory/blocked sources，或 exception.md，而不是默认进入首环。

### 规则 0CC：知识补全关口（名词消歧）

事实卡抽完、归类成功能候选**之后**、升首环**之前**，必须对事实卡里的业务名词做一次知识查询。否则容易把"已经是独立数据模型/独立服务/独立 gate 的名词"误判成"runtime 细节"，或把"完全没听过的新概念"当成现有能力直接派工。

#### 总公式

```
PRD 事实卡 + Obsidian 已有知识 + Curator 三色裁决 = 可执行首环
```

首环是**知识校准后的工作块**，不是"PRD 段落 + 直觉"。

#### 触发条件（不是看到名词就查；命中以下 5 类之一才必须查）

不加触发条件就会爆炸——PRD 里几十个名词全查一遍是浪费 Curator 资源。只查命中以下任一条件的名词：

| 触发条件 | 例子（morph72 PRD） |
|---|---|
| 影响首环资格 | "冠军贴纸" 是否已是独立数据模型 → 决定它是单独首环还是某首环的 runtime 细节 |
| 影响锚点边界 | "AI 锐评得分" 由哪些 input 决定 → 决定"贴纸不影响得分"这条锚点能不能立住 |
| 影响派工边界 | "服务端自动 Ready" 是 GSC / room-service / 前端态 → 决定派给哪个 Worker |
| 影响红黄绿状态 | "prompt 未定" 是 A/B/C 哪类未决点 → 决定锚点 owner 和阻塞面 |
| 影响验收证据 | `round_rank` / 公聊 / OS 真实运行链路 → 决定验证节点能挂什么 |

#### 查询动作

主 Agent 调用 curator skill 的 `knowledge-hit-detect` 子能力。Curator 输出：

- `matched_business_domain`
- `matched_feature_points`
- 该名词当前的 `knowledge_color`（white/gray/black）
- `authority_level`（A/B/C/D）
- `writeback_reason`（如有）

回写到事实卡：每张事实卡的 `对象 / 动作` 字段，标注命中情况。

#### 三种结果与下一步动作

| 查询结果 | 下一步 |
|---|---|
| `no_hit`（vault 完全没有该名词） | Curator 进 `knowledge-curate` 补完知识；事实卡先标 `gray knowledge`；如果该名词影响首环资格，**等 Curator 补完才升首环**，不允许猜测升首环 |
| `hit_readonly` + **white** | 事实卡标 `A/B authority + white`；可进 `baseline sources`、可挂锚点、可进 Worker Pack |
| `hit_readonly` + **gray** | 事实卡标 `gray + 当前 authority`；只能进 `advisory sources`；如要支撑首环升级，必须 Curator 显式提级；不进默认 baseline |
| `hit_readonly` + **black** | 事实卡进 `blocked sources`；**不允许升首环**；**不允许进 Worker Pack**；如该名词指向已弃用方案，事实卡作废或归 exception.md |
| `hit_writeback_required`（vault 有但需更新） | 触发 curator 的 `knowledge-curate` writeback；该事实卡先冻结，writeback 完成后再升首环 |

#### 反模式

- 看到 PRD 里出现的所有名词都给 Curator 查 → 爆炸；只查命中 5 条触发条件之一的
- 跳过名词消歧直接升首环 → 容易把"已是独立数据模型的名词"误判成"runtime 细节"
- 让 Worker 自己判断名词含义 → 违反"没有 Knowledge Pack 不允许派代码型 Worker"
- 名词查询结果是 `no_hit` 但仍然升首环 → 等于建板时把未消歧的猜测当结论
- 名词查询结果是 `hit_writeback_required` 但 Curator 还没 writeback 就升首环 → 锚点会引用旧版本知识，下次 Curator writeback 完成后必须走规则 0J 锚点版本管理
- **`hit_readonly` + black 但仍升首环或进 Worker Pack** → 把已弃用方案当成执行链，违反 curator 三色分层；black 必须进 `blocked sources`，不进 baseline / advisory
- **`hit_readonly` + gray 直接当 white 用**（直接进 baseline / 锚点 locked facts）→ 跳过了 Curator 的 authority 提级，会让未确权的灰知识被当成基线

### 规则 0D：首环 = 主干工作块

首环是整张路书的主干层，表达“这份需求最终要闭合哪些工作块”。首环不是功能清单，不是 PRD 摘要，不是 OpenSpec 章节目录，也不是 Agent 执行计划。

一个候选项满足以下任一条件，才允许提升为首环工作块。提升对象必须是闭环工作块，不是 task tree、OpenSpec copy、agent flow：

- 有独立的用户可感知结果或业务阶段结果
- 有独立的入口/出口、状态推进或验收边界
- 会派生多项调查 / 实现 / 验证叶子任务
- 会阻塞下游阶段，或需要单独红黄绿跟踪
- 需要独立 Knowledge Pack / Worker Pack 或 gate 才能安全执行

首环规模默认控制在 3-7 个工作块。超过 7 个时，优先再收敛为更高层主干；少于 3 个时，检查是否把多个交付面粗暴糊成了一个节点。

首环在 canvas 上必须竖向排布，形成 `开始 → 工作块1 → 工作块2 → ... → 结束` 的主干。首环主干不是横向闭合环；任何运行时处理过程都必须进入右侧 runtime group。

首环节点命名建议使用“能力/阶段 + 闭合结果”：

- `集体亮相社交体验闭环`
- `锐评颁奖表达优化闭环`
- `小局结算与 Ready 推进闭环`
- `题目衔接 OS 闭环`
- `故事反馈探索裁决`

### 规则 0E：首环必须带纲要事实锚点，但不能变成知识库

首环节点是工作块，允许嵌入 2-5 条纲要事实锚点，帮助主 Agent、Curator 和 Worker 理解“文档到底要求我们做什么”。

纲要事实锚点只能放这些内容：

- 当前问题 / 目标
- 必须交付的行为摘要
- 入口 / 出口 / 时序边界
- 明确非目标或不能破坏的约束
- authoritative source 指针
- 当前未决点或 Exception 编号

禁止在首环节点里堆：

- 完整 PRD 原文
- 长表格、长日志、长截图说明
- 可配置文案全集
- 具体 UI 像素细节
- 每个 edge case 的完整处理逻辑
- 已被标记为探索、弃用或不可信的材料

如果一个事实锚点需要超过 1-2 行才能讲清，它应下沉为 runtime group 节点、Knowledge Pack 条目或配套 `.md` 摘要。路书节点里的事实锚点不是业务真源，必须能追溯到 PRD / OpenSpec / 业务域文档。

### 规则 0F：runtime group 承接零散点

runtime group 是闭环推进里的细节层，承接首环工作块下面的功能点、子步骤、条件、异常和验证。它可以吸收 OpenSpec 的放射材料，但只保留会影响当前工作块推进、验证、裁决、回退或子环展开的内容。group 矩形**包住 P 自身 + P 派生的所有 runtime 节点 + 内部子链递归到底**（详见规则 0K）；group 在视觉上向 P 节点右侧扩展，但左边界覆盖 P，让"被处理工作块整体"被一个 `工作块:` group 圈住。

默认下沉到 runtime group 的内容：

- UI 局部改动、文案池、素材、动效、贴纸、按钮文案
- 排序规则、分值规则、倒计时、兜底内容、离线策略
- “如果 / 是否 / 当 ... 时”这类条件分支
- 需要调查但还没有结论的探索项
- 只影响某一阶段内部的实现细节
- 验证证据：截图、E2E、日志、配置 inspect、人工验收点
- OpenSpec / 原型 drift 中只服务当前工作块的组件结构、视觉状态、交互占位和删除项；如果只是解释材料，放材料/说明节点；如果影响推进或验证，转 runtime 节点

runtime group 内继续按 `事实卡 / 调查 / 实现 / 验证 / 证据 / 未决点 / Exception` 拆叶子。叶子要能可追溯覆盖 tasks.md checkbox 或等价可检查任务，但不是把 checkbox 机械复制成路书结构。

每个 runtime group 的入口事实卡必须保留：`动作 / 对象 / 目标 / 边界 / 入口出口 / 证据 / 未决点 / 顺序约束`。这些字段不是只用于首环建板；任何运行中新增节点、补处理 runtime 链、阻塞修复链路，都必须先用同一组字段收敛，再插入横向链。

提升 / 下沉判定：

- 多个首环都依赖的基础能力：提升为独立首环或前置 gate
- 只服务一个首环的细节：下沉到该首环右侧 runtime group
- 暂无执行权或未定方案：在 runtime group 内下沉为调查节点；如果阻塞当前交付，标红并写 exception.md
- 明确弃用或“不用看”的方案：进入 blocked/advisory，不进入默认执行链

### 规则 0G：以 morph72 PRD 为例的首环生成

对 `update-morph72-gsc-v14/prd` 这类材料，PRD 的“页面/板块/截图”不是首环。更合适的首环是从交付语义收敛出的工作块，例如：

1. `集体亮相社交体验闭环`
   - 纲要事实：当前 60s 集体亮相空洞；目标是强化社交体验；不能影响 AI 锐评内容和得分；采用总-分-总节奏承接亮相、公聊、结算。
   - runtime group：顶部公告和倒计时、贴纸工具栏、贴纸可见性、个人 C 位展示、最后聊天、贴纸定格、OS 文案、验证截图/E2E。

2. `锐评颁奖表达优化闭环`
   - 纲要事实：颁奖页面要区分第一二三名和名次加分；颁奖顺序不变；UI 需要突出名次信息。
   - runtime group：名次徽章、加分展示、排序不变验证、截图验收。

3. `小局结算与 Ready 推进闭环`
   - 纲要事实：入口/出口：锐评结束后进入结算，全员 Ready 或倒计时结束离开；未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现；非目标：保持公聊，离线玩家自动 Ready 不阻塞下一轮。
   - runtime group：分数结算板、round_rank 排序、前三轮/第四轮加分、Ready 按钮文案、小人状态同步、离线/重连、倒计时自动推进。

4. `题目衔接剧情 OS 闭环`
   - 纲要事实：所有人 Ready 或倒计时结束后触发；中央弹出动画 OS 并播放语音；不影响玩家准备；未配置时走兜底。
   - runtime group：触发条件、资源配置、兜底内容、语音播放、与下一题切换验证。

5. `故事反馈探索裁决`
   - 纲要事实：策划 prompt 未定，RD 只探索生成时长；没有裁决前不能当成实现型工作块派发。
   - runtime group：调查生成链路、记录耗时、等待策划方案；若阻塞交付，标红并写 exception.md。

`冠军贴纸` 在这个例子里默认属于 `集体亮相社交体验闭环` 的 runtime 细节；只有当它发展成独立数据模型、资源管理、跨页面复用或跨阶段 gate 时，才提升为首环。`更多探索方案（不用看）` 和 `弃用方案` 默认不能进入首环执行链，只能作为 advisory/blocked 材料保留引用。

### 规则 0H：锚点写法尺度

锚点 vs runtime 细节的差别**不是字数，是约束面**——一条信息会约束多少个 Worker / 多少段实现。规则 0E 给出了"2-5 条 / 1-2 行"的形状要求，0H 给出"什么内容算锚点"的内容判定。

#### 判定表（任一命中"是"列升锚点；任一命中"否"列下沉 runtime group；冲突时约束面优先）

| 这条句子... | 是 → 锚点 | 否 → runtime group / Knowledge Pack |
|---|---|---|
| 会约束 ≥2 个工作块或 Worker | ✓ |  |
| 是入口/出口/时序边界 | ✓ |  |
| 是非目标 / 红线 / 不能破坏的约束 | ✓ |  |
| 带"暂定/未决/待定" | ✓（必须保留标记） |  |
| 是参数表、阈值、文案池 |  | ✓（→ Knowledge Pack locked facts） |
| 是单点 UI 形态、像素、动效 |  | ✓ |
| 1-2 行写不清楚 |  | ✓ |

冲突情况：信息既命中升又命中下时，**约束面优先**——只要它约束 ≥2 个工作块，无论字数和细节都先升锚点，太细的部分再切片下沉到 runtime group。

#### 5 类类型词

锚点开头带类型词，让 Worker 一眼看出是用来卡哪种事的：

| 类型词 | 干什么 | 示例 |
|---|---|---|
| `非目标` | 全局红线 | `非目标：贴纸属社交表达，禁止进入得分链路` |
| `入口/出口` | 时序边界、状态切换点 | `入口/出口：阶段一 10s，贴纸仅自己可见` |
| `时序` | 顺序约束 | `时序：个人 C 位按座位 1→4 顺序展示` |
| `未决点` | 待拍方案 / 暂定值 / 待裁冲突 | `未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工` |
| `来源` | authoritative source 指针 | `来源：v1.4.2 PRD §方案详情·亮相` |

这 5 类正好对应规则 0E 允许放入锚点的内容。其他类型一律不进锚点。

#### 正反例（用 morph72-v14 PRD 真句）

| # | PRD 原句 | 判定 | 理由 |
|---|---|---|---|
| 1 | 「贴纸不影响得分」 | **锚点** | 全局红线，约束 UI/结算/锐评等多 Worker |
| 2 | 「每位玩家对每位玩家（含自己）均可贴」 | **runtime 细节** | 贴纸功能内部矩阵，只约束贴纸 UI 一处 |
| 3 | 「阶段一 10s 内贴纸仅自己可见」 | **锚点** | 时序边界，整个亮相状态机绕它转 |
| 4 | 「前三轮 1/2/3/4 名 +10/+6/+3/+1，第四轮加倍」 | **runtime 细节** | 参数表，只服务结算 Worker（→ Knowledge Pack locked facts） |
| 5 | 「结算页 15s（暂定）」 | **拆开** | 时序 + 参数值夹一层，必须先拆：时序进锚点，15s 进 runtime 参数；详见下方"句子拆分"第二例 |
| 6 | 「断线时卡片置灰，服务端自动设 Ready」 | **拆开** | 后半句锚点（多 Worker），前半句 runtime UI |
| 7 | 「展示按座位 1→4 顺序」 | **锚点** | 状态机驱动顺序，跨前后端 |
| 8 | 「故事反馈策划 prompt 未定」 | **锚点** | 未决点 + 派工准入条件（禁派实现） |

#### 反例：产品宣言不能进锚点

PRD 里这种显眼的口号**不进锚点**：

- "这是 V1.4 的核心目标：让亮相变得有趣"
- "强化社交体验"
- "提升玩家留存"

它们没有可执行约束面，Worker 拿不出尺子量"我做的够不够有趣"。要保留就去 Knowledge Pack 开篇说明，不进路书锚点。

锚点的判定标准：**Worker 能拿来量自己实现的合规性**。
- "贴纸不影响得分" → 能量（看代码有没有把贴纸算进 score）
- "让亮相变得有趣" → 量不出来 → 不是锚点

#### 句子拆分（一句话夹两层时）

PRD 一句话夹两层很常见，至少有两种夹法都需要先拆。

**夹法 1：动作 + UI 形态**

> 「断线时**卡片置灰显示『已离线』**，**服务端自动将其设为 Ready**」

- "服务端自动设 Ready" → 行为约束，影响 Ready 状态机/倒计时跳转/下一轮触发 → **锚点**
- "卡片置灰显示『已离线』" → UI 形态，只约束前端展示 → **runtime group（实现节点）**

**夹法 2：时序边界 + 参数值**

> 「**结算页面时长暂定 15s**」

- "锐评结束 → 结算页 → 全员 Ready 或倒计时结束 → 离开" → 时序+入口/出口约束，约束 Ready 状态机 / 倒计时跳转 / OS 触发 / 下一轮 → **锚点**
- "15s" 数值 → 配置常量，只服务倒计时一处 → **runtime 参数 + Knowledge Pack locked facts**
- "暂定" → 标识值还没锁，但方案已定 → **未决点 A 类锚点的修饰**

正确写法是两条锚点：
```
入口/出口：锐评结束 → 结算页 → 全员 Ready 或倒计时结束 → 离开
未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现
```

错误写法（粗暴整句当一条锚点）：
```
未决点：结算页 15s 暂定 → owner=Curator → 不阻塞   ← 把时序和参数糊一起
```

锚点只取**约束面广的那一部分**。不拆直接整句抄，等于规则 0E 禁止的"完整 PRD 原文"。

### 规则 0I：未决点 A/B/C 三类与生命周期

PRD 里的"未决"是杂类词，至少分三类，路书表现不同。混着写就会"明明只是暂定却整个首环卡红""明明是冲突却被当成暂定放着不管"。

#### 三类未决点

| 类型 | 例子（morph72 真句） | 当前是否有结论 | 阻塞面 | 路书表现 |
|---|---|---|---|---|
| **A. 参数暂定** | 「结算页 15s 暂定」 | 方案有，值待锁 | 不阻塞 | 锚点 + runtime 参数节点（实现仍可派） |
| **B. 方案未定** | 「故事反馈策划 prompt 未定」 | 没有 | 阻塞实现派工 | 锚点 + runtime 全调查节点（不可派实现） |
| **C. 冲突未裁** | "PRD 写 15s，Figma 标 20s" | 有但相互矛盾 | 阻塞整个工作块 | exception.md + 红节点（必须人工裁决） |

#### 锚点写法

未决点类锚点必须带 **owner** 和 **阻塞面**，否则驱散动作漂浮：

```
未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工
未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现
未决点：PRD 与 Figma 时长冲突 → owner=Curator → KP-02 阻塞
```

注意第二条不能写成"未决点：结算页 15s 暂定 → ..."——这违反规则 0H 句子拆分。"结算页面时长暂定 15s" 这句 PRD 夹了"时序入口/出口"和"参数值"两层，必须先拆：时序进 `入口/出口` 锚点，参数值 15s 进 runtime 参数节点 + Knowledge Pack locked facts，"暂定"修饰留在未决点锚点上。

owner 决定**谁去追**，阻塞标记决定**追之前路书允不允许派工**。两条信息少一条都会漂。

#### 颜色路径

未决点本身**不会让首环直接变红**。颜色路径是：

```
首环灰（还没开始）
    ↓ 主 Agent 决定推进
首环黄 + 必须建右侧 runtime group（规则 3）
    ↓ runtime group 里挂调查节点
调查节点黄（持续追 owner 中）
    ↓
    ├─ 拿到答案 → 调查变绿 → 锚点改写（去"暂定"）→ 所属 runtime group 派实现
    └─ 调查不下去（外部阻塞）→ 调查变红 + exception.md
```

**调查节点持续黄是合法状态**。"在追"不等于"卡死"。

#### 调查节点变红的阈值

规则 7 只说了"红色 = 阻塞/异常"，没说"调查节点要黄多久才变红"。务实阈值（任一命中即变红）：

| 阈值 | 例子 |
|---|---|
| owner 跨 sprint 边界（≥1 sprint）仍无进展回报或 ETA | 主 Agent 追了一周策划仍没有回复或时间表 |
| owner 明确说"我给不了答案"，且没有给出下一任 owner | 策划说"等产品总监决定"，但没有明确谁承接 |
| 输入超出当前 owner 能力边界，且没有升级路径或 ETA | 等微信小程序审核，但没有提交单/负责人/预计反馈时间 |
| 出现"未决套未决" | 调查贴纸模型时发现配置中心方案也没定 |
| 调查耗时 ≥ 该首环可承受总时间 50% | 2 周交付的首环已花 1 周在调查 |

两条配套规则：

1. **判定主体永远是主 Agent**。Worker / Curator 只能上报事实，红不红由主 Agent 拍。
2. **持续黄是合法状态**。不要因时间稍长就草率变红。

#### 完整生命周期

```
[T0] PRD 抓事实卡时识别未决点
    ↓
[T1] 升首环时挂锚点（owner + 阻塞面 + "暂定/未定/冲突" 标记）
    ↓
[T2] 首环开始处理，建右侧 runtime group，group 内加调查节点
    ↓
[T3] 调查节点持续黄；主 Agent 至少每 sprint 回访 owner
    ↓
[T4a] 拿到答案 → 调查变绿 → 锚点改写（去"暂定/未定"）→ 派实现节点
[T4b] 超期/外部阻塞 → 调查变红 → exception.md 立条
    ↓
[T5] Exception 关闭 → 调查变绿 → 同 T4a
```

T3 的回访频率与"跨 sprint 边界"阈值挂钩——主 Agent 至少每 sprint 回访一次。跨了一个 sprint 仍无进展回报或 ETA，才升级到 T4b；如果 owner 明确在推进并给出下一步时间表，调查节点保持黄色。

#### Exception 升级条件（任一命中即升级）

- 未决点跨 sprint 边界仍无进展回报或 ETA
- 驱散需要主 Agent / Curator 之外的人介入，但没有明确承接人、升级路径或 ETA
- 未决点会让多个首环连锁变红（不只它自己）
- 未决点和 PRD/代码现状直接冲突（不只是缺值）—— 此条直接归 C 类，从一开始就该写 Exception

反向校验：**exception.md 每条都要指向至少一个红节点**。无对应红节点的 Exception 条目是死信，必须清理（说明阻塞已解除但没回写）。

### 规则 0J：错知识反路径与锚点版本管理

错知识 vs 未决点的本质差别：**错知识从绿撤、未决点从灰爬**——方向相反。

| 维度 | 错知识 | 未决点 |
|---|---|---|
| 当前是否有结论 | 有（已写进文档/代码/PRD/锚点） | 没有 |
| 病灶 | 已有结论错了/失效/被 supersede | 还没有结论可用 |
| 起点 | 已经进过执行链 | 从来没进过 |
| 驱动方向 | **退出**默认上下文 | **进入**默认上下文 |
| Curator 字段 | `conflicting / stale / superseded` | `gray knowledge` |

#### 错知识路书侧反路径

curator skill 的 Repair Loop 7 步是知识库视角写的（移出 README → 降级 D → 替代真源 → Repair Record → 重组路径 → 新 KP）。**路书侧的反路径**在这里：

```
[T0] Worker 跑 E2E / 实现时撞到现状不符 → 上报主 Agent
[T1] 主 Agent 把当前节点（甚至已绿的节点）标红 + exception.md 立条
[T2] 主 Agent 派 Curator 走 Repair Loop（curator skill 7 步）
[T3] Curator 完成 → 主 Agent 拿到新 Knowledge Pack
[T4] 主 Agent grep .canvas 找所有引用了这条 knowledge_id 的首环锚点
[T5] 改写锚点为新真源；若旧锚点曾让节点变绿，相关节点回退到黄
[T6] 节点红→黄继续推
```

**T4 / T5 是 skill 闭环关键**：不审计锚点，新派工的 Worker 还会拿错锚点干活，Repair Loop 白做。

#### 锚点版本管理（核心规则）

**每次 Curator 出新版本 Knowledge Pack（不论是 Repair Loop 触发，还是未决点驱散触发），主 Agent 都要在写回 `.canvas` 前做一次锚点 grep 审计**：

1. grep `.canvas` 找所有首环锚点中引用旧 knowledge_id / 旧 source 路径 / 旧 fact 字面值的位置
2. 引用了已被替代/降级的真源 → 改写为新真源指针
3. 引用了已删除/已归档的真源 → 删除该锚点；若该首环锚点剩余 < 2 条，复核 5 选 1 资格是否仍成立
4. 该锚点曾支撑某个绿节点 → 相关绿节点回退到黄重新验证
5. 审计完成后才写 `.canvas` 并跑 audit.py

#### "假绿"撤回

错知识能让节点错误地变绿（Worker 跟错知识对齐了反而通过验收）——这种**假绿**必须能撤销。规则 7.3 已经允许"出现新问题或回退" 触发绿→黄/红，撤假绿就走这条。

撤假绿动作清单：

- 节点绿 → 红（标 Exception 起因）→ 黄（Repair Loop 完成后）
- runtime group 若已折叠/简化，需重建相应跟踪链
- 如果假绿曾向上传播让父节点也变绿，父节点同步回退
- Worker Pack 重新生成（带新 KP），重派 Worker 验证

#### 三色知识到锚点的映射

curator 的三色知识体系是知识库视角，对应到路书锚点视角：

| Curator 三色 | 路书锚点对应 |
|---|---|
| white knowledge | 锚点正面陈述（"贴纸不影响得分"） |
| gray knowledge | 锚点带"暂定/未定"标记（未决点 A/B 类） |
| black knowledge | 锚点完全不引用（弃用方案、"不用看"） |
| `conflicting` | exception.md + 红节点（未决点 C 类） |
| `stale / superseded` | 锚点 grep 审计后改写或删除 |

也就是说：**首环锚点是 curator 三色知识的"被使用面"**。一旦某条 white 被降级到 gray 或 black，主 Agent 必须把对应锚点撤掉或加未决标记。

### 规则 0K：canvas.group 包裹工作块整体

每个被处理的 spine 节点必须被一个 JSON Canvas `type:"group"` 节点几何包住，**包裹范围含 P 自身 + P 的所有 runtime 节点 + runtime 内部子链递归到底**。

#### 强制条件

- **当 `color(P) ∈ {黄/红/绿}` 且 P 是 spine 节点**：必须存在 group `G_P`，几何完全包含 `Workblock(P) = {P} ∪ runtime(P) ∪ runtime 子链(...) ∪ ...`
- **当 P 是灰色 spine 节点**：禁止有 group（违反规则 6 + 0K）
- group label：`工作块:<P.id>:[处理中|已完成|阻塞]`
- group color 镜像 P：`处理中=5`（青，不参与传播）/ `已完成=4`（绿）/ `阻塞=1`（红）
- group label 状态后缀必须与 P.color 一致：黄↔处理中、绿↔已完成、红↔阻塞

#### 嵌套规则

**允许完全包含**：子工作块的 group 可以套在父工作块的 group 内，但必须几何**完全包含**或**完全分离**——即任意两个 group 矩形 G_a / G_b 满足以下三种之一：

1. G_a 完全包含 G_b（含 padding 容差）
2. G_b 完全包含 G_a
3. G_a 与 G_b 完全分离（无重叠）

**禁止部分相交**：任意两个 group 矩形发生 partial intersect（既有重叠又互不完全包含）是 P0 违规。

#### 装饰 group（非语义 group）

除 `工作块:` 和 `Gate:` 外，允许存在纯视觉用途的 JSON Canvas group。装饰 group 只能用于框选、标注或分区，不能承载进度语义：

- label 不得以 `工作块:` 或 `Gate:` 开头；推荐使用 `装饰:<名称>` / `区域:<名称>` 这类前缀。
- 装饰 group 不产生 owner，不镜像任何节点颜色，不参与红黄绿传播，不代表 runtime group 或 gate group。
- audit.py 在判定 `innermost`、runtime 链归属、跨 group edge 时把装饰 group 视为透明；真正的结构归属仍只看 `工作块:` / `Gate:` 语义 group。
- 装饰 group 可以完全包含一个或多个语义 group，也可以完全位于某个语义 group 内；但仍必须遵守“完全包含或完全分离”，任何 partial intersect 仍是 P0。
- 装饰 group 不能放宽跨 group edge 规则：两个不同 `工作块:` group 之间即使被同一个装饰 group 框住，也仍然禁止直接连 runtime 边。

#### 工作流约束（与规则 3 联动）

spine 节点灰→黄时，主 Agent 必须**同时**做三件事：

1. 把节点 color 改黄
2. 在节点右侧创建 runtime 链（开始→...→结束）
3. 创建 `工作块:<P>:[处理中]` group 包住 P 自身 + 整条 runtime 链

任何节点变色都必须同步更新对应 group 的 label 状态后缀和 color：黄→绿时 group label `[处理中]→[已完成]` + color `5→4`；黄→红时 group label `[处理中]→[阻塞]` + color `5→1`。

#### 黄→绿后保留 group

工作块完成（P 黄→绿）后，group 不删除，作为历史证据：

- 规则 0J 锚点 grep 审计需要找出"哪些 group 引用了被替代的 knowledge_id"
- 假绿撤回（绿→红）需要 group 还在以便 audit 追踪
- 项目结题归档时才考虑折叠或删除 group

### 规则 0L：Gate group

KP-00 ~ KP-06 等 gate 是**闭环门禁节点**，不是左侧说明牌、也不是 Agent 流程图。Gate 必须连接在前任务之后、后任务之前，用 `前置工作块 → Gate → 后续工作块` 表达它阻挡和验证的具体进度：gate 未过，后续闭环不能合法推进或转绿。

Gate 节点仍必须封装到独立 group：

- gate 节点的 text 以 `Gate:` 前缀或 `KP-` 开头
- gate group label：`Gate:<gate_id>:<gate 名>`，例如 `Gate:KP-00:Domain Locked`
- gate group color：`6`（紫，护栏，不参与传播）
- **位置**：gate group 位于首环主干上，夹在被它验证/阻挡的前后节点之间；与所有 `工作块:` group 完全分离（不允许任何重叠）
- gate 节点不在 Gate group 内是 P0 违规
- gate 节点不在 spine 主干上、没有前驱或没有后继，都是 P0 违规

gate group 与 workblock group 不允许嵌套——它们必须完全分离。

## 新角色规则

### 主 Agent

- 唯一可写 `.canvas`
- 负责 checkpoint、路书回写、`exception.md`、Worker Pack 生成
- 不能跳过 Curator 直接给代码型 Worker 派工

### Knowledge Curator

- 负责业务域确认、文档检索、authority 分级、冲突裁决建议、错知识修正与文档回写
- 不能改 `.canvas`
- 不能直接把节点改绿；只能通过 `KP-04/KP-05` 向主 Agent 证明知识面已闭环

### Worker

- 只做执行、验证、证据采集
- 不能直接修改业务域知识结论
- 发现知识冲突只能上报，不能私自覆盖

## 业务域门禁规则

### 规则 9：没有业务域，先问用户

如果任务属于代码、设计、排障、方案裁决、联调分析中的任一种：

- 没有业务域时，先问用户业务域
- 没有 `[[功能点]]` 或域文档时，先由 Curator 判断是否需要补齐业务域资料
- 在 `KP-00 Domain Locked` 前，不允许派代码型 Worker

### 规则 10：文档读取顺序固定

Curator 的默认读取顺序必须是：

1. `rg/grep` 业务域 README 与 `[[功能点]]`
2. `obsidian-cli` 的 `search/read/backlinks/property`
3. MCP 兜底

只要前一步拿到了足够信息，就不要继续扩大上下文。

### 规则 11：默认知识面必须被索引

- 只有业务域 README 中被索引的知识项，才允许进入默认 `Knowledge Pack`
- 未索引文档默认视为旁路材料，除非 Curator 显式提级

## Knowledge Pack 规则

### 规则 12：代码型 Worker 必须拿到 Knowledge Pack

`Knowledge Pack` 固定字段（必须和 curator skill 字段定义保持一致；任一字段缺失即视为 KP 不完整）：

- 业务域
- 功能点
- authoritative sources
- baseline sources（白知识）
- advisory sources（按需命中的灰知识）
- blocked sources（黑知识或本轮禁用知识）
- locked facts
- open conflicts
- stale sources to ignore
- writeback targets

字段语义见 curator skill 「输出物 / Knowledge Pack」一节。没有完整 `Knowledge Pack`，不允许触发 `KP-03 Worker Pack Ready`。

Worker Pack 是 gate 的产物，也是闭环门禁的一部分：它只覆盖当前 runtime group 安全推进所需的最小上下文、写域和证据要求。它不是复制 OpenSpec、不是复制 tasks.md，也不是 SubAgent 自己的完整执行计划。

**Worker Pack 派发约束**：
- `baseline sources` 默认进 Worker Pack，可作为 Worker 实现依据
- `advisory sources` 仅当当前任务命中时进入，且 Worker Pack 必须显式标记"按需"
- `blocked sources` **不进 Worker Pack**；如果 Worker 上报中触及 blocked source，主 Agent 必须立即标红并写 exception.md

### 规则 13：证据和知识分离

- `HAR`、日志、截图、rerun JSON 属于 `C.evidence`
- 证据可以被引用，但不能整份塞进默认 `Knowledge Pack`
- `Knowledge Pack` 只收摘要和路径，不收长原文

## 错知识规则

### 规则 14：发现错知识必须触发 Repair Loop

当 Curator 发现某条知识存在以下任一情况时，必须触发 `Repair Loop`：

- 与 PRD 冲突
- 与代码事实冲突
- 与更高 authority 文档冲突
- 已被新结论 supersede
- 虽未完全错误，但继续保留在默认上下文会误导 Worker

### 规则 15：默认处理方式是降权 + 归档

错知识的默认处理方式固定为：

1. 从业务域 README 和默认 `Knowledge Pack` 中移除
2. 降级为 `D.stale/legacy`
3. 移入 `archive/legacy/`，或保留原地但不再被索引
4. 在 authoritative 文档补上替代真源

只有以下三类内容允许直接删除：

- 纯重复副本
- 无追溯价值的 AI 草稿
- 未被任何索引和引用的临时中间文件

### 规则 16：Repair Loop 必须形成记录

每次 Repair Loop 都要有一条 `Knowledge Repair Record`，至少包含：

- `knowledge_id`
- 业务域
- 功能点
- 错误原因
- 被移除入口
- 替代真源
- 受影响节点
- 重新调研范围

### 规则 17：Repair Loop 未闭环时不能转绿

如果当前节点依赖的知识项仍处于 `conflicting/stale` 且还没完成：

- 索引移除
- 替代真源写回
- 新 `Knowledge Pack` 生成

则 `KP-05 Knowledge Repair Closed` 不通过，节点不能转绿。

## Gate 规则

### 规则 18：KP-00 到 KP-06

- `KP-00 Domain Locked`：业务域已确认
- `KP-01 Sources Locked`：Curator 已锁 authoritative sources
- `KP-02 Conflict Verdict Issued`：冲突已被裁决或已进入 `exception.md`
- `KP-03 Worker Pack Ready`：Knowledge Pack 和 Worker Pack 已准备好
- `KP-04 Docs Writeback Done`：README / 叶子文档 / 代码落点已回写
- `KP-05 Knowledge Repair Closed`：错知识已退出默认上下文，替代真源已就位
- `KP-06 Node Can Turn Green`：进度、知识、证据、异常四者一致

### 规则 19：回写顺序不可颠倒

收到回报后的顺序必须是：

1. 如回报包含新 Knowledge Pack / Repair Loop / 未决点驱散，主 Agent 先按规则 0J 审计当前 `.canvas` 锚点
2. 主 Agent 改 `.canvas`（状态变化、锚点改写/删除、必要节点回退同批写入）
3. 主 Agent 更新 `exception.md`（若需要）
4. Curator 回写业务域 docs
5. 主 Agent 再决定是否转绿

禁止先改 docs 再补 `.canvas`；也禁止 Curator 出新 KP 后跳过 0J 锚点审计直接回写 `.canvas`。

## 文档关联规则补充

### 规则 20：变绿不仅要有代码证据，还要有 docs 证据

当节点需要知识闭环时，黄→绿至少要同时满足：

- 代码/测试/运行证据存在
- 业务域 README 或叶子文档已更新
- 代码落点已写入文档
- 若曾触发 Repair Loop，则旧知识已降权或归档

## 拓扑规则

### 规则 0：单棵树 / 单连通图（硬约束）

**整个 canvas 必须是从唯一根节点出发的单连通图。** 所有业务节点必须能从根节点沿 edge 走到。

- 禁止多个并行、互不连通的子图
- 禁止悬挂分支（无 edge 连接到主树的业务节点）
- 历史节点 / 归档节点要么折叠进主树（作为已绿的上游里程碑），要么直接删除；不允许作为并行子图挂在 canvas 上
- 说明节点（左上角外侧）不参与连通性要求，可以游离

**校验方法**：从根节点跑 DFS/BFS，收集所有可达的业务节点；`unreached = biz_nodes - reached` 必须为空。直接用 `audit.py` 校验。

> **踩过的坑**：早期版本允许 `v14-historical-root` 青色分支挂历史 drilldown、`admin-web` 绿块独立成行、`fanout-*` 节点孤立——结果 canvas 变成 4 个并行子图，Obsidian 渲染出来一看就是"散架的项目板"。单棵树是唯一能支持"从头到尾一层一层往下走"的拓扑。

### 规则 0A：闭环可验收，必要时才下钻到任务叶子

路书不是概览，是**完成闭环的执行真源**。它必须能回答：当前目标从开始到结束还差哪些可验收工作块、每个工作块的 runtime 链是否足够支撑派工和验证。

tasks.md 的单行 checkbox 或等价颗粒用于校验 runtime group 是否足够可执行；它**不能反向决定首环结构**，也不能把每个 checkbox、OpenSpec 章节或组件名提升为主干节点。

- 首环主干按完成闭环组织；tasks.md 只用于检查右侧 runtime group 是否漏了可验收叶子。
- 首环主干节点开始处理后，右侧 runtime group 内按事实卡 / 调查 / 实现 / 验证 / 证据 / 未决点拆到可分配、可验收的粒度。
- 只有 3 层（根 → 首环 → phase）的结构通常过浅——phase 下面至少还要有能证明闭环推进的 runtime 叶子。
- 如果一个工作块的 tasks.md 有 10 条勾选项，路书不一定要生成 10 个 spine 节点；但这个工作块的 runtime group 应能覆盖这些任务对应的动作、证据或裁决点，外加 `开始-/结束-` 节点。
- 节点数量和树深不是目标本身。大型联调路书经常会超过 60 个业务节点、深度 ≥ 5，但这是闭环被拆细后的结果，不是建板指标。

> **踩过的坑**：早期版本把 `ring-1-gsc-question` 画成一个 phase 就带过，下面只有 4 个 `r1-p1..p4` 节点——但 `update-morph72-v14/morph72-v14-union-dev/main-pharse/tasks.md` 里 Ring 1 有 16 条 checkbox。结果派工时根本看不到"下一步具体做哪一条"。正确做法是让 runtime group 覆盖这 16 条背后的动作、证据和裁决点，按 resource-delivery / createroom / runtime / async-history / knowledge-lock 五组组织叶子，而不是把 checkbox 原样复制成主干。

## 首环主干与运行时闭环规则详解

### 规则 1：首环 = 竖向主干，runtime = 横向闭合回路

规则 1 拆为三条精确化子规则：1A 管首环 spine，1B 管 runtime 链，1C 管 runtime 内部子链。

**首环视觉形态**（开始在最下、结束在最上、自下而上推进）：

```
                根（顶部）
              ↑    ↓
              ↑   结束（紧贴根下方）
              ↑    ↑
              ↑   工作块 N-1
              ↑    ↑
              ↑   ...
              ↑    ↑
              ↑   工作块 1
              ↑    ↑
              ↑   开始（最下方）
              ↑    ↑（root → 开始 是 top→bottom 外圈起跳）
              └────┘（结束 → 根 是 left→left 左侧外圈）
```

**runtime 视觉形态**（spine 节点右侧水平展开）：

```
工作块 P  ──→  ┌─ 工作块:P:[处理中] group ──────────────────────┐
              │  开始处理 → 调查/实现/验证 → 结束处理            │
              │                ↓                                 │
              │         子链开始 → 子链处理 → 子链结束            │  （同 group 内向下另起一行泳道）
              └─────────────────────────────────────────────────┘
```

### 规则 1A：首环 spine 三槽位精确化

首环主干竖向闭合，开始在最下、结束在最上。spine edge 必须严格按以下三槽位之一：

| 槽位 | fromSide | toSide | 视觉 |
|---|---|---|---|
| 根 → 开始（spine 起始） | `top` | `bottom` | 根的上边出，开始的下边进。开始在根下方。 |
| spine 链内（i → i+1） | `top` | `bottom` | i 的上边出，i+1 的下边进。i+1 在 i 上方。视觉是从下往上推进。 |
| 结束 → 根（spine 闭环） | `left` | `left` | 结束的左边出，沿左侧外圈回根的左边，避开主干节点。 |

audit.py 用 `(fromSide, toSide, fromNode==root, toNode==root)` 四元组判定 spine edge 槽位归属。

### 规则 1B：runtime 链三槽位

工作块 P 派生的 runtime 链必须横向闭合：

| 槽位 | fromSide | toSide |
|---|---|---|
| 工作块 P → runtime 开始 | `right` | `left` |
| runtime 链内 | `right` | `left` |
| runtime 结束 → P | `bottom` | `bottom` |

### 规则 1C：runtime 内部子链

runtime 节点 Q 又派生子链时，**保持横向方向**（不交替方向，避免视觉混乱），y 偏移另起泳道：

| 槽位 | fromSide | toSide | 备注 |
|---|---|---|---|
| Q → 子链开始 | `bottom` | `top` | 从 Q 下方进入子泳道，避免与 Q 的横向出边同侧 |
| 子链内 | `right` | `left` | 同 1B 方向 |
| 子链结束 → Q | `top` | `top` | 子链结束的 top 出，回 Q 的 top |
| 子链节点 y 偏移 | — | — | `y = Q.y + GAP_VERTICAL_LANE`，仍在同一 group 内 |

子子链以下层级递归同此规则，不引入"depth % 2 交替方向"。所有 runtime 内部链都是水平方向，仅用 y 偏移区分泳道——audit.py 不需要识别 depth，只校验"同一 group 内边方向一致 + 节点 x 单调递增"。

### 规则 1D：节点端口分离与线段避让

同一个可见节点上，任何入边 `toSide` 不得与任何出边 `fromSide` 使用同一侧。否则读图时无法判断该节点是在承接、放行还是回收进度，是 P0 违规。

Edge 不得穿过非端点节点的矩形内部。runtime 闭合回线必须走节点外侧通道（例如 `bottom → bottom` 下绕），不能用同一行长回线横穿已经画出的 runtime 子节点。

因此：

- spine 节点通常用 `bottom` 进、`top` 出。
- runtime 节点通常用 `left` 进、`right` 出；闭合回父节点走下方通道。
- runtime 子环从父 runtime 节点 `bottom` 出、从 `top` 回，和横向主链端口分离。

### 规则 2：最小环 = 两个节点

一个父节点派生的最小 runtime 链只有两个节点：

```
父 → 开始X → 结束X → 父
```

这是合法的最小运行时闭环。不允许只有开始没有结束，也不允许只有结束没有开始。

### 规则 3：灰→黄 = 必须补横向 runtime 链（核心触发规则）

**这是整个路书系统最关键的规则。**

当一个节点从灰色（无色，未开始）变成黄色（开始处理）时，**必须立即**补一条从开始到结束的横向 runtime 链：

- 如果它是首环主干节点或 gate：在该节点右侧创建 `工作块:` / `Gate:` group。
- 如果它已经在某个 runtime group 内：在同一个 group 内另起横向子链；只有需要独立 gate、独立 Worker Pack、跨工作块隔离，或会改变 spine 闭环顺序时，才评估升为 spine。

```
之前: 节点A (灰色, 无 color)
之后: 节点A (黄色, "3") → [工作块:节点A:[处理中] group: 开始处理A → 结束处理A] → 节点A
```

**没有闭合 runtime 链的黄色节点是违规的。** 开始处理一件事 = 必须为它建立横向工作台来跟踪过程。

灰色节点没有 runtime 链是正常的——因为还没开始，不需要跟踪。

### 规则 4：新问题插入 runtime 横向链条

执行过程中遇到的新问题**先插入所属 runtime group 的横向链条中**，不是插回首环主干，也不是分叉成树枝。插入后再判断它是否需要在同 group 派生子环；只有满足规则 3 / 5 的升 spine 条件时，才从 runtime 细节提升为主干工作块。

**合规（插入链条）**：
```
之前: 父 → 开始 → 结束 → 父
之后: 父 → 开始 → 问题A → 问题B → 结束 → 父
```

**违规（分叉成树）**：
```
父 → 开始 → 结束 → 父
       ├→ 问题A
       └→ 问题B
  ← 违规：问题A/B 没有在 runtime 链条中，成了悬挂分支
```

插入的新节点**默认灰色（无色）**——还没开始处理。当它被开始处理时，走灰→黄触发规则 3，为它补横向 runtime 链；若它是首环/gate 节点才新建右侧 group。

插入操作的 edge 变更：
- 断开原有 edge（例如 开始→结束）
- 新增：开始→问题A（edge 无 color，因为问题A 是灰色）
- 新增：问题A→结束（edge 无 color）
- 保留：结束→父

### 规则 5：中间节点可派生横向 runtime 子链

runtime 链条中的任何中间节点，如果需要进一步拆解，它自身成为新的父节点，在同一 runtime group 内右侧继续派生横向子链；空间不足时可在同一 group 内向下另起一条横向泳道：

```
runtime 主链: 父 → 开始 → 问题A → 结束 → 父
                            ↘
runtime 子链:                 开始解决A → 结束解决A → 问题A
```

子链同样可以继续插入节点、继续派生更深的 runtime 子链。**嵌套深度没有限制，但默认都留在所属 runtime group 内**；只有跨工作块依赖、独立 gate 或需要单独派工隔离时，才拆成相邻的独立 group。所有子链都遵守同一套事实卡/顺序/证据/未决点收敛规则。

禁止把“发现新问题”直接理解成“新增 spine 节点”。默认路径必须是：`同 group 插入灰节点 → 开始处理时同 group 子环 → 评估是否跨工作块/gate/Worker Pack/主干顺序 → 必要时升 spine`。

同一个 runtime group 只有一个**外部 owner**（它右侧对应的首环/gate 节点），但 group 内允许多个内部 runtime 父节点继续生横向子链。脚本判定时应区分外部 owner 和内部父节点，避免把“补处理子链”误判成 group 多 owner。

### 规则 5A：Loop 状态事务（绝对同步）

每一次 Loop 回报都必须被主 Agent 压成一个 `Loop Delta`，并作为一次不可拆的 `.canvas` 状态事务写入。路书的目标不是事后总结，而是让用户随时打开 canvas 就能看见任务是怎么被完成的。

`Loop Delta` 最小字段：

| 字段 | 含义 |
|---|---|
| `scope` | 当前 spine 节点 / runtime group / runtime 节点 |
| `event` | `start / complete / block / unblock / discover / repair / rollback` |
| `state_after` | 回写后的目标颜色：灰 / 黄 / 红 / 绿 |
| `evidence` | 支撑状态变化的证据；黄/红可记录原因，绿必须有验收证据 |
| `structure_delta` | 新增节点、插入链条、创建子环、扩 group、升 spine、写 Gate |
| `knowledge_delta` | 新 KP、Conflict Verdict、Repair Loop、旧知识退出、锚点改写 |
| `sync_required` | edge color、父节点传播、group label/color/几何、exception/docs 回写 |

状态事务顺序固定：

1. **定位 scope**：先找到当前 workblock group 和被回报的 runtime 节点；没有明确 scope 的回报不能直接落路书。
2. **结构先行**：发现新任务先插入同 group 横向链；开始处理则同 group 派生子环；只有跨工作块、独立 gate / Worker Pack 或改变 spine 顺序时才升 spine。
3. **写节点状态与证据**：节点文字只写最小证据索引，不把长日志、长讨论塞进 canvas。
4. **自底向上传播颜色**：子环 → runtime 节点 → 外部 owner → spine；全绿才绿，全红才红，其余黄。
5. **同步 edge color**：所有 edge color 必须跟随 `toNode` 的颜色。
6. **同步 group**：group label 后缀、group color、group 几何必须和 owner 及内部节点一致；新增节点后 group 需要扩到完整包含递归子链。
7. **跑 audit + 人工清单**：`audit.py` 过 P0 后，再人工检查状态是否与 agent 真实进度一致。

禁止拆事务：

- 只改节点颜色，不补 runtime 链 / 子环 / group。
- 只在聊天或 Todo 里记录新任务，不插入 `.canvas`。
- 只改节点文本，不同步 edge color。
- 父节点变色后不改 group label 状态后缀和 group color。
- 新增 runtime 节点后不扩大 group，导致 group 不能完整包含 P + runtime + 子链。
- Worker 已经推进下一步，主 Agent 还没先回写上一轮状态。

如果工具暂时不能自动应用事务，主 Agent 也必须按上述顺序手工修改 `.canvas`；不能把“后面统一整理”作为理由延迟同步。

### 规则 5B：外部循环必须映射成内部子环

Codex Goal / 进度面板、Claude Code Ralph Loop、SubAgent review round、主 Agent 自查 checklist 都不是 `.canvas` 的替代状态源。它们只要影响 roadmap closeout、节点颜色、回退、验收或 gate，就必须先被压成 `Loop Delta`，再在当前 runtime 节点下创建一个闭合的内部子环。

适用触发：

| 外部循环信号 | 必须落到路书的结构 |
|---|---|
| Codex Goal checklist 出现一组“本轮已完成/待完成”项 | 当前 runtime 节点下创建 `Round N / Goal step` 子环；checklist item 只能作为子环节点或证据摘要，不能直接升父环 sibling |
| Claude Code `/ralph-loop` iteration 完成 | 当前 runtime 节点下创建 `Ralph iteration N` 子环；iteration 的发现、修复、验证、review 作为该子环内部节点 |
| reviewer / skeptic / 主 Agent 自查发现需要回退或补证据 | 先在当前 runtime group 插入灰/黄节点；若已经开始处理，立即派生子环 |
| Repair Loop / 旧知识退出导致假绿撤销 | 被撤销节点回退黄/红，同时在回退节点下创建 `Repair / rollback` 子环记录“识别旧知 -> 替代真源 -> 改锚点 -> 重验” |

子环状态传播要求：

1. **一轮一个子环**：一轮外部循环对应一个内部子环；不要把外部 progress checklist 一项项散落成父 runtime 链 sibling。
2. **子环整体变色**：同一轮子环的节点、edge、group 几何和父节点传播必须在同一批事务里写入；不得今天绿一个 checklist、明天绿一个 checklist。
3. **父节点不跟着假完成**：子环全绿只证明“这一轮执行闭合”；父 runtime / spine 是否转绿仍取决于外层入口/出口、证据和 gate。父节点可以继续黄或红。
4. **证据留在节点摘要**：子环节点只放短证据索引；长日志、长 review、长问答放 OpenSpec evidence、audit-log、exception.md 或业务域文档。
5. **audit 后才能宣称完成**：子环写入后必须跑 `audit.py` 并人工检查 P0 清单；audit 失败时，外部循环只能报 blocked / partial，不能包装成完成。

#### Codex Goal 约束

Codex Goal 是执行会话的目标包装，不是路书状态源：

- 只有用户显式要求创建 Goal，或当前会话已经存在 active Goal 时，才把 roadmap 节点绑定到 Goal；不能为了“显得有进度”临时造 Goal。
- Goal 只能描述当前闭环的目标、gate 和停止条件；不能把未创建/未批准/未验证的子 OpenSpec 或代码实现写成已完成目标。
- Goal checklist 每次 closeout 前必须映射到 `.canvas`：有状态变化则创建/更新子环；没有状态变化也要说明“本轮无 roadmap delta”。
- `update_goal complete` 只能发生在 `.canvas` 已写回、父环颜色传播完成、`audit.py` 通过、快问快答自检完成之后；Goal complete 不能作为节点转绿证据。
- Goal 超预算、暂停、被中断或只完成部分 gate 时，roadmap 对应节点保持黄/红，并写明唯一阻塞面；不能把“本轮停下”写成“目标完成”。

#### Claude Code Ralph Loop 约束

Claude Code `/ralph-loop` 是 stop-hook 驱动的重复 prompt，不会自动理解 roadmap 状态；因此 roadmap 侧必须加硬约束：

- 启动 Ralph Loop 时必须写 `--max-iterations` 与 `--completion-promise`；prompt 必须要求每次 iteration 先读 `.canvas`、结束前输出 Loop Delta。
- 每个 Ralph iteration 都必须落一个内部子环，命名建议 `Ralph iteration N:<本轮闭合点>`；iteration 里的实现、验证、review、回退只在该子环内变色。
- Ralph Loop 达到 completion promise 前，必须满足：子环写回、父节点传播、`audit.py` 通过、快问快答自检无阻塞。否则只允许写 `partial / blocked / awaiting human`。
- Ralph Loop 连续 3 轮没有推进同一个 roadmap 节点的颜色、证据或结构，必须写红/黄阻塞节点并升级人工；禁止靠无限 iteration 消耗上下文。
- 如果 Ralph Loop 的本轮成果只完成了代码草稿、命令行验证或材料整理，roadmap 节点只能转到对应的子环绿；外层 E2E、owner gate 或上线 gate 未过时，父环保持黄/红。

### 规则 6：灰色节点不需要环

灰色（无色）节点表示"还没开始处理"，不需要也不应该有 runtime 链。它就是主干或横向链条中一个待处理的节点。只有当它从灰色变成黄色（开始处理）时，才需要派生 runtime 链。

### 规则 7：红色节点 = 阻塞/异常

红色表示执行过程中发现了问题。红色节点可以有 runtime group（在它变黄开始处理后才建的工作台），但 runtime group 内一定有未完成的阻塞。红色节点应有对应的 exception.md 条目，说明阻塞原因。

### 规则 8：绿色节点的环已闭合

绿色节点意味着它（及其 runtime group，如果有的话）已经全部完成。不需要再操作。

## 颜色传播详解

### 四色状态模型

| 状态 | Canvas `color` | 显示 | 含义 |
|---|---|---|---|
| 未开始 | 不设 color | 灰色（默认） | 还没开始处理 |
| 进行中 | `"3"` | 黄色 🟡 | 已开始处理，有推进 |
| 阻塞/异常 | `"1"` | 红色 🔴 | 执行中发现问题，阻塞了 |
| 已完成 | `"4"` | 绿色 🟢 | runtime group 内全绿，已闭环 |

### 传播方向

**runtime group → 父节点**：先确定 runtime group 内所有节点的颜色，再推导父节点颜色。如果 group 内节点本身有 runtime 子链，先递归确定子链状态。

### 传播矩阵

| runtime group 状态 | 父节点颜色 |
|---|---|
| 全绿 | 绿色 `"4"` |
| 有绿有黄 | 黄色 `"3"` |
| 有绿有红 | 黄色 `"3"` |
| 有绿有灰 | 黄色 `"3"` |
| 全黄 | 黄色 `"3"` |
| 有黄有红 | 黄色 `"3"` |
| 有黄有灰 | 黄色 `"3"` |
| 全红 | 红色 `"1"` |
| 全灰 | 黄色 `"3"`（新建 runtime group 初始态，父节点刚从灰转黄） |

简化：**全绿才绿，全红才红，其余都黄**。全灰不是完成态，而是父节点刚开始处理、runtime group 刚建好的初始黄态。

### 传播边界

以下节点**不参与**状态传播：

- 材料/说明节点（OpenSpec drift、UI 细节说明、决策点说明、颜色图例等）
- 紫色 `"6"` 节点（护栏/房间）
- 青色 `"5"` 节点（分支路径）
- 说明节点（图表规则框等）

### 变色条件与证据要求

| 变色方向 | 触发条件 | 证据要求 | 路书操作 |
|---|---|---|---|
| 灰→黄 | 开始处理该节点 | — | **必须立即创建或扩展横向 runtime 链** |
| 灰→红 | 还没开始就发现被外部阻塞 | 阻塞原因 | 写入 exception.md |
| 黄→绿 | runtime group 内所有节点全绿 | 代码路径/测试结果/文档引用 | 传播到父节点 |
| 黄→红 | 执行中发现阻塞/异常 | 阻塞原因 | 写入 exception.md |
| 红→黄 | 阻塞已解除 | 解除说明 | 更新 exception.md |
| 绿→黄/红 | 出现新问题或回退 | 回退原因 | 环中插入新节点 |

### 文档关联格式

变绿时关联知识文档的方式：

1. 在节点 text 中直接引用代码文件路径
2. 在配套 `.md` 摘要文档中记录闭环证据

## Edge 规则

### 颜色规则

Edge 颜色跟随**目标节点**（`toNode`）的颜色：
- 指向绿色节点的 edge → 绿色 `"4"`
- 指向黄色节点的 edge → 黄色 `"3"`
- 指向红色节点的 edge → 红色 `"1"`
- 指向灰色（无色）节点的 edge → 不设 color

### 方向规则

edge 的 `fromSide` / `toSide` 标准按图形语义区分（详见规则 1A/1B/1C）：

| 连接类型 | fromSide | toSide | 说明 |
|---|---|---|---|
| 根 → 开始（spine 起始） | `top` | `bottom` | 开始在根下方（开始 y > 根 y） |
| spine 链内 i → i+1 | `top` | `bottom` | i+1 在 i 上方，自下而上推进 |
| 结束 → 根（spine 闭环） | `left` | `left` | 左侧外圈回根，不穿过主干节点 |
| 父节点 → runtime 开始 | `right` | `left` | runtime group 在父节点右侧 |
| runtime 链条内 | `right` | `left` | 横向从左到右推进 |
| runtime 结束 → 父节点 | `bottom` | `bottom` | 从下方通道闭合回父节点，禁止穿过 runtime 节点 |
| runtime 节点 → 同 group 内子链开始 | `bottom` | `top` | 子链另起下方泳道，和横向主链端口分离 |
| 子链结束 → runtime 节点 | `top` | `top` | 子链 top 出，回父节点 top |

## 布局规则

### 0. 防重叠是硬约束

**节点不允许重叠。** 写入 canvas 前必须检查所有节点的矩形区域 `(x, y, x+width, y+height)` 无交集。

### 1. 首环竖向主干模型

首环在 canvas 上必须是竖向主干，**开始最下、结束最上、根在结束上方**：

```
                     根 (y 最小)
                      │
                     结束 (紧贴根)
                      │ top→bottom（链内；视觉是自下而上推进）
                      │
                     工作块 N-1
                      │
                     ... ↑↑↑ 自下而上
                      │
                     工作块 1
                      │
                     开始 (y 最大)

边方向槽位：
- 根 → 开始：top→bottom（从根外圈起跳到最下方开始）
- 开始 → 工作块 1 → ... → 结束：top→bottom
- 结束 → 根：left→left（沿左侧外圈闭合）
```

- 主干节点 `x` 中心点对齐根节点，偏差 ≤ `ALIGN_TOLERANCE`（推荐 80px）
- spine 节点 i=1（开始）y 最大，i=N（结束）y 最小，**y 单调递减**：从开始往上每隔 `GAP_VERTICAL_SPINE`（推荐 220px）
- 开始 y > 根 y（开始位于根下方），间距 ≥ `MIN_SPINE_Y_GAP`（默认 40px）
- 首环主干不放运行时事实卡、证据、Exception、Worker Pack 明细——这些都进 `工作块:` group 内的 runtime 节点

### 2. runtime group 横向工作台模型

任意首环主干节点或 gate 开始处理后，在该节点右侧生成一个 JSON Canvas `type:"group"`。group 内的 runtime 节点继续开始处理时，默认在同一个 group 内另起横向子链；只有当它变成跨工作块依赖、独立 gate 或需要单独派工隔离时，才创建相邻的独立 group：

```
父节点  →  ┌─ 工作块:<P>:[处理中] ─────────────────────┐
           │  事实卡/开始 → 调查/实现/验证 → 证据/未决 → 结束 │
           │                    ↓                              │
           │             子问题开始 → 子问题处理 → 子问题结束    │
           └───────────────────────────────────────────────────┘
```

- group 必须完整包住该外部 owner 的运行时节点，不包住其他首环主干节点
- group label 建议：`工作块:<P>:[处理中]`；gate group 建议：`Gate:<gate_id>:<gate名>`
- group 内每条处理链横向排列，中心点 `x` 单调递增
- 递归产生的新子链仍在同一 group 内横向展开；空间不足时向下另起泳道，但不能穿插到别的 group
- 非父子关系的 edge 禁止跨 runtime group 连接；允许的跨 group edge 只有“父节点→自己的 runtime 开始”和“自己的 runtime 结束→父节点”

### 3. 间距常量

权威定义见 `geometry.py`，文档值与 `geometry.py` 必须一致；以下是 v2 推荐值的速查表：

| 常量名（geometry.py） | 推荐值 | 说明 |
|---|---|---|
| `GAP_VERTICAL_SPINE` | 220px | 首环竖向主干节点间距 |
| `OFFSET_SPINE_TO_RUNTIME` | 280px | spine 节点 → 它的第一个 runtime 节点中心 |
| `GAP_HORIZONTAL_RUNTIME` | 200px | runtime 链内相邻节点水平间距 |
| `GAP_VERTICAL_LANE` | 200px | 同一 group 内多条横向泳道间距 |
| `GROUP_PADDING` | 50px | group 边框到内部节点的留白 |
| `OFFSET_GATE_GROUP_X` | -700px | gate group 相对主干的 x 偏移（左侧独立列） |
| `MIN_SPINE_Y_GAP` | 40px | 相邻 spine 节点最小 y 距离 |
| `MIN_RUNTIME_X_GAP` | 20px | runtime 节点最小 x 距离 |
| `ALIGN_TOLERANCE` | 80px | spine x 对齐容差 |
| `LANE_Y_TOLERANCE` | 120px | runtime 同泳道 y 容差 |
| `CONTAINMENT_MARGIN` | 8px | group 包含子节点时允许的边距宽容 |

### 4. 推荐尺寸

| 节点类型 | 宽度 | 高度 |
|---|---|---|
| 首环主干节点 | 240-320 | 90-140 |
| 调查/实现/验证节点 | 250-300 | 120-200 |
| runtime 开始/结束节点 | 240 | 90 |
| runtime group | 按内部节点包围盒 + padding | 按内部节点包围盒 + padding |
| 说明节点 | 380 | 按内容自适应 |

高度自适应估算：`height = max(80, 行数 × 24 + 40)`

### 5. group 矩形几何约束

按规则 0K：

- group 必须几何包含 `Workblock(P) = {P} ∪ runtime(P) ∪ runtime 子链(...)` 全部成员
- group **不能包含其他工作块的 owner 节点**（即不同 spine 节点的 P）；但**子工作块的 group 完全包含在父工作块的 group 里**是合法嵌套（规则 0K 嵌套规则）
- 任意两 group 矩形：必须满足 (a) 完全包含 (b) 完全分离；**部分相交是 P0 违规**
- group 内部节点不得越界；group 与其内部节点矩形重叠是合法的（group 是容器）
- gate group 与 workblock group 必须完全分离（规则 0L）

### 6. 插入节点定位

在 runtime group 横向链条中插入新节点时：

1. 确定前驱节点 A 和后继节点 B
2. 新节点 x = A.x + A.width + GAP_X_SIBLING
3. 新节点 y = A.y（保持同行）
4. 将 B 及其后所有节点向右偏移 `新节点.width + GAP_X_SIBLING`
5. 检查偏移后是否与其他环区域重叠，如有则继续向右偏移
6. 更新所有受影响的 edge

### 7. 说明节点位置

说明节点放在业务节点区域的**左上角外侧**，不影响业务节点的布局计算。

## 主/子 Agent 编排规则

Agent 编排只是路书闭环的执行投影，不是路书本体。路书先表达目标闭环：开始、核心工作块、gate、runtime 证据链、结束；SubAgent、Worker Pack、agent-* OpenSpec 只是把某个 runtime group 分配出去推进的方式。没有 SubAgent 时，roadmap 仍必须能独立表达“这件事怎样完成”。

### runtime group 是 SubAgent 的最小工作面

一个 runtime group 被分配给 SubAgent 后，group 内横向链条顺序就是 SubAgent 的执行顺序。SubAgent 按事实卡/开始→中间→结束依次推进，每推进一个节点就上报主 Agent。

这不意味着 runtime group 等同于 SubAgent 的 Plan。Plan 可以引用 runtime group，也可以拆得更细；但 `.canvas` 只保留会影响闭环状态、证据、阻塞、裁决或子环结构的节点。

### SubAgent 回报触发的路书操作

| SubAgent 回报内容 | 主 Agent 路书操作 |
|---|---|
| 节点完成 + 证据 | 节点变绿，传播到父节点 |
| 节点开始处理 | 节点灰→黄，**必须为该节点创建或扩展横向 runtime 链** |
| 发现新问题 | 在所属 runtime group 横向链条中插入新灰色节点 |
| 遇到阻塞/知识冲突 | 节点标红，写入 exception.md |
| 阻塞已解除 | 节点红→黄，更新 exception.md |
| 发现进度与预期不符 | 评估是否调整环结构或修正上下文 |

### Exception 处理规则

SubAgent 遇到以下情况时必须上报主 Agent：

- **知识冲突**：设计文档 vs 代码 vs PRD 说法不一致
- **外部阻塞**：缺少 kubectl / token / 部署入口等外部依赖
- **需要人工决策**：正式命名、技术选型等无法自动判定的事项

主 Agent 收到后：
1. 将对应的 runtime group 内节点标红色 `"1"`
2. 写入 `exception.md`，格式见 SKILL.md
3. 传播颜色到父节点
4. Exception 不阻塞其他 runtime group 的推进
5. 等待人工决策后，节点从红→黄→继续推进

### runtime group 与 OpenSpec 的对应关系

OpenSpec 是设计与任务材料，不是路书的结构真源。核心 OpenSpec 可以描述组件、状态、文案、约束、验收点和候选任务；roadmap 只吸收其中影响目标闭环推进的部分。

被分配给 SubAgent 的 runtime group 可以有对应的 `agent-*/` OpenSpec：

- `proposal.md`：runtime group 的目标和范围
- `tasks.md`：可追溯覆盖 group 内节点的任务清单

这里的“可追溯覆盖”只适用于**已经被路书吸收的 runtime 工作面**：tasks.md 要能说明每个 runtime 节点如何执行和验收，但不能反向要求 OpenSpec 的每个章节、组件或 checkbox 都成为路书节点。

当主 Agent 在 runtime group 中插入会影响闭环推进的新节点时，同步更新对应 `agent-*/tasks.md`。
当 runtime group 全绿时，对应的 `agent-*/` OpenSpec 可以归档或清理。

### 并行与串行规则

- 互不依赖的父节点 runtime group：可以分配给不同 SubAgent 并行推进
- 同一 runtime group 内的节点：必须按横向链条顺序串行推进
- 同一父 group 内的多个 runtime 子链：如果互不依赖，可以并行推进
- 有依赖的 group：上游 group 的阻塞节点全绿后，下游 group 才能启动

### 路书写入权限

**只有主 Agent 能写 `.canvas`。** 这是硬约束。SubAgent 只能通过上报间接影响路书内容。主 Agent 收到回报后统一回写，保证路书的一致性。

### 实时同步规则

路书状态必须和 Agent 实际工作进度尽可能一致：

- SubAgent 每次状态变更（灰→黄/黄→绿/→红/新问题），必须**一个节点一次上报**，不能攒着
- 主 Agent 每次收到回报，必须**立即回写 `.canvas`**，不能等多个回报一起写
- 主 Agent 在回写路书之前不能分配新工作——先同步路书，再推进下一步
- 任何时刻打开路书，状态都应该反映 Agent 当前真实进展

## 审计检查清单

每项标注：`[脚本]` = audit.py 自动校验；`[半自动]` = 脚本能检测一部分，结论需人工核；`[人工]` = 脚本无法判断，必须人工 review。**只跑 `audit.py` 不够**——`[人工]` 项必须主 Agent 自己核对。

### P0：必须修复

- [ ] `[脚本]` **路书不是单连通图**（违反规则 0：从根节点 DFS 无法到达所有业务节点）
- [ ] `[人工]` **路书层次过浅**（违反规则 0A：runtime group 无法覆盖任务动作、证据或裁决点 — 脚本不读 tasks.md/OpenSpec）
- [ ] `[人工]` **首环主干被 OpenSpec / tasks / Agent 分工反向决定**（违反路书第一语义：主干只能按完成闭环组织）
- [ ] `[人工]` **材料/说明节点接入了业务 edge 或参与状态判断**（违反材料/说明节点规则：只能解释来源，不能表示进度）
- [ ] `[人工]` **路书状态与 Agent 实际进度不一致**（Agent 已推进但路书没更新 — 流程审计）
- [ ] `[人工]` **Loop Delta 没有作为同一批状态事务落入 `.canvas`**（只改 Todo/聊天/节点文字/颜色，未同步结构、edge、group、传播 — 违反规则 5A）
- [ ] `[人工]` **Codex Goal / Claude Ralph Loop / review round 已完成但没有对应内部子环**（外部 checklist 或 iteration 被当成路书状态源 — 违反规则 5B）
- [ ] `[人工]` **子环节点被逐项散落到父 runtime 链并逐个转绿**（一轮外部循环没有作为一个子环整体变色 — 违反规则 5B）
- [ ] `[脚本]` 黄色节点没有闭合的 runtime 链（违反规则 3：灰→黄必须补横向工作台）
- [ ] `[脚本]` runtime 链不闭合（找不到 end→parent 的 bottom→bottom edge）
- [ ] `[脚本]` 黄/红 runtime 子节点缺少闭合 inner runtime 子环（违反规则 3 递归触发）
- [ ] `[脚本]` 同一节点入边和出边使用同一侧（违反规则 1D）
- [ ] `[脚本]` Edge 穿过非端点节点矩形（违反规则 1D）
- [ ] `[脚本]` 父节点颜色与 runtime group 节点状态不符合传播矩阵
- [ ] `[脚本]` 灰色节点有 runtime 链（违反规则 6：灰节点不应有环）
- [ ] `[脚本]` spine edge 不在 1A 三槽位（根→开始 / 链内 / 结束→根）（违反规则 1A）
- [ ] `[脚本]` runtime edge 不在 1B 三槽位（违反规则 1B）
- [ ] `[脚本]` 黄/红/绿 spine 节点没有对应 `工作块:<P>` group（违反规则 0K）
- [ ] `[脚本]` `工作块:` group 不几何包含 P 节点本身（违反规则 0K，止血版常见 bug）
- [ ] `[脚本]` group label 状态后缀与 P.color 不一致（违反规则 0K）
- [ ] `[脚本]` group color 不镜像 P.color（处理中=5/已完成=4/阻塞=1）（违反规则 0K）
- [ ] `[脚本]` 任意两个 group 矩形部分相交（违反规则 0K，必须完全包含或完全分离）
- [ ] `[脚本]` gate 节点不在 `Gate:` group 内（违反规则 0L）
- [ ] `[脚本]` gate 节点不在 spine 主干上，或没有前驱/后继（违反规则 0L）
- [ ] `[脚本]` gate group 与 workblock group 重叠（违反规则 0L）
- [ ] `[脚本]` Edge 引用了不存在的节点 ID
- [ ] `[脚本]` 节点之间存在矩形重叠
- [ ] `[脚本]` 节点 / Edge 有重复 id
- [ ] `[脚本]` 节点使用非法 color 值
- [ ] `[人工]` SubAgent 直接修改了 `.canvas`（绕过主 Agent — 流程审计）
- [ ] `[人工]` 进度只写在 `.md` 文件里，没有更新到 `.canvas`（流程审计）
- [ ] `[半自动]` **首环数量超过 7 或少于 3**（违反规则 0D — 脚本可数根节点子节点，但"首环"需人工判定）
- [ ] `[半自动]` **首环节点锚点超过 5 条或少于 2 条**（违反规则 0E — 需 grep 节点 text 判定锚点条数）
- [ ] `[半自动]` **未决点类锚点缺 owner 或缺阻塞面**（违反规则 0I — 需 grep 锚点 text）
- [ ] `[人工]` **首环节点把零散文案、像素细节、参数表直接当锚点**（违反规则 0H — 内容判定）
- [ ] `[人工]` **runtime group 复刻 OpenSpec 章节但没有闭环推进语义**（违反规则 0F — 内容判定）
- [ ] `[人工]` **新 Knowledge Pack 出炉后，主 Agent 没做锚点 grep 审计就回写 `.canvas`**（违反规则 0J — 流程审计）

### P1：应当修复

- [ ] `[脚本]` 红色节点提示需要 exception.md 条目（脚本会 flag 红节点；条目内容需人工核）
- [ ] `[半自动]` **exception.md 条目没有对应的红节点**（死信，违反规则 0I 反向校验 — 需 cross-check）
- [ ] `[人工]` 绿色节点没有任何文档/代码证据关联（需读节点 text）
- [ ] `[脚本]` Edge 颜色与目标节点颜色不一致
- [ ] `[脚本]` 存在多个根候选节点（multiple roots）
- [ ] `[脚本]` 一个父节点有多个闭合 runtime group（违反"一父一运行时工作台"）
- [ ] `[半自动]` 存在孤立业务节点（无 edge 连接 — 脚本可检测无 incoming/outgoing edge 的节点）
- [ ] `[脚本]` runtime 链条不是横向从左到右推进，或 group label 未标出 `工作块:<P>`
- [ ] `[人工]` runtime group 有对应的 SubAgent 但缺少 `agent-*/tasks.md`
- [ ] `[人工]` `agent-*/tasks.md` 与 runtime group 内节点不对应
- [ ] `[人工]` **调查节点持续黄超过 1 sprint 仍未升级 Exception**（违反规则 0I 阈值 — 需 sprint 时间元数据）
- [ ] `[人工]` **错知识 Repair Loop 完成但路书锚点未改写**（违反规则 0J T4-T5）
- [ ] `[人工]` **首环节点中出现产品宣言/口号/无可执行约束面的句子**（违反规则 0H 反例）

### P2：建议优化

- [ ] `[脚本]` Edge 方向不在 `geometry.py` 定义的六类槽位（spine / runtime / inner-runtime）
- [ ] `[人工]` 开始/结束节点 text 过于笼统
- [ ] `[半自动]` 节点尺寸与内容行数不匹配（`height ≈ max(80, lines×24+40)`）
- [ ] `[半自动]` runtime group 与父节点水平间距过小，导致线条穿插
- [ ] `[半自动]` 锚点没有按 5 类类型词（`非目标 / 入口/出口 / 时序 / 未决点 / 来源`）开头标注（规则 0H 建议格式）

## 自动校验脚本

写回 `.canvas` 之前，主 Agent 必须跑一次 `audit.py`。v2 起 audit.py 合一校验拓扑、颜色、几何、group——单脚本一次跑完。

**Exit code 语义**：
- `exit 0`：通过（无 P0 违规；P1 仅警告时也算通过）
- `exit 1`：有 P0 违规，**必须修复才能提交**
- `exit 2`：有 P1 违规且开了 `--strict`（默认 P1 不阻断）
- `exit 3`：脚本读文件或解析失败

```bash
# 在 host 仓库根目录跑（本仓库 skill 实际挂载在 submodules/skills/）：
python3 submodules/skills/project-roadmap-board/audit.py /path/to/roadmap.canvas

# 可选：显式指定根节点
python3 submodules/skills/project-roadmap-board/audit.py /path/to/roadmap.canvas --root v14-root

# 严格模式：P0 + P1 都必须 0 才 exit 0
python3 submodules/skills/project-roadmap-board/audit.py /path/to/roadmap.canvas --strict
```

如果 host 仓库挂载位置不同，改前缀即可。`audit.py` 从 `geometry.py` import 所有常量与工具函数，禁止本地复制。

**脚本校验项**（完整清单见 `audit.py`）：

- JSON 合法
- 重复 node/edge id
- edge 引用不存在的节点
- 非法 color 值
- 业务节点矩形重叠（group 节点不参与重叠校验）
- **单连通 DFS**（从根节点可达所有业务节点；root 即使是紫色护栏也参与拓扑）
- spine 识别 + 1A 三槽位精确方向校验
- spine 节点 y 单调（开始最大、结束最小；开始 y > 根 y）
- runtime ring 闭合（right→left 起，沿 right→left 链，bottom→bottom 回 P）
- 黄/红/绿 spine 节点必须有对应 `工作块:` group + group 包含 P + 状态后缀 + color 镜像
- 任意两 group 不能部分相交（允许完全包含或完全分离）
- gate 节点必须在 Gate group 内
- runtime 颜色推父节点颜色（传播矩阵）
- edge 颜色 = toNode 颜色
- spine edges 自然跨 group 不报警
- 跨 group 非 spine edge：仅"P → P 的 runtime"和"P 的 runtime → P"两种合法

**正向生成器（`layout.py`）**：

```bash
# 输入 JSON spec，输出完整 .canvas（坐标、edges、groups 自动生成；方向严格按 1A/1B/1C）
python3 submodules/skills/project-roadmap-board/layout.py spec.json -o roadmap.canvas --validate
```

`--validate` 自动调 audit.py 复核生成结果。layout.py 也从 geometry.py import 所有常量，与 audit.py 同步。

业务节点 vs 容器/说明节点的判定：`type:"group"`、`color="5"` 青色、`color="6"` 紫色、或 text 中含 `说明/图例/护栏/KP gate` 关键字的节点视为容器/说明节点，不参与颜色传播和矩形重叠校验（紫色 root 仍参与连通性 BFS 作为源点）。
