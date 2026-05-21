---
name: say-show-boundary
description: >-
  Use when 用户或 agent 把价值判断、审美判断、愿景、伦理边界、产品品味、方向感或“好/坏/高级/自然/有趣”
  伪装成事实命题，或需要区分可说的事实与只能展示的取向时使用。
---

# Say Show Boundary

本 skill 区分两类东西：

- **可说**：能写成事实命题，能被证据支持或反驳。
- **只能 show**：价值、审美、愿景、品味、伦理边界、方向感。它们不能被当作事实证明，只能通过选择、约束、例子、体验和后果展示。

目标不是禁止价值判断，而是防止 agent 把价值判断伪装成事实，污染后续决策。

## 输入前置检查

router 已经做了一道分流，但 router 可能判错或被绕过。本 skill 在开工前必须自检一次——这是冗余兜底，不是 router 的替代：

- 输入是纯对象/关系/状态/字段问题（如 "X 字段能不能挂在 Y 表"）时，**转 `logical-grammar`**——这种句子里没有价值层可剥，让本 skill 判别会空转。
- 输入是已成句、不含价值词的 claim / gate 真值问题时，**转 `truth-condition-checker`**。
- 输入来自 PRD / 设计稿，且需要把事实规则写入 Obsidian / OpenSpec / roadmap 时，事实层剥出来后必须交 `canonical-claim-compiler`，不要直接落 wiki。

本 skill 只处理"含 价值/审美/愿景/伦理/方向感 词"或"明显是品味/偏好表达"的输入。

## 判断流程

```mermaid
flowchart LR
  A["输入判断"] --> B{"能否被证伪?"}
  B -->|能| C["可说<br/>事实命题"]
  B -->|不能| D["只能 show<br/>价值 / 审美 / 愿景"]
  C --> E["交给 truth-condition-checker"]
  D --> F["改写为取向 + 约束 + 例子 + 选择后果"]
```

## 快速判别

| 表达 | 类型 | 处理 |
|---|---|---|
| “日志里出现了 X” | 可说 | 查日志验证 |
| “这个字段由服务端写入” | 可说 | 查代码/契约验证 |
| “这个体验更高级” | 只能 show | 改成品味标准和例子 |
| “这条路更正确” | 只能 show | 改成目标取向和代价 |
| “用户会更喜欢” | 混合 | 拆成假设、观测指标、价值取向 |
| “我们应该保持克制” | 只能 show | 改成设计原则和拒绝事项 |

## 纠正方式

当用户或 agent 把价值判断伪装成事实时，必须提示并改写：

```md
这里不是事实命题，不能直接用证据证明。
它更像一个 <价值/审美/愿景/伦理> 取向。

可改写为：
- 取向：我们偏向 ...
- 约束：因此不做 ...
- 可观察信号：如果这个取向被执行，用户/系统会看到 ...
- 反例/代价：它可能牺牲 ...
```

不要只说“这是主观的”。要给出能继续工作的表达方式。

## 输出格式

```md
结论：可说 / 只能 show / 混合命题

原句：
<用户或 agent 的判断>

拆分：
| 片段 | 类型 | 为什么 | 下一步 |
|---|---|---|---|
| ... | fact/value/aesthetic/vision/ethic | ... | 验证 / 改写 |

纠正后的说法：
- 可说事实：
- 只能 show 的取向：
- 决策约束：
- 可观察后果：
```

## 混合命题处理

很多产品判断是混合命题，要拆开：

```md
“这个方案会让体验更自然。”
```

拆成：

- 可说事实：交互步骤减少、等待时间降低、错误率下降、用户不用理解内部术语。
- 只能 show：我们偏好低解释成本、少打断、动作像日常习惯。
- 验证方式：可观测指标或用户测试。
- 决策约束：即使指标相近，也优先选择解释成本低的方案。

如果拆出的可说事实要进入 durable knowledge，继续走：

```text
say-show-boundary
  -> canonical-claim-compiler
  -> project-knowledge-curator
```

价值 / 审美 / 愿景只能成为 `claim_type=value/taste/vision/decision` 的 boundary claim，不能写成 accepted fact/rule。

## 常见反模式

- 把“高级”“正确”“自然”“有趣”“克制”直接写进验收条件。
- 用用户价值判断替代事实验证。
- 用数据强行证明审美取向；数据最多证明某些可观测后果。
- 因为价值不能证伪，就把它丢掉。正确做法是把它改成选择原则、拒绝事项和例子。
- 把只能 show 的愿景写成不可挑战的事实，导致后续 agent 误以为已经验证。

## 与其他 skill 的关系

- `logical-grammar`：先判断对象、关系、状态能不能合法组合。
- `canonical-claim-compiler`：事实层要进入知识库、OpenSpec 或 roadmap 时，负责生成 concept / claim / pending / drift。
- `truth-condition-checker`：只处理可证伪的事实条件、gate 和 decision。
- 本 skill：处理事实验证之外的价值、审美、愿景和边界表达。

## 术语边界（Wittgenstein vs Hume）

本 skill 借用 Tractatus 的 say/show 命名，但工程落点是 Hume 的 fact/value 二分（事实可证伪 vs 规范不可证伪）。

| | Tractatus 原义 | 本 skill 工程化 |
|---|---|---|
| say | 事实命题（picture theory） | 事实命题（含可证伪事实/规则/推断） |
| show | 逻辑形式自身显示 + 伦理 transcendental | 价值 / 审美 / 愿景 / 品味 / 方向感 / 伦理 |

差异：Tractatus 的 show 主战场是"逻辑形式不能被语言说出来"，伦理只是子集；本 skill 把"任何不可被事实证据驱动的取向表达"都归 show。如果以 Tractatus 严格语义反驳本 skill，引此段说明：本 skill 借的是名词，落的是工程。
