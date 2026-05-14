---
name: dq-be-tech-design
description: 当用户要为 openspec change、新服务、新领域、功能迭代、库表/schema 变更、跨服务/架构改动编写或评审 tech_design.md，判断是否要技术方案、画架构图、处理评审、归档、change 生命周期、核心变更记录时使用。
status: beta
---

> **公理继承 / Axiom Inheritance**
> 本 skill 服从顶层公理 `typed evidence gates action`——
> 未经类型化（三色 + authority + kind）的上下文不允许驱动行动。
> 在该公理下，本 skill 的职能：为 OpenSpec change 生成类型化的 tech_design.md 证据（23 节模板 + 多轮 review），gate 跨服务/架构/库表的合法改动

# 后端技术方案设计规范 【beta】

> **权威源**：本文件是权威。飞书门户跳转见仓库 README 的"门户跳转"节。

## 状态

`beta` — 主体规范已定稿可落地，进入团队内试用阶段收集反馈。少数细节见 `references/backlog.md`。

本规范定义后端技术方案文档的**产出、归档、评审、与 openspec 工作流的集成**。

## 1. 适用范围与触发分档

哪些改动需要写 `tech_design.md`：

| 档位      | 触发条件                                       | tech_design 要求                |
| ------- | ------------------------------------------ | ----------------------------- |
| **必须写** | 新服务 / 新领域模块 / 跨服务改造 / **库表结构变更** / 架构影响性改动 | 全量模板（必填节 + 条件必填节；不触发的节写"无改动"） |
| **建议写** | 单服务内 3+ 文件的新功能                             | 同上全量模板（但更多条件节可能是"无改动"）        |
| **可不写** | 单文件 bug fix / 参数调整 / 文案更新 / 轻量重构（无结构变化）    | 无                             |



## 核心原则（快查）

- **必须写**：新服务 / 新领域模块 / 跨服务改造 / 库表结构变更 / 架构影响性改动。
- **建议写**：单服务内 3+ 文件的新功能。
- **可不写**：单文件 bug fix / 参数调整 / 文案更新 / 无结构变化的轻量重构。
- **一个需求一个 change**：同一需求从 proposal 到归档都在同一个 change 内持续维护。
- **仓库自闭环优先**：每个仓库 / 服务都有自己的 openspec change 和当前态 tech_design；跨多端 / 多仓库公共汇总统一放 `gitlab.daqian369.com/esm/narnia/dev`，但不替代仓库内文档。
- **多轮人工 review**：技术设计、开发联调、测试阶段都可能触发 review。

## 按需加载导航

| 场景                                                    | 读取                                          |
| ----------------------------------------------------- | ------------------------------------------- |
| 写 `tech_design.md` 23 节模板、判断必填/条件必填、处理常见反例            | `references/template-sections.md`           |
| 实施前人工确认、多次 review、AI Native 操作流程、生成时机、change 使用原则     | `references/review-and-change-lifecycle.md` |
| 查示例文档、openspec schema source of truth、install.sh、升级路径 | `references/examples-and-schema.md`         |
| 维护本规范 TODO / 未定稿条目                                    | `references/backlog.md`                     |

## 相关

- 开发流程 / openspec change 节奏 → `dq-be-dev-practice`
- 代码结构 → `dq-be-code-structure`
- idl / Proto 契约 → `dq-be-idl-convention`
- MySQL DDL / 字段规范 → `dq-be-mysql-design`
- 日志 / 错误码 / 公共库 → `dq-be-libs`
- 部署 → `dq-be-deploy`
- 问题排查 → `dq-be-troubleshooting`
