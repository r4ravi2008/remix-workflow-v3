#!/usr/bin/env python3
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
APP_ROOT = REPO_ROOT / "apps" / "release-kit-studio"
APP_ROOT_REL = "apps/release-kit-studio"
EXCLUDED_DIRS = {".runs", ".state", ".local", "node_modules", "target", "dist", ".git"}
# Archived records remain in the source tree, but they are not maintained prose.
# Keep this list explicit so an unrelated directory named ``archive`` remains active.
ARCHIVE_PREFIXES = (
    PurePosixPath("docs/archive"),
    PurePosixPath("native-editor/docs/archive"),
)
EXPECTED_STE_SHA256 = "71850aa6f0aebaf980b176c59a18d13c713640ecd30d773e2fd04cf09a2244a2"
EXPECTED_WORD_LIST_SHA256 = "28bc1c52d2d1a1b1f564ed9e8e36f22a39ec0fb128ed973f7ba3212849a53afd"
APPROVAL_FIELDS = {
    "file",
    "sentence",
    "word",
    "occurrenceCount",
    "kind",
    "conceptDefinition",
    "reason",
}
APPROVAL_KINDS = {"technical-name", "official-name"}
APPROVALS_FIELDS = {"schemaVersion", "upstreamSha256", "records"}
WORD_RE = re.compile(r"[A-Za-z-]+")
WARNING_WORD_RE = re.compile(r'^"([^"\n]+)"')


class CheckerFailure(Exception):
    def __init__(self, category, message):
        super().__init__(message)
        self.category = category
        self.message = message


def json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CheckerFailure("approvals-file", f"cannot read approvals file: {exc}") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON constant: {value}")),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise CheckerFailure("approvals-file", f"invalid approvals JSON: {exc}") from exc


def sha256(path):
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise CheckerFailure("upstream-checker", f"cannot read the upstream checker: {exc}") from exc
    return digest.hexdigest()


def is_within(path, root):
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def excluded(relative):
    return any(part in EXCLUDED_DIRS for part in relative.parts)


def archive_excluded(relative):
    return any(relative == prefix or prefix in relative.parents for prefix in ARCHIVE_PREFIXES)


def repository_relative(path):
    return path.relative_to(REPO_ROOT).as_posix()


def validate_repository_file(value, corpus_files=None):
    if not isinstance(value, str) or not value:
        return None, "file must be a non-empty string"
    if "\\" in value:
        return None, "file must use repository-relative POSIX separators"
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return None, "file must be a normalized repository-relative path"
    if pure.as_posix() != value:
        return None, "file must be a normalized repository-relative path"
    if not value.startswith(APP_ROOT_REL + "/"):
        return None, "file is outside apps/release-kit-studio"
    relative_to_app = PurePosixPath(value).relative_to(APP_ROOT_REL)
    if excluded(relative_to_app) or archive_excluded(relative_to_app) or pure.suffix != ".md":
        return None, "file is outside the maintained Markdown corpus"
    path = (REPO_ROOT / Path(*pure.parts)).resolve()
    if not is_within(path, APP_ROOT.resolve()):
        return None, "file resolves outside apps/release-kit-studio"
    if not path.is_file():
        return None, "file does not exist"
    normalized = repository_relative(path)
    if normalized != value:
        return None, "file is not the canonical repository-relative path"
    if corpus_files is not None and value not in corpus_files:
        return None, "file is not in the selected maintained corpus"
    return value, None


def discover_corpus():
    root = APP_ROOT.resolve()
    if not root.is_dir():
        raise CheckerFailure("corpus-path", "apps/release-kit-studio does not exist")
    files = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if excluded(relative) or archive_excluded(relative):
            continue
        if not path.is_file():
            continue
        resolved = path.resolve()
        if not is_within(resolved, root):
            raise CheckerFailure("corpus-path", f"corpus file resolves outside apps/release-kit-studio: {relative}")
        files.append(repository_relative(resolved))
    files = sorted(set(files))
    if not files:
        raise CheckerFailure("corpus-path", "the maintained Markdown corpus is empty")
    return files


def resolve_cli_path(raw):
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    if path.parts and path.parts[0] == "apps":
        return (REPO_ROOT / path).resolve()
    return (Path.cwd() / path).resolve()


def resolve_option_path(path):
    if path is None:
        return None
    return resolve_cli_path(str(path))


def select_corpus(raw_files):
    if not raw_files:
        return discover_corpus()
    selected = []
    seen = set()
    for raw in raw_files:
        path = resolve_cli_path(raw)
        try:
            value = repository_relative(path)
        except ValueError as exc:
            raise CheckerFailure("unsafe-path", f"input file is outside the repository: {raw}") from exc
        normalized, error = validate_repository_file(value)
        if error:
            category = "unsafe-path" if "outside" in error or "normalized" in error else "corpus-path"
            raise CheckerFailure(category, f"{raw}: {error}")
        if normalized in seen:
            raise CheckerFailure("corpus-path", f"duplicate input file: {normalized}")
        seen.add(normalized)
        selected.append(normalized)
    return sorted(selected)


def import_upstream(skill_dir_arg):
    skill_value = skill_dir_arg or os.environ.get("STE_SKILL_DIR")
    if not skill_value:
        raise CheckerFailure("upstream-checker", "set STE_SKILL_DIR or pass --skill-dir")
    skill_dir = resolve_cli_path(skill_value).expanduser().resolve()
    script = skill_dir / "scripts" / "ste_check.py"
    word_list = skill_dir / "references" / "word-list.md"
    if not script.is_file() or not word_list.is_file():
        raise CheckerFailure("upstream-checker", "skill directory must contain scripts/ste_check.py and references/word-list.md")
    actual_hash = sha256(script)
    actual_word_list_hash = sha256(word_list)
    if actual_hash != EXPECTED_STE_SHA256:
        raise CheckerFailure("upstream-checker-hash", "the upstream checker hash does not match the pinned checkpoint")
    if actual_word_list_hash != EXPECTED_WORD_LIST_SHA256:
        raise CheckerFailure("upstream-word-list-hash", "the upstream word-list hash does not match the pinned checkpoint")
    spec = importlib.util.spec_from_file_location("project_upstream_ste", script)
    if spec is None or spec.loader is None:
        raise CheckerFailure("upstream-checker", "cannot import the upstream checker")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise CheckerFailure("upstream-checker", f"cannot import the upstream checker: {exc}") from exc
    required = ("Report", "check_text", "check_sentence", "load_word_list")
    if any(not hasattr(module, name) for name in required):
        raise CheckerFailure("upstream-checker", "the upstream checker does not expose its expected interface")
    return module, word_list, actual_word_list_hash


def warning_word(message):
    match = WARNING_WORD_RE.match(message)
    return match.group(1) if match else None


def json_value(value):
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    return value


def run_upstream(module, word_list, files):
    report = module.Report()
    try:
        approved = module.load_word_list(word_list)
    except Exception as exc:
        raise CheckerFailure("upstream-checker", f"cannot load the upstream word list: {exc}") from exc
    if not approved:
        raise CheckerFailure("upstream-word-list", "the upstream word list is empty")
    warnings = []
    original_check_sentence = module.check_sentence

    def observed_sentence(sentence, mode, current_report, location):
        previous = len(current_report.warnings)
        original_check_sentence(sentence, mode, current_report, location)
        for raw_location, rule, message in current_report.warnings[previous:]:
            warnings.append(
                {
                    "file": files[current_file_index],
                    "location": raw_location,
                    "rule": rule,
                    "message": message,
                    "sentence": sentence,
                    "word": warning_word(message) if rule == "3.5" else None,
                }
            )

    module.check_sentence = observed_sentence
    try:
        for current_file_index, file in enumerate(files):
            text = (REPO_ROOT / Path(*PurePosixPath(file).parts)).read_text(encoding="utf-8")
            module.check_text(text, "mixed", report, file, approved)
    except OSError as exc:
        raise CheckerFailure("corpus-path", f"cannot read corpus file: {exc}") from exc
    finally:
        module.check_sentence = original_check_sentence
    raw_errors = [json_value(item) for item in report.errors]
    raw_warnings = [json_value(item) for item in report.warnings]
    if len(warnings) != len(raw_warnings):
        for index in range(len(warnings), len(raw_warnings)):
            raw = raw_warnings[index]
            warnings.append(
                {
                    "file": raw[0].rsplit(":", 1)[0] if isinstance(raw, list) and raw else None,
                    "location": raw[0] if isinstance(raw, list) and raw else None,
                    "rule": raw[1] if isinstance(raw, list) and len(raw) > 1 else None,
                    "message": raw[2] if isinstance(raw, list) and len(raw) > 2 else None,
                    "sentence": None,
                    "word": None,
                }
            )
    return raw_errors, raw_warnings, warnings, json_value(report.unknown)


def record_key(record):
    return (record["file"], record["sentence"], record["word"])


def validate_record(record, index, corpus_files):
    if not isinstance(record, dict):
        return None, [("invalid-record", f"record {index} must be an object")]
    errors = []
    if set(record) != APPROVAL_FIELDS:
        missing = sorted(APPROVAL_FIELDS - set(record))
        extra = sorted(set(record) - APPROVAL_FIELDS)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unknown " + ", ".join(extra))
        errors.append(("invalid-record", f"record {index}: " + "; ".join(details)))
        return None, errors
    file, file_error = validate_repository_file(record["file"], corpus_files)
    if file_error:
        category = "unsafe-path" if "outside" in file_error or "normalized" in file_error else "invalid-record"
        errors.append((category, f"record {index}: {file_error}"))
    sentence = record["sentence"]
    if not isinstance(sentence, str) or not sentence or sentence.strip() != sentence:
        errors.append(("invalid-record", f"record {index}: sentence must be the exact upstream-normalized sentence"))
    word = record["word"]
    if not isinstance(word, str) or not WORD_RE.fullmatch(word):
        errors.append(("invalid-record", f"record {index}: word must be one exact upstream word"))
    count = record["occurrenceCount"]
    if type(count) is not int or count < 1:
        errors.append(("invalid-record", f"record {index}: occurrenceCount must be a positive integer"))
    kind = record["kind"]
    if not isinstance(kind, str) or kind not in APPROVAL_KINDS:
        errors.append(("invalid-record", f"record {index}: kind must be technical-name or official-name"))
    for field in ("conceptDefinition", "reason"):
        value = record[field]
        if not isinstance(value, str) or not value.strip():
            errors.append(("invalid-record", f"record {index}: {field} must be a non-empty string"))
    if errors:
        return None, errors
    return (file, sentence, word), errors


def load_approvals(path, corpus_files):
    if path is None:
        return [], []
    data = load_json(path)
    if not isinstance(data, dict):
        return [], [{"category": "invalid-record", "message": "approvals JSON must be an object"}]
    if set(data) != APPROVALS_FIELDS:
        missing = sorted(APPROVALS_FIELDS - set(data))
        extra = sorted(set(data) - APPROVALS_FIELDS)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unknown " + ", ".join(extra))
        return [], [{"category": "invalid-record", "message": "approvals JSON: " + "; ".join(details)}]
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        return [], [{"category": "invalid-record", "message": "approvals JSON schemaVersion must be 1"}]
    if data["upstreamSha256"] != EXPECTED_STE_SHA256:
        return [], [{"category": "upstream-checker-hash", "message": "approvals JSON upstreamSha256 does not match the pinned checkpoint"}]
    if not isinstance(data["records"], list):
        return [], [{"category": "invalid-record", "message": "approvals JSON records must be an array"}]
    records = []
    failures = []
    for index, record in enumerate(data["records"]):
        key, errors = validate_record(record, index, corpus_files)
        failures.extend({"category": category, "message": message} for category, message in errors)
        if key is not None:
            records.append((key, record, index))
    return records, failures


def review_approvals(records, warnings):
    observed = [warning for warning in warnings if warning.get("rule") == "3.5" and warning.get("word")]
    counts = Counter((warning["file"], warning["sentence"], warning["word"]) for warning in observed)
    failures = []
    records_by_key = {}
    resolved = []
    for key, record, index in records:
        if key in records_by_key:
            failures.append(
                {
                    "category": "duplicate-approval",
                    "message": f"records {records_by_key[key]} and {index} approve the same file, sentence, and word",
                    "file": key[0],
                    "sentence": key[1],
                    "word": key[2],
                }
            )
            continue
        records_by_key[key] = index
        expected = counts.get(key)
        if expected is None:
            failures.append(
                {
                    "category": "unused-stale-approval",
                    "message": f"record {index} does not match a current rule 3.5 warning",
                    "file": key[0],
                    "sentence": key[1],
                    "word": key[2],
                }
            )
            continue
        actual = record["occurrenceCount"]
        if actual != expected:
            failures.append(
                {
                    "category": "count-mismatch",
                    "message": f"record {index} declares {actual} occurrences but upstream emitted {expected}",
                    "file": key[0],
                    "sentence": key[1],
                    "word": key[2],
                }
            )
            continue
        resolved.append(
            {
                "file": key[0],
                "sentence": key[1],
                "word": key[2],
                "occurrenceCount": expected,
                "kind": record["kind"],
            }
        )
    resolved_keys = {(item["file"], item["sentence"], item["word"]) for item in resolved}
    unresolved = []
    for warning in warnings:
        if warning.get("rule") == "3.5" and warning.get("word"):
            key = (warning["file"], warning["sentence"], warning["word"])
            if key not in resolved_keys:
                unresolved.append(warning)
        else:
            unresolved.append(warning)
    for warning in unresolved:
        category = "long-sentence-warning" if warning.get("rule") == "5.1" else "unresolved-warning"
        failures.append(
            {
                "category": category,
                "message": warning.get("message"),
                "file": warning.get("file"),
                "location": warning.get("location"),
                "rule": warning.get("rule"),
                "sentence": warning.get("sentence"),
                "word": warning.get("word"),
            }
        )
    return {
        "observedRule35": len(observed),
        "resolved": resolved,
        "unresolved": unresolved,
        "failures": failures,
    }


def result_template(files):
    return {
        "schemaVersion": 1,
        "passed": False,
        "corpus": {
            "root": APP_ROOT_REL,
            "mode": "mixed",
            "archiveRoots": [prefix.as_posix() for prefix in ARCHIVE_PREFIXES],
            "files": files,
            "count": len(files),
        },
        "upstream": {
            "checker": "scripts/ste_check.py",
            "expectedSha256": EXPECTED_STE_SHA256,
            "sha256": None,
            "expectedWordListSha256": EXPECTED_WORD_LIST_SHA256,
            "wordListSha256": None,
        },
        "errors": [],
        "warnings": [],
        "rawWarnings": [],
        "unknownVocabulary": {},
        "approvals": {
            "records": 0,
            "resolved": [],
            "unresolved": [],
        },
        "failures": [],
    }


def write_output(path, result):
    if path is None:
        return True
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR cannot write output: {exc}", file=sys.stderr)
        return False
    return True


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Run the strict project Simplified Technical English check.")
    parser.add_argument("files", nargs="*", help="maintained Markdown files; default: the complete project corpus")
    parser.add_argument("--approvals", type=Path, help="strict rule 3.5 approval JSON")
    parser.add_argument("--output", type=Path, help="write the complete JSON result to this path")
    parser.add_argument("--skill-dir", type=Path, help="installed simplified-technical-english skill directory")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        files = select_corpus(args.files)
        if not files:
            raise CheckerFailure("corpus-path", "the selected Markdown corpus is empty")
        result = result_template(files)
    except CheckerFailure as failure:
        result = result_template([])
        result["failures"].append({"category": failure.category, "message": failure.message})
        output_saved = write_output(resolve_option_path(args.output), result)
        if not output_saved:
            print("FAIL output-file: the requested result was not saved")
        print(f"FAIL {failure.category}: {failure.message}")
        return 1

    try:
        module, word_list, word_list_hash = import_upstream(args.skill_dir)
        script_path = Path(module.__file__).resolve()
        result["upstream"]["sha256"] = sha256(script_path)
        result["upstream"]["wordListSha256"] = word_list_hash
        raw_errors, raw_warnings, warnings, unknown_vocabulary = run_upstream(module, word_list, files)
        result["errors"] = raw_errors
        result["warnings"] = warnings
        result["rawWarnings"] = raw_warnings
        result["unknownVocabulary"] = unknown_vocabulary
    except CheckerFailure as failure:
        result["failures"].append({"category": failure.category, "message": failure.message})
        output_saved = write_output(resolve_option_path(args.output), result)
        if not output_saved:
            print("FAIL output-file: the requested result was not saved")
        print(f"FAIL {failure.category}: {failure.message}")
        return 1

    try:
        approvals_path = resolve_option_path(args.approvals)
        records, approval_failures = load_approvals(approvals_path, set(files))
    except CheckerFailure as failure:
        records = []
        approval_failures = [{"category": failure.category, "message": failure.message}]
    review = review_approvals(records, result["warnings"])
    result["approvals"] = {
        "records": len(records),
        "resolved": review["resolved"],
        "unresolved": review["unresolved"],
    }
    result["failures"].extend(approval_failures)
    result["failures"].extend(review["failures"])
    result["failures"].extend(
        {
            "category": "upstream-error",
            "message": raw_error,
        }
        for raw_error in result["errors"]
    )
    result["passed"] = not result["failures"]
    output_saved = write_output(resolve_option_path(args.output), result)
    if args.output and not output_saved:
        result["passed"] = False
        result["failures"].append(
            {"category": "output-file", "message": "the requested result was not saved"}
        )
    print(
        f"{'PASS' if result['passed'] else 'FAIL'} "
        f"{len(files)} files, {len(result['errors'])} errors, "
        f"{len(result['warnings'])} warnings, "
        f"{len(result['unknownVocabulary'])} vocabulary forms, "
        f"{len(review['resolved'])} resolved rule 3.5 uses, "
        f"{len(result['failures'])} failures"
    )
    return 0 if result["passed"] and output_saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
