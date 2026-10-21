#!/usr/bin/env python3
"""The quality report of the application (quality.json): what its tests, coverage and linters said in the CI.

The CI attaches it to both images in the registry next to their SBOM (oras attach, artifact type
application/vnd.refresquito.quality.v1+json); Backstage reads it for the scorecard Quality & Security.

    quality.py backend  OUT --junit junit.xml --coverage coverage.json --ruff ruff.json --mypy mypy.txt
    quality.py frontend OUT --karma karma.log --coverage coverage-summary.json --eslint eslint.json
    quality.py merge    OUT backend.json frontend.json --revision <sha>

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


def drop_none(d):
    return {k: v for k, v in d.items() if v is not None}


def summary(title, part):
    rows = []
    for key, value in part.items():
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
    for opt in ("junit", "coverage", "ruff", "mypy", "karma", "eslint", "revision"):
        p.add_argument(f"--{opt}")
    a = p.parse_args()

    if a.part == "backend":
        part = drop_none({"tests": junit(a.junit), "coverage": pytest_coverage(a.coverage), "ruff": ruff(a.ruff), "mypy": mypy(a.mypy)})
    elif a.part == "frontend":
        part = drop_none({"tests": karma(a.karma), "coverage": istanbul(a.coverage), "eslint": eslint(a.eslint)})
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
