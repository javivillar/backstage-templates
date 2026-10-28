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

One skeleton per maintained line of the Python Framework (LINES below), skeletons/python-framework-app-<line>/. The
petstore runs on the newest line, so only that one is generated from it; the skeletons of the older lines stay as
they were committed (an older line gets no new features). The template offers each line in its form.

From 3.0 the petstore uses every platform block in its code, one file per block (backend module and test, frontend
component and spec) and one line per block in the files they share. The skeleton keeps a block's files and lines only
when the template marks the block (BLOCKS below): a file whose name renders empty is not created by fetch:template.
backend/openapi.json is composed the same way, from the OpenAPI the petstore publishes with and without each block.

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
LINES = {"0.1": ("0.1.0", "0.1.0"), "2.0": ("2.0.0", "2.0.0"), "3.0": ("3.0.1", "3.0.0"), "3.1": ("3.1.2", "3.1.1"),
         "3.2": ("3.2.0", "3.2.0"), "3.3": ("3.3.0", "3.3.1")}
# from 3.2 the framework has its database, refresquito-postgres: the Dockerfile of its release goes to
# vendor/refresquito-postgres-<version>/ (the image is private: compose.yaml and the CI build it from there)
POSTGRES = {"3.2": "3.2.0", "3.3": "3.3.0"}
NEWEST = max(LINES, key=lambda line: tuple(int(n) for n in line.split(".")))
OVERRIDES = HERE / "python-app-overrides"
src = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else sys.exit(__doc__)

V = lambda name: "${{ values.%s }}" % name   # noqa: E731
# entityTitle and entitiesTitle are the capitalized names. They cannot be called Entity and Entities: the
# catalog rejects a template whose keys differ only in case ("duplicate keys that vary only in casing")
RULES = [   # in order: the longer names first
    # 3.3: the icons of the petstore in <rq-shell> (Bootstrap Icons) are about pets: neutral ones for any application
    ('icon="heart-fill"', 'icon="grid-3x3-gap-fill"'), ("icon: 'heart'", "icon: 'collection'"),
    ('<i class="bi bi-heart-fill" aria-hidden="true"></i>', '<i class="bi bi-grid-3x3-gap-fill" aria-hidden="true"></i>'),
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
# ---- the platform blocks in the code (3.0): the template value that marks each one
BLOCKS = {"processes": "values.processes", "flows": "values.flows", "s3": "(values.buckets | length) > 0",
          "dms": "(values.sites | length) > 0", "dashboards": "values.dashboards"}
# the files of one block, by their path in the petstore
BLOCK_FILES = {
    "backend/src/petstore/review.py": "processes", "backend/tests/test_review.py": "processes",
    "frontend/src/app/pets/pet-review.ts": "processes", "frontend/src/app/pets/pet-review.spec.ts": "processes",
    "frontend/src/app/pages/tasks.ts": "processes", "frontend/src/app/pages/tasks.spec.ts": "processes",
    "backend/src/petstore/welcome.py": "flows", "backend/tests/test_welcome.py": "flows",
    "frontend/src/app/pets/pet-welcome.ts": "flows", "frontend/src/app/pets/pet-welcome.spec.ts": "flows",
    "backend/src/petstore/files.py": "s3", "backend/tests/test_files.py": "s3",
    "frontend/src/app/pets/pet-files.ts": "s3", "frontend/src/app/pets/pet-files.spec.ts": "s3",
    "backend/src/petstore/documents.py": "dms", "backend/tests/test_documents.py": "dms",
    "frontend/src/app/pets/pet-documents.ts": "dms", "frontend/src/app/pets/pet-documents.spec.ts": "dms",
    # 3.1: the runs of its flows (a page), and the block dashboards (its dashboard embedded, the data of its dataset)
    "frontend/src/app/pages/flows.ts": "flows", "frontend/src/app/pages/flows.spec.ts": "flows",
    "backend/src/petstore/dashboards.py": "dashboards", "backend/tests/test_dashboards.py": "dashboards",
    "frontend/src/app/pages/dashboard.ts": "dashboards", "frontend/src/app/pages/dashboard.spec.ts": "dashboards",
}
# the lines of one block in the files they share: (file, text of the line, block). A line that is only a comment
# naming the block ("// block processes: ...") takes the next line with it.
BLOCK_LINES = [
    ("backend/src/petstore/main.py", "from .review import", "processes"),
    ("backend/src/petstore/main.py", "from .welcome import", "flows"),
    ("backend/src/petstore/main.py", "from .files import", "s3"),
    ("backend/src/petstore/main.py", "from .documents import", "dms"),
    ("backend/src/petstore/main.py", "# block processes", "processes"),
    ("backend/src/petstore/main.py", "# block flows", "flows"),
    ("backend/src/petstore/main.py", "# block s3", "s3"),
    ("backend/src/petstore/main.py", "# block dms", "dms"),
    ("backend/tests/conftest.py", "# block processes", "processes"),
    ("backend/tests/conftest.py", "# block flows", "flows"),
    ("backend/tests/conftest.py", "# block s3", "s3"),
    ("backend/tests/conftest.py", "# block dms", "dms"),
    ("frontend/src/app/pets/pet-detail.ts", "from './pet-review'", "processes"),
    ("frontend/src/app/pets/pet-detail.ts", "from './pet-welcome'", "flows"),
    ("frontend/src/app/pets/pet-detail.ts", "from './pet-files'", "s3"),
    ("frontend/src/app/pets/pet-detail.ts", "from './pet-documents'", "dms"),
    ("frontend/src/app/pets/pet-detail.ts", "// block processes", "processes"),
    ("frontend/src/app/pets/pet-detail.ts", "// block flows", "flows"),
    ("frontend/src/app/pets/pet-detail.ts", "// block s3", "s3"),
    ("frontend/src/app/pets/pet-detail.ts", "// block dms", "dms"),
    ("frontend/src/app/pets/pet-detail.html", "<app-pet-review", "processes"),
    ("frontend/src/app/pets/pet-detail.html", "<app-pet-welcome", "flows"),
    ("frontend/src/app/pets/pet-detail.html", "<app-pet-files", "s3"),
    ("frontend/src/app/pets/pet-detail.html", "<app-pet-documents", "dms"),
    ("frontend/src/app/app.routes.ts", "from './pages/tasks'", "processes"),
    ("frontend/src/app/app.routes.ts", "// block processes", "processes"),
    ("frontend/src/app/app.ts", "link: '/tasks'", "processes"),
    # 3.1
    ("backend/src/petstore/main.py", "from .dashboards import", "dashboards"),
    ("backend/src/petstore/main.py", "# block dashboards", "dashboards"),
    ("backend/src/petstore/api.py", "# block flows", "flows"),
    ("backend/tests/conftest.py", "# block dashboards", "dashboards"),
    ("frontend/src/app/app.routes.ts", "from './pages/dashboard'", "dashboards"),
    ("frontend/src/app/app.routes.ts", "from './pages/flows'", "flows"),
    ("frontend/src/app/app.routes.ts", "// block dashboards", "dashboards"),
    ("frontend/src/app/app.routes.ts", "// block flows", "flows"),
    ("frontend/src/app/app.ts", "link: '/dashboard'", "dashboards"),
    ("frontend/src/app/app.ts", "link: '/flows'", "flows"),
    # 3.1.2: the lineage of each operation in the OpenAPI, one line per block
    ("backend/tests/test_lineage.py", '{pet_id}/review"', "processes"),
    ("backend/tests/test_lineage.py", '{pet_id}/welcome"', "flows"),
    ("backend/tests/test_lineage.py", '{pet_id}/files"', "s3"),
    ("backend/tests/test_lineage.py", '{pet_id}/documents"', "dms"),
]
# the names a block uses that the template asks for: the first bucket and the first site declared
BLOCK_NAMES = [
    ("backend/src/petstore/files.py", 'BUCKET = "files"', 'BUCKET = "${{ values.buckets[0] }}"'),
    ("backend/src/petstore/documents.py", 'SITE = "documents"', 'SITE = "${{ values.sites[0] }}"'),
    ("backend/tests/conftest.py", 'FakeStorage(["files"],', 'FakeStorage(["${{ values.buckets[0] if values.buckets | length else \'files\' }}"],'),
    ("backend/tests/conftest.py", 'FakeDocuments(["documents"],', 'FakeDocuments(["${{ values.sites[0] if values.sites | length else \'documents\' }}"],'),
    ("backend/tests/test_files.py", "/petstore-files/", "/petstore-${{ values.buckets[0] }}/"),
    ("backend/tests/test_files.py", 'storage.bucket("files")', 'storage.bucket("${{ values.buckets[0] }}")'),
    # 3.1: the block flows in the code the blocks share (the event of a new entity, the page of the runs of its flows)
    ("backend/src/petstore/api.py", ", flows: FlowsDep) -> PetOut:", "{% if values.flows %}, flows: FlowsDep{% endif %}) -> PetOut:"),
    ("backend/src/petstore/main.py", "from .api import ADMIN, VIEWER, router", "from .api import {% if values.flows %}ADMIN, VIEWER, {% endif %}router"),
    ("backend/tests/test_lineage.py", '["bucket:files"]', '["bucket:${{ values.buckets[0] }}"]'),
    ("backend/tests/test_lineage.py", '["site:documents"]', '["site:${{ values.sites[0] }}"]'),
    ("backend/pyproject.toml", '"refresquito-fastapi[db,s3]', '"refresquito-fastapi[db${{ \',s3\' if values.buckets | length else \'\' }}]'),
]


def wrap_lines(rel: str, text: str) -> str:
    """The lines of BLOCK_LINES of this file, each one kept only when its block is marked."""
    lines = text.split("\n")
    out, i = [], 0
    rules = [(needle, block) for path, needle, block in BLOCK_LINES if path == rel]
    used = set()
    while i < len(lines):
        line = lines[i]
        match = next(((n, b) for n, b in rules if n in line), None)
        if match is None:
            out.append(line)
            i += 1
            continue
        used.add(match[0])
        take = 2 if line.strip().startswith(("//", "#")) and line.strip().lstrip("/# ").startswith("block") else 1
        out += [f"{{%- if {BLOCKS[match[1]]} %}}", *lines[i:i + take], "{%- endif %}"]
        i += take
    missing = {n for n, _ in rules} - used
    assert not missing, f"{rel}: lines not found: {missing}"
    return "\n".join(out)


def block_name(name: str, block: str) -> str:
    """The name of a block's file, empty when the block is not marked (fetch:template then skips the file)."""
    parts = re.split(r"(\$\{\{ values\.\w+ \}\})", name)
    expr = " + ".join(f"values.{m.group(1)}" if (m := re.fullmatch(r"\$\{\{ values\.(\w+) \}\}", part)) else repr(part)
                      for part in parts if part)
    return f"${{{{ ({expr}) if {BLOCKS[block]} else '' }}}}"


BINARY = (".ico", ".whl", ".tgz")
# kept as they are: binaries, the lock file, and what has its own ${...} syntax
VERBATIM = ("vendor/", "frontend/package-lock.json", "backend/migrations/script.py.mako")
# generated when the application is built, or replaced by an override
DROP = ("frontend/src/app/api/schema.ts", "README.md", "CHANGELOG.md", "catalog-info.yaml", ".github/workflows/ci.yml")


ROUTERS = {"processes": "review", "flows": "welcome", "s3": "files", "dms": "documents", "dashboards": "dashboards"}


def openapi_of(blocks: list[str]) -> dict:
    """The OpenAPI the petstore publishes with these blocks only (its backend venv, as its own openapi.py builds it)."""
    code = (
        "import json, importlib, sys\n"
        "from refresquito_fastapi import Settings, create_app\n"
        "from petstore import __version__\n"
        "from petstore.api import ADMIN, VIEWER, router\n"
        "routers = [router] + [importlib.import_module(f'petstore.{m}').router for m in sys.argv[1:]]\n"
        "app = create_app(Settings(app_name='petstore', log_level='ERROR'), title='Petstore API', version=__version__,\n"
        "                 routers=routers, docs_url='/api/docs', openapi_url='/api/openapi.json',\n"
        "                 flow_runs=(VIEWER, ADMIN) if 'welcome' in sys.argv[1:] else None)\n"
        "print(json.dumps(app.openapi()))\n")
    python = src / "backend/.venv/bin/python"
    out = subprocess.run([str(python), "-c", code, *(ROUTERS[b] for b in blocks)], cwd=src / "backend",
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def openapi_by_blocks() -> str:
    """backend/openapi.json as a template: the paths and schemas of a block only when it is marked. Each object lists
    the entries of the blocks first, each one followed by a comma, and its own entries last: valid JSON whatever is
    marked."""
    full = openapi_of(list(BLOCKS))
    assert full == json.loads((src / "backend/openapi.json").read_text()), \
        "openapi_of() does not build what the petstore publishes (backend/openapi.json): keep it in step with main.py"
    base = openapi_of([])
    alone = {b: openapi_of([b]) for b in BLOCKS}
    full["info"]["version"] = "0.1.0"   # a new application starts at 0.1.0

    def condition(section: str, key: str) -> str | None:
        if key in base[section] if section == "paths" else key in base["components"]["schemas"]:
            return None
        owners = [b for b in BLOCKS if key in (alone[b]["paths"] if section == "paths" else alone[b]["components"]["schemas"])]
        assert owners, (section, key)
        return " or ".join(f"({BLOCKS[b]})" for b in owners)

    def entries(section: str, items: dict, indent: str) -> str:
        conditional = [(k, v, condition(section, k)) for k, v in items.items() if condition(section, k)]
        own = [(k, v) for k, v in items.items() if not condition(section, k)]
        assert own, f"{section}: the last entry must not depend on a block"
        body = lambda k, v: indent + json.dumps(k) + ": " + json.dumps(v, indent=2, sort_keys=True).replace("\n", "\n" + indent)  # noqa: E731
        text = [f"{{%- if {cond} %}}\n" + body(k, v) + ",\n{%- endif %}" for k, v, cond in conditional]
        text += [body(k, v) + ("," if i < len(own) - 1 else "") for i, (k, v) in enumerate(own)]
        return "\n".join(text)

    rest = {k: v for k, v in full.items() if k not in ("paths", "components")}
    components = {k: v for k, v in full["components"].items() if k != "schemas"}
    head = json.dumps(rest, indent=2, sort_keys=True)[:-2] + ",\n"
    parts = [head, '  "components": {\n']
    for k, v in components.items():
        parts.append("    " + json.dumps(k) + ": " + json.dumps(v, indent=2, sort_keys=True).replace("\n", "\n    ") + ",\n")
    parts += ['    "schemas": {\n', entries("schemas", full["components"]["schemas"], "      "), "\n    }\n  },\n",
              '  "paths": {\n', entries("paths", full["paths"], "    "), "\n  }\n}\n"]
    return "".join(parts)


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
    if name in BLOCK_FILES:
        head, _, base = target.rpartition("/")
        target = f"{head}/{block_name(base, BLOCK_FILES[name])}"
    dest = OUT / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    data = (src / name).read_bytes()
    if name.endswith(BINARY) or name.startswith(VERBATIM):
        dest.write_bytes(data)
    else:
        text = data.decode()
        for path, old, new in BLOCK_NAMES:
            if path == name:
                assert text.count(old) == 1, (name, old)
                text = text.replace(old, new)
        dest.write_text(convert(wrap_lines(name, text)))
    shutil.copymode(src / name, dest)

# ---- what differs from the petstore on purpose
# a new application starts at 0.1.0, whatever version the petstore is at
for rel, old_re, new in (("backend/pyproject.toml", r'(?m)^version = "[^"]+"', 'version = "0.1.0"'),
                         (f"backend/src/{V('name')}/__init__.py", r'__version__ = "[^"]+"', '__version__ = "0.1.0"')):
    path = OUT / rel
    text, count = re.subn(old_re, new, path.read_text(), count=1)
    assert count == 1, rel
    path.write_text(text)
# ... and so does its OpenAPI document (its CI checks it matches the code, as JSON): composed by blocks
api_path = OUT / "backend/openapi.json"
api_text = convert(openapi_by_blocks())
# the lineage of the blocks s3 and dms names the bucket and the site the application was given (files.py and
# documents.py use the first one), not the petstore's: its CI compares this file with what the code publishes
for old, new in (('"bucket:files"', '"bucket:${{ values.buckets[0] }}"'), ('"site:documents"', '"site:${{ values.sites[0] }}"')):
    assert old in api_text, old
    api_text = api_text.replace(old, new)
api_path.write_text(api_text)
# the API types of the web are generated from backend/openapi.json when it is built, tested or
# served (not committed): a new application starts with whatever entity name it was given
pkg_path = OUT / "frontend/package.json"
pkg = json.loads(pkg_path.read_text())
pkg["name"] = "app-frontend"
pkg["version"] = "0.1.0"
pkg["scripts"].update({"prestart": "npm run gen:api", "prebuild": "npm run gen:api", "pretest": "npm run gen:api"})
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


base_fastapi, base_angular = (re.search(r"refresquito-fastapi\[[^\]]*\]~=([\d.]+)", (OUT / "backend/pyproject.toml").read_text()).group(1),
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
for line, (fastapi, angular) in LINES.items():
    dest = SKELETONS / f"python-framework-app-{line}"
    if line != NEWEST:
        assert dest.is_dir(), f"the skeleton of the line {line} is not committed (only {NEWEST} is generated)"
        continue
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(OUT, dest)
    for old in (dest / "vendor").iterdir():
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    if line in POSTGRES:
        pg = POSTGRES[line]
        local = src / "vendor" / f"refresquito-postgres-{pg}" / "Dockerfile"
        (dest / "vendor" / f"refresquito-postgres-{pg}").mkdir()
        (dest / "vendor" / f"refresquito-postgres-{pg}" / "Dockerfile").write_bytes(
            local.read_bytes() if local.exists() else package("refresquito-postgres", f"refresquito-postgres-v{pg}.Dockerfile"))
    wheel, tgz = f"refresquito_fastapi-{fastapi}-py3-none-any.whl", f"refresquito-angular-{angular}.tgz"
    (dest / "vendor" / wheel).write_bytes(package("refresquito-fastapi", wheel))
    tgz_bytes = package("refresquito-angular", tgz)
    (dest / "vendor" / tgz).write_bytes(tgz_bytes)
    edits = {
        "backend/pyproject.toml": [(f"]~={base_fastapi}", f"]~={fastapi}")],
        "frontend/package.json": [(f"refresquito-angular-{base_angular}.tgz", tgz)],
        "README.md": [],
    }
    # the versions it is built with (the CHANGELOG comes from python-app-overrides/, whatever version it names)
    changelog = dest / "CHANGELOG.md"
    text, count = re.subn(r"refresquito-fastapi \d+\.\d+\.\d+ and refresquito-angular \d+\.\d+\.\d+",
                          f"refresquito-fastapi {fastapi} and refresquito-angular {angular}", changelog.read_text())
    assert count == 1, (line, "CHANGELOG.md", count)
    changelog.write_text(text)
    # the audit trail of refresquito-fastapi (since 2.0)
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
