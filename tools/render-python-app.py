#!/usr/bin/env python3
"""render-python-app.py — render the skeleton the way Backstage's fetch:template does, to test it.

    python3 tools/render-python-app.py OUT_DIR [name=orders title=Orders entity=order entities=orders owner=javivillar]
    python3 tools/render-python-app.py OUT_DIR --deploy DEPLOY_DIR [... tag=<commit> environments=nato-sirtap admins=javi buckets=documents]

Then run the tests of the application in OUT_DIR (its README says how). With --deploy it also
renders what the template proposes to refresquito-services to deploy it: copy DEPLOY_DIR over a
checkout of that repository and run its checks. Needs jinja2.
"""
import json, pathlib, shutil, sys
import jinja2

HERE = pathlib.Path(__file__).resolve().parent
SKELETON = HERE.parent / "skeletons" / "python-framework-app"
# the files the template lists in copyWithoutTemplating
VERBATIM = ("vendor/", "frontend/package-lock.json", "frontend/public/favicon.ico", ".github/workflows/",
            "backend/migrations/script.py.mako")
argv = sys.argv[1:]
deploy = None
if "--deploy" in argv:
    at = argv.index("--deploy")
    deploy = pathlib.Path(argv[at + 1]).expanduser().resolve()
    del argv[at:at + 2]
out = pathlib.Path(argv[0]).expanduser().resolve()
values = {"name": "orders", "title": "Orders", "description": "Orders of the shop", "entity": "order", "entities": "orders",
          "owner": "javivillar"}
values.update(dict(a.split("=", 1) for a in argv[1:]))
values["entityTitle"] = values["entity"].capitalize()
values["entitiesTitle"] = values["entities"].capitalize()
env = jinja2.Environment(variable_start_string="${{", variable_end_string="}}", undefined=jinja2.StrictUndefined,
                         keep_trailing_newline=True)
env.filters["dump"] = json.dumps   # nunjucks has it built in
def render(skeleton, out, verbatim=()):
    if out.exists():
        shutil.rmtree(out)
    for path in sorted(skeleton.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(skeleton))
        dest = out / env.from_string(rel).render(values=values)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith(verbatim):
            dest.write_bytes(path.read_bytes())
        else:
            dest.write_text(env.from_string(path.read_text()).render(values=values))
        shutil.copymode(path, dest)


render(SKELETON, out, VERBATIM)
print(f"rendered {values['name']} ({values['entityTitle']}/{values['entities']}) in {out}")
if deploy:
    # what the template adds for the deployment pull request (its step "deploy")
    values.update(tag=values.get("tag", "0000000"), fastapi=values.get("fastapi", "0.1.0"), angular=values.get("angular", "0.1.0"),
                  environments=values.get("environments", "nato-sirtap").split(","),
                  admins=[a for a in values.get("admins", "").split(",") if a],
                  buckets=[b for b in values.get("buckets", "").split(",") if b])
    render(SKELETON.parent / "python-framework-deploy", deploy)
    print(f"rendered its deployment (the pull request to refresquito-services) in {deploy}")
