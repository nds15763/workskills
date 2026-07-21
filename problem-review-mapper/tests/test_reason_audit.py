from pathlib import Path
import re
import unittest


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


class ReasonAuditContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def _update_blocks(self, text):
        updates = re.search(
            r"updates:\n(?P<body>.*?)(?=\n\nconfounders:)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(updates)
        return re.findall(
            r"^      - hypothesis:.*?(?=^      - hypothesis:|\Z)",
            updates.group("body"),
            re.DOTALL | re.MULTILINE,
        )

    def _assert_each_update_has_complete_reason_audit(self, text):
        blocks = self._update_blocks(text)
        self.assertGreaterEqual(len(blocks), 2)
        required = (
            'relation: "supports | contradicts | no_update"',
            'lr_bucket: "-- | - | 0 | + | ++"',
            'case_fit: "pass | fail | unknown"',
            "case_fit_reason:",
            'positive_fit: "strong | weak | unknown"',
            "positive_reason:",
            'contrast_fit: "strong | weak | none | unknown"',
            "contrast_reason:",
            "scope:",
            "confounder_refs:",
            'verdict: "valid_update | invalid | cannot_confirm"',
        )
        for index, block in enumerate(blocks):
            self.assertIn("reason_audit:", block, f"update[{index}]")
            for field in required:
                self.assertIn(field, block, f"update[{index}] missing {field}")

    def test_reason_audit_is_review_only_not_a_global_thinking_rule(self):
        self.assertIn("## 论因审计（因明 lens）", self.text)
        scope = re.search(
            r"### 触发范围\n(?P<body>.*?)(?=\n### |\n## |\Z)",
            self.text,
            re.DOTALL,
        )
        self.assertIsNotNone(scope)
        body = scope.group("body")
        self.assertRegex(body, r"review.*排查.*归因.*claim.*裁决")
        self.assertIn("不是所有 thinking", body)
        self.assertRegex(body, r"普通编码.*翻译.*机械任务")
        self.assertIn("只有列入关键 `E → H` 的 `updates` 项才强制审计", body)
        self.assertIn("其余证据更新不强制", body)

    def test_reason_audit_is_embedded_in_each_evidence_to_hypothesis_update(self):
        self._assert_each_update_has_complete_reason_audit(self.text)
        self.assertIn("E → H", self.text)

    def test_per_update_check_fails_if_second_audit_is_removed(self):
        blocks = self._update_blocks(self.text)
        self.assertGreaterEqual(len(blocks), 2)
        second_without_audit = re.sub(
            r"^        reason_audit:\n(?:^          .*\n?)+",
            "",
            blocks[1],
            count=1,
            flags=re.MULTILINE,
        )
        self.assertNotEqual(second_without_audit, blocks[1])
        mutated = self.text.replace(blocks[1], second_without_audit, 1)
        with self.assertRaises(AssertionError):
            self._assert_each_update_has_complete_reason_audit(mutated)

    def test_reason_audit_has_bounded_verdict_semantics(self):
        required_rules = (
            "verdict 优先级：invalid > cannot_confirm > valid_update",
            "case_fit=fail 无论其他字段为何，verdict=invalid",
            "case_fit=fail => verdict=invalid => relation=no_update, lr_bucket=0",
            "任一 fit=unknown（且未先命中 case_fit=fail）=> verdict=cannot_confirm => relation=no_update, lr_bucket=0",
            "contrast_fit=none => verdict=cannot_confirm => relation=no_update, lr_bucket=0",
            "contrast_fit=none 的优先级低于 invalid",
            "反例：case_fit=fail + contrast_fit=none => verdict=invalid",
            "relation=supports 只能使用 lr_bucket=+ / ++",
            "relation=contradicts 只能使用 lr_bucket=- / --",
            "relation=no_update 只能使用 lr_bucket=0",
            "不要求所有同类必现或所有异类必无",
            "只更新 H，不关闭 claim / gate",
        )
        for rule in required_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.text)

    def test_proxy_and_external_similar_cases_cannot_replace_current_target_evidence(self):
        self.assertIn("代理或外部相似案例不能替当前对象的 target evidence", self.text)


if __name__ == "__main__":
    unittest.main()
