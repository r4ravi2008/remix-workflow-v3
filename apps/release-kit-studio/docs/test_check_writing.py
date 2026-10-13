#!/usr/bin/env python3
"""Focused standard-library probes for the maintained writing corpus boundary."""

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[3]
CHECKER_PATH = REPO_ROOT / "apps" / "release-kit-studio" / "docs" / "check-writing.py"
FIXTURE_TEXT = """# Strict checker fixture

The audio timing remains stable.

Audio timing and visual timing remain linked.

The operator is running the check.

The old sentence changed.

The audit records source timing, frame mapping, color values, audio level, output format, release identity, reviewer state, and exact evidence path for each document entry.

The file can't open.

The quasar token remains in the record.
"""
CLEAN_FIXTURE_TEXT = "The file exists.\n"

spec = importlib.util.spec_from_file_location("project_writing_checker", CHECKER_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load {CHECKER_PATH}")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def approval(warning, occurrence_count=1):
    return {
        "file": warning["file"],
        "sentence": warning["sentence"],
        "word": warning["word"],
        "occurrenceCount": occurrence_count,
        "kind": "technical-name",
        "conceptDefinition": "the time relation between events",
        "reason": "The sentence uses the word as a named technical concept.",
    }


class WritingCheckerMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_dir = os.environ.get("STE_SKILL_DIR")
        if not cls.skill_dir:
            raise RuntimeError("STE_SKILL_DIR must point to the configured pinned STE skill")
        cls.upstream, cls.word_list, _ = checker.import_upstream(None)
        cls.project = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.project.cleanup)
        cls.repository = Path(cls.project.name).resolve()
        cls.app = cls.repository / "apps" / "release-kit-studio"
        cls.fixture_path = cls.app / "docs" / "fixture.md"
        cls.clean_fixture_path = cls.app / "docs" / "clean-fixture.md"
        cls.fixture_path.parent.mkdir(parents=True, exist_ok=True)
        cls.fixture_path.write_text(FIXTURE_TEXT, encoding="utf-8")
        cls.clean_fixture_path.write_text(CLEAN_FIXTURE_TEXT, encoding="utf-8")
        cls.fixture = "apps/release-kit-studio/docs/fixture.md"
        cls.clean_fixture = "apps/release-kit-studio/docs/clean-fixture.md"
        (
            cls.raw_errors,
            cls.raw_warnings,
            cls.warnings,
            cls.vocabulary,
        ) = cls.run_fixture()

    @classmethod
    def run_fixture(cls):
        with patch.object(checker, "REPO_ROOT", cls.repository), patch.object(
            checker, "APP_ROOT", cls.app
        ):
            return checker.run_upstream(cls.upstream, cls.word_list, [cls.fixture])

    def test_exact_archive_prefixes_are_excluded_and_reported(self):
        self.assertEqual(
            ["docs/archive", "native-editor/docs/archive"],
            [prefix.as_posix() for prefix in checker.ARCHIVE_PREFIXES],
        )
        self.assertTrue(checker.archive_excluded(Path("docs/archive/2026-10-05/old.md")))
        self.assertTrue(
            checker.archive_excluded(Path("native-editor/docs/archive/2026-10-05/old.md"))
        )
        self.assertFalse(checker.archive_excluded(Path("docs/archive-old/active.md")))
        self.assertFalse(
            checker.archive_excluded(Path("native-editor/docs/reference/archive/active.md"))
        )

        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve()
            app = repository / "apps" / "release-kit-studio"
            paths = {
                "docs/archive/2026-10-05/old.md": "archived app record",
                "native-editor/docs/archive/2026-10-05/old.md": "archived native record",
                "docs/archive-old/active.md": "active app record",
                "native-editor/docs/reference/archive/active.md": "active native record",
            }
            for relative, contents in paths.items():
                path = app / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")

            with patch.object(checker, "REPO_ROOT", repository), patch.object(
                checker, "APP_ROOT", app
            ):
                discovered = checker.discover_corpus()

        self.assertIn("apps/release-kit-studio/docs/archive-old/active.md", discovered)
        self.assertIn(
            "apps/release-kit-studio/native-editor/docs/reference/archive/active.md",
            discovered,
        )
        self.assertNotIn("apps/release-kit-studio/docs/archive/2026-10-05/old.md", discovered)
        self.assertNotIn(
            "apps/release-kit-studio/native-editor/docs/archive/2026-10-05/old.md",
            discovered,
        )
        self.assertEqual(
            ["docs/archive", "native-editor/docs/archive"],
            checker.result_template(discovered)["corpus"]["archiveRoots"],
        )

    def test_archived_approval_is_rejected_as_noncorpus(self):
        archived = (
            "apps/release-kit-studio/native-editor/docs/archive/2026-10-05/"
            "docs/ARCHITECTURE.md"
        )
        normalized, error = checker.validate_repository_file(archived, {archived})
        self.assertIsNone(normalized)
        self.assertIn("maintained Markdown corpus", error)

        record = approval(
            {
                "file": archived,
                "sentence": "The archived sentence remains historical.",
                "word": "historical",
            }
        )
        key, failures = checker.validate_record(record, 0, {archived})
        self.assertIsNone(key)
        self.assertTrue(any(category in {"invalid-record", "unsafe-path"} for category, _ in failures))

    def test_exact_approval_does_not_hide_stale_or_other_diagnostics(self):
        timing = next(item for item in self.warnings if item["word"] == "timing")
        repeated = [
            item
            for item in self.warnings
            if item["sentence"] == "Audio timing and visual timing remain linked."
        ]
        running = next(item for item in self.warnings if item["word"] == "running")
        long_sentence = next(item for item in self.warnings if item["rule"] == "5.1")

        resolved = checker.review_approvals(
            [(checker.record_key(approval(timing)), approval(timing), 0)], [timing]
        )
        self.assertEqual(1, len(resolved["resolved"]))

        stale = checker.review_approvals(
            [(checker.record_key(approval(timing)), approval(timing), 0)],
            [{**timing, "sentence": "The old sentence changed."}],
        )
        self.assertTrue(any(item["category"] == "unused-stale-approval" for item in stale["failures"]))

        count_mismatch = checker.review_approvals(
            [(checker.record_key(approval(repeated[0])), approval(repeated[0]), 0)], repeated
        )
        self.assertTrue(any(item["category"] == "count-mismatch" for item in count_mismatch["failures"]))

        duplicate = checker.review_approvals(
            [
                (checker.record_key(approval(timing)), approval(timing), 0),
                (checker.record_key(approval(timing)), approval(timing), 1),
            ],
            [timing],
        )
        self.assertTrue(any(item["category"] == "duplicate-approval" for item in duplicate["failures"]))

        unresolved = checker.review_approvals([], [running])
        self.assertEqual([running], unresolved["unresolved"])
        self.assertTrue(any(item["category"] == "unresolved-warning" for item in unresolved["failures"]))

        long_result = checker.review_approvals([], [long_sentence])
        self.assertTrue(any(item["category"] == "long-sentence-warning" for item in long_result["failures"]))
        self.assertTrue(self.raw_errors)
        self.assertTrue(self.raw_warnings)
        self.assertIn("quasar", self.vocabulary)

    def test_strict_record_schema_and_dictionary_pin_remain_enforced(self):
        timing = next(item for item in self.warnings if item["word"] == "timing")
        def validate(record):
            with patch.object(checker, "REPO_ROOT", self.repository), patch.object(
                checker, "APP_ROOT", self.app
            ):
                return checker.validate_record(record, 0, {self.fixture})

        valid_key, valid_failures = validate(approval(timing))
        self.assertEqual(checker.record_key(approval(timing)), valid_key)
        self.assertEqual([], valid_failures)

        invalid = {**approval(timing), "extra": "reject"}
        key, failures = validate(invalid)
        self.assertIsNone(key)
        self.assertTrue(any(category == "invalid-record" for category, _ in failures))

        for field in ("sentence", "conceptDefinition", "reason"):
            empty = approval(timing)
            empty[field] = ""
            key, failures = validate(empty)
            self.assertIsNone(key)
            self.assertTrue(any(category == "invalid-record" for category, _ in failures))

        for count in (0, -1, True, 1.0):
            invalid_count = approval(timing, count)
            key, failures = validate(invalid_count)
            self.assertIsNone(key)
            self.assertTrue(any(category == "invalid-record" for category, _ in failures))

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "approvals.json"
            path.write_text(json.dumps({"schemaVersion": 1}), encoding="utf-8")
            records, failures = checker.load_approvals(path, {self.fixture})
        self.assertEqual([], records)
        self.assertTrue(any(item["category"] == "invalid-record" for item in failures))

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text('{"schemaVersion": 1, "schemaVersion": 1}', encoding="utf-8")
            with self.assertRaises(checker.CheckerFailure) as failure:
                checker.load_approvals(path, {self.fixture})
        self.assertEqual("approvals-file", failure.exception.category)

        with patch.object(checker, "EXPECTED_STE_SHA256", "0" * 64):
            with self.assertRaises(checker.CheckerFailure) as failure:
                checker.import_upstream(None)
        self.assertEqual("upstream-checker-hash", failure.exception.category)

        with patch.object(checker, "EXPECTED_WORD_LIST_SHA256", "0" * 64):
            with self.assertRaises(checker.CheckerFailure) as failure:
                checker.import_upstream(None)
        self.assertEqual("upstream-word-list-hash", failure.exception.category)

    def test_upstream_errors_and_output_save_failures_are_nonzero(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary).resolve()
            output = temporary_path / "result.json"
            with patch.object(checker, "REPO_ROOT", self.repository), patch.object(
                checker, "APP_ROOT", self.app
            ):
                exit_code = checker.main(
                    [
                        str(self.fixture_path),
                        "--output",
                        str(output),
                    ]
                )
            self.assertNotEqual(0, exit_code)
            result = json.loads(output.read_text(encoding="utf-8"))
            self.assertTrue(any(item["category"] == "upstream-error" for item in result["failures"]))

            clean_output = temporary_path / "clean-result.json"
            with patch.object(checker, "REPO_ROOT", self.repository), patch.object(
                checker, "APP_ROOT", self.app
            ):
                clean_exit_code = checker.main(
                    [
                        str(self.clean_fixture_path),
                        "--output",
                        str(clean_output),
                    ]
                )
            self.assertEqual(0, clean_exit_code)
            clean_result = json.loads(clean_output.read_text(encoding="utf-8"))
            self.assertTrue(clean_result["passed"])
            self.assertEqual([], clean_result["failures"])

            blocked_output = temporary_path / "blocked-output"
            blocked_output.mkdir()
            with patch.object(checker, "REPO_ROOT", self.repository), patch.object(
                checker, "APP_ROOT", self.app
            ):
                output_failure_code = checker.main(
                    [
                        str(self.clean_fixture_path),
                        "--output",
                        str(blocked_output),
                    ]
                )
            self.assertNotEqual(0, output_failure_code)


if __name__ == "__main__":
    unittest.main()
