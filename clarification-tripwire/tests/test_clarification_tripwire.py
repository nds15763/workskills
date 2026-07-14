#!/usr/bin/env python3
"""Contract tests for the clarification tripwire skill."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
FORWARD_TEST_PATH = Path(__file__).resolve().parent / "forward-test.md"


class ClarificationTripwireContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL_PATH.read_text(encoding="utf-8") if SKILL_PATH.exists() else ""
        cls.folded = cls.text.casefold()
        cls.fragments = [
            fragment.casefold()
            for fragment in [*cls.text.splitlines(), *re.split(r"\n\s*\n", cls.text)]
            if fragment.strip()
        ]

    def fragments_with(self, term: str) -> list[str]:
        return [fragment for fragment in self.fragments if term in fragment]

    def test_skill_document_exists(self) -> None:
        self.assertTrue(
            SKILL_PATH.is_file(),
            f"missing clarification-tripwire skill document: {SKILL_PATH}",
        )

    def test_distinguishes_blocking_branchable_and_non_blocking(self) -> None:
        requirements = {
            "blocking": (("提问", "澄清", "ask", "clarif"), ("暂停", "等待", "stop", "wait")),
            "branchable": (("分支", "双轴", "保留", "branch"), ("继续", "输出", "continue")),
            "non_blocking": (("假设", "assumption"), ("继续", "continue")),
        }
        problems: list[str] = []
        for disposition, action_groups in requirements.items():
            matching = self.fragments_with(disposition)
            if not matching:
                problems.append(f"missing disposition {disposition}")
                continue
            for alternatives in action_groups:
                if not any(any(term in fragment for term in alternatives) for fragment in matching):
                    problems.append(
                        f"{disposition} is missing action semantics: "
                        + " / ".join(alternatives)
                    )
        self.assertFalse(
            problems,
            "clarification dispositions must be operationally distinct:\n"
            + "\n".join(problems),
        )

    def test_contract_covers_material_conclusions_and_delivered_responses(self) -> None:
        self.assertTrue(
            "material conclusion" in self.folded
            and "delivered response" in self.folded,
            "tripwire must run before committing a material conclusion or delivered response, "
            "not only before tools or fanout",
        )

        frontmatter_end = self.folded.find("\n---", 4)
        frontmatter = self.folded[:frontmatter_end]
        self.assertIn("material conclusion", frontmatter)
        self.assertIn("delivered response", frontmatter)

    def test_context_lookup_is_separate_from_user_owned_semantics(self) -> None:
        requirements = (
            "bounded read-only lookup",
            "authoritative",
            "user-owned semantics",
            "permission",
            "optimization",
        )
        missing = [term for term in requirements if term not in self.folded]
        self.assertFalse(
            missing,
            "skill must allow bounded contextual disambiguation while reserving intent, "
            "values, permission, and optimization targets for the user: " + ", ".join(missing),
        )

    def test_clear_disposition_avoids_forced_clarification(self) -> None:
        matching = self.fragments_with("clear")
        self.assertTrue(
            any(
                any(term in fragment for term in ("no material ambiguity", "无实质歧义"))
                and any(term in fragment for term in ("without asking", "无需提问", "不提问"))
                and any(term in fragment for term in ("continue", "继续"))
                for fragment in matching
            ),
            "skill needs a clear/no-material-ambiguity path that continues without asking",
        )

    def test_non_blocking_requires_all_safety_bounds(self) -> None:
        matching = self.fragments_with("non_blocking")
        requirements = ("assumption", "cheap", "reversible", "outcome-invariant", "continue")
        missing = [
            term for term in requirements if not any(term in fragment for fragment in matching)
        ]
        self.assertFalse(
            missing,
            "non_blocking must keep every safety bound: " + ", ".join(missing),
        )

    def test_should_merge_keeps_value_fit_separate_from_readiness_risk(self) -> None:
        motivating_fragments = self.fragments_with("应该合入")
        self.assertTrue(
            motivating_fragments,
            "skill must include the motivating 应该合入 ambiguity",
        )
        context = "\n".join(motivating_fragments)
        self.assertIn(
            "value/fit",
            context,
            "应该合入 must preserve the value/fit interpretation",
        )
        self.assertIn(
            "readiness/risk",
            context,
            "应该合入 must preserve the readiness/risk interpretation",
        )
        self.assertTrue(
            any(term in context for term in ("不能", "不得", "不等于", "≠", "separate")),
            "skill must forbid collapsing value/fit into readiness/risk",
        )

    def test_high_quality_is_multi_axis_not_hygiene_only(self) -> None:
        fragments = self.fragments_with("高质量")
        self.assertTrue(fragments, "skill must include the motivating 高质量 ambiguity")
        context = "\n".join(fragments)
        self.assertTrue(
            any(term in context for term in ("多轴", "多个轴", "multi-axis")),
            "高质量 must be declared a multi-axis judgment",
        )
        self.assertTrue(
            any(term in context for term in ("卫生", "细节错误", "hygiene")),
            "高质量 example must name hygiene/detail correctness as only one axis",
        )
        self.assertTrue(
            any(term in context for term in ("价值", "独特", "适配", "收益", "value", "fit")),
            "高质量 example must retain substantive value/fit axes",
        )
        self.assertTrue(
            any(term in context for term in ("不只", "不能只", "不应只", "not only")),
            "skill must forbid reducing 高质量 to hygiene-only",
        )

    def test_fanout_freezes_only_confirmed_facts_and_retains_semantic_variables(self) -> None:
        matching = [
            fragment
            for fragment in self.fragments
            if "fanout" in fragment
            and any(term in fragment for term in ("冻结", "freeze"))
            and any(term in fragment for term in ("已确认", "confirmed"))
            and any(term in fragment for term in ("未确认", "未决", "unresolved"))
            and any(term in fragment for term in ("变量", "variable"))
            and any(term in fragment for term in ("保留", "retain", "preserve"))
        ]
        self.assertTrue(
            matching,
            "fanout must freeze confirmed facts only and retain unresolved semantic "
            "variables; it must not freeze a guessed interpretation",
        )

    def test_fanout_exposes_variables_and_collectively_covers_branches(self) -> None:
        matching = self.fragments_with("fanout")
        self.assertTrue(
            any(
                any(term in fragment for term in ("every worker prompt", "每个 worker prompt"))
                and any(term in fragment for term in ("unresolved semantic variable", "未决语义变量"))
                and any(term in fragment for term in ("collectively", "整体"))
                and any(term in fragment for term in ("every preserved branch", "每个保留分支"))
                and any(term in fragment for term in ("branch ownership", "分支 ownership", "分支归属"))
                and any(term in fragment for term in ("one owner by default", "默认一个 owner"))
                and any(term in fragment for term in ("independent verification", "独立验证"))
                for fragment in matching
            ),
            "every worker prompt must expose unresolved variables while the fanout "
            "collectively covers every branch with non-duplicated ownership except "
            "explicit independent verification",
        )

    def test_motivating_singular_shortlist_asks_before_fanout(self) -> None:
        start = self.folded.find("## motivating example")
        end = self.folded.find("\n## ", start + 4)
        section = self.folded[start : end if end != -1 else None]
        self.assertIn("singular shortlist", section)
        self.assertIn("blocking", section)
        self.assertTrue(any(term in section for term in ("ask one", "提一个")))
        self.assertTrue(any(term in section for term in ("wait", "等待")))
        self.assertTrue(any(term in section for term in ("before fanout", "fanout 前")))
        self.assertTrue(
            any(term in section for term in ("explicitly authorizes", "明确授权"))
            and "branchable" in section,
            "dual-axis continuation is branchable only after the user explicitly authorizes it",
        )

    def test_forward_test_evidence_records_red_and_green_samples(self) -> None:
        self.assertTrue(FORWARD_TEST_PATH.is_file(), "missing fresh-context forward-test evidence")
        evidence = FORWARD_TEST_PATH.read_text(encoding="utf-8").casefold()
        requirements = (
            "single-sample",
            "red baseline",
            "green prompt a",
            "green prompt b",
            "green prompt c",
            "not deterministic proof",
        )
        missing = [term for term in requirements if term not in evidence]
        self.assertFalse(missing, "forward-test evidence is incomplete: " + ", ".join(missing))


if __name__ == "__main__":
    unittest.main(verbosity=2)
