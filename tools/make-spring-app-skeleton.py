#!/usr/bin/env python3
"""make-spring-app-skeleton.py — the skeleton of the template "New application (Spring Framework)".

    python3 tools/make-spring-app-skeleton.py ~/petstore-spring

The same as make-python-app-skeleton.py, for the Spring Framework: the skeleton is NOT written by hand, it is
petstore-spring (github.com/javivillar/petstore-spring), the reference application of the framework, with its names
turned into template values. Run this again when petstore-spring changes, and commit the result
(skeletons/spring-framework-app-<line>/ and skeletons/spring-framework-deploy/).

    petshop, Pet Shop             ${{ values.name }}, ${{ values.title }}
    pet, Pet, pets, Pets          ${{ values.entity }}, ${{ values.entityTitle }}, ${{ values.entities }}, ${{ values.entitiesTitle }}
    species, birth_date           category, start_date      (a text to filter by and an optional date)
    available / pending / sold    active / pending / closed

The application it makes has the service of its entity (services/<entities>: its API and the platform blocks) and
the service notifier (it handles the events of the other). The service adoptions of petstore-spring, its page and its
button are an example of a call between services about pets: they are left out (DROP, DROP_LINES).

The platform blocks work as in the Python skeleton: a block's files (its controller and its test class, its web
components) and its lines in the files they share are kept only when the template marks the block (BLOCKS), and the
openapi.json of the service is composed by blocks from the one petstore-spring publishes (each operation belongs to
the block of its controller: its operationId is <controller>_<method>).

What is not a plain copy is in tools/spring-app-overrides/ (README, catalog entry, release notes, CODEOWNERS...),
copied over the result. The deployment the template proposes to refresquito-services is tools/spring-app-deploy/ plus
the openapi.json of the service, in skeletons/spring-framework-deploy/. Check a change with
tools/render-spring-app.py, which renders the skeleton the way Backstage does and leaves an application whose tests
can be run.
"""
import json, pathlib, re, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
SKELETONS = HERE.parent / "skeletons"
OUT = SKELETONS / "spring-framework-app"           # built here first, then one copy per line
# the maintained lines of the Spring Framework: line -> the versions of its parts (refresquito-spring-boot in vendor/maven)
LINES = {"1.0": {"spring": "1.0.0-SNAPSHOT", "angular": "3.3.1", "postgres": "3.3.0"}}
NEWEST = max(LINES, key=lambda line: tuple(int(n) for n in line.split(".")))
OVERRIDES = HERE / "spring-app-overrides"
src = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else sys.exit(__doc__)

V = lambda name: "${{ values.%s }}" % name   # noqa: E731
PKG = "services/pets/src/main/java/io/refresquito/petshop/pets/"
TEST = "services/pets/src/test/java/io/refresquito/petshop/pets/"
RULES = [   # in order: the longer names first
    # the icons of the petstore in <rq-shell> (Bootstrap Icons) are about pets: neutral ones for any application
    ('icon="shop"', 'icon="grid-3x3-gap-fill"'), ("icon: 'heart'", "icon: 'collection'"),
    ('<i class="bi bi-heart-fill" aria-hidden="true"></i>', '<i class="bi bi-grid-3x3-gap-fill" aria-hidden="true"></i>'),
    ("javivillar/petstore-spring", f"{V('owner')}/{V('name')}"),
    ("petstore-spring", V("name")),
    ("Pet Shop", V("title")), ("Petshop", V("title")), ("Petstore", V("title")),
    ("petshop", V("name")), ("petstore", V("name")),
    ("Pets", V("entitiesTitle")), ("pets", V("entities")), ("Pet", V("entityTitle")), ("pet", V("entity")),
    ("species=dog", "category=tools"),     # a filter in a URL of a test
    ("Date of birth", "Start date"), ("Born", "Starts"), ("born", "starts"), ("BirthDate", "StartDate"), ("birthDate", "startDate"),
    ("Birth", "Start"), ("Species", "Category"), ("species", "category"), ("birth_date", "start_date"),
    # whole words only: not ServiceUnavailable of the framework
    (re.compile(r"\bavailable\b"), "active"), (re.compile(r"\bsold\b"), "closed"),
    ('"dog"', '"tools"'), ("'dog'", "'tools'"), ('"cat"', '"books"'), ("'cat'", "'books'"), ("dog, cat", "tools, books"),
]
PATHS = [
    # the dashboard export: the names Superset gave its files, made neutral (as in the Python skeleton)
    ("platform/dashboards/databases/Petshop.yaml", "platform/dashboards/databases/application.yaml"),
    ("platform/dashboards/datasets/Petshop/pet.yaml", f"platform/dashboards/datasets/application/{V('entity')}.yaml"),
    ("platform/dashboards/dashboards/Petshop_1.yaml", "platform/dashboards/dashboards/overview.yaml"),
    ("platform/dashboards/charts/Pets_by_status_1.yaml", "platform/dashboards/charts/by_status.yaml"),
    ("platform/dashboards/charts/Pets_2.yaml", "platform/dashboards/charts/count.yaml"),
]
# ---- left out: the service adoptions and what is about it; generated or replaced by an override
DROP = ("services/adoptions/", PKG + "AdoptionEvents.java", TEST + "AdoptionEventsTest.java",
        "frontend/src/app/api/adoptions.ts", "frontend/src/app/pages/adoptions.ts", "frontend/src/app/pages/adoptions.spec.ts",
        "frontend/src/app/pets/pet-adopt.ts", "frontend/src/app/pets/pet-adopt.spec.ts",
        "frontend/src/app/api/pets-schema.ts", "frontend/src/app/api/adoptions-schema.ts",
        "README.md", "CHANGELOG.md", "catalog-info.yaml")
# lines about adoptions in the files that stay: (file, the line it starts at, how many lines; "}" = to the end of the
# method it starts, and the blank line after it), dropping also the lines before it (`before`)
DROP_LINES = [
    ("pom.xml", "<module>services/adoptions</module>", 1, 0),
    ("services/Dockerfile", "services/adoptions/pom.xml", 1, 0),
    ("dev/initdb/10-services.sql", "CREATE USER adoptions", 2, 0),
    ("frontend/src/app/app.routes.ts", "import { Adoptions }", 1, 0),
    ("frontend/src/app/app.routes.ts", "// the service adoptions", 2, 0),
    ("frontend/src/app/app.ts", "link: '/adoptions'", 1, 0),
    ("frontend/src/app/pets/pet-detail.ts", "import { PetAdopt }", 1, 0),
    ("frontend/src/app/pets/pet-detail.ts", "PetAdopt, // the service adoptions", 1, 0),
    ("frontend/src/app/pets/pet-detail.ts", "/** Asked for: pets marks it pending", 4, 1),
    ("frontend/src/app/pets/pet-detail.html", "@if (p.status === 'available') {", 3, 0),
    ("frontend/src/styles.scss", ".status-requested", 3, 0),
    ("services/notifier/src/main/java/io/refresquito/petshop/notifier/Notices.java", "// the service adoptions", "}", 0),
    ("services/notifier/src/test/java/io/refresquito/petshop/notifier/NoticesTest.java", "void an_adoption_approved_is_a_notice", "}", 1),
]
EDITS = [   # (file, old, new): words about adoptions in lines that stay
    ("services/notifier/src/main/java/io/refresquito/petshop/notifier/Notices.java",
     "a new pet and a change of status for everyone, an adoption for its\n * adopter. In the transaction",
     "a new pet and a change of status, for everyone. In\n * the transaction"),
    ("services/notifier/src/test/java/io/refresquito/petshop/notifier/NoticesTest.java",
     "the events that pets and adoptions publish", "the events that pets publishes"),
]
# ---- the platform blocks in the code: the template value that marks each one
BLOCKS = {"processes": "values.processes", "flows": "values.flows", "s3": "(values.buckets | length) > 0",
          "dms": "(values.sites | length) > 0", "dashboards": "values.dashboards"}
# the controller of each block (its operations in the OpenAPI are <controller>_<method>)
CONTROLLERS = {"review": "processes", "welcome": "flows", "files": "s3", "documents": "dms", "dashboards": "dashboards"}
BLOCK_FILES = {
    PKG + "ReviewController.java": "processes", TEST + "ReviewTest.java": "processes",
    PKG + "WelcomeController.java": "flows", TEST + "WelcomeTest.java": "flows",
    PKG + "FilesController.java": "s3", TEST + "FilesTest.java": "s3",
    PKG + "DocumentsController.java": "dms", TEST + "DocumentsTest.java": "dms",
    PKG + "DashboardsController.java": "dashboards", TEST + "DashboardsTest.java": "dashboards",
    # the web: the same files as the petstore's (make-python-app-skeleton.py)
    "frontend/src/app/pets/pet-review.ts": "processes", "frontend/src/app/pets/pet-review.spec.ts": "processes",
    "frontend/src/app/pages/tasks.ts": "processes", "frontend/src/app/pages/tasks.spec.ts": "processes",
    "frontend/src/app/pets/pet-welcome.ts": "flows", "frontend/src/app/pets/pet-welcome.spec.ts": "flows",
    "frontend/src/app/pages/flows.ts": "flows", "frontend/src/app/pages/flows.spec.ts": "flows",
    "frontend/src/app/pets/pet-files.ts": "s3", "frontend/src/app/pets/pet-files.spec.ts": "s3",
    "frontend/src/app/pets/pet-documents.ts": "dms", "frontend/src/app/pets/pet-documents.spec.ts": "dms",
    "frontend/src/app/pages/dashboard.ts": "dashboards", "frontend/src/app/pages/dashboard.spec.ts": "dashboards",
}
# the lines of one block in the files they share. A line that is only a comment naming the block ("// block s3")
# takes the next line with it.
BLOCK_LINES = [
    (TEST + "PetsTest.java", "// block s3", "s3"),
    (TEST + "PetsTest.java", "// block processes", "processes"),
    (TEST + "PetsTest.java", "// block dms", "dms"),
    (TEST + "PetsTest.java", "// block flows", "flows"),
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
    ("frontend/src/app/app.routes.ts", "from './pages/dashboard'", "dashboards"),
    ("frontend/src/app/app.routes.ts", "from './pages/flows'", "flows"),
    ("frontend/src/app/app.routes.ts", "// block processes", "processes"),
    ("frontend/src/app/app.routes.ts", "// block dashboards", "dashboards"),
    ("frontend/src/app/app.routes.ts", "// block flows", "flows"),
    ("frontend/src/app/app.ts", "link: '/tasks'", "processes"),
    ("frontend/src/app/app.ts", "link: '/dashboard'", "dashboards"),
    ("frontend/src/app/app.ts", "link: '/flows'", "flows"),
]
# the names a block uses that the template asks for: the first bucket and the first site declared
BLOCK_NAMES = [
    (PKG + "FilesController.java", 'BUCKET = "files"', 'BUCKET = "${{ values.buckets[0] }}"'),
    (PKG + "DocumentsController.java", 'SITE = "documents"', 'SITE = "${{ values.sites[0] }}"'),
    (TEST + "FilesTest.java", 'storage.bucket("files")', 'storage.bucket("${{ values.buckets[0] }}")'),
    (TEST + "DocumentsTest.java", 'documents.site("documents")', 'documents.site("${{ values.sites[0] }}")'),
    (TEST + "PetsTest.java", '"\\"bucket:files\\""', '"\\"bucket:${{ values.buckets[0] }}\\""'),
    (TEST + "PetsTest.java", '"\\"site:documents\\""', '"\\"site:${{ values.sites[0] }}\\""'),
]
# ... and everywhere in the controller of its block (its @Lineage): the OpenAPI the service publishes says them
LINEAGE_NAMES = [
    (PKG + "FilesController.java", '"bucket:files"', '"bucket:${{ values.buckets[0] }}"'),
    (PKG + "DocumentsController.java", '"site:documents"', '"site:${{ values.sites[0] }}"'),
]
BINARY = (".ico", ".jar", ".tgz", ".sha1", ".md5")
# kept as they are: binaries, the framework, the lock file, and what has its own ${{ }} syntax (GitHub Actions)
VERBATIM = ("vendor/", "frontend/package-lock.json", ".github/workflows/", ".github/quality.py")


def drop_lines(rel: str, text: str) -> str:
    lines = text.split("\n")
    for path, needle, count, before in DROP_LINES:
        if path != rel:
            continue
        at = [i for i, line in enumerate(lines) if needle in line]
        assert len(at) == 1, (rel, needle, len(at))
        start = at[0]
        if count == "}":       # a method of a class: to its closing brace, at the indentation of a member
            end = next(i for i in range(start + 1, len(lines)) if lines[i] == "    }") + 1
            if end < len(lines) and not lines[end].strip():
                end += 1
        else:
            end = start + count
        del lines[start - before:end]
    return "\n".join(lines)


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


def convert(text: str) -> str:
    for old, new in RULES:
        text = old.sub(new, text) if isinstance(old, re.Pattern) else text.replace(old, new)
    return text


def openapi_by_blocks(full: dict) -> str:
    """openapi.json of the service as a template: the operations of a block's controller (operationId
    <controller>_<method>) and the schemas only they use, each one only when the block is marked. Each object lists
    the entries of the blocks first, each one followed by a comma, and its own entries last: valid JSON whatever is
    marked (the test of the service compares it as JSON with what the service publishes)."""
    def block_of(operation: dict) -> str | None:
        return CONTROLLERS.get(operation.get("operationId", "").split("_")[0])

    def refs(node, out: set) -> set:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "$ref" and isinstance(v, str):
                    out.add(v.rsplit("/", 1)[-1])
                else:
                    refs(v, out)
        elif isinstance(node, list):
            for v in node:
                refs(v, out)
        return out

    def closure(names: set) -> set:
        schemas = full["components"]["schemas"]
        todo, seen = list(names), set()
        while todo:
            n = todo.pop()
            if n not in seen:
                seen.add(n)
                todo += refs(schemas.get(n, {}), set())
        return seen

    path_blocks = {}
    for path, item in full["paths"].items():
        blocks = {block_of(op) for op in item.values() if isinstance(op, dict)}
        assert len(blocks) == 1, (path, blocks)          # a path belongs to one controller
        path_blocks[path] = blocks.pop()
    base = closure(refs({p: v for p, v in full["paths"].items() if path_blocks[p] is None}, set()))
    owners = {}
    for b in BLOCKS:
        for name in closure(refs({p: v for p, v in full["paths"].items() if path_blocks[p] == b}, set())) - base:
            owners.setdefault(name, []).append(b)

    def condition(section: str, key: str) -> str | None:
        found = [path_blocks[key]] if section == "paths" and path_blocks[key] else owners.get(key, []) if section == "schemas" else []
        return " or ".join(f"({BLOCKS[b]})" for b in found) or None

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


if OUT.exists():
    shutil.rmtree(OUT)
files = subprocess.run(["git", "-C", str(src), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
for name in files:
    if name.startswith(DROP):
        continue
    target = name
    for old, new in PATHS:
        target = target.replace(old, new)
    if not name.startswith(VERBATIM):
        target = convert(target)
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
        for path, old, new in EDITS:
            if path == name:
                assert text.count(old) == 1, (name, old)
                text = text.replace(old, new)
        for path, old, new in LINEAGE_NAMES:
            if path == name:
                assert old in text, (name, old)
                text = text.replace(old, new)
        for path, old, new in BLOCK_NAMES:
            if path == name:
                assert text.count(old) == 1, (name, old)
                text = text.replace(old, new)
        dest.write_text(convert(wrap_lines(name, drop_lines(name, text))))
    shutil.copymode(src / name, dest)

# ---- what differs from petstore-spring on purpose
entities = f"services/{V('entities')}"
# the OpenAPI of the service, composed by blocks; the lineage of the blocks s3 and dms names the bucket and the site
# the application was given (its controllers use the first one)
published = json.loads((src / "services/pets/openapi.json").read_text())


def sort_required(node):
    """The framework lists the required fields of a schema sorted: sorted again by their new names (category...)."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "required" and isinstance(v, list) and all(isinstance(x, str) for x in v):
                node[k] = sorted(convert(x) for x in v)
            else:
                sort_required(v)
    elif isinstance(node, list):
        for v in node:
            sort_required(v)


sort_required(published)
api_text = convert(openapi_by_blocks(published))
# the title the framework gives: "<app> API: <service>", or "<app> API" when the service is named as the application
for old, new in (('"bucket:files"', '"bucket:${{ values.buckets[0] }}"'), ('"site:documents"', '"site:${{ values.sites[0] }}"'),
                 ('"title": "${{ values.name }} API: ${{ values.entities }}"',
                  '"title": "${{ values.name }} API{% if values.name != values.entities %}: ${{ values.entities }}{% endif %}"')):
    assert old in api_text, old
    api_text = api_text.replace(old, new)
(OUT / entities / "openapi.json").write_text(api_text)
# the API types of the web are generated from the openapi.json of the service when it is built, tested or served
# (not committed): a new application starts with whatever entity name it was given
pkg_path = OUT / "frontend/package.json"
pkg = json.loads(pkg_path.read_text())
pkg["name"] = "app-frontend"
pkg["version"] = "0.1.0"
pkg["scripts"]["gen:api"] = f"openapi-typescript ../{entities}/openapi.json -o src/app/api/{V('entities')}-schema.ts"
pkg["scripts"].update({"prestart": "npm run gen:api", "prebuild": "npm run gen:api", "pretest": "npm run gen:api"})
pkg_path.write_text(json.dumps(pkg, indent=2) + "\n")
lock_path = OUT / "frontend/package-lock.json"
lock = json.loads(lock_path.read_text())
lock["name"] = lock["packages"][""]["name"] = "app-frontend"
lock_path.write_text(json.dumps(lock, indent=2) + "\n")
with (OUT / "frontend/.gitignore").open("a") as f:
    f.write("\n# generated from ../services/*/openapi.json (npm run gen:api)\n/src/app/api/*-schema.ts\n")
docker = OUT / "frontend/Dockerfile"
text = docker.read_text()
old = "COPY frontend ./frontend\n"
assert text.count(old) == 1
text = text.replace(old, f"COPY frontend ./frontend\n# the API types are generated from it (npm run gen:api, which 'npm run build' runs first)\nCOPY {entities}/openapi.json ./{entities}/openapi.json\n")
old = "npx ng build"
assert text.count(old) == 1
docker.write_text(text.replace(old, "npm run build"))

# ---- overrides
for path in OVERRIDES.rglob("*"):
    if path.is_file():
        dest = OUT / path.relative_to(OVERRIDES)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)

# ---- the deployment: what the template proposes to refresquito-services in a pull request
DEPLOY = OUT.parent / "spring-framework-deploy"
if DEPLOY.exists():
    shutil.rmtree(DEPLOY)
shutil.copytree(HERE / "spring-app-deploy", DEPLOY)
api = DEPLOY / "catalog" / "apis" / f"{V('name')}-{V('entities')}.json"
api.parent.mkdir(parents=True)
shutil.copyfile(OUT / entities / "openapi.json", api)

# ---- one skeleton per line (today one: the framework of petstore-spring's vendor/)
for line, versions in LINES.items():
    dest = SKELETONS / f"spring-framework-app-{line}"
    if line != NEWEST:
        assert dest.is_dir(), f"the skeleton of the line {line} is not committed (only {NEWEST} is generated)"
        continue
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(OUT, dest)
    parent = (dest / "services" / "notifier" / "pom.xml").read_text()
    assert f"<version>{versions['spring']}</version>" in parent, ("the vendor/ of petstore-spring is not", versions["spring"])
    assert (dest / "vendor" / f"refresquito-angular-{versions['angular']}.tgz").exists(), versions["angular"]
    assert (dest / "vendor" / f"refresquito-postgres-{versions['postgres']}").is_dir(), versions["postgres"]
    print(f"skeleton of the line {line}: " + ", ".join(f"{k} {v}" for k, v in versions.items()))

left = [str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file() and not str(p.relative_to(OUT)).startswith(VERBATIM)
        and p.suffix not in BINARY and re.search(r"pet|adopt", p.read_text(errors="ignore").lower().replace("perpetual", "").replace("competi", ""))]
print(f"{sum(1 for _ in OUT.rglob('*'))} entries in {OUT.relative_to(HERE.parent)}")
print("files that still say 'pet' or 'adopt':", left or "none")
shutil.rmtree(OUT)   # only the skeletons of the lines stay
