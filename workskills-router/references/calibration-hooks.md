# Calibration Hooks 调度契约

本仓库声明六个触发点的调度契约（输入 / 拦截条件 / 失败动作）。本机 `context-compiler` 是该契约的一种实现，不是契约本身。换机器需重建本机实现，但契约不变。

设计原则：**router 判 + skill 自检 + 本机 hook**，三层冗余。接受重复，不接受逻辑失效。

## 六个触发点

### 1. skill discovery（选 skill 之前）

- **输入**：用户请求 + 已加载 skill 列表。
- **拦截条件**：请求里出现"对象/关系/状态/字段/价值词/真值/gate"等校准信号但 router 未命中三类逻辑 skill。
- **失败动作**：`workskills-router` 强制接管，按 router flowchart（"含价值词 → say-show 先剥层 / 纯事实 → grammar / 已成句真值 → truth"）走分流。

### 2. fanout（扇出子任务之前）

- **输入**：主 agent 准备扇出的子任务 prompt 列表。
- **拦截条件**：存在语义歧义，即两个合理解释会实质改变结果、候选范围、worker scope 或行动；或子任务 prompt 里出现"应该 / 更好 / 高级 / 自然 / 有趣 / 克制 / 正确方向"等价值词。
- **歧义动作**：只有 material semantic ambiguity 才先调用 `clarification-tripwire`，并服从它返回的 disposition 与 Interrupt Protocol。
- **价值词动作**：价值词本身只触发 `say-show-boundary` 剥层，不因出现价值词而强制调用 `clarification-tripwire`；只有剥层后仍存在 material semantic ambiguity 才升级到歧义动作。

### 3. subtask exec（子任务执行之前）

- **输入**：子任务 prompt + 上下文片段。
- **拦截条件**：仍有会实质改变执行结果、行动、写入或外部影响的语义歧义；或上下文里有未通过 SourceCheck 的 claim，或有未带 `claim_type` 的 source。
- **歧义动作**：只有 material semantic ambiguity 才先调用 `clarification-tripwire`，并服从它返回的 disposition 与 Interrupt Protocol。
- **知识动作**：SourceCheck 或 `claim_type` 缺口本身只触发 `project-knowledge-curator` 标 `claim_type`（fact/rule/inference/value/taste/vision/decision）和 `knowledge_color`，不强制调用 `clarification-tripwire`。

### 4. pre-execution（主 agent 直接执行之前）

- **输入**：主 agent 即将直接执行的行动、写入、material conclusion 或 delivered response。
- **拦截条件**：存在两个合理语义解释，并且不同解释会实质改变结果、行动或用户收到的回答。
- **失败动作**：调用 `clarification-tripwire`，并服从它返回的 disposition 与 Interrupt Protocol。

### 5. pre-finish（标记任务完成之前）

- **输入**：当前任务的产出（代码/文档/卡片/图）。
- **拦截条件**：产出里出现"已验证 / 已成立 / 已收口 / 通过 gate"等结论但缺失 truth condition 或 support/refute。
- **失败动作**：先让 `truth-condition-checker` 拆 support/refute/contradiction，补齐才允许收口。

### 6. skill authoring（写新 skill 之前）

- **输入**：新 skill 的 SKILL.md 草稿。
- **拦截条件**：草稿描述里出现"自动判断 / 智能识别 / 推荐 / 适当地"等 fuzzy 动作。
- **失败动作**：让作者用 `logical-grammar` 改写成"对象 + 关系 + 状态 + 动作"四段式可成句描述。

## Skill × 触发点矩阵

| Skill | discovery | fanout | subtask exec | pre-execution | pre-finish | skill authoring |
|---|---|---|---|---|---|---|
| `clarification-tripwire` | | ✓ | ✓ | ✓ | | |
| `say-show-boundary` | ✓ | ✓ | | | | |
| `logical-grammar` | ✓ | | | | | ✓ |
| `truth-condition-checker` | ✓ | | | | ✓ | |
| `project-knowledge-curator` | | | ✓ | | | |

空格表示该 skill 不在该触发点被自动调用，但仍可被显式 invoke。

## 失效模式（必须意识到）

- 本契约不是仓库级硬门禁。clone workskills 后，没有 hook 实现的环境里，调度层完全失效。
- 失效场景下的回退路径，按优先级：
  1. `workskills-router` 主动按 flowchart 分流（router 是仓库级的，clone 后仍生效）
  2. 三类逻辑 skill 各自的"输入前置检查"段做兜底（每个 skill 自检"我是不是该接这个输入"）
  3. 用户/主 agent 显式指明用哪个 skill
- **不要假设 hook 一定存在**。下游 skill 的前置检查段是冗余设计，不是冗余浪费——它在 hook 失效时是唯一防线。

## 与本机 context-compiler 的关系

| 层 | 职责 | 是否仓库级 | 失效后果 |
|---|---|---|---|
| 仓库内 router flowchart | 声明意图 → skill 的映射 | 是 | clone 即生效 |
| 仓库内下游 skill 前置检查段 | 每个 skill 自检输入合法性 | 是 | clone 即生效 |
| 本仓库 calibration-hooks.md | 声明触发点契约 | 是 | clone 可读，但需本机实现 |
| 本机 context-compiler | 在六个触发点强制调用三类逻辑 skill | 否 | clone 不带过来；换机器即失效 |

如果 context-compiler 的实现细节迭代，应回头更新本契约——契约比实现稳定。
