---
name: narnia-stuck-lock-diagnosis
description: >-
  Narnia morph66/morph72/v19 房间卡锁票（group_finale / group_last 卡死、灰按钮）的标准诊断流程。
  当用户说 X 房间卡了 / 又卡了 / 卡锁票 / 卡 group_finale / 卡 group_last / 灰按钮 /
  卡结票 / 房间不推进 / FSM 不动 / 锁票循环时使用。目标：5 分钟内出真因 + 修复方向，
  全程过程对用户可见，不让用户瞎等。
---

# 卡锁票诊断 (narnia-stuck-lock-diagnosis)

> 适用 morph66 / morph72 / v19 三个游戏类型的"房间卡在锁票相关阶段"问题。
> 历史上这类问题平均 20+ 分钟才能定位，本 skill 把流程标准化、并行化、可见化。

## 触发条件

用户说任何下列之一就用本 skill，**不需要用户解释症状**：

- 「X 房间卡了」（X 是 4 字母 room name，如 NEIY / GTFE / GTDU / QPAE）
- 「又卡了」「还在卡」
- 「卡锁票」「卡结票」「锁票卡了」
- 「卡 group_finale」「卡 group_last」「卡 settlement」
- 「灰按钮」「滑动按钮没出来」「host 按钮不亮」
- 「房间不推进」「FSM 不动」「state 不切换」
- 「锁票循环」「死循环」「retry 一直跑」

## 流程总览（5 步，每步标注 SLA）

```
Step 1 [30s]  确认 pod image 是不是最新部署 → pod 跑老版的话直接告知不用诊断
Step 2 [60s]  从 room name 反查 game_id（如果用户直接给了 game_id 跳过）
Step 3 [3min] tls-log-search 拉 lockMorph66FinalVotes 完整事件链
Step 4 [60s]  对照「已知卡点模式表」分类 + 出真因结论
Step 5 [30s]  给修复方向决策卡（不直接改代码，等用户拍）
```

总 SLA：5 分钟内出结论。**全程派 narnia-ops 跑，主 Agent 实时把派活内容告诉用户**。

## Step 1：pod image 确认（30s）

```bash
kubectl get pods -l app=gsc,lane=<lane> -o jsonpath='{.items[*].spec.containers[*].image}'
```

- 期望：image tag 含**最新 commit SHA 后缀**（用户记忆里通常知道）
- 如果不是最新 → **直接告知用户 pod 没在跑最新版**，问要不要先重新部署再诊断（90% 的"又卡了"其实是部署没生效）
- 是最新 → 继续 Step 2

## Step 2：room name → game_id（60s）

用户给的是 4 字母 room name (room_name 字段)，但 log 关键字段是 `game_id`（数字）。

派 narnia-ops 用 tls-log-search：
```
query: room_name:"<NAME>" AND service:gsc
time: 最近 1 小时
fields: game_id, game_round_id, game_type, players
```

输出锁定：
- `game_id`（数字，给 Step 3 用）
- `game_round_id`（当前轮）
- `game_type`（morph66 / morph72 / v19）
- `players`（座位/玩家列表，几人房）

## Step 3：拉锁票事件链（3min）

派 narnia-ops 用 tls-log-search 拉**这一档 12 个 event 名**，按时间排序成表格：

| 阶段 | event 名 | 含义 |
|---|---|---|
| 进入 | `gsc.morph66.lock_final_votes.enter` | lockFinalVotes 被触发 |
| ① finalize | `gsc.morph66.lock_final_votes.poison_result.call` | GetOrFinalizePoisonResult 调用 |
| ① finalize | `gsc.morph66.lock_final_votes.poison_result.ok` | GetOrFinalizePoisonResult 成功 |
| ① finalize | `gsc.morph66.lock_final_votes.poison_result.error` | GetOrFinalizePoisonResult 失败 |
| ② sponsors | `gsc.morph66.lock_final_votes.sponsor.attempt_failed` | sponsor inline retry 失败 |
| ② sponsors | `gsc.morph66.lock_final_votes.sponsor.retry_ok` | sponsor retry 成功 |
| ② sponsors | `gsc.morph66.lock_final_votes.sponsor.error` | sponsor 最终失败 |
| ③ witch | `gsc.morph66.lock_final_votes.witch.attempt_failed` | witch inline retry 失败 |
| ③ witch | `gsc.morph66.lock_final_votes.witch.retry_ok` | witch retry 成功 |
| ③ witch | `gsc.morph66.lock_final_votes.witch.error` | witch 最终失败 |
| 汇合 | `gsc.morph66.lock_final_votes.sponsor_witch.ok` | 两个 RPC 都成功 |
| 退出 | `gsc.morph66.lock_final_votes.exit` | action 结束（changed=? group_last_changed=?） |

如果是 morph72 / v19，替换前缀 `gsc.morph66.` → `gsc.morph72.` / `gsc.v19.`。

**关键：要拿到完整 raw error message**（不是只看 event 名），错误消息里通常有真因关键词（如 `final_votes missing seat=3`）。

### 数据源 fallback：audience-interaction 端 grpc trace

如果 GSC `gsc.morph66.lock_final_votes.*` 这一档 event 在 TLS 查不到（可能 GSC pod 没起或日志没落库），可以从 **audience-interaction 服务端的 `grpc.server.end` event** 拿权威响应：

- 服务名：`audience-interaction`
- event：`grpc.server.end`（每个 RPC 都会打）
- 关键 RPC 名：`GetOrFinalizePoisonResult` / `GetSponsorLeaderboard` / `GetPoisonCandidates`
- response 字段含完整 `finalVotes` / `hitPlayerUid` / `hitSeat` / `hitRule` / `lockedAtMs` / `sponsors`

这是 audience 自己 log 的真实响应，不依赖 GSC pod 版本，作为查询失败时的 fallback。**如果只是查"谁中毒了"这类业务问题，直接用 audience 端 grpc trace 更直接**，不用走 GSC 那一档。

## Step 4：对照已知卡点模式表分类（60s）

按 Step 3 拉到的事件链，对号入座：

### 模式 A：业务校验 reject（最常见，~60% case）

**特征**：finalize.ok 已出，后续无 sponsor/witch 事件，**没有 exit 事件**，下一秒立刻又有新 enter 事件。

**典型 error message 关键词**：
- `final_votes missing seat=N` ← NEIY 模式（已修：85b4bb0 + bian-fix），audience 真返实际座位数被 GSC 校验拒
- `final_votes must cover seats 1..4` ← 同源
- `final_votes contains invalid seat=N` ← 同源
- `final_votes contains duplicated seat=N` ← 同源
- `negative vote_count` ← 同源
- `sponsor leaderboard row N missing display fields` ← GTDU 模式（已修：85b4bb0）

**真因**：GSC 端硬编码假设违反"audience 返啥用啥"原则。

**修复**：grep 出 reject error 字面量定位代码点，按 85b4bb0 / `服务器返啥用啥` 原则删校验。

### 模式 B：audience RPC 真挂（~15%）

**特征**：finalize.error / sponsor.error / witch.error 任一出现，retryable=true 反复触发 reset retry。

**修复方向**：派人去看 audience-interaction pod 是不是挂了、回滚 audience 版本、调 retry 次数。

### 模式 C：hitPlayer empty / lockedAt invalid（~10%）

**特征**：finalize.ok 但走 `gsc.morph66.lock_final_votes.hit_player_empty` / `locked_at_invalid` → reset retry。

**真因**：audience 给的 hit_player_uid 不在 room state 里 / lockedAtMs 是 0 或负。

**修复方向**：看 audience 端 GetOrFinalizePoisonResult 实现是不是返了脏数据。

### 模式 D：FSM 死循环（~10%）

**特征**：reset retry 每 3000ms 一次，已重复几十次 / 几百次。

**修复方向**：看 `resetMorph66GroupFinaleLockRetry` 是不是无上限。可能要加最大 retry 次数 + game failed 兜底。

### 模式 E：tick 死循环（~5%，最危险）

**特征**：lockFinalVotes 每 200ms 一次 enter 事件，没有 reset retry log。

**真因**：error 返回路径绕过 `morph66AudienceErrorRetryable` 判断，FSM timer 没 reset，下个 tick 重新触发。NEIY 就是这模式。

**修复方向**：(b) 删 reject 源头消除问题 / (a) 让 error path 走 retryable 判断。

### 模式 F：state 已切走但 UI 卡（~5%）

**特征**：exit 事件 changed=true，state.show 显示已经在 `group_last` 或 `settlement`，但 UI 显示卡。

**真因**：是 FE 端问题（codec throw / displayExtra 残留 / 字段读路径错）。

**修复方向**：派 narnia-fe-dev 看 FE codec 和渲染层。**不要再改 BE**。

## Step 5：决策卡（30s）

按 Step 4 分类出来真因后，给用户**一张决策卡**（不直接改代码）：

```markdown
# NEIY 卡死真因：模式 X

## 证据
[Step 3 时间线表 + Step 4 error message 关键字]

## 修复方向候选
- (a) ...
- (b) ...
- (c) ...

## 你的答：__
```

用户拍完才动代码。

## 标准报告模板（让 narnia-ops 用）

```markdown
## <房间> 卡锁票分析报告

### 1. Pod Image 确认
[YES/NO] image tag = <tag>，pod = <count> 个 Running

### 2. <房间> 基本信息
- game_id = <id>，game_round_id = <id>，game_type = <type>
- <N> 人游戏：seat=<...>
- 进入卡点阶段：<timestamp>
- 当前 state：<state.value/state.show>，卡了 <duration>

### 3. 锁票链路逐事件时间线
| 时间戳（UTC） | 事件 | 关键字段 |
|---|---|---|
| ... | ... | ... |

### 4. 真因判断
模式 <A/B/C/D/E/F>：<一句话>

### 5. 修复建议
代码位置：`<file:line>`
建议方向：(a) / (b) / (c)
```

## 硬约束（必须遵守）

- ❌ 不改代码（先出结论让用户拍方向）
- ❌ 不重新部署（除非用户授权）
- ❌ 不重启 pod
- ❌ 不重新 deploy_lane.sh
- ✅ 只读 log + kubectl get（read-only ops）
- ✅ 全程过程可见：每派一个 narnia-ops 子任务都告诉用户在派什么

## 沉淀新模式

发现新的卡点模式（不在 A-F 里）→ 用 [knowledge-card-qa](../knowledge-card-qa/SKILL.md) 抛卡确认 → 加进本 skill 的「已知卡点模式表」。每加一个模式就让下次诊断快一截。

## 跟其它 skill 协同

- 出真因需要业务知识时 → 用 [project-wiki](../project-wiki/SKILL.md) 查 Obsidian vault
- 真因牵涉错知识时 → 用 [project-knowledge-curator](../project-knowledge-curator/SKILL.md) 裁决
- 修复方向定下来后 → 主 Agent 自己改代码或派 golang-backend 改
- 改完部署 → 派 narnia-ops 走 commit/push/deploy 一条龙
