# 路书标准范例（v2）

v2 关键形态约束（必读）：

- **路书第一语义是完成闭环**：先表达“这件事从开始到完成要闭合什么”，再下沉 OpenSpec / PRD / 原型 / tasks.md 的细节。
- **首环主干竖向闭合，开始最下、结束最上、自下而上推进**（见图 3）。
- **每个被处理（黄/红/绿）spine 节点必须被一个 `工作块:` group 包住**，group 范围 = P 节点本身 + P 的所有 runtime 节点 + runtime 子链递归到底。
- **runtime 横向展开**：从 spine 节点右侧进入 `开始 → 中间 → 结束` 横向链，结束边用 `bottom→bottom` 从下方通道闭合到 P；子链 y 偏移另起泳道，方向不变。
- **嵌套 group 允许完全包含、禁止部分相交**。
- **gate 节点封到独立 `Gate:` group**，与 workblock group 完全分离。
- 所有范例 .canvas 推荐用 `layout.py` 从 JSON spec 自动生成，避免手画方向出错。

阅读顺序建议：

1. 先看范例 8 / 9，理解“OpenSpec 材料池 → 完成闭环 roadmap”的语义。
2. 再看范例 1-7，理解几何、group、gate 和 runtime 子环的画法。
3. 最后看反模式，避免把路书画成 PRD 复刻、任务树或 Agent 协作图。

## 范例 1：竖向首环 + 右侧 runtime group + group 包住 P

最小 v2 路书：1 个 root 连通锚点 + 3 个 spine 节点（开始/买菜闭环/结束）+ 1 个被处理节点的 runtime（开始处理买菜/结束处理买菜）。

### 视觉形态

```
                │   结束 [灰]                         ← y=155，业务主干最顶
                │     ↑
                │     │ top→bottom（视觉是向上）
                │     ↓
                │   买菜闭环 [黄] ───→ ┌─ 工作块:买菜闭环:[处理中] [青] ─┐
                │     ↑                │  ┃                              │
                │     │ top→bottom    │  ┃ 买菜闭环（在 group 内）      │
                │     │               │  ┃   right→left                  │
                │     ↓               │  ┃   ↓                           │
                │   开始 [绿] ──────→  │  开始处理买菜 → 结束处理买菜    │
                │     ↑                │  [灰]            [灰]           │
                │     │ top→bottom     │              bottom→bottom      │
                │     │ (root→开始)    │                  ↓              │
                │   v14-root           │ ←────────────────┘              │
                │     ↑                │                                  │
                └─────┘ left→left      │                                  │
                                       └─────────────────────────────────┘
```

注意：

- **`工作块:买菜闭环:[处理中]` group 圈住的是 P（"买菜闭环"节点本身）+ 它的 runtime 节点**——这是 v2 与 v1 的关键差别。
- 开始节点已绿（state=green），所以也有自己的 `工作块:开始:[已完成]` group（color=4 绿），保留作为历史证据。
- 结束节点灰色，禁止有 group。

### Edge 方向语义（规则 1A / 1B）

| Edge | from | to | 槽位 |
|---|---|---|---|
| `v14-root → 开始` | top | bottom | 1A 根→开始 |
| `开始 → 买菜闭环` | top | bottom | 1A spine 链内（视觉向上） |
| `买菜闭环 → 结束` | top | bottom | 1A spine 链内 |
| `结束 → v14-root` | left | left | 1A spine 闭环（左侧外圈） |
| `买菜闭环 → 开始处理买菜` | right | left | 1B 父→runtime 开始 |
| `开始处理买菜 → 结束处理买菜` | right | left | 1B runtime 链内 |
| `结束处理买菜 → 买菜闭环` | bottom | bottom | 1B runtime 结束→父（下方通道） |

### 完整 Canvas JSON（由 layout.py 生成）

```json
{
  "nodes": [
    {"id": "v14-root", "type": "text", "text": "v14-root", "x": -140, "y": 945, "width": 280, "height": 110},
    {"id": "开始", "type": "text", "text": "开始", "x": -140, "y": 725, "width": 280, "height": 110, "color": "4"},
    {"id": "买菜闭环", "type": "text", "text": "买菜闭环", "x": -140, "y": 415, "width": 280, "height": 110, "color": "3"},
    {"id": "结束", "type": "text", "text": "结束", "x": -140, "y": 155, "width": 280, "height": 110},
    {"id": "开始处理买菜", "type": "text", "text": "开始处理买菜", "x": 420, "y": 420, "width": 240, "height": 100},
    {"id": "结束处理买菜", "type": "text", "text": "结束处理买菜", "x": 860, "y": 420, "width": 240, "height": 100},
    {"id": "g-开始", "type": "group", "label": "工作块:开始:[已完成]", "x": -190, "y": 675, "width": 380, "height": 210, "color": "4"},
    {"id": "g-买菜闭环", "type": "group", "label": "工作块:买菜闭环:[处理中]", "x": -190, "y": 365, "width": 1340, "height": 210, "color": "5"}
  ],
  "edges": [
    {"id": "e1", "fromNode": "买菜闭环", "fromSide": "right", "toNode": "开始处理买菜", "toSide": "left"},
    {"id": "e2", "fromNode": "开始处理买菜", "fromSide": "right", "toNode": "结束处理买菜", "toSide": "left"},
    {"id": "e3", "fromNode": "结束处理买菜", "fromSide": "bottom", "toNode": "买菜闭环", "toSide": "bottom", "color": "3"},
    {"id": "e4", "fromNode": "v14-root", "fromSide": "top", "toNode": "开始", "toSide": "bottom", "color": "4"},
    {"id": "e5", "fromNode": "开始", "fromSide": "top", "toNode": "买菜闭环", "toSide": "bottom", "color": "3"},
    {"id": "e6", "fromNode": "买菜闭环", "fromSide": "top", "toNode": "结束", "toSide": "bottom"},
    {"id": "e7", "fromNode": "结束", "fromSide": "left", "toNode": "v14-root", "toSide": "left"}
  ]
}
```

### 等价 layout.py spec.json（推荐写法）

```json
{
  "root": "v14-root",
  "spine": [
    {"id": "开始", "state": "green"},
    {"id": "买菜闭环", "state": "yellow",
     "runtime": [
       {"id": "开始处理买菜"},
       {"id": "结束处理买菜"}
     ]},
    {"id": "结束"}
  ]
}
```

跑 `python3 layout.py spec.json -o roadmap.canvas --validate` 直接生成且 audit exit 0。

## 范例 2：灰→黄触发 group + runtime 链

灰色节点表示未开始，禁止有 group。主 Agent 决定推进时**同时**做三件事：

1. 把节点 color 改黄
2. 在节点右侧建 runtime 链（开始 → 结束）
3. 创建 `工作块:<P>:[处理中]` group 包住 P + runtime 链

```
之前：
买菜闭环 [灰]   （没有任何 group）

之后：
                 [工作块:买菜闭环:[处理中] [青]]
                 ┌──────────────────────────────┐
买菜闭环 [黄]  ──┤  买菜闭环 + 开始处理 → 结束处理 │
                 └──────────────────────────────┘
```

**P 必须在 group 内**——这是 v1 → v2 的关键修正。group 的左上角附近就是 P 节点。

## 范例 3：runtime 内插入新问题

SubAgent 在 `工作块:买菜闭环` 的 runtime 链里发现两个新问题：车坏了、酱油需要补。新问题插入横向链条，**仍在同一 group 内**。

```
[工作块:买菜闭环:[处理中]]
买菜闭环 → 开始处理买菜 [绿] → 车坏了需要修车 [黄] → 酱油需要补充 [灰] → 结束处理买菜 [灰]
                                                                            └──────────→ 买菜闭环
```

操作（注意 group 矩形要扩展以包住新节点）：

1. 断开 `开始处理买菜 → 结束处理买菜`
2. 新增 `开始处理买菜 → 车坏了需要修车`
3. 新增 `车坏了需要修车 → 酱油需要补充`
4. 新增 `酱油需要补充 → 结束处理买菜`
5. 保留 `结束处理买菜 → 买菜闭环`
6. **同步把 group 矩形 width 扩大** 以包住新节点（layout.py 重新生成时自动算包围盒）

## 范例 4：runtime 节点派生子链（同 group 内泳道）

`车坏了需要修车` 已经开始处理，它自己也要有 `开始 → 结束` 子链。**仍在同一个 `工作块:买菜闭环` group 内**，y 偏移另起一行泳道：

```
[工作块:买菜闭环:[处理中]]
主链：开始处理买菜 [绿] → 车坏了需要修车 [黄] → 酱油需要补充 [灰] → 结束处理买菜 [灰]
                                ↘ (right→left)
子链：                            开始修车 [灰] → 结束修车 [灰] ──→ (top→top 回到 车坏了需要修车 [黄])
```

子链方向规则（规则 1C）：

- `车坏了需要修车 → 开始修车`：bottom→top（从下方进入子泳道）
- `开始修车 → 结束修车`：right→left
- `结束修车 → 车坏了需要修车`：top→top（子链 top 出，回父节点 top）
- 子链节点 y = 车坏了需要修车.y + GAP_VERTICAL_LANE（向下偏移一行）

如果子链发展成跨工作块的独立交付，才升级为新的 spine 节点。

## 范例 5：嵌套 group——完全包含 vs 部分相交

v2 允许嵌套 group（子工作块的 group 套在父工作块的 group 里），但**只能完全包含或完全分离**。

### 合法：完全包含

```
┌─ 工作块:外层:[处理中] [青] ─────────────────────────────────┐
│                                                              │
│  外层节点                                                     │
│                                                              │
│  ┌─ 工作块:内层:[处理中] [青] ─────────────────────────┐    │
│  │  内层节点 + 它的 runtime + 子链                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

audit.py 用 `rect_contains` 判定，外层完全含内层即合法。

### 违法：部分相交（P0 违规）

```
┌─ 工作块:A:[处理中] ────────────────┐
│                                     │
│        ┌─ 工作块:B:[处理中] ────────┼──────┐
│        │                            │      │
└────────┼────────────────────────────┘      │
         │                                    │
         └────────────────────────────────────┘
```

audit.py 报：`group partial intersect g-A <-> g-B`。两个 group 必须重新规划——要么 A 完全包含 B（B 整个移进 A），要么完全分离（B 移到 A 外）。

## 范例 6：Gate group 独立成列

gate 节点（KP-00 ~ KP-06）必须封到独立 `Gate:` group，放在主干左侧独立列。

```
[Gate:KP-00:Domain Locked [紫]]            spine 主干（中间）         工作块 group（右侧）
┌──────────────────────────┐
│  KP-00 Domain Locked     │              v14-root [紫]
└──────────────────────────┘                 ↑     ↓
                                              │   结束
[Gate:KP-01:Sources Locked [紫]]              │     ↑
┌──────────────────────────┐                 │   买菜闭环 [黄] ──→ [工作块:买菜闭环 group]
│  KP-01 Sources Locked    │                 │     ↑
└──────────────────────────┘                 │   开始 [绿]
                                              └─────┘
```

- gate group color = `6`（紫，护栏，不参与传播）
- gate group 与所有 `工作块:` group 完全分离（不允许任何重叠）
- gate 节点不在 Gate group 内是 P0 违规

## 范例 7：主 Agent + SubAgent 协作

以 `后端跑通` 为例：

1. 主 Agent 读 spine，选灰色节点 `后端跑通`
2. 主 Agent 把 `后端跑通` 变黄；同时建：
   - 右侧 runtime 链 `开始后端联调 → 结束后端联调`
   - `工作块:后端跑通:[处理中]` group 包住"后端跑通"+ 整条 runtime 链
3. 主 Agent 生成 Worker Pack，包含 `当前 runtime group ID = g-后端跑通`、节点链条、Knowledge Pack 摘要
4. SubAgent 只在 group 内推进，不能改 `.canvas`
5. SubAgent 上报"配置未同步到 DB"，主 Agent 在 group 内插入灰色节点 `配置同步到 DB`，并扩 group 矩形
6. SubAgent 开始处理 `配置同步到 DB`：在同 group 另起泳道 `开始:gsc → resource → llm → 结束:dry-run match`
7. group 内全绿后，`后端跑通` 才能黄→绿；group label `[处理中]→[已完成]` + group color `5→4`；group 保留作为历史证据

## 范例 8：从 PRD 生成首环（morph72-v14）

PRD 没有显式功能编号时，先抓动词事实卡，再按用户旅程收敛为 3-7 个首环工作块。

事实卡样例：

```
对象=亮相阶段一 / 动作=贴贴纸 / 边界=仅自己可见 / 入口=10s 总体亮相 / 出口=个人 C 位
对象=个人展示 / 动作=放大头像 / 顺序=座位 1→4 / 节奏=每人 10s
对象=结算页 / 动作=展示分数+Ready / 入口=锐评结束 / 出口=全员 Ready 或倒计时结束
对象=离线玩家 / 动作=自动 Ready / 边界=不阻塞下一轮
对象=故事反馈 / 未决点=策划 prompt 未定 / 阻塞=实现派工
```

收敛后的 spec.json：

```json
{
  "root": "morph72-root",
  "spine": [
    {"id": "开始"},
    {"id": "集体亮相社交体验闭环"},
    {"id": "锐评颁奖表达优化闭环"},
    {"id": "小局结算与 Ready 推进闭环", "state": "yellow",
     "runtime": [
       {"id": "事实卡:结算入口出口"},
       {"id": "调查:现有锐评结束推进链路"},
       {"id": "实现:分数结算板"},
       {"id": "实现:Ready 状态同步"},
       {"id": "实现:离线自动 Ready"},
       {"id": "验证:Ready/超时进入下一轮"}
     ]},
    {"id": "题目衔接剧情 OS 闭环"},
    {"id": "故事反馈探索裁决", "state": "yellow",
     "runtime": [
       {"id": "调查:策划 prompt 进度"},
       {"id": "调查:生成链路打通"},
       {"id": "调查:生成耗时基线"}
     ]},
    {"id": "结束"}
  ]
}
```

`小局结算与 Ready 推进闭环` 节点 text 中嵌入锚点（2-5 条，每条 1-2 行）：

```
来源：v1.4.4 PRD §结算页面和 Ready 环节
入口/出口：锐评结束 → 结算页 → 全员 Ready 或倒计时结束 → 下一轮
非目标：保持公聊语音；离线玩家不阻塞下一轮
时序：分数按 round_rank 排序展示
未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现
```

`故事反馈探索裁决` 锚点只有调查准入：

```
来源：v1.4.x PRD §故事反馈
未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工
```

它的 runtime 只允许调查节点，不允许实现节点。

## 范例 9：OpenSpec 材料池 → 本地 UI 闭环 roadmap

OpenSpec 可以同时描述组件、状态、文案、边界、技术方案和任务列表，但 roadmap 只回答一个问题：

> 怎样把用户或系统从入口推进到可验证完成？

下面用通用化的“本地素材盒”示例说明。示例借用了贴纸盒 / OrganizeSheet / ConfirmToast 这类 UI 结构，但规则适用于任何本地 UI 闭环。

### OpenSpec 材料池

OpenSpec / 原型里可能有这些材料：

- `本地素材盒`：展示本地生成或收藏的素材
- `OrganizeSheet`：用户整理、选择、删除、分组
- `ConfirmToast`：完成后给出可见确认
- UI 细节：3 列 grid、按钮文案、toast 颜色、状态 pill、同步占位
- 未决点：是否同步远端、失败是否重试、删除是否二次确认
- 删除项：v1 不做自动归类、不做远端合并、不做某个高级编辑入口

这些不是天然 spine 节点。它们先进入事实卡 / runtime 候选，再按闭环语义收敛。

### 材料池节点 / 说明节点怎么画

材料池节点和说明节点是**视觉上下文**，不是业务节点：不接 edge、不参与颜色传播、不改变父节点黄红绿。它们应该放在所属 `工作块:` group 内、runtime 链下方或旁侧，用 `role/roadmapRole/kind = material | note | annotation` 标记；text 以 `说明:`、`材料:`、`删除项:`、`证据索引:` 这类前缀开头，便于 audit.py 识别。

颜色表达建议：

| 材料类型 | 颜色 | 含义 | 是否进 runtime |
|---|---|---|---|
| 原型截图、UI drift 索引、OpenSpec 段落引用 | `"5"` 青 | 旁路材料 / advisory，不参与传播 | 默认不进，只作为说明节点 |
| 已裁决的设计或证据索引 | `"4"` 绿 | 已确认材料，可支撑验证 | 只有要交付或验收时才转成 `验证:` / `证据:` runtime 节点 |
| 决策点待裁 | `"3"` 黄 | 需要 owner 裁决，但可能不阻塞 | 阻塞实现或影响出口时转成 `未决点:` / `调查:` runtime 节点 |
| 删除项、弃用方案、blocked source | `"1"` 红 | 不进默认执行链；提醒不要误用 | 只有需要实际删代码、写 exception 或验证未引用时才转成 runtime 节点 |

判定口诀：**会改变入口/出口、状态、数据、证据或阻塞面的 material，才变 runtime 节点；只解释来源、原型差异、被删除边界的 material，保留为说明节点。**

### 动作事实卡

```
对象=本地素材盒 / 动作=打开 / 目标行为=看到本地素材列表 / 证据=空态、加载态、错误态、列表渲染
对象=整理面板 / 动作=调整选择或分组 / 目标行为=本地状态变更可回显 / 证据=选择、归类、取消后状态一致
对象=确认反馈 / 动作=完成整理后提示 / 目标行为=关闭面板并出现确认提示 / 证据=ConfirmToast 出现且数据保持一致
对象=失败或取消 / 动作=回退 / 目标行为=回到进入前状态或给出错误提示 / 证据=本地状态不污染
```

### 首环 spine

合适的首环按完成闭环命名：

```json
{
  "root": "local-ui-root",
  "spine": [
    {"id": "开始", "state": "green"},
    {"id": "本地素材可见闭环"},
    {"id": "整理操作落地闭环", "state": "yellow",
     "runtime": [
       {"id": "事实卡:整理入口出口", "state": "green"},
       {"id": "实现:OrganizeSheet 选择与分组"},
       {"id": "验证:选择/取消/归类回显"}
     ],
     "materials": [
       {"id": "mat-ui-drift", "text": "材料:UI drift 索引：原型 3 列 grid + 底部稍后整理", "color": "5"},
       {"id": "mat-decision-undo", "text": "说明:决策点：undo toast 时长待定，owner=主 Agent，不阻塞基础实现", "color": "3", "role": "note"},
       {"id": "mat-delete-remote-merge", "text": "删除项:v1 不做远端合并，不进默认执行链", "color": "1", "kind": "annotation"}
     ]},
    {"id": "确认反馈与回退闭环"},
    {"id": "结束"}
  ]
}
```

不合适的首环是按组件或 OpenSpec 章节命名：

```
开始 → 本地素材盒 → OrganizeSheet → ConfirmToast → 同步占位 → 结束
```

这是设计材料顺序，不是完成闭环。

### runtime 下沉

`OrganizeSheet`、`ConfirmToast`、按钮文案、动画、空态、错误态、状态 pill、占位 toast 都不是默认首环。它们下沉到对应工作块右侧 runtime group：

```
[工作块:整理操作落地闭环:[处理中]]
整理操作落地闭环
  → 事实卡:整理入口出口 [绿]
  → 实现:OrganizeSheet 选择与分组 [黄]
  → 验证:选择/取消/归类回显 [灰]
  → 结束验证:整理操作
  → 整理操作落地闭环
```

如果要把 OpenSpec drift 可视化，优先写成 runtime 节点或说明节点：

```
实现:OrganizeSheet pick mode
验证:对照原型 3 列 grid + 底部稍后整理
未决点:undo toast 时长待定 → owner=主 Agent → 不阻塞基础实现
说明节点:UI drift 索引（不接 edge，不参与传播）
```

上面四项里，`实现:OrganizeSheet pick mode` 和 `验证:对照原型...` 会改变可交付行为和证据，所以是 runtime 节点；`undo toast 时长待定` 如果不阻塞基础实现，可先是黄色说明节点，阻塞出口体验时再转成 `未决点:` runtime；`UI drift 索引` 只是材料导航，保持说明节点。

### runtime 派生子环

如果 `删除素材` 从一个 runtime 节点演化出独立风险：

- 入口：点击删除
- 出口：数据删除 / 取消恢复 / 失败回滚
- 证据：本地列表、缓存、toast、重进页面全部一致

则先在同一个 workblock group 内派生子链：

```
实现:删除素材 [黄]
  ↓
调查:删除影响面 → 实现:二次确认 → 实现:本地删除事务 → 验证:取消/确认/失败回滚 → 实现:删除素材
```

只有当它阻塞多个工作块、需要独立 Knowledge Pack / Worker Pack、或必须经过独立 gate 时，才提升为新的 spine 工作块。

删除项的两种落点要分开：

- `v1 不做自动归类` 这类非目标：红色材料节点，提醒 Worker 不要把它做进默认链。
- `删除旧高级编辑入口` 这类真实代码动作：runtime 节点 `实现:移除旧高级编辑入口 → 验证:入口不可达且无坏链路`，因为它有代码落点和证据要求。

多 Agent 也只投影到这些 runtime 节点上：Worker A 可以拿 `实现:OrganizeSheet 选择与分组`，Worker B 可以拿 `验证:选择/取消/归类回显`，但 spine 不应该变成 `Worker A → Worker B → 主 Agent 回写`。

### 闭环完成判定

一个 runtime group 能推动父节点变绿，不是因为“OpenSpec 章节都写完了”，而是因为：

- runtime 链条闭合，且所有传播节点全绿
- 入口 / 出口 / 状态变化有证据
- 未决点已裁决或明确不阻塞
- 错知识、弃用方案、删除项没有进入默认执行链
- 相关 docs / Knowledge Pack / 代码落点已回写（如该节点需要知识闭环）

## 范例 10：锚点 vs runtime 细节判定

| PRD 原句 | 判定 | 落点 |
|---|---|---|
| 贴纸不影响得分 | 锚点 | `非目标：贴纸属社交表达，禁止进入得分链路` |
| 每位玩家对每位玩家均可贴 | runtime 细节 | 节点 `实现:贴纸可见性矩阵` |
| 阶段一 10s 内贴纸仅自己可见 | 锚点 | `入口/出口：阶段一 10s，贴纸仅自己可见；切换后揭晓` |
| 前三轮 10/6/3/1，第四轮加倍 | runtime 细节 | 节点 `实现:加分规则表` + Knowledge Pack locked facts |
| 结算页 15s 暂定 | 拆开 | 时序进锚点；15s 进 runtime 参数；暂定进未决点锚点 |
| 断线时卡片置灰，服务端自动 Ready | 拆开 | 自动 Ready 进锚点；卡片置灰进 runtime UI 节点 |
| 故事反馈策划 prompt 未定 | 锚点 | `未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工` |

锚点是宪法条款不是 PRD 摘要：约束面广、能限制多个 Worker 或阶段的事实才进锚点。

## 范例 11：未决点生命周期

A 类参数暂定，不阻塞实现：

```
节点 text 锚点：未决点：倒计时默认 15s 暂定 → owner=Curator → 不阻塞实现
[工作块:小局结算与 Ready 推进闭环:[处理中]] 内 runtime 节点：实现:倒计时配置（默认 15s，可调）
```

B 类方案未定，阻塞实现派工：

```
节点 text 锚点：未决点：策划 prompt 未定 → owner=主 Agent → 阻塞实现派工
[工作块:故事反馈探索裁决:[处理中]] runtime 链：调查:策划 prompt 进度 → 调查:生成耗时基线 → 结束:裁决
```

调查节点持续黄合法。跨 sprint 仍无进展回报、无 ETA、无下一任 owner，才升级红节点 + `exception.md`。group label 同步 `[处理中]→[阻塞]`、color `5→1`。

C 类冲突未裁，阻塞整个工作块：

```
节点 text 锚点：未决点：PRD 与 Figma 时长冲突（15s vs 20s）→ owner=Curator → KP-02 阻塞
spine 节点：小局结算与 Ready 推进闭环 [红]
group：工作块:小局结算与 Ready 推进闭环:[阻塞] color=1
exception.md：记录冲突事实、阻塞面、需要谁裁决
```

## 范例 12：错知识 Repair Loop

场景：路书锚点引用 `[[旧观众入口]]`，Curator Repair Loop 后确认它已被 `[[观众固定分享投票页]]` 替代。

主 Agent 在写回 `.canvas` 前必须 grep 审计：

```bash
grep -n "旧观众入口" path/to/roadmap.canvas
grep -n "audience enter" path/to/roadmap.canvas
```

处理规则：

1. 首环锚点（spine 节点 text 内）引用旧真源 → 改写为新真源
2. runtime 节点引用旧事实 → 改写节点 text；已绿节点回退到黄重新验证；group label 同步 `[已完成]→[处理中]`、color `4→5`
3. 错知识造成的假绿 → 先红 + Exception，Repair 完成后回黄重新跑证据；group label `[处理中]→[阻塞]→[处理中]` 来回切
4. 回写后跑 `audit.py`，exit 0 才算完成

---

## 反模式

### 反模式 1：首环画成横向闭合环

```
开始 → 集体亮相 → 结算 Ready → 故事反馈 → 结束 → 开始
```

违规：这是把顶层路线画成 runtime 链。spine 必须竖向（开始最下、结束最上），runtime 链才横向且只在 group 内。

### 反模式 2：黄色 spine 节点没有 group

```
后端跑通 [黄]   （没有 工作块:后端跑通 group）
```

违规：灰→黄必须**同时**建 group + runtime 链。audit.py 报 `colored spine node 后端跑通 missing 工作块: group`。

### 反模式 3：group 不含 spine 节点 P 本身（v1 → v2 关键修正）

```
spine 节点 P 在 (x=0, y=200)
group "工作块:P:[处理中]" 在 (x=400, y=150, width=600, height=200)
runtime 节点都在 group 内
```

违规：group 矩形从 x=400 起，但 P 在 x=0，**P 不在 group 内**。audit.py 报 `workblock group g-P does not contain its spine node P`。

修：group 矩形必须 x 从 P.x - GROUP_PADDING 起，包住 P 自身 + 所有 runtime。

### 反模式 4：嵌套 group 部分相交（v2 新增）

```
group A 矩形：(0..600, 0..400)
group B 矩形：(300..900, 200..600)
A 和 B 既有重叠区 (300..600, 200..400)，又互不完全包含
```

违规：audit.py 报 `group partial intersect g-A <-> g-B`。修：要么把 B 整个移进 A（完全包含），要么把 B 移出 A 重叠区（完全分离）。

### 反模式 5：方向用 v1 规范

```
spine 链内继续沿用 v1 的 (bottom, top)
runtime 结束回父仍走右/左横穿
spine 结束回 root 仍走 v1 的 (bottom, top)
```

违规：v2 spine 链内必须 `(top, bottom)`（视觉自下而上）；runtime 结束→父必须 `(bottom, bottom)` 从下方通道闭合；spine 结束→root 必须 `(left, left)` 走左侧外圈。audit.py 报 `spine edge ... wrong direction` 或 runtime closure 方向错误。

### 反模式 6：group label 状态后缀与 P 颜色不一致

```
P [黄]
group label "工作块:P:[已完成]"
```

违规：audit.py 报 `workblock group g-P status '已完成' mismatches spine node P color '3' (expected status '处理中')`。

P 颜色变化时必须同步更新 group label 状态后缀和 group color。

### 反模式 7：runtime 细节插回 spine 主干

```
spine：
  开始
   ↓
  结算 Ready 闭环
   ↓
  按钮文案    ← 违规
   ↓
  倒计时图标  ← 违规
   ↓
  结束
```

违规：按钮文案、图标、参数、UI 状态都属于 `结算 Ready` 右侧 `工作块:结算 Ready` group 内的 runtime 节点，不能放在 spine 上。

### 反模式 8：group 包住多个 spine 节点

```
group "工作块:settlement:[处理中]" 包住：
  小局结算与 Ready 推进闭环（spine）
  题目衔接剧情 OS 闭环（spine）
```

违规：一个 `工作块:` group 只能包一个 spine owner。跨多个 spine 的依赖应提升为新 spine 节点或前置 gate。

### 反模式 9：group 内部分叉成树

```
工作块 group 内：
  开始处理买菜
    ├→ 车坏了
    ├→ 酱油
    └→ 缺袋子
```

违规：group 内必须按 `父 → 开始 → 中间链 → 结束 → 父` 横向收束，结束边用 `bottom→bottom` 下方通道闭合，不能散成树枝。需要三件事一起处理时，按时间顺序串成链；并行才能进入 runtime group 的多条泳道。

### 反模式 10：gate 节点散在 spine 主干

```
spine：
  开始
   ↓
  KP-00 Domain Locked    ← 没有 Gate group 包
   ↓
  集体亮相社交体验闭环
```

违规：gate 节点必须封到独立 `Gate:KP-00:Domain Locked` group，gate group 在主干左侧独立列。audit.py 报 `gate node KP-00 not inside any Gate: group`。

### 反模式 11：Curator 出新 KP 后不审计锚点

```
Curator 完成 Repair Loop → 主 Agent 直接派下一个 Worker
```

违规：必须先 grep `.canvas`（含 group label），改写或删除旧锚点；假绿节点要回退重新验证。规则 0J T4-T5。

### 反模式 12：把 OpenSpec 章节直接画成 spine

```
开始 → 本地素材盒 → OrganizeSheet → ConfirmToast → 同步占位 → 结束
```

违规：这是组件/设计材料顺序，不是完成闭环。应先抽动作和状态变化，再收敛为 `本地素材可见闭环 → 整理操作落地闭环 → 确认反馈与回退闭环` 这类可验收工作块。

### 反模式 13：把 UI 组件当成业务闭环

```
spine:
  开始
  ConfirmToast
  结束
```

违规：`ConfirmToast` 本身通常只是反馈 UI，不是首环工作块。除非它代表跨阶段的完成确认契约，否则 toast 文案、出现时机、颜色、动效都应下沉到所属 runtime group。

### 反模式 14：runtime 横向状态永远不收束

```
[工作块:整理操作落地闭环:[处理中]]
调查:方案A → 调查:方案B → 方案:原型C
```

违规：runtime group 也是闭环推进记录，不能只堆调查和方案。它必须收束到验证、证据或明确阻塞，并保留 `结束 → 父节点` 的 `bottom→bottom` 闭合回路。

### 反模式 15：子问题一复杂就升 spine

```
开始 → 整理操作落地闭环 → 删除按钮样式 → 空态文案 → toast 动效 → 结束
```

违规：删除按钮样式、空态文案、toast 动效默认是 runtime 细节。只有当子问题具备独立入口/出口、状态推进、验收证据，或阻塞多个工作块 / 需要独立 gate / Worker Pack 时，才升级为新的 spine 工作块。

### 反模式 16：把 Agent 分工画成主干

```
开始 → Curator 扫文档 → Worker-A 实现 → Worker-B 测试 → 主 Agent 回写 → 结束
```

违规：这是协作流程，不是目标闭环。Agent 分工应该映射到对应 runtime group 的执行记录；spine 主干仍然只能表达“为了完成这件事必须闭合的工作块”。
