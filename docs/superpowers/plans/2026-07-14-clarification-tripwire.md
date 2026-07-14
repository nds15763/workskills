# Clarification Tripwire Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested clarification gate that prevents silent semantic collapse before execution and fanout.

**Architecture:** A focused `clarification-tripwire` skill owns the interpretation-fork protocol. The router owns discovery/routing, while calibration hooks enforce pre-execution and pre-fanout interception. Static contract tests protect the documents; fresh-context prompt runs provide behavioral evidence.

**Tech Stack:** Markdown agent skills, Python `unittest`, fresh-context subagent forward tests.

---

### Task 1: RED scenario contracts

**Files:**
- Create: `clarification-tripwire/tests/test_clarification_tripwire.py`
- Modify: `workskills-router/tests/test_router_boundary.py`

- [ ] Add a failing test that requires the new skill to distinguish `blocking`, `branchable`, and `non_blocking` outcomes.
- [ ] Add a failing router test requiring materially ambiguous requests to route to `clarification-tripwire` before execution or fanout.
- [ ] Add a failing scenario assertion for `应该合入`: value/fit must remain separate from readiness/risk, and `高质量` must not equal hygiene alone.
- [ ] Run `python3 clarification-tripwire/tests/test_clarification_tripwire.py` and `python3 workskills-router/tests/test_router_boundary.py`; confirm failure is caused by the missing skill and missing route.

### Task 2: GREEN discipline skill

**Files:**
- Create: `clarification-tripwire/SKILL.md`

- [ ] Write minimal frontmatter whose description triggers on multiple reasonable interpretations, conflicting goals, unclear scope, and semantic choices that change actions or outcomes.
- [ ] Define the counterfactual interpretation test and the three typed outcomes.
- [ ] Require one concise user question for `blocking`; require branch preservation for `branchable`; allow declared assumptions only for reversible outcome-invariant details.
- [ ] Include the `应该合入` example and explicit rationalization counters such as “the likely meaning is obvious” and “fanout can decide later.”
- [ ] Run the new skill test and confirm it passes.

### Task 3: Router and hook integration

**Files:**
- Modify: `workskills-router/SKILL.md`
- Modify: `workskills-router/references/calibration-hooks.md`

- [ ] Add the no-silent-semantic-collapse invariant next to decision-first calibration.
- [ ] Add a quick-routing row and responsibility boundary for `clarification-tripwire` without duplicating its full workflow.
- [ ] Add pre-execution and pre-fanout interception conditions that block worker launch when interpretations materially diverge.
- [ ] Specify that fanout freezes confirmed facts only and carries unresolved branch variables into worker prompts.
- [ ] Run both Python test files and confirm all tests pass.

### Task 4: Behavioral verification and review

**Files:**
- Verify: `clarification-tripwire/SKILL.md`
- Verify: `workskills-router/SKILL.md`
- Verify: `workskills-router/references/calibration-hooks.md`
- Verify: both Python test files

- [ ] Re-run the raw motivating prompt in a fresh context with the new skill and record whether the first action occurs before fanout.
- [ ] Run counterexamples: a reversible outcome-invariant detail must proceed with a declared assumption; a report-only task that can preserve both branches must not block unnecessarily.
- [ ] Have an independent reviewer check spec compliance, scope, dirty-worktree preservation, and whether static tests overclaim behavioral proof.
- [ ] Run `git diff --check` and inspect the final diff without staging unrelated files.
