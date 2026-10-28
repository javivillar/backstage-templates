#!/usr/bin/env python3
"""render-spring-app.py — render the skeleton of the Spring Framework the way Backstage's fetch:template does, to test it.

    python3 tools/render-spring-app.py OUT_DIR [frameworkVersion=1.0 name=orders title=Orders entity=order entities=orders owner=javivillar dataStewards=@javivillar securityApprovers=@javivillar]
                                              [processes=true flows=true buckets=files sites=documents dashboards=true]   (the example code of each block)
    python3 tools/render-spring-app.py OUT_DIR --deploy DEPLOY_DIR [... tag=<commit> environments=nato-sirtap admins=javi buckets=documents sites=records siteGroups=finance
                                              datahub=true 'dataClassification=NATO RESTRICTED' dataReleasability=NATO dataOwners=ana dataOwnerGroups=finance
                                              gateway=true gatewayTeam=gravitee-team-alpha
                                              processes=true processGroups=finance dashboards=true
                                              flows=true flowGroups=finance]

Then run the tests of the application in OUT_DIR (its README says how). With --deploy it also
renders what the template proposes to refresquito-services to deploy it: copy DEPLOY_DIR over a
checkout of that repository and run its checks. Needs jinja2.
"""
import json, pathlib, shutil, sys
import jinja2

HERE = pathlib.Path(__file__).resolve().parent
SKELETONS = HERE.parent / "skeletons"
# the files the template lists in copyWithoutTemplating
VERBATIM = ("vendor/", "frontend/package-lock.json", "frontend/public/favicon.ico", ".github/workflows/", ".github/quality.py")
argv = sys.argv[1:]
deploy = None
if "--deploy" in argv:
    at = argv.index("--deploy")
    deploy = pathlib.Path(argv[at + 1]).expanduser().resolve()
    del argv[at:at + 2]
out = pathlib.Path(argv[0]).expanduser().resolve()
values = {"name": "orders", "title": "Orders", "description": "Orders of the shop", "entity": "order", "entities": "orders",
          "owner": "javivillar", "dataStewards": "@javivillar", "securityApprovers": "@javivillar"}
values.update(dict(a.split("=", 1) for a in argv[1:]))
# the line of the Spring Framework: its own skeleton, as the template's step fetch picks it
line = values.setdefault("frameworkVersion", "1.0")
SKELETON = SKELETONS / f"spring-framework-app-{line}"
if not SKELETON.is_dir():
    sys.exit(f"no skeleton for the line {line} of the Spring Framework: {', '.join(sorted(p.name for p in SKELETONS.glob('spring-framework-app-*')))}")
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
        target = env.from_string(rel).render(values=values)
        if not target or target.endswith("/") or "//" in target:
            continue   # a name that renders empty: fetch:template does not create the file (a block not marked)
        dest = out / target
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.startswith(verbatim):
            dest.write_bytes(path.read_bytes())
        else:
            dest.write_text(env.from_string(path.read_text()).render(values=values))
        shutil.copymode(path, dest)


# the platform blocks: the skeleton keeps the example code of the marked ones
values.update(buckets=[b for b in values.get("buckets", "").split(",") if b] if isinstance(values.get("buckets", ""), str) else values["buckets"],
              sites=[s for s in values.get("sites", "").split(",") if s] if isinstance(values.get("sites", ""), str) else values["sites"],
              processes=values.get("processes", "") in ("true", "1", "yes", True),
              flows=values.get("flows", "") in ("true", "1", "yes", True),
              dashboards=values.get("dashboards", "") in ("true", "1", "yes", True))
render(SKELETON, out, VERBATIM)
print(f"rendered {values['name']} ({values['entityTitle']}/{values['entities']}) in {out}")
if deploy:
    # what the template adds for the deployment pull request (its step "deploy")
    values.update(tag=values.get("tag", "0000000"), stage=values.get("stage", "dev"), spring=values.get("spring", f"{line}.0"), angular=values.get("angular", "3.3.1"), postgres=values.get("postgres", "3.3.0"),
                  environments=values.get("environments", "nato-sirtap").split(","),
                  admins=[a for a in values.get("admins", "").split(",") if a],

                  siteGroups=[g for g in values.get("siteGroups", "").split(",") if g],
                  datahub=values.get("datahub", "true") in ("true", "1", "yes"),
                  dataClassification=values.get("dataClassification", "NATO UNCLASSIFIED"), dataReleasability=values.get("dataReleasability", "NATO"),
                  dataOwners=[u for u in values.get("dataOwners", "").split(",") if u],
                  dataOwnerGroups=[g for g in values.get("dataOwnerGroups", "").split(",") if g],
                  gateway=values.get("gateway", "") in ("true", "1", "yes"), gatewayTeam=values.get("gatewayTeam", ""),

                  processGroups=[g for g in values.get("processGroups", "").split(",") if g],
                  dashboards=values.get("dashboards", "") in ("true", "1", "yes", True),
                  monitoring=values.get("monitoring", "true") in ("true", "1", "yes"),

                  flowGroups=[g for g in values.get("flowGroups", "").split(",") if g])
    render(SKELETONS / "spring-framework-deploy", deploy)
    print(f"rendered its deployment (the pull request to refresquito-services) in {deploy}")
