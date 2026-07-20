---
name: causal-evidence-rca
description: >-
  Use when an optional downstream after `problem-review-mapper` is needed for
  time-series, system-metric, or dependency-graph RCA requiring causal candidate
  structure, confounder calibration, discriminating probes, or bounded
  investigation priority.
---

# Causal Evidence RCA

Use this as a downstream technique after `workskills-router` has stabilized
the issue and `problem-review-mapper` has established competing hypotheses.
It produces bounded causal evidence for metric- and dependency-heavy RCA. It
does not replace generic routing, semantic ownership, project evidence policy,
or an independent final verifier.

## Non-negotiable boundary

Correlation, temporal precedence, a plausible story, and a recovered service
are different claims. **Mitigation is not confirmed RCA.** A rollback, cache
flush, restart, or traffic shift can be a verified mitigation while the cause
remains unknown.

PC, Granger, PageRank, and LLM-generated graphs are **replaceable evidence
producers**. They can generate candidate edges, predictions, or a bounded
investigation order; they cannot close the root-cause gate or establish
**confirmed root-cause truth**. Keep their assumptions and failure modes beside
their outputs.

## Investigation workflow

### 1. Bound the incident before drawing a graph

Write the observable symptom, affected population, time window, expected
behavior, and the currently verified mitigation status. Preserve at least two
competing explanations; include recent deploys, config changes, traffic shifts,
and observability changes as candidates or possible confounders.

Do not turn a dependency diagram or an LLM summary into an observed edge. Mark
it as `prior` until incident data or a controlled probe supports it.

### 2. Build candidate causal edges

For each candidate, state a directional, falsifiable claim:

```text
edge: A -> B
mechanism: why a change in A could produce B
time expectation: lag/order and affected scope
alternative: another candidate that could also produce B
status: prior | observed association | supported candidate | rejected
```

An edge is not a root cause. A chain is only as strong as its weakest untested
edge. Keep distinct candidates even when they share a symptom.

### 3. Classify evidence and confounders

Use these labels in the evidence ledger:

| Evidence classification | What it can support | What it cannot establish alone |
|---|---|---|
| `observation` | a measured fact in a named window | why it happened |
| `association` | co-movement, order, or prediction | causal direction or mechanism |
| `prior` | a plausible architecture, runbook, or LLM edge | incident behavior |
| `probe` | a measured result of a scoped intervention | claims outside the probed scope |
| `mitigation` | recovery after an action | that action's target was the root cause |
| `independent confirmation` | a tested mechanism that defeats alternatives | certainty beyond its stated scope |

Record **Confounders** explicitly: concurrent deploy/config changes, traffic or
seasonality, shared upstream dependencies, retries/backpressure, sampling
changes, clock skew, missing telemetry, and interventions that affect several
nodes. State which observation each confounder can imitate and how a probe
would control for it.

### 4. Write discriminating predictions and probes

For every leading candidate, write one expected observation if true, one
observation that would weaken it, and a low-risk probe that separates it from
the nearest alternative. Prefer a time- and cohort-aligned comparison,
canary/control contrast, replay, or narrow reversible intervention over a
global change.

If a production action is needed to restore service, label it mitigation first.
Only upgrade it to causal evidence when the intervention changed the proposed
cause, produced the predicted effect, and competing explanations were checked.

### 5. Prioritize investigation without declaring a winner

Set a **Bounded investigation priority** for the next probe, not a causal
ranking. Favor the smallest safe action with high expected discrimination,
adequate observability, and clear stop conditions. PageRank or Bayesian scores
may order where to inspect; they must carry the graph source, data window,
assumptions, and uncertainty.

### 6. Report gate status

Use a separate status for each claim:

| Gate status | Meaning | Required next step |
|---|---|---|
| `open` | symptom or mitigation is known, cause is not | collect a discriminating probe |
| `candidate` | an edge has bounded supporting evidence | test its mechanism and alternatives |
| `mitigated` | service recovery is verified | keep RCA open unless causal conditions hold |
| `confirmed` | mechanism, scope, alternatives, and confounders were independently addressed | record the evidence boundary and prevention action |
| `blocked` | decisive evidence is unavailable or unsafe to obtain | name the missing evidence and owner |

Do not write `confirmed` merely because PC/Granger found an edge, an LLM drew a
graph, PageRank ranked a node first, or a mitigation worked.

## Compact example

**Symptom:** checkout 5xx rose from 10:02–10:20; a Redis restart at 10:18 was
followed by recovery.

| Item | Bounded result |
|---|---|
| Candidate causal edges | `Redis eviction -> cache miss -> MySQL saturation -> 5xx`; `10:00 connection-pool deploy -> MySQL saturation -> 5xx` |
| Evidence classification | Redis eviction and 5xx dashboards are `observation`; their ordering is `association`; an LLM dependency graph is `prior`; recovery after restart is `mitigation` |
| Confounders | The pool deploy overlaps the incident; retry traffic can inflate both cache misses and MySQL load |
| Discriminating predictions and probes | Compare canary vs non-canary pool settings; inspect eviction/miss lag by shard; replay the candidate pool setting against a controlled baseline |
| Bounded investigation priority | First compare deploy cohorts because it separates both candidates cheaply; do not use reverse PageRank as a verdict |
| Gate status | `mitigated`, RCA `open` until the predicted intervention result and alternatives are independently checked |

## Quick reference

| Method | Use it to produce | Keep this boundary |
|---|---|---|
| PC / constraint discovery | candidate conditional-dependence structure | hidden confounders, selection bias, and violated assumptions can orient edges wrongly |
| Granger | a predictive lead/lag candidate | improved prediction is not causality |
| Bayesian scoring | explicit belief updates under declared assumptions | a posterior inherits the graph and prior errors |
| PageRank / reverse traversal | an inspection order on a supplied graph | rank is not causal proof |
| LLM graph extraction | architecture/runbook priors and missing-edge questions | generated relations need data or probe validation |

## Common mistakes

- Collapse correlated Redis, database, and gateway metrics into a confirmed chain.
- Treat an LLM graph plus PageRank as proof and greenlight the RCA.
- Call PC or Granger output causality while a deploy, traffic shift, or telemetry
  change can explain both signals.
- Close RCA after a successful restart or rollback without testing the predicted
  mechanism or alternatives.
- Hide unavailable telemetry; use `blocked` with a named evidence gap instead.
