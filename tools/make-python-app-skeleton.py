#!/usr/bin/env python3
"""make-python-app-skeleton.py — the skeleton of the template "New application (Python Framework)".

    python3 tools/make-python-app-skeleton.py ~/petstore

The skeleton is NOT written by hand: it is the petstore (github.com/javivillar/petstore), the
reference application of the framework, with its names turned into template values. Run this
again when the petstore changes, and commit the result (skeletons/python-framework-app-<line>/).

    petstore, Petstore            ${{ values.name }}, ${{ values.title }}
    pet, Pet, pets, Pets          ${{ values.entity }}, ${{ values.entityTitle }}, ${{ values.entities }}, ${{ values.entitiesTitle }}
    species, birth_date           category, start_date      (a text to filter by and an optional date)
    available / pending / sold    active / pending / closed

What is not a plain copy is in tools/python-app-overrides/ (README, CI, catalog entry...), copied
over the result.

One skeleton per maintained line of the Python Framework (LINES below), skeletons/python-framework-app-<line>/:
the same application, built on that line's refresquito-fastapi and refresquito-angular (their packages in
vendor/, downloaded from their GitHub releases with gh when the petstore does not carry them). The template
offers each line in its form.

It also writes skeletons/python-framework-deploy/: the two files the template proposes to
refresquito-services in a pull request to deploy the application (tools/python-app-deploy/: the
file of the application; and the definition of its API, which is the openapi.json of the skeleton). Check a change with tools/render-python-app.py, which renders the skeleton the
way Backstage does and leaves an application whose tests can be run.
"""
import json, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
SKELETONS = HERE.parent / "skeletons"
OUT = SKELETONS / "python-framework-app"          # built here first, then one copy per line
# the maintained lines of the Python Framework (its SUPPORT.md): line -> (refresquito-fastapi, refresquito-angular)
LINES = {"0.1": ("0.1.0", "0.1.0"), "2.0": ("2.0.0", "2.0.0")}
OVERRIDES = HERE / "python-app-overrides"
src = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else sys.exit(__doc__)

V = lambda name: "${{ values.%s }}" % name   # noqa: E731
# entityTitle and entitiesTitle are the capitalized names. They cannot be called Entity and Entities: the
# catalog rejects a template whose keys differ only in case ("duplicate keys that vary only in casing")
RULES = [   # in order: the longer names first
    ("PETSTORE_", "APP_"),
    ("petstore_test", "app_test"),
    ("javivillar/petstore", f"{V('owner')}/{V('name')}"),
    ("Petstore", V("title")),
    ("petstore", V("name")),
    ("Pets", V("entitiesTitle")), ("pets", V("entities")), ("Pet", V("entityTitle")), ("pet", V("entity")),
    ("Date of birth", "Start date"), ("Born", "Starts"), ("Birth", "Start"),
    ("Species", "Category"), ("species", "category"), ("birth_date", "start_date"),
    ("available", "active"), ("sold", "closed"),
    ('"dog"', '"tools"'), ("'dog'", "'tools'"), ('"cat"', '"books"'), ("'cat'", "'books'"), ("dog, cat", "tools, books"),
]
PATHS = [
    ("backend/src/petstore/", f"backend/src/{V('name')}/"),
    ("_pets.py", f"_{V('entities')}.py"),
    ("frontend/src/app/api/pets.ts", f"frontend/src/app/api/{V('entities')}.ts"),
    ("frontend/src/app/pets/pet-", f"frontend/src/app/{V('entities')}/{V('entity')}-"),
    ("platform/processes/petstore-", f"platform/processes/{V('name')}-"),
    # the dashboard export: the names Superset gave its files, made neutral
    ("platform/dashboards/databases/Petstore.yaml", "platform/dashboards/databases/application.yaml"),
    ("platform/dashboards/datasets/Petstore/pet.yaml", f"platform/dashboards/datasets/application/{V('entity')}.yaml"),
    ("platform/dashboards/dashboards/Petstore_1.yaml", "platform/dashboards/dashboards/overview.yaml"),
    ("platform/dashboards/charts/Pets_by_status_1.yaml", "platform/dashboards/charts/by_status.yaml"),
    ("platform/dashboards/charts/Pets_2.yaml", "platform/dashboards/charts/count.yaml"),
    # the example flow: its file names its webhook (ACTIVEPIECES_FLOW_NEW_<ENTITY>_URL)
    ("platform/flows/new-pet.json", f"platform/flows/new-{V('entity')}.json"),
]
BINARY = (".ico", ".whl", ".tgz")
# kept as they are: binaries, the lock file, and what has its own ${...} syntax
VERBATIM = ("vendor/", "frontend/package-lock.json", "backend/migrations/script.py.mako")
# generated when the application is built, or replaced by an override
DROP = ("frontend/src/app/api/schema.ts", "README.md", "CHANGELOG.md", "catalog-info.yaml", ".github/workflows/ci.yml")


def convert(text: str) -> str:
    for old, new in RULES:
        text = text.replace(old, new)
    return text


if OUT.exists():
    shutil.rmtree(OUT)
files = subprocess.run(["git", "-C", str(src), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
for name in files:
    if name in DROP:
        continue
    target = name
    for old, new in PATHS:
        target = target.replace(old, new)
    dest = OUT / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = (src / name).read_bytes()
    if name.endswith(BINARY) or name.startswith(VERBATIM):
        dest.write_bytes(data)
    else:
        dest.write_text(convert(data.decode()))
    shutil.copymode(src / name, dest)

# ---- what differs from the petstore on purpose
# a new application starts at 0.1.0, whatever version the petstore is at
for rel, old_re, new in (("backend/pyproject.toml", r'(?m)^version = "[^"]+"', 'version = "0.1.0"'),
                         (f"backend/src/{V('name')}/__init__.py", r'__version__ = "[^"]+"', '__version__ = "0.1.0"')):
    path = OUT / rel
    text, count = re.subn(old_re, new, path.read_text(), count=1)
    assert count == 1, rel
    path.write_text(text)
# ... and so does its OpenAPI document (its CI checks it matches the code)
api_path = OUT / "backend/openapi.json"
api_text = api_path.read_text()
api_doc = json.loads(api_text)
api_doc["info"]["version"] = "0.1.0"
api_path.write_text(json.dumps(api_doc, indent=2) + ("\n" if api_text.endswith("\n") else ""))
# the API types of the web are generated from backend/openapi.json when it is built, tested or
# served (not committed): a new application starts with whatever entity name it was given
pkg_path = OUT / "frontend/package.json"
pkg = json.loads(pkg_path.read_text())
pkg["name"] = "app-frontend"
pkg["version"] = "0.1.0"
pkg["scripts"].update({"prestart": "npm run gen:api", "prebuild": "npm run gen:api", "pretest": "npm run gen:api"})
pkg["dependencies"]["refresquito-angular"] = "file:../vendor/refresquito-angular-0.1.0.tgz"
pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
lock_path = OUT / "frontend/package-lock.json"
lock = json.loads(lock_path.read_text())
lock["name"] = lock["packages"][""]["name"] = "app-frontend"
lock_path.write_text(json.dumps(lock, indent=2) + "\n")
with (OUT / "frontend/.gitignore").open("a") as f:
    f.write("\n# generated from ../backend/openapi.json (npm run gen:api)\n/src/app/api/schema.ts\n")
docker = OUT / "frontend/Dockerfile"
text = docker.read_text()
old = "COPY frontend ./frontend\n"
assert text.count(old) == 1
text = text.replace(old, "COPY frontend ./frontend\n# the API types are generated from it (npm run gen:api, which 'npm run build' runs first)\nCOPY backend/openapi.json ./backend/openapi.json\n")
# 'npx ng build' would skip the prebuild script, and the types (src/app/api/schema.ts) are not committed
old = "npx ng build"
assert text.count(old) == 1
docker.write_text(text.replace(old, "npm run build"))

# the names of a new application are longer than "pet" and "petstore", so lines that fit in the
# petstore may not fit any more: the line length is not checked (ruff format wraps them when wanted)
py = OUT / "backend/pyproject.toml"
text = py.read_text()
old = 'ignore = ["B008"]\n'
assert text.count(old) == 1
py.write_text(text.replace(old, '# E501: the names given when the application was created can make a line too long\nignore = ["B008", "E501"]\n'))

# ---- overrides
for path in OVERRIDES.rglob("*"):
    if path.is_file():
        dest = OUT / path.relative_to(OVERRIDES)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)

# ---- the deployment: what the template proposes to refresquito-services in a pull request
DEPLOY = OUT.parent / "python-framework-deploy"
if DEPLOY.exists():
    shutil.rmtree(DEPLOY)
shutil.copytree(HERE / "python-app-deploy", DEPLOY)
api = DEPLOY / "catalog" / "apis" / f"{V('name')}.json"
api.parent.mkdir(parents=True)
shutil.copyfile(OUT / "backend" / "openapi.json", api)

# ---- one skeleton per line: the packages of the framework, and what names their versions
import base64, hashlib, tempfile  # noqa: E401,E402


def package(repo: str, name: str) -> bytes:
    """A package of the framework: from the petstore's vendor/ if it has that version, else its GitHub release."""
    local = src / "vendor" / name
    if local.exists():
        return local.read_bytes()
    tag = "v" + re.search(r"(\d+\.\d+\.\d+)", name).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["gh", "release", "download", tag, "-R", f"javivillar/{repo}", "-p", name, "-D", tmp], check=True)
        return (pathlib.Path(tmp) / name).read_bytes()


base_fastapi, base_angular = (re.search(r"refresquito-fastapi\[db\]~=([\d.]+)", (OUT / "backend/pyproject.toml").read_text()).group(1),
                              json.loads((OUT / "frontend/package.json").read_text())["dependencies"]["refresquito-angular"].split("-")[-1][:-4])
AUDIT_SECTION = """## Logs and the audit trail

The API writes two streams, both JSON on stdout, told apart by `log_type`: `application` (its logs and one line per
request) and `audit` (who did what). Every write (`POST`, `PUT`, `PATCH`, `DELETE`) and every refused request (401,
403) is audited by itself, with the user, the route, the outcome and the request ID. What matters to the business is
audited by the code:

```python
from refresquito_fastapi import audit

audit("${{ values.entity }}.archive", resource=f"${{ values.entity }}/{item.id}")
```

On the platform each stream is its own in Loki (`{namespace_name="<namespace>", log_type="audit"}`), and every event
counts in `audit_events_total{action, outcome}` on `/metrics`, scraped by Prometheus. Grafana has both in the
dashboard *Python Framework - Audit*. Never put secrets or personal data you do not need in an event.

"""
for old_dir in SKELETONS.glob("python-framework-app-*"):
    shutil.rmtree(old_dir)
for line, (fastapi, angular) in LINES.items():
    dest = SKELETONS / f"python-framework-app-{line}"
    shutil.copytree(OUT, dest)
    for old in (dest / "vendor").iterdir():
        old.unlink()
    wheel, tgz = f"refresquito_fastapi-{fastapi}-py3-none-any.whl", f"refresquito-angular-{angular}.tgz"
    (dest / "vendor" / wheel).write_bytes(package("refresquito-fastapi", wheel))
    tgz_bytes = package("refresquito-angular", tgz)
    (dest / "vendor" / tgz).write_bytes(tgz_bytes)
    edits = {
        "backend/pyproject.toml": [(f"refresquito-fastapi[db]~={base_fastapi}", f"refresquito-fastapi[db]~={fastapi}")],
        "frontend/package.json": [(f"refresquito-angular-{base_angular}.tgz", tgz)],
        "README.md": [(f"`v{base_fastapi}` tags", f"`v{fastapi}` tags")],
        "CHANGELOG.md": [(f"refresquito-fastapi {base_fastapi} and refresquito-angular {base_angular}",
                          f"refresquito-fastapi {fastapi} and refresquito-angular {angular}")],
    }
    if line != "0.1":
        # from 2.0 on, the audit trail of refresquito-fastapi (the 0.1 README stays as it was)
        edits["README.md"].append(("## `vendor/`", AUDIT_SECTION + "## `vendor/`"))
    for rel, pairs in edits.items():
        path = dest / rel
        text = path.read_text()
        for old, new in pairs:
            assert old in text, (line, rel, old)
            text = text.replace(old, new)
        path.write_text(text)
    lock_path = dest / "frontend/package-lock.json"
    lock = json.loads(lock_path.read_text())
    lock["packages"][""]["dependencies"]["refresquito-angular"] = f"file:../vendor/{tgz}"
    entry = lock["packages"]["node_modules/refresquito-angular"]
    entry.update(version=angular, resolved=f"file:../vendor/{tgz}",
                 integrity="sha512-" + base64.b64encode(hashlib.sha512(tgz_bytes).digest()).decode())
    lock_path.write_text(json.dumps(lock, indent=2) + "\n")
    print(f"skeleton of the line {line}: refresquito-fastapi {fastapi}, refresquito-angular {angular}")

left = [str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file() and not str(p.relative_to(OUT)).startswith(VERBATIM)
        and p.suffix not in BINARY and "pet" in p.read_text(errors="ignore").lower().replace("perpetual", "")]
print(f"{len(list(OUT.rglob('*')))} entries in {OUT.relative_to(HERE.parent)}")
print("files that still say 'pet':", left or "none")
shutil.rmtree(OUT)   # only the skeletons of the lines stay
