---
name: mewt-field-log-forensics
description: >-
  Mewt 外采诊断日志（FEATURE_FIELD_DIAG）的抓取与复盘标准流程。
  当用户说 拉日志 / 抓日志 / 把手机日志拽下来 / 复盘外采 / 猫咖实测复盘 /
  看看刚才录音识别效果 / wav 在哪 / 为什么没翻译 / 为什么丢弃 /
  召回率怎么算 / mewt-field 时使用。目标：一条命令拽全设备证据，
  用前缀表把"系统判了什么"逐事件还原，wav 负责"实际发生了什么"。
---

# Mewt 外采日志取证与复盘 (mewt-field-log-forensics)

> 适用 Mewt iOS 实测包（`FEATURE_FIELD_DIAG=true`）。首验 2026-06-11：办公室 1 分钟人声
> （25 block 全部正确丢弃、零误译）+ 半分钟录音/拍照/识别，全链路走通。
> 本卡是人话入口 + 可执行 SOP，**不是权威源**——权威源见文末反查表，冲突以仓库代码与
> `Mewt/docs/基建/外采诊断日志-取证与复盘SOP.md` 为准。

## 触发条件

用户说任何下列之一就用本 skill，不需要用户解释背景：

- 「拉日志」「抓日志」「把日志拽下来」「日志回溯」
- 「复盘外采」「猫咖实测复盘」「看看刚才录音/识别效果」
- 「为什么没翻译」「为什么丢弃」「漏喵了吗」「wav 在哪/没有音频」
- 「召回率/准确率怎么从日志算」

## 日志规则（系统长什么样）

**落盘结构**（设备上 `Documents/mewt-field/`）：

```
logs/<appSessionId>/chunk-NNNN.jsonl   # 每次 app 启动一个目录(id=启动时刻 yyyyMMdd-HHmmss-rand)
                                       # 2s/100条批量 flush, 1000 行轮转, 7 天自动清理
audio/<deepmewtSessionId>.wav          # 每次聆听坞会话一个 wav(16-bit PCM)
                                       # 只覆盖聆听坞开着的时段, 不是全程环境录音
```

**JSONL 行格式**：`{"ts":毫秒,"lvl":"log|warn|error|info","msg":"[前缀] {json payload}"}`。
DeepMewt 会话 id 是 uuid（在 `deepmewt_session_start` / `[AudioDump]` 行里），用它把 wav 和日志钉到同一时间轴。

**业务前缀表**（msg 开头 → 回答什么问题）：

| 前缀 | 回答 | 关键字段 |
|---|---|---|
| `🟢 [StreamingSession] start` / `[DeepMewt:Session] session_stopped` | 录音会话边界+汇总 | totalBlocks/silentBlocks/mimicBlocks/llmBlocks |
| `🔊[DBG-VAD]` | 有没有声响(0.5s采样) | rms, thr, pass |
| `[MeowVAD] segment_rejected` | 短段为何被 VAD 丢 | startSec, durationSec, peakRms, reason |
| `🐱[DBG-GATE]` | block 路由/快路径结果/译文 | type, route, fast=category/emotion/confidence |
| `[DeepMewt:kNN] block_silent/block_mimic` | **为什么丢弃**(带分数) | catScore/humanSpeechScore/meowLikeScore, gate_reason |
| `[DeepMewt:kNN] classify` | kNN 投票明细 | top3, 两级 confidence vs 0.7 |
| `[DeepMewt:kNN] streaming_fail` / `[DeepMewt:Session] block_timeout` | 慢路径 LLM 为何失败 | reason, status, elapsedMs |
| `[AudioDump] start/complete/failed` | wav 落了没、多长 | path, durationSec(按样本数), wallClockSec |
| `capture-ui-pressed` / `[StickerPipeline]` | 手动拍照→抠图→入盒 | captureId, settled, localStickerId |
| `[stickerService]` / `🧬[EMBED诊断]` | 抠图引擎与 embedding | maskSource, confidence vs 0.3, dim=1024, norm≈1 |
| `[ReidLine2]` / `[ReidDemo]` | 巡检识别命中谁、分数 | bucket, query_vs_stored, ranked[猫:cosine] |
| `[ReidEngine]` | reID 引擎为何早退 | exit:empty_query/no_cats/..., dim_mismatch |
| `[StickerSort]` | 抽屉排序与归类动作 | mode:reid/count_fallback, commit/create/undo |
| `[CatDetect]` | 相机检到/丢失猫 | transition:acquired/lost |
| `[GalleryImport]` | 相册导入逐张结果 | outcome, skipReason, gps |

**写日志的规则**（改 Mewt 代码新增日志时必须遵守）：
`console.log('[Tag]', JSON.stringify({event,...}))` 单行；前缀只能用上表已有的（新增前缀要同步更新本卡+仓库 SOP）；不打逐帧/循环内日志；劫持与落盘由 `FEATURE_FIELD_DIAG` 统一 gate，业务日志本身不包 flag。

## 怎么抓日志（按优先级）

**路 1 — devicectl（首选：开发签名包，iOS 17+，不需要文件共享 key）：**

```bash
xcrun devicectl list devices        # 取 connected 设备的 Identifier
rm -rf /tmp/mewt-field-pull && mkdir -p /tmp/mewt-field-pull
xcrun devicectl device copy from \
  --device <Identifier> \
  --domain-type appDataContainer --domain-identifier com.xyakim.mewt \
  --source Documents/mewt-field --destination /tmp/mewt-field-pull
```

**路 2 — Finder/afcclient（包必须是 prebuild 后打的，Info.plist 才有 UIFileSharingEnabled）：**
插线 → Finder → 设备 → 文件 → Mewt → 拖走 `mewt-field`；或 `afcclient --documents com.xyakim.mewt`。
报 `InstallationLookupFailed` = 打包时跳过了 `npx expo prebuild -p ios`，换路 1。

**路 3 — App 内导出（现场无 Mac 应急）：** 贴纸盒 → 设置齿轮 → 调试日志 → 导出（AirDrop 当前会话 JSONL；**不含 wav**）。

## 复盘配方

1. 选会话：`for f in /tmp/mewt-field-pull/logs/*/chunk-*.jsonl; do echo "$(wc -l < $f) $f"; done`（行数最大≈测试主会话）。
2. 前缀直方图看全貌 → 按前缀表逐链提取时间线（python3 标准库即可，逐行 json.loads 按 ts 排序，关键词过滤）。完整配方代码在仓库 SOP §2。
3. 录音链验收序列：`session_start → [AudioDump] start → (block_silent/mimic 带分数 | submitted→译文) → [MeowVAD] rejected → session_stopped 汇总 → [AudioDump] complete`。缺哪环查哪环。
4. wav 对账：complete 的 durationSec ≈ 聆听坞开启时长；连续能量证据以 wav 为准（可重灌 pipeline），日志只管离散判定。

## 已踩坑（全部真机实证）

1. **先点 toggle 停止再杀 app**：直接杀 → session_stopped 丢、wav 文件头不收尾可能打不开、最后 ≤2s 日志丢在 flush 窗口。
2. `[AudioDump]` 有 start 无 complete/failed = 2026-06-11 前的老包；failed 事件之后才有。原生失败细节只在 NSLog（连线 Console.app）。
3. 给原生传路径必须剥 `file://` 前缀（已在 JS+原生双侧修复，commit `e6ec6b1d`）——看到 audio 目录空先查包版本。
4. iOS release 包 console 不进系统日志，本落盘体系是唯一回溯通道；Android 现场 `adb logcat -s ReactNativeJS`，不落 wav。
5. 离线时 `[supabaseQuery] 请求超时` 是正常噪音；慢路径必失败，看 streaming_fail 的 reason 区分网络/逻辑。
6. wav 只覆盖聆听坞时段——算召回率分母以会话时段为准，现场保持会话开启再逗猫。

## 失效条件（出现任一，本卡降权并回权威源重校）

- `constants/featureFlags.ts` 的 `FEATURE_FIELD_DIAG` 被翻 `false`（上架态）→ 整个落盘体系不存在。
- Bundle id 不再是 `com.xyakim.mewt`，或测试机 iOS < 17（路 1 失效）。
- 前缀表与代码 grep 结果不一致 → 以代码为准并回写本卡与仓库 SOP。

## 权威源反查

| 层 | 位置 |
|---|---|
| 仓库 SOP（命令/配方全文） | `Mewt/docs/基建/外采诊断日志-取证与复盘SOP.md` |
| 落盘实现 | `Mewt/lib/fieldLogSink.ts` · `lib/debugLogger.ts` |
| 录音/wav/拒绝事件 | `hooks/useDeepMewtRecorder.ts` · `ios/Mewt/CatMeowAnalyzerBridge.swift`（改完必须 cp 同步 `plugins/native-backup/`） |
| flag 与上架 checklist | `constants/featureFlags.ts` 的 `FEATURE_FIELD_DIAG` 注释 |
| 落地 commit | `05c2c19a`（全链路）· `c6f2f423`（emit 异步化）· `e6ec6b1d`（wav 根因+SOP） |
