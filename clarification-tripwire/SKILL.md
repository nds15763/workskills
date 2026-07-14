---
name: clarification-tripwire
description: Use when multiple reasonable interpretations could materially change execution, fanout, a material conclusion, or a delivered response.
---

# Clarification Tripwire

## Core rule

Before execution, fanout, a **material conclusion**, or a **delivered response**, run a counterfactual check: **Can two reasonable interpretations of the user's wording lead to materially different work or conclusions?** Do not silently collapse them into the interpretation that feels most probable.

Treat divergence as material when it changes any of these:

- decision object, requested action, or criteria axes;
- candidate inclusion, ranking, or elimination;
- worker scope, files/modules touched, or fanout prompt;
- writes, external effects, irreversible actions, or the delivered outcome.

Before asking, a **bounded read-only lookup** may resolve factual reference ambiguity from supplied context or authoritative project defaults. Lookup must never infer **user-owned semantics**: intent, values, **permission**, or **optimization** targets. Bayesian confidence can rank factual hypotheses; it cannot close those user-owned variables. A high-confidence guess is still a guess when only the user can close the variable.

## Interrupt Protocol

The **first semantic commitment point** is the interrupt boundary: stop before candidate exclusion or candidate elimination, fanout, any write or external effect, a material conclusion, or a delivered response.

For a blocking ambiguity:

1. The **only pre-STOP exception** is a **bounded read-only lookup** for factual references. It must not infer user intent, value, permission, or optimization.
2. Enter explicit **STOP** and **freeze** candidate exclusion/elimination, fanout, writes and external effects, material conclusions, and delivered responses.
3. Ask **exactly one minimal, decision-changing question**. End the turn and wait.
4. **Resume only** when the **user chooses** or selects an interpretation, **explicitly authorizes branches** or a dual axis, or **delegates the choice**. On resume, propagate the resolved semantic contract to direct execution and every worker prompt.

## Disposition

- **clear**: There is **no material ambiguity** after the counterfactual check or bounded factual lookup. Continue **without asking**.
- **blocking**: The interpretations produce materially different outcomes and cannot both be honored. Enter STOP, ask exactly one minimal decision-changing question, end, and wait under the Interrupt Protocol.
- **branchable**: The user authorizes a dual-axis or branched output, and both interpretations can be preserved without loss. Keep both branches explicit and continue; do not merge one branch into the other.
- **non_blocking**: The detail is cheap, reversible, and outcome-invariant. State the assumption and continue. If changing the assumption could alter the conclusion, candidate set, worker scope, or side effect, it is not non_blocking.

For fanout, freeze confirmed facts only and preserve unresolved semantic variables. **Every worker prompt** must expose each **unresolved semantic variable**; the fanout must **collectively** cover **every preserved branch** with explicit **branch ownership**. Each preserved branch has one owner by default; duplicate ownership is allowed only for an explicitly declared independent verification lane. Never freeze a guessed interpretation as shared truth.

## Motivating example

“哪些 skill **应该合入**，一定要找**高质量**的 skill” contains two independent ambiguities:

- **应该合入** may mean strong **value/fit** after reasonable adaptation, or current **readiness/risk** for direct merge. These axes must remain separate; readiness/risk 不能替代或否定 value/fit。
- **高质量** is a **多轴** judgment: substantive 价值、独特性、团队适配、收益、改造成本、风险，以及 hygiene/细节错误。高质量不能只等于卫生正确或没有细节错误。

This case is **blocking** when the user requested a **singular shortlist** or selection and value/fit versus readiness/risk changes candidate membership. Ask one minimal question: “May the shortlist include valuable-but-needs-adaptation skills, or only currently merge-ready skills?” Then wait **before fanout** or tools. It is **branchable** only when the user **explicitly authorizes** a dual-axis or branched output.

## Rationalization counters

| Rationalization | Counter |
|---|---|
| “我有八成把握，先做更快。” | 概率不能替用户定义意图；material ambiguity 必须先分类。 |
| “先让 workers 看，之后再统一。” | fanout 会复制并放大未确认语义；先澄清或显式保留变量。 |
| “我只是采用常见含义。” | 常见含义不是用户授权；若另一合理解释改变结果，就不能静默选择。 |
| “以后可以修正。” | 候选淘汰、写入或外部动作已经改变结果；可回滚不等于 outcome-invariant。 |
| “看到歧义就先问最保险。” | clear 直接继续；branchable 保留分支继续。只有不可并存的 material ambiguity 才 blocking。 |

## Red flags

- 把“最可能的解释”写成“用户的目标”。
- 用 readiness blocker 整包否定 value/fit。
- 以“自主性”“少打扰”“先推进”为由跳过 blocking 提问。
- fanout 后才暴露会改变 worker scope 的歧义。
