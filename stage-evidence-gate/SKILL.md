---
name: stage-evidence-gate
description: Use when a multi-step workflow, visible outcome, E2E result, generated artifact, or human-observed phenomenon needs to be checked against the intended shared concept/claim; completion alone is not proof.
---

# Stage Evidence Gate

## Overview

Use this skill when the question is not "did something run?", but:

```text
Did the visible result, the user's intended concept, and the system's evidence actually refer to the same thing?
```

The skill is a method for cross-language evidence alignment. It must not encode project-specific business rules, implementation vocabulary, field names, log names, file paths, tools, or fixed E2E shapes.

Core rule:

```text
A step is not accepted until its user-facing meaning, shared claim, evidence surface, and failure mode are explicit.
```

## Language Layers

Always separate three layers before choosing evidence:

| Layer | Question | Examples |
|---|---|---|
| User phenomenon | What did the user see, expect, doubt, or feel was wrong? | "It looks broken", "the result did not show up", "E2E passed but I do not know what it proved" |
| Shared concept / claim | What would have to be true for that phenomenon to count as correct? | "the result is traceable", "this step handed usable evidence to the next step", "the visible output matches the intended object" |
| Evidence projection | What observable signs can support or refute that claim in this project? | A screenshot, report, trace, test assertion, stored record, generated file, manual observation, metric, or log line |

Do not let evidence projection words replace the shared concept. A file, row, URL, green test, trace, or screenshot is only evidence for a claim; it is not the claim itself.

## Boundary

This skill defines method, not domain logic.

| Belongs here | Belongs in current goal / spec / runbook |
|---|---|
| How to translate user phenomenon into a shared concept | Actual product terms and business objects |
| How to choose evidence surfaces | Exact tools, commands, field names, screenshots, tables, files, log lines |
| How to distinguish target evidence from proxy evidence | Project-specific pass/fail thresholds |
| How to preserve example lessons without copying the example | Concrete example shapes such as fishbone/video/frame/sticker/game flows |
| How to update uncertainty after new evidence | Exact priors, test data, and rollout-specific decisions |

## Evidence Loop

For any multi-step or visible-result workflow:

1. Record the user's phenomenon in their language.
2. Rewrite it as a shared concept or claim.
3. Name the relationship to check: sequence, handoff, transformation, visibility, persistence, explanation, or another relation from the current goal.
4. Choose only the evidence surfaces needed for this claim.
5. Mark each surface as target evidence, proxy evidence, or missing evidence.
6. State what would support the claim and what would refute it.
7. Add or inspect the smallest evidence that can change the judgment.
8. Update every competing explanation, not only the favored one.
9. Reconcile the selected evidence surfaces.
10. Stop, reroute, or declare a gap.

Do not rerun a long happy path unless you can say what belief it should change.

## Minimal Templates

Goal contract:

```md
User phenomenon:
<what the user sees / expects / doubts>

Shared concept / claim:
<what must be true for this to count as correct>

Relationship under test:
<sequence / handoff / transformation / visibility / persistence / explanation / other>

Evidence surfaces:
| Surface | Target / Proxy / Missing | What it can prove | What it cannot prove |
|---|---|---|---|
| <surface> | <type> | <support> | <boundary> |

Failure modes:
- <what would refute the claim>

Stop / reroute conditions:
- <condition>
```

Evidence ledger:

```md
route: workskills-router -> stage-evidence-gate -> <evidence surface>
user phenomenon: <in user language>
shared claim: <claim being checked>
competing explanation: <what else could explain the same phenomenon>
expected update: <what would raise/lower belief>
evidence action: <inspect / run / observe / ask / compare>
```

After evidence:

```md
observed:
what changed:
still not proven:
next gate:
```

## Snapshot Shape

When the workflow has multiple steps, a snapshot can help. This is a reporting shape, not a project schema, E2E harness standard, or code template.

```md
| Step | User meaning | Input meaning | Output meaning | Missing / rejected | Evidence verdict | Next allowed? |
|---|---|---|---|---|---|---|
| <step> | <human concept> | <what this step receives> | <what this step must hand off> | <gap> | right / wrong / absent / ambiguous | yes / no + reason |
```

Use the project's own names only inside the current evidence plan, never as a universal rule.

## Example Boundary

Examples are allowed only as lenses.

For example, a "fishbone" video-processing story may teach portable practices:

- break a visible result into intermediate claims;
- keep handoffs traceable;
- separate target evidence from proxy evidence;
- define counterexamples before accepting a step;
- keep missing evidence as a gap instead of pretending it passed.

But the example's concrete shape is not a rule. Do not require every workflow to have frames, crops, embeddings, poses, storage rows, or any other example-specific object. Carry forward the practice, not the case.

## Evidence Rules

- User-visible meaning comes before implementation evidence.
- A proxy can support a claim but cannot close it by itself.
- A final result does not prove intermediate relationships unless the selected evidence surfaces can explain the relationship.
- Evidence predicted by all explanations does not change belief.
- Missing evidence is a gap, not a pass.
- A surprising positive result is also evidence; treat it as feedback that may update the user's concept, not only as a bug or success.
- If no observable evidence surface exists for an important claim, add an evidence surface or mark the claim unverified.

## Report Shape

```md
Verdict:
confirmed / leading / weakened / pending / gap

Concept alignment:
| User phenomenon | Shared claim | Evidence surface | Target or proxy | Verdict |

Competing explanations:
| Explanation | Prior | Evidence update | Status |

Reconciliation:
<which surfaces agree, which diverge, and what remains unproven>

Next test:
<smallest evidence-producing action>
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating a green E2E result as final truth | State which user phenomenon and claim it covers, and which it does not cover |
| Putting project-specific objects into the skill | Move them to the current goal/spec/evidence plan |
| Letting implementation words replace user concepts | Translate back to the shared concept before deciding |
| Trusting a visible or generated output just because it exists | Give it a verdict against the user-facing claim |
| Accepting one plausible cause | Keep competing explanations until evidence separates them |
| Checking whatever is easiest | Check the surface that can change the judgment |
| Copying an example as a universal template | Extract portable practices and discard the example shape |
