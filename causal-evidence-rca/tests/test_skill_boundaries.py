from pathlib import Path
import re
import unittest


SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"


class CausalEvidenceRcaSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_declares_the_required_investigation_outputs(self):
        for section in (
            "Candidate causal edges",
            "Evidence classification",
            "Confounders",
            "Discriminating predictions and probes",
            "Bounded investigation priority",
            "Gate status",
        ):
            with self.subTest(section=section):
                self.assertIn(section, self.text)

    def test_description_is_a_bounded_downstream_trigger(self):
        match = re.search(
            r"^---\nname: causal-evidence-rca\ndescription: >-\n"
            r"(?P<body>(?:  .*\n)+)---",
            self.text,
        )
        self.assertIsNotNone(match)
        description = " ".join(
            line.strip() for line in match.group("body").splitlines()
        )
        self.assertTrue(description.startswith("Use when "))
        self.assertIn(
            "optional downstream after `problem-review-mapper`", description
        )
        self.assertLess(len(description), 500)

    def test_separates_mitigation_from_confirmed_root_cause(self):
        self.assertIn("Mitigation is not confirmed RCA", self.text)
        self.assertIn("confirmed root-cause truth", self.text)

    def test_keeps_algorithm_outputs_as_bounded_evidence(self):
        self.assertIn("PC, Granger, PageRank, and LLM-generated graphs", self.text)
        self.assertRegex(self.text, r"replaceable evidence\s+producers")
        self.assertIn("cannot close the root-cause gate", self.text)


if __name__ == "__main__":
    unittest.main()
