# Clarification Tripwire Design

## Goal

Prevent an agent from silently collapsing a materially ambiguous user request into one narrow interpretation before execution or fanout.

## Core contract

Before execution, candidate elimination, or fanout, the agent performs a counterfactual interpretation check:

1. Write two reasonable interpretations of the user request when they exist.
2. Compare whether they change the decision object, requested action, criteria axes, candidate inclusion, worker instructions, write scope, or external effect.
3. If they materially diverge, do not choose one silently.

The outcome is typed as one of:

- `blocking`: ask one concise clarification question and wait.
- `branchable`: preserve both interpretations and return both branches; do not eliminate candidates on either unresolved axis.
- `non_blocking`: proceed only when the assumption is reversible, cheap, and cannot change the user's requested outcome; state the assumption.

Bayesian or confidence-based reasoning cannot resolve a user-owned semantic choice. It may rank factual hypotheses inside a confirmed interpretation, but it cannot select the interpretation itself.

## Fanout behavior

Fanout freezes only confirmed shared facts. Unresolved semantic variables remain explicit in every worker prompt. If ambiguity is `blocking`, no worker starts. If it is `branchable`, the fanout collectively covers every preserved branch with explicit branch ownership. Each branch has one owner by default; duplication is reserved for an explicit independent-verification lane.

For the motivating prompt, `应该合入` must preserve at least:

- value/fit: worth absorbing, possibly after adaptation;
- readiness/risk: safe to merge unchanged now.

`高质量` must not collapse to hygiene. Evaluation must keep core value, distinctiveness, team benefit, correctness, adaptation cost, and readiness separable.

## Integration

- Add `clarification-tripwire/SKILL.md` as the reusable discipline skill.
- Route materially ambiguous requests to it from `workskills-router/SKILL.md`.
- Add pre-execution and pre-fanout interception rules to `workskills-router/references/calibration-hooks.md`.
- Add scenario-level static contract tests and forward-test the raw prompt in a fresh context.

## Non-goals

- Do not ask about harmless implementation details that are reversible and outcome-invariant.
- Do not replace `decision-tripwire`; it still handles option selection without a winning criterion.
- Do not let clarification become an excuse to stop when both branches can be preserved cheaply.
- Do not claim a Markdown skill guarantees model behavior; deployment requires forward-test evidence.

## Acceptance

Given the motivating prompt, the first action must expose the value/fit versus readiness/risk interpretation fork and ask the user, or preserve both axes without excluding candidates. It must happen before any fanout or substantive recommendation.
