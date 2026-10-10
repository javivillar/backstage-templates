#!/usr/bin/env python3
"""make-python-app-skeleton.py — the skeleton of the template "New application (Python Framework)".

    python3 tools/make-python-app-skeleton.py ~/petstore

The skeleton is NOT written by hand: it is the petstore (github.com/javivillar/petstore), the
reference application of the framework, with its names turned into template values. Run this
again when the petstore changes, and commit the result (skeletons/python-framework-app/).

    petstore, Petstore            ${{ values.name }}, ${{ values.title }}
    pet, Pet, pets, Pets          ${{ values.entity }}, ${{ values.Entity }}, ${{ values.entities }}, ${{ values.Entities }}
    species, birth_date           category, start_date      (a text to filter by and an optional date)
    available / pending / sold    active / pending / closed

What is not a plain copy is in tools/python-app-overrides/ (README, CI, catalog entry...), copied
over the result. Check a change with tools/render-python-app.py, which renders the skeleton the
way Backstage does and leaves an application whose tests can be run.
"""
import json, pathlib, shutil, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent / "skeletons" / "python-framework-app"
OVERRIDES = HERE / "python-app-overrides"
src = pathlib.Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else sys.exit(__doc__)

V = lambda name: "${{ values.%s }}" % name   # noqa: E731
RULES = [   # in order: the longer names first
    ("PETSTORE_", "APP_"),
    ("petstore_test", "app_test"),
    ("javivillar/petstore", f"{V('owner')}/{V('name')}"),
    ("Petstore", V("title")),
    ("petstore", V("name")),
    ("Pets", V("Entities")), ("pets", V("entities")), ("Pet", V("Entity")), ("pet", V("entity")),
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
# the API types of the web are generated from backend/openapi.json when it is built, tested or
# served (not committed): a new application starts with whatever entity name it was given
pkg_path = OUT / "frontend/package.json"
pkg = json.loads(pkg_path.read_text())
pkg["name"] = "app-frontend"
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
docker.write_text(text.replace(old, "COPY frontend ./frontend\n# the API types are generated from it (npm run gen:api, before the build)\nCOPY backend/openapi.json ./backend/openapi.json\n"))

# ---- overrides
for path in OVERRIDES.rglob("*"):
    if path.is_file():
        dest = OUT / path.relative_to(OVERRIDES)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)

left = [str(p.relative_to(OUT)) for p in OUT.rglob("*") if p.is_file() and not str(p.relative_to(OUT)).startswith(VERBATIM)
        and p.suffix not in BINARY and "pet" in p.read_text(errors="ignore").lower().replace("perpetual", "")]
print(f"{len(list(OUT.rglob('*')))} entries in {OUT.relative_to(HERE.parent)}")
print("files that still say 'pet':", left or "none")
