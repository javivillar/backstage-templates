#!/usr/bin/env python3
"""The quality report of the application (quality.json): what its tests, coverage and linters said in the CI.

The CI attaches it to both images in the registry next to their SBOM (oras attach, artifact type
application/vnd.refresquito.quality.v1+json); Backstage reads it for the scorecard Quality & Security.

    quality.py backend  OUT --junit junit.xml --coverage coverage.json --ruff ruff.json --mypy mypy.txt
    quality.py frontend OUT --karma karma.log --coverage coverage-summary.json --eslint eslint.json \
                            [--specs specs.json] [--coverage-final coverage-final.json]
    quality.py merge    OUT backend.json frontend.json --revision <sha>

Besides the numbers, each part has a detail (Backstage shows it in the tab Quality & Security): every test with its
result and time ("detail.tests"; the frontend's from the reporter "specs" of karma.conf.js), and every file with its
coverage and the lines its tests do not run ("detail.coverage").

Each part also writes a table to the summary of the job ($GITHUB_STEP_SUMMARY). A report that is missing (its tool
did not run) leaves its numbers out; the scorecard then says the report is incomplete.
"""
import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SCHEMA = "refresquito.quality/v1"


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def junit(path):
    text = read(path)
    if text is None:
        return None
    root = ET.fromstring(text)
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    total = lambda key: sum(int(s.get(key, 0)) for s in suites)
    return {"total": total("tests"), "failures": total("failures"), "errors": total("errors"), "skipped": total("skipped")}


def pytest_coverage(path):
    text = read(path)
    if text is None:
        return None
    totals = json.loads(text)["totals"]
    out = {"lines": round(totals["percent_covered"], 1)}
    if totals.get("num_branches"):
        out["branches"] = round(100 * totals["covered_branches"] / totals["num_branches"], 1)
    return out


def ruff(path):
    text = read(path)
    return None if text is None else {"issues": len(json.loads(text or "[]"))}


def mypy(path):
    text = read(path)
    if text is None:
        return None
    m = re.search(r"Found (\d+) errors?", text)
    return {"errors": int(m.group(1)) if m else 0}


def karma(path):
    """The last 'Executed N of M (K FAILED) (skipped S)' line of the progress reporter."""
    text = read(path)
    if text is None:
        return None
    runs = re.findall(r"Executed (\d+) of (\d+)(?: \((\d+) FAILED\))?(?: \(skipped (\d+)\))?", text)
    if not runs:
        return None
    executed, total, failed, skipped = runs[-1]
    return {"total": int(total), "failures": int(failed or 0), "errors": 0, "skipped": int(skipped or 0)}


def istanbul(path):
    text = read(path)
    if text is None:
        return None
    t = json.loads(text)["total"]
    return {k: t[k]["pct"] for k in ("lines", "branches", "statements", "functions") if k in t}


def eslint(path):
    text = read(path)
    if text is None:
        return None
    files = json.loads(text or "[]")
    return {"errors": sum(f["errorCount"] for f in files), "warnings": sum(f["warningCount"] for f in files)}


MAX_TESTS = 3000  # the report stays small (Backstage reads at most 1 MB)
MAX_MESSAGE = 500


def first_lines(text):
    text = (text or "").strip()
    return text if len(text) <= MAX_MESSAGE else text[:MAX_MESSAGE] + "…"


def ranges(lines):
    """[1, 2, 3, 7, 9, 10] -> "1-3, 7, 9-10" """
    out, lines = [], sorted(set(lines))
    for n in lines:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return ", ".join(str(a) if a == b else f"{a}-{b}" for a, b in out)


def junit_tests(path):
    """Every test case of junit.xml (pytest --junitxml): its name, result, time and, if it did not pass, why."""
    text = read(path)
    if text is None:
        return None
    tests = []
    for case in ET.fromstring(text).iter("testcase"):
        status, message = "passed", None
        for tag in ("failure", "error", "skipped"):
            el = case.find(tag)
            if el is not None:
                status = {"failure": "failed", "error": "error", "skipped": "skipped"}[tag]
                message = first_lines(el.get("message") or el.text)
                break
        test = {"name": f"{case.get('classname', '')}::{case.get('name', '')}".lstrip(":"), "status": status,
                "time": round(float(case.get("time") or 0), 3)}
        if message:
            test["message"] = message
        tests.append(test)
    return tests[:MAX_TESTS]


def karma_specs(path):
    """The specs.json the reporter "specs" of karma.conf.js writes: one entry per spec."""
    text = read(path)
    if text is None:
        return None
    tests = []
    for spec in json.loads(text):
        test = {"name": " › ".join(spec.get("suite", []) + [spec.get("description", "")]), "status": spec.get("status", "passed"),
                "time": round((spec.get("time") or 0) / 1000, 3)}
        if spec.get("message"):
            test["message"] = first_lines(spec["message"])
        tests.append(test)
    return tests[:MAX_TESTS]


def pytest_files(path):
    """Every file of coverage.json (pytest --cov-report=json): its line coverage and the lines no test runs."""
    text = read(path)
    if text is None:
        return None
    files = []
    for name, data in json.loads(text).get("files", {}).items():
        summary = data.get("summary", {})
        files.append({"file": name, "lines": round(summary.get("percent_covered", 0), 1),
                      "statements": summary.get("num_statements", 0), "missing": ranges(data.get("missing_lines", []))})
    return sorted(files, key=lambda f: (f["lines"], f["file"]))


def istanbul_files(summary_path, final_path):
    """Every file of coverage-summary.json (karma-coverage) and, from coverage-final.json, the lines no test runs."""
    text = read(summary_path)
    if text is None:
        return None
    missing = {}
    final = read(final_path) if final_path else None
    if final:
        for name, data in json.loads(final).items():
            lines = {}
            for sid, loc in data.get("statementMap", {}).items():
                line = loc["start"]["line"]
                lines[line] = lines.get(line, False) or data.get("s", {}).get(sid, 0) > 0
            missing[name] = ranges([n for n, hit in lines.items() if not hit])
    files = []
    for name, data in json.loads(text).items():
        if name == "total":
            continue
        short = name[name.index("/src/") + 1:] if "/src/" in name else name
        entry = {"file": short, "lines": data["lines"]["pct"], "statements": data["statements"]["total"]}
        if data.get("branches", {}).get("total"):
            entry["branches"] = data["branches"]["pct"]
        if name in missing:
            entry["missing"] = missing[name]
        files.append(entry)
    return sorted(files, key=lambda f: (f["lines"], f.get("branches", 100), f["file"]))


def detail(tests, files):
    d = drop_none({"tests": tests, "coverage": files})
    return d or None


def drop_none(d):
    return {k: v for k, v in d.items() if v is not None}


def summary(title, part):
    rows = []
    for key, value in part.items():
        if key == "detail":
            continue
        rows.append(f"| {key} | {', '.join(f'{k}: {v}' for k, v in value.items())} |")
    text = f"### Quality report: {title}\n\n| | |\n|---|---|\n" + "\n".join(rows) + "\n"
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("part", choices=["backend", "frontend", "merge"])
    p.add_argument("out")
    p.add_argument("inputs", nargs="*")
    for opt in ("junit", "coverage", "ruff", "mypy", "karma", "eslint", "revision", "specs", "coverage-final"):
        p.add_argument(f"--{opt}")
    a = p.parse_args()

    if a.part == "backend":
        part = drop_none({"tests": junit(a.junit), "coverage": pytest_coverage(a.coverage), "ruff": ruff(a.ruff), "mypy": mypy(a.mypy),
                          "detail": detail(junit_tests(a.junit), pytest_files(a.coverage))})
    elif a.part == "frontend":
        part = drop_none({"tests": karma(a.karma), "coverage": istanbul(a.coverage), "eslint": eslint(a.eslint),
                          "detail": detail(karma_specs(a.specs), istanbul_files(a.coverage, a.coverage_final))})
    else:
        part = {"schema": SCHEMA, "revision": a.revision or "", "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
        for path in a.inputs:
            name = os.path.basename(path).split(".")[0].replace("quality-", "")
            text = read(path)
            if text is not None:
                part[name] = json.loads(text)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(part, f, indent=2)
    if a.part != "merge":
        summary(a.part, part)
    else:
        print(json.dumps(part, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
