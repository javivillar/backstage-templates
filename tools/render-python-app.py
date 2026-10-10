#!/usr/bin/env python3
"""render-python-app.py — render the skeleton the way Backstage's fetch:template does, to test it.

    python3 tools/render-python-app.py OUT_DIR [name=orders title=Orders entity=order entities=orders owner=javivillar]

Then run the tests of the application in OUT_DIR (its README says how). Needs jinja2.
"""
import json, pathlib, shutil, sys
import jinja2

HERE = pathlib.Path(__file__).resolve().parent
SKELETON = HERE.parent / "skeletons" / "python-framework-app"
# the files the template lists in copyWithoutTemplating
VERBATIM = ("vendor/", "frontend/package-lock.json", "frontend/public/favicon.ico", ".github/workflows/",
            "backend/migrations/script.py.mako")
out = pathlib.Path(sys.argv[1]).expanduser().resolve()
values = {"name": "orders", "title": "Orders", "description": "Orders of the shop", "entity": "order", "entities": "orders",
          "owner": "javivillar"}
values.update(dict(a.split("=", 1) for a in sys.argv[2:]))
values["entityTitle"] = values["entity"].capitalize()
values["entitiesTitle"] = values["entities"].capitalize()
env = jinja2.Environment(variable_start_string="${{", variable_end_string="}}", undefined=jinja2.StrictUndefined,
                         keep_trailing_newline=True)
env.filters["dump"] = json.dumps   # nunjucks has it built in
if out.exists():
    shutil.rmtree(out)
for path in sorted(SKELETON.rglob("*")):
    if not path.is_file():
        continue
    rel = str(path.relative_to(SKELETON))
    dest = out / env.from_string(rel).render(values=values)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if rel.startswith(VERBATIM):
        dest.write_bytes(path.read_bytes())
    else:
        dest.write_text(env.from_string(path.read_text()).render(values=values))
    shutil.copymode(path, dest)
print(f"rendered {values['name']} ({values['entityTitle']}/{values['entities']}) in {out}")
