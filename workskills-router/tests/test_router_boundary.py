#!/usr/bin/env python3
"""Regression guardrails for keeping workskills-router project-neutral."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
HOOKS_PATH = Path(__file__).resolve().parents[1] / "references" / "calibration-hooks.md"


def markdown_table_blocks(lines: list[str]) -> list[list[str]]:
    """Return contiguous, valid Markdown pipe-table blocks."""
    candidates: list[list[str]] = []
    current: list[str] = []
    for line in [*lines, ""]:
        if re.fullmatch(r"\s*\|.*\|\s*", line):
            current.append(line)
            continue
        if current:
            candidates.append(current)
            current = []

    separator_cell = re.compile(r"^:?-{3,}:?$")
    return [
        block
        for block in candidates
        if len(block) >= 2
        and all(
            separator_cell.fullmatch(cell.strip())
            for cell in block[1].strip().strip("|").split("|")
        )
    ]


class RouterBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL_PATH.read_text(encoding="utf-8")
        cls.hooks_text = HOOKS_PATH.read_text(encoding="utf-8")
        cls.hooks_folded = cls.hooks_text.casefold()
        cls.folded = cls.text.casefold()
        cls.lines = cls.text.splitlines()
        cls.table_blocks = markdown_table_blocks(cls.lines)
        cls.paragraphs = [
            paragraph.casefold()
            for paragraph in re.split(r"\n\s*\n", cls.text)
            if paragraph.strip()
        ]

    def test_skill_stays_within_line_budget(self) -> None:
        self.assertLessEqual(
            len(self.lines),
            220,
            f"{SKILL_PATH} has {len(self.lines)} lines; maximum is 220",
        )

    def test_skill_contains_no_project_or_harness_leakage(self) -> None:
        forbidden = (
            "/Users/",
            "mewt",
            "sidecar",
            "run_id",
            "session_id",
            ".git/codex",
            "head_up",
            "crisis_threshold",
            "stability_score",
            "Concept Convergence Process",
        )
        hits: list[str] = []
        for needle in forbidden:
            matching_lines = [
                str(number)
                for number, line in enumerate(self.lines, start=1)
                if needle.casefold() in line.casefold()
            ]
            if matching_lines:
                hits.append(f"{needle!r} on line(s) {', '.join(matching_lines)}")

        self.assertFalse(
            hits,
            "project-specific or harness-specific content leaked into router:\n"
            + "\n".join(hits),
        )

    def test_router_explicitly_routes_without_replacing_downstream(self) -> None:
        routing_only_patterns = (
            r"只\s*负责[^。\n]{0,40}路由",
            r"(?:router|本\s*skill)[^.\n]{0,40}(?:only|solely)[^.\n]{0,40}rout",
        )
        downstream_patterns = (
            r"不[^。\n]{0,16}替代[^。\n]{0,60}(?:下游|具体)"
            r"[^。\n]{0,40}(?:skill|技能|方法|流程)",
            r"(?:does not|must not|never)[^.\n]{0,24}replace[^.\n]{0,60}"
            r"(?:downstream|selected|specialized)",
        )
        self.assertTrue(
            any(re.search(pattern, self.folded) for pattern in routing_only_patterns),
            "SKILL.md must explicitly say the router is only responsible for routing",
        )
        self.assertTrue(
            any(re.search(pattern, self.folded) for pattern in downstream_patterns),
            "SKILL.md must explicitly say the router does not replace downstream skills",
        )

    def test_evidence_form_is_project_decided_and_not_hardcoded(self) -> None:
        evidence_form_is_contextual = any(
            any(term in paragraph for term in ("证据形式", "证据形态", "evidence form"))
            and any(term in paragraph for term in ("goal", "目标"))
            and any(term in paragraph for term in ("project", "项目"))
            and any(term in paragraph for term in ("决定", "取决于", "determined"))
            for paragraph in self.paragraphs
        )
        no_router_hardcoding = any(
            any(term in paragraph for term in ("router", "路由层", "路由器"))
            and (
                re.search(r"(?:不|不会|不得)[^。\n]{0,24}硬编码", paragraph)
                or re.search(r"(?:does not|must not|never)[^.\n]{0,24}hard-?code", paragraph)
            )
            for paragraph in self.paragraphs
        )

        self.assertTrue(
            evidence_form_is_contextual,
            "SKILL.md must state that the evidence form is determined by the goal "
            "and project",
        )
        self.assertTrue(
            no_router_hardcoding,
            "SKILL.md must state that the router does not hard-code the evidence form",
        )

    def test_has_exactly_route_and_responsibility_tables(self) -> None:
        headers = [block[0] for block in self.table_blocks]
        problems: list[str] = []
        if len(self.table_blocks) != 2:
            problems.append(
                f"expected exactly 2 Markdown table blocks, found "
                f"{len(self.table_blocks)}: {headers}"
            )
        if not any("用户意图" in header and "主 skill" in header for header in headers):
            problems.append("missing the quick-routing table")
        if not any(
            "skill" in header.casefold() and "负责" in header and "不负责" in header
            for header in headers
        ):
            problems.append("missing the responsibility-boundary table")
        self.assertFalse(problems, "\n".join(problems))

    def test_decision_object_action_and_criteria_are_bullets(self) -> None:
        section_match = re.search(
            r"(?ms)^### 决策先行校准\s*$\n(.*?)(?=^### |^## |\Z)",
            self.text,
        )
        self.assertIsNotNone(section_match, "missing decision-calibration section")
        decision_section = section_match.group(1) if section_match else ""
        required_bullets = ("decision object", "requested action", "criteria axes")
        missing = [
            label
            for label in required_bullets
            if not re.search(
                rf"(?mi)^\s*[-*]\s+[^\n]*{re.escape(label)}",
                decision_section,
            )
        ]
        self.assertFalse(
            missing,
            "decision calibration must express these as bullets, not a table: "
            + ", ".join(missing),
        )

    def test_open_low_precedent_cross_domain_routes_to_review_mapper(self) -> None:
        routing_blocks = [
            block
            for block in self.table_blocks
            if "用户意图" in block[0] and "主 skill" in block[0]
        ]
        candidate_rows = [
            row.casefold()
            for block in routing_blocks
            for row in block[2:]
            if "problem-review-mapper" in row.casefold()
        ]
        matching_rows = [
            row
            for row in candidate_rows
            if "开放" in row
            and "低先例" in row
            and "跨域" in row
            and any(term in row for term in ("外部成熟解法", "类似方案"))
        ]
        self.assertTrue(
            matching_rows,
            "quick routing must send open/low-precedent/cross-domain requests "
            "for external mature solutions or similar approaches to "
            "problem-review-mapper",
        )

    def test_quick_routing_uses_only_resolvable_skill_names(self) -> None:
        routing_blocks = [
            block
            for block in self.table_blocks
            if "用户意图" in block[0] and "主 skill" in block[0]
        ]
        self.assertEqual(len(routing_blocks), 1, "expected one quick-routing table")
        routing_block = routing_blocks[0] if routing_blocks else []
        routing_text = "\n".join(routing_block).casefold()

        canonical_names = (
            "clarification-tripwire",
            "canonical-claim-compiler",
            "project-knowledge-curator",
            "project-wiki",
            "logical-grammar",
            "truth-condition-checker",
            "problem-review-mapper",
        )
        missing = [name for name in canonical_names if name not in routing_text]
        self.assertFalse(
            missing,
            "quick-routing table is missing full skill name(s): " + ", ".join(missing),
        )

        aliases = ("compiler", "curator", "wiki", "grammar", "mapper", "truth")
        alias_patterns = {
            alias: re.compile(
                rf"(?<![a-z0-9_-]){re.escape(alias)}(?![a-z0-9_-])",
                re.IGNORECASE,
            )
            for alias in aliases
        }
        table_start = self.lines.index(routing_block[0]) if routing_block else 0
        hits: list[str] = []
        for offset, row in enumerate(routing_block, start=0):
            found = [
                alias for alias, pattern in alias_patterns.items() if pattern.search(row)
            ]
            if found:
                hits.append(
                    f"line {table_start + offset + 1}: "
                    f"unresolvable alias(es) {', '.join(found)} in {row.strip()}"
                )
        self.assertFalse(
            hits,
            "quick-routing table must use complete, resolvable skill names:\n"
            + "\n".join(hits),
        )

    def test_uninstalled_tripwire_routes_have_guard_and_resolvable_fallback(self) -> None:
        installed_roots = (
            Path.home() / ".codex/skills",
            Path.home() / ".agents/skills",
        )
        installed_skills = {
            child.name.casefold()
            for root in installed_roots
            if root.is_dir()
            for child in root.iterdir()
            if child.is_dir() and (child / "SKILL.md").is_file()
        }

        routing_blocks = [
            block
            for block in self.table_blocks
            if "用户意图" in block[0] and "主 skill" in block[0]
        ]
        self.assertEqual(len(routing_blocks), 1, "expected one quick-routing table")
        routing_rows = routing_blocks[0][2:] if routing_blocks else []

        problems: list[str] = []
        for tripwire in ("clarification-tripwire", "decision-tripwire"):
            matching_rows = [row for row in routing_rows if tripwire in row.casefold()]
            if len(matching_rows) != 1:
                problems.append(
                    f"expected exactly one route row for {tripwire}, found {len(matching_rows)}"
                )
                continue
            if tripwire in installed_skills:
                continue

            row = matching_rows[0]
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            primary_cell = cells[1].casefold() if len(cells) > 1 else ""
            fallback_cell = cells[2].casefold() if len(cells) > 2 else ""
            has_availability_guard = bool(
                re.search(
                    r"(?:仅|只).{0,16}(?:环境|skill|技能)?.{0,12}可用时"
                    r"|(?:only|when|if).{0,12}available",
                    primary_cell,
                    re.I,
                )
            )
            fallback_targets = sorted(
                skill
                for skill in installed_skills
                if skill != tripwire and skill in fallback_cell
            )
            if not has_availability_guard:
                problems.append(
                    f"uninstalled {tripwire} route lacks an inline availability guard"
                )
            if not fallback_targets:
                problems.append(
                    f"uninstalled {tripwire} route lacks a fallback to an installed skill"
                )

        self.assertFalse(
            problems,
            "unavailable tripwire routes must fail closed at the routing row:\n"
            + "\n".join(problems),
        )

    def test_material_semantic_ambiguity_routes_to_clarification_before_action(self) -> None:
        routing_blocks = [
            block
            for block in self.table_blocks
            if "用户意图" in block[0] and "主 skill" in block[0]
        ]
        self.assertEqual(len(routing_blocks), 1, "expected one quick-routing table")
        rows = [row.casefold() for row in routing_blocks[0][2:]] if routing_blocks else []
        matching_rows = [
            row
            for row in rows
            if "clarification-tripwire" in row
            and any(term in row for term in ("歧义", "ambiguity"))
            and any(term in row for term in ("改变", "影响", "material"))
            and any(term in row for term in ("结果", "行动", "动作", "结论", "outcome", "action"))
        ]
        self.assertTrue(
            matching_rows,
            "quick routing must send material semantic ambiguity that changes an "
            "outcome or action to clarification-tripwire",
        )

        pre_action_contract = any(
            "clarification-tripwire" in paragraph
            and any(term in paragraph for term in ("歧义", "ambiguity"))
            and "fanout" in paragraph
            and any(term in paragraph for term in ("执行", "execution"))
            and any(term in paragraph for term in ("前", "before"))
            for paragraph in self.paragraphs
        )
        self.assertTrue(
            pre_action_contract,
            "router must invoke clarification-tripwire before execution and fanout "
            "when material semantic ambiguity remains",
        )

    def test_calibration_hooks_declare_clarification_before_fanout_and_execution(self) -> None:
        fanout_match = re.search(
            r"(?ms)^### 2\. fanout.*?$(.*?)(?=^### |\Z)",
            self.hooks_text,
        )
        execution_match = re.search(
            r"(?ms)^### 3\. subtask exec.*?$(.*?)(?=^### |\Z)",
            self.hooks_text,
        )
        problems: list[str] = []
        for stage, match in (("fanout", fanout_match), ("subtask exec", execution_match)):
            if match is None:
                problems.append(f"missing {stage} hook section")
                continue
            section = match.group(1).casefold()
            if "clarification-tripwire" not in section:
                problems.append(f"{stage} does not invoke clarification-tripwire")
            if not any(term in section for term in ("歧义", "ambiguity")):
                problems.append(f"{stage} does not declare semantic ambiguity input")
            if not any(term in section for term in ("先", "before", "不得", "暂停", "等待")):
                problems.append(f"{stage} does not block action until clarification")
        self.assertFalse(
            problems,
            "calibration hooks must enforce clarification before fanout/execution:\n"
            + "\n".join(problems),
        )

    def test_calibration_hooks_cover_direct_main_agent_pre_execution(self) -> None:
        hooks = self.hooks_text.casefold()
        self.assertIn(
            "pre-execution",
            hooks,
            "hook contract needs a direct main-agent pre-execution trigger",
        )
        lines = [line.casefold() for line in self.hooks_text.splitlines()]
        matrix_lines = [line for line in lines if "clarification-tripwire" in line and "|" in line]
        self.assertTrue(matrix_lines, "hook matrix must include clarification-tripwire")
        self.assertTrue(
            any(line.count("✓") >= 3 for line in matrix_lines),
            "clarification-tripwire must cover pre-execution, fanout, and subtask execution",
        )

    def test_fanout_freezes_confirmed_facts_not_unresolved_semantics(self) -> None:
        fanout_contract = any(
            "fanout" in paragraph
            and any(term in paragraph for term in ("冻结", "freeze"))
            and any(term in paragraph for term in ("已确认", "confirmed"))
            and any(term in paragraph for term in ("未确认", "未决", "unresolved"))
            and any(term in paragraph for term in ("变量", "variable"))
            and any(term in paragraph for term in ("保留", "retain", "preserve"))
            for paragraph in self.paragraphs
        )
        self.assertTrue(
            fanout_contract,
            "fanout contract must freeze confirmed facts only and preserve unresolved "
            "semantic variables instead of silently choosing an interpretation",
        )

    def test_preserves_cross_project_semantic_guards(self) -> None:
        semantic_guards = {
            "pre-fanout decision calibration": (
                "fanout" in self.folded
                and "decision object" in self.folded
                and "requested action" in self.folded
                and "criteria axes" in self.folded
                and bool(re.search(r"(?:执行|execution)[^。\n]{0,20}(?:前|before)", self.folded))
            ),
            "value/fit differs from readiness/risk": (
                "value/fit" in self.folded
                and "readiness/risk" in self.folded
                and "≠" in self.text
            ),
            "blocker is scoped to its direct axis": bool(
                re.search(r"blocker[^。\n]{0,30}(?:只|only)[^。\n]{0,30}(?:轴|axis)", self.folded)
            ),
            "correlation differs from established cause": (
                "correlation" in self.folded
                and "established cause" in self.folded
                and "≠" in self.text
            ),
            "proxy evidence differs from target evidence": (
                "proxy evidence" in self.folded
                and "target evidence" in self.folded
                and "≠" in self.text
            ),
            "maker differs from verifier": (
                "maker" in self.folded and "verifier" in self.folded and "≠" in self.text
            ),
            "external priors are classified": all(
                term in self.folded for term in ("prior", "adopt", "reject", "pending")
            ),
            "abstract loop phases stay ordered": bool(
                re.search(
                    r"issue\s*→\s*internal/external intake\s*→\s*"
                    r"candidates/evidence update\s*→\s*action\s*→\s*reflection",
                    self.folded,
                )
            ),
        }
        missing = [name for name, present in semantic_guards.items() if not present]
        self.assertFalse(
            missing,
            "missing cross-project semantic guard(s): " + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
