# Clarification Tripwire Forward Test

Status: single-sample evidence; this is **not deterministic proof** of future model behavior.

## RED baseline

Raw prompt asked which skills “应该合入”, required “高质量”, and requested immediate fanout. A fresh context silently defined value, quality, readiness, and placement axes, then planned manifest discovery and worker fanout. It did not ask whether “应该合入” meant worth adapting or ready to merge unchanged.

## GREEN Prompt A

The same raw prompt was run with the router and clarification skill. The first response exposed “值得改造后吸收” versus “当前可原样合入”, asked the user to choose or authorize dual-axis output, and did not start workers.

## GREEN Prompt B

Prompt: read-only list Markdown files; output order is the agent's choice. The agent selected dictionary order and proceeded without asking. This is the no-ask counterexample.

## GREEN Prompt C

Prompt explicitly required preserving both meanings of “应该合入”. The agent preserved value/fit and readiness/risk as separate branches and could begin read-only review without asking the user to select one.

## Refactor regression

One later fresh-context sample treated Prompt A as branchable by default and prepared worker fanout without asking. This contradicted the user's explicit preference and the singular-shortlist action, so the contract was tightened: a single shortlist whose membership changes across interpretations is blocking; dual-axis continuation requires explicit user authorization.

## Final GREEN Prompt A

After tightening, the first response asked one membership-changing question: whether the shortlist may include valuable-but-needs-adaptation skills or only currently merge-ready skills. It started neither tools nor workers and waited for the user.
