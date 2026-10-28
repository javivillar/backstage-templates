#!/usr/bin/env python3
"""The quality report of the application (quality.json): what its tests, coverage and linters said in the CI.

The CI attaches it to both images in the registry next to their SBOM (oras attach, artifact type
application/vnd.refresquito.quality.v1+json); Backstage reads it for the scorecard Quality & Security.

    quality.py backend  OUT --junit junit.xml --coverage coverage.json --ruff ruff.json --mypy mypy.txt
    quality.py services OUT --surefire 'services/*/target/surefire-reports' --jacoco 'services/*/target/site/jacoco/jacoco.xml' \
                            --openapi <service>=services/<service>/openapi.json      (once per service with an API)
    quality.py frontend OUT --karma karma.log --coverage coverage-summary.json --eslint eslint.json \
                            [--specs specs.json] [--coverage-final coverage-final.json]
    quality.py secrets  OUT --gitleaks gitleaks.json [--trivy api=trivy-api.json --trivy web=trivy-web.json]
    quality.py exceptions OUT --file platform/security-exceptions.yaml
    quality.py merge    OUT backend.json frontend.json secrets.json exceptions.json --revision <sha>

`services` is the backend of an application of refresquito-spring-boot (Spring Framework): the tests of every service
(the JUnit reports of Surefire), their coverage (JaCoCo) and who can call each operation (x-refresquito-auth of their
OpenAPI, written by the framework as it enforces it). It writes the part `backend`, the same as a Python backend.

Code findings (the backend also takes --endpoints endpoints.json --bandit bandit.json; the frontend's come from its
eslint report): who can call each endpoint (.github/endpoints.py: "unauthenticated" counts the operations of the
application with no authentication that are not declared public), the static analysis of the code (Bandit; the
rules of eslint.config.js marked security) and the secrets found in the history of the repository (gitleaks) and in
the images (Trivy). Their detail is "detail.endpoints" and "detail.findings": rule, file, line, never the secret.

Besides the numbers, each part has a detail (Backstage shows it in the tab Quality & Security): every test with its
result and time ("detail.tests"; the frontend's from the reporter "specs" of karma.conf.js), and every file with its
coverage and the lines its tests do not run ("detail.coverage").

Each part also writes a table to the summary of the job ($GITHUB_STEP_SUMMARY). A report that is missing (its tool
did not run) leaves its numbers out; the scorecard then says the report is incomplete.
"""
import argparse
import glob
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

SCHEMA = "refresquito.quality/v1"


def read(path):
    if not path:
        return None
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


# the eslint rules of the part security (eslint.config.js: the block "Security", messages prefixed [security])
SECURITY_RULES = {"no-eval", "no-implied-eval", "no-new-func", "no-script-url"}
MAX_FINDINGS = 500


def is_security(message):
    return message.get("ruleId") in SECURITY_RULES or str(message.get("message", "")).startswith("[security]")


def eslint_security(path):
    text = read(path)
    if text is None:
        return None, None
    findings = []
    for f in json.loads(text or "[]"):
        name = f["filePath"]
        name = name[name.index("/src/") + 1:] if "/src/" in name else name
        for m in f.get("messages", []):
            if is_security(m):
                findings.append({"tool": "eslint", "rule": m.get("ruleId"), "severity": "MEDIUM", "file": name,
                                 "line": m.get("line"), "message": first_lines(m.get("message"))})
    return {"errors": len(findings)}, findings[:MAX_FINDINGS]


def bandit(path):
    """Bandit's JSON report: counts by severity, and every finding (rule, severity, confidence, file, line)."""
    text = read(path)
    if text is None:
        return None, None
    results = json.loads(text or "{}").get("results", [])
    count = lambda sev: sum(r.get("issue_severity") == sev for r in results)
    findings = [{"tool": "bandit", "rule": f"{r.get('test_id')} {r.get('test_name', '')}".strip(),
                 "severity": r.get("issue_severity"), "confidence": r.get("issue_confidence"),
                 "file": r.get("filename"), "line": r.get("line_number"), "message": first_lines(r.get("issue_text"))}
                for r in results]
    findings.sort(key=lambda f: ({"HIGH": 0, "MEDIUM": 1}.get(f["severity"], 2), f["file"], f["line"] or 0))
    return {"high": count("HIGH"), "medium": count("MEDIUM"), "low": count("LOW")}, findings[:MAX_FINDINGS]


def endpoints(path):
    """The report of .github/endpoints.py: its counts, and the list of operations as detail."""
    text = read(path)
    if text is None:
        return None, None
    report = json.loads(text)
    return {k: v for k, v in report.items() if k != "endpoints"}, report.get("endpoints", [])


def secrets(gitleaks_path, trivy):
    """gitleaks (the whole git history, run with --redact) and Trivy (--scanners secret) on each image: where, never what."""
    findings, repo, images = [], None, None
    text = read(gitleaks_path) if gitleaks_path else None
    if text is not None:
        leaks = json.loads(text or "[]") or []
        repo = len(leaks)
        findings += [{"tool": "gitleaks", "where": "repository", "rule": f.get("RuleID"), "severity": "HIGH",
                      "file": f.get("File"), "line": f.get("StartLine"), "commit": (f.get("Commit") or "")[:12]}
                     for f in leaks]
    for item in trivy or []:
        name, _, path = item.partition("=")
        text = read(path)
        if text is None:
            continue
        images = images or 0
        for result in json.loads(text).get("Results", []) or []:
            for f in result.get("Secrets", []) or []:
                images += 1
                findings.append({"tool": "trivy", "where": f"image {name}", "rule": f.get("RuleID"),
                                 "severity": f.get("Severity"), "file": result.get("Target"), "line": f.get("StartLine")})
    part = drop_none({"repo": repo, "images": images})
    return part or None, findings[:MAX_FINDINGS]


# The approved exceptions to the checks of Quality & Security (platform/security-exceptions.yaml, approved by the
# CODEOWNERS of that file). Validated here, applied by Backstage: an exception takes its finding out of its check.
EXCEPTION_CHECKS = {
    "vulnerability": "a CVE / GHSA id of the image scan; `image:` (repository) to limit it to one image",
    "endpoint": "an operation without authentication: \"METHOD /path\" as the quality report lists it",
    "sast": "a rule of Bandit (B608) or eslint (no-eval) with the `file:` it is in",
    "secret": "a rule of gitleaks / Trivy (generic-api-key) with the `file:` it is in",
    "license": "a dependency of the application (its name) whose license is denied or unknown",
    "os-eol": "an image (repository) whose OS is out of support",
}
MAX_EXCEPTION_DAYS = 365


def exceptions(path, today=None):
    """The exceptions file, sorted into active, expired and invalid (with why). Missing file: no exceptions."""
    from datetime import date
    text = read(path)
    if text is None:
        return {"active": [], "expired": [], "invalid": [], "file": False}
    import yaml
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as e:
        return {"active": [], "expired": [], "invalid": [{"why": f"not valid YAML: {first_lines(str(e))}"}], "file": True}
    today = today or datetime.now(timezone.utc).date()
    out = {"active": [], "expired": [], "invalid": [], "file": True}
    for i, e in enumerate(doc.get("exceptions") or []):
        if not isinstance(e, dict):
            out["invalid"].append({"entry": i + 1, "why": "an exception is a mapping (check, id, reason, approvedBy, expires)"})
            continue
        entry = {k: (str(v) if k == "expires" else v) for k, v in e.items()
                 if k in ("check", "id", "file", "image", "reason", "approvedBy", "expires")}
        why = []
        if e.get("check") not in EXCEPTION_CHECKS:
            why.append(f"check is one of {', '.join(EXCEPTION_CHECKS)}")
        if not str(e.get("id") or "").strip():
            why.append("id is required")
        if e.get("check") in ("sast", "secret") and not str(e.get("file") or "").strip():
            why.append("file is required for a sast / secret exception")
        if len(str(e.get("reason") or "").strip()) < 10:
            why.append("reason is required (why it is accepted, at least a sentence)")
        if not str(e.get("approvedBy") or "").strip():
            why.append("approvedBy is required (the approver, a CODEOWNER of the file)")
        try:
            expires = e["expires"] if isinstance(e.get("expires"), date) else date.fromisoformat(str(e.get("expires")))
        except (TypeError, ValueError):
            expires = None
            why.append("expires is a date (YYYY-MM-DD)")
        if expires and (expires - today).days > MAX_EXCEPTION_DAYS:
            why.append(f"expires at most {MAX_EXCEPTION_DAYS} days ahead")
        if why:
            out["invalid"].append({**entry, "entry": i + 1, "why": "; ".join(why)})
        elif expires < today:
            out["expired"].append(entry)
        else:
            out["active"].append({**entry, "days_left": (expires - today).days})
    return out


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


# ---------------------------------------------------------------- Spring Framework (refresquito-spring-boot)
def expand(patterns):
    """Paths from globs (a folder: its TEST-*.xml)."""
    out = []
    for pattern in patterns or []:
        for path in sorted(glob.glob(pattern)):
            out += sorted(glob.glob(os.path.join(path, "TEST-*.xml"))) if os.path.isdir(path) else [path]
    return out


def surefire(patterns):
    """The JUnit reports of Surefire (one per test class, in every service): totals and every test."""
    files = expand(patterns)
    if not files:
        return None, None
    totals = {"total": 0, "failures": 0, "errors": 0, "skipped": 0}
    tests = []
    for path in files:
        part = junit(path)
        for k in totals:
            totals[k] += part[k]
        service = path.split("services/")[-1].split("/")[0] if "services/" in path else ""
        for t in junit_tests(path) or []:
            tests.append({**t, "name": f"{service}: {t['name']}" if service else t["name"]})
    return totals, tests[:MAX_TESTS]


def jacoco(patterns):
    """JaCoCo (jacoco.xml of every service): the coverage of lines and branches of all, and every file with the lines
    its tests do not run."""
    files = expand(patterns)
    if not files:
        return None, None
    sums = {"LINE": [0, 0], "BRANCH": [0, 0]}
    detail_files = []
    for path in files:
        root = ET.parse(path).getroot()
        service = path.split("services/")[-1].split("/")[0] if "services/" in path else ""
        for c in root.findall("counter"):
            if c.get("type") in sums:
                sums[c.get("type")][0] += int(c.get("missed"))
                sums[c.get("type")][1] += int(c.get("covered"))
        for package in root.findall("package"):
            for source in package.findall("sourcefile"):
                counters = {c.get("type"): c for c in source.findall("counter")}
                line = counters.get("LINE")
                if line is None:
                    continue
                missed, covered = int(line.get("missed")), int(line.get("covered"))
                entry = {"file": f"services/{service}/src/main/java/{package.get('name')}/{source.get('name')}" if service
                         else f"{package.get('name')}/{source.get('name')}",
                         "lines": round(100 * covered / (missed + covered), 1) if missed + covered else 100.0,
                         "statements": missed + covered,
                         "missing": ranges([int(l.get("nr")) for l in source.findall("line") if int(l.get("ci")) == 0 and int(l.get("mi")) > 0])}
                branch = counters.get("BRANCH")
                if branch is not None and int(branch.get("missed")) + int(branch.get("covered")):
                    entry["branches"] = round(100 * int(branch.get("covered")) / (int(branch.get("missed")) + int(branch.get("covered"))), 1)
                detail_files.append(entry)
    pct = lambda t: round(100 * sums[t][1] / (sums[t][0] + sums[t][1]), 1) if sum(sums[t]) else None
    totals = drop_none({"lines": pct("LINE"), "branches": pct("BRANCH")})
    return totals, sorted(detail_files, key=lambda f: (f["lines"], f.get("branches", 100), f["file"]))


def spring_endpoints(items):
    """Who can call each operation of every service: x-refresquito-auth of its OpenAPI (refresquito-spring-boot writes
    it as it enforces it). Every route needs a user of the realm unless declared public, so `none` is an operation
    the framework did not describe (an OpenAPI not made by it): a finding, as in endpoints.py."""
    if not items:
        return None, None
    endpoints = []
    for item in items:
        service, _, path = item.partition("=")
        doc = json.loads(read(path) or "{}")
        for route, operations in (doc.get("paths") or {}).items():
            for method, op in operations.items():
                if not isinstance(op, dict):
                    continue
                auth = op.get("x-refresquito-auth") or {}
                entry = {"method": method.upper(), "path": route, "auth": auth.get("kind", "none"),
                         "owner": auth.get("owner", "app"), "operation": op.get("operationId", ""), "service": service}
                if auth.get("roles"):
                    entry["roles"] = auth["roles"]
                if auth.get("reason"):
                    entry["reason"] = auth["reason"]
                endpoints.append(entry)
    endpoints.sort(key=lambda e: (e["owner"] != "app", e["path"], e["method"]))
    mine = [e for e in endpoints if e["owner"] == "app"]
    for e in mine:
        if e["auth"] == "none":
            print(f"::warning::{e['service']}: {e['method']} {e['path']} says nothing of who can call it (x-refresquito-auth)")
    report = {"total": len(mine), "unauthenticated": sum(e["auth"] == "none" for e in mine),
              "public": sum(e["auth"] == "public" for e in mine), "custom": sum(e["auth"] == "custom" for e in mine),
              "with_roles": sum(e["auth"] == "roles" for e in mine), "flow": sum(e["auth"] == "flow" for e in mine)}
    return report, endpoints


def detail(tests, files, endpoint_list=None, findings=None):
    d = drop_none({"tests": tests, "coverage": files, "endpoints": endpoint_list, "findings": findings or None})
    return d or None


def drop_none(d):
    return {k: v for k, v in d.items() if v is not None}


def summary(title, part):
    rows = []
    for key, value in part.items():
        if key == "detail":
            continue
        if isinstance(value, list):
            shown = f"{len(value)}" + (": " + "; ".join(str(x.get("id", x.get("why", ""))) for x in value[:10]) if value else "")
        else:
            shown = ", ".join(f"{k}: {v}" for k, v in value.items()) if isinstance(value, dict) else value
        rows.append(f"| {key} | {shown} |")
    text = f"### Quality report: {title}\n\n| | |\n|---|---|\n" + "\n".join(rows) + "\n"
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("part", choices=["backend", "services", "frontend", "secrets", "exceptions", "merge"])
    p.add_argument("out")
    p.add_argument("inputs", nargs="*")
    for opt in ("junit", "coverage", "ruff", "mypy", "karma", "eslint", "revision", "specs", "coverage-final",
                "endpoints", "bandit", "gitleaks", "file"):
        p.add_argument(f"--{opt}")
    p.add_argument("--trivy", action="append", help="<image>=<Trivy JSON report>, once per image")
    p.add_argument("--surefire", action="append", help="services: a folder (or glob) of Surefire reports")
    p.add_argument("--jacoco", action="append", help="services: a jacoco.xml (or glob)")
    p.add_argument("--openapi", action="append", help="services: <service>=<its openapi.json>, once per service")
    a = p.parse_args()

    if a.part == "backend":
        ep, ep_list = endpoints(a.endpoints)
        sast, sast_findings = bandit(a.bandit)
        part = drop_none({"tests": junit(a.junit), "coverage": pytest_coverage(a.coverage), "ruff": ruff(a.ruff), "mypy": mypy(a.mypy),
                          "endpoints": ep, "bandit": sast,
                          "detail": detail(junit_tests(a.junit), pytest_files(a.coverage), ep_list, sast_findings)})
    elif a.part == "services":
        tests, test_list = surefire(a.surefire)
        cov, cov_files = jacoco(a.jacoco)
        ep, ep_list = spring_endpoints(a.openapi)
        part = drop_none({"tests": tests, "coverage": cov, "endpoints": ep,
                          "detail": detail(test_list, cov_files, ep_list, None)})
    elif a.part == "frontend":
        sec, sec_findings = eslint_security(a.eslint)
        part = drop_none({"tests": karma(a.karma), "coverage": istanbul(a.coverage), "eslint": eslint(a.eslint),
                          "security": sec,
                          "detail": detail(karma_specs(a.specs), istanbul_files(a.coverage, a.coverage_final), None, sec_findings)})
    elif a.part == "exceptions":
        part = exceptions(a.file)
        for e in part["invalid"]:
            print(f"::error::{a.file}: exception {e.get('entry', '?')}: {e['why']}")
    elif a.part == "secrets":
        found, found_list = secrets(a.gitleaks, a.trivy)
        part = drop_none({**(found or {}), "detail": detail(None, None, None, found_list)})
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
