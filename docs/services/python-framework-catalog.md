# El Python Framework en el catálogo

Cómo está descrito el **Python Framework** en Backstage, qué significa cada dato de su ficha y qué hay que mantener
al día cuando se publica una versión. Para crear una aplicación con él, ve a
[Aplicación nueva (Python Framework)](python-framework.md).

## Qué entidades hay y dónde se declaran

| Entidad | Qué es | Dónde se declara | Cómo llega a Backstage |
|---|---|---|---|
| `python-framework` | El framework completo (tipo `library`). No es un repositorio | `refresquito-services`, `bootstrap/app-of-apps/values.yaml`, en `catalog.components` | Con una pasada del bootstrap |
| `refresquito-fastapi` | La parte de backend | `catalog-info.yaml` de su repositorio | Sola: Backstage relee los repositorios cada 30 minutos |
| `refresquito-angular` | La parte de frontend | `catalog-info.yaml` de su repositorio | Sola, igual |
| Cada aplicación (`petstore`, `orders`…) | Lo que se construye con él | `catalog-info.yaml` de su repositorio (lo escribe la plantilla) | Sola, igual |

Las dos partes cuelgan del framework con `subcomponentOf: component:default/python-framework`. Cada aplicación declara
`dependsOn` hacia el framework **y hacia cada una de las dos partes**: así la ficha de una librería lista las aplicaciones
a las que llega un cambio suyo.

Solo cuenta lo que está en la rama `main`. Para no esperar al refresco, usa el icono de refrescar de la ficha.

## Qué dice la ficha de cada librería

| Dato | Ejemplo | Qué significa |
|---|---|---|
| `refresquito.io/version` | `0.1.0` | La versión publicada |
| `refresquito.io/python`, `refresquito.io/fastapi` | `>=3.12`, `>=0.115,<1` | Sobre qué funciona el backend |
| `refresquito.io/angular`, `refresquito.io/keycloak-js` | `>=20.0.0`, `>=26.0.0` | Sobre qué funciona el frontend |
| `refresquito.io/used-with` | `refresquito-angular 0.1.x` | La versión de la otra parte con la que se usa: las dos comparten el número menor |
| `refresquito.io/supported-versions` | `0.1.x` | Las versiones que se mantienen |
| `refresquito.io/support-policy` | — | Resumen de la política de soporte |
| `lifecycle` | `experimental` | Pasa a `production` con la versión 1.0 |
| Enlaces | — | Repositorio, notas de versión, última *release*, política de soporte, incidencias y la parte correspondiente del petstore |

Estos datos **no se escriben a ojo**: en cada repositorio el CI falla si dejan de coincidir con el paquete
(`tests/test_catalog_info.py` en `refresquito-fastapi`, `check-catalog-info.mjs` en `refresquito-angular`).

## Política de soporte

Está completa en el `SUPPORT.md` de cada librería, y es la misma en las dos:

- **Mientras sea 0.x**: solo se mantiene la última versión. Una versión menor puede traer cambios incompatibles,
  siempre anotados en las notas de versión con *Action required*. Una versión de parche nunca rompe nada.
- **Desde la 1.0**: se mantienen la última versión mayor y la anterior durante 6 meses. Los cambios incompatibles solo
  llegan en versión mayor, avisados al menos una versión menor antes, y con guía de migración.
- Backend y frontend se usan con el **mismo número menor**. El petstore va siempre con la última versión.

## La documentación de cada librería

*View TechDocs* en la ficha de una librería muestra tres páginas: inicio (su README), política de soporte y notas de
versión. Salen de los documentos que el repositorio ya tiene:

```bash
python3 make-docs.py           # escribe docs/ desde README, SUPPORT.md y CHANGELOG.md
python3 make-docs.py --check   # lo que ejecuta el CI: falla si docs/ no está al día
```

`docs/` **no se edita a mano**. Hace falta porque este Backstage solo construye la documentación de un repositorio que
tenga una carpeta `docs/` junto a su `mkdocs.yml`.

## Al publicar una versión

En el repositorio de la librería:

1. Sube la versión del paquete (`pyproject.toml`, o `projects/refresquito-angular/package.json`).
2. Añade su entrada a `CHANGELOG.md`.
3. Actualiza en `catalog-info.yaml`: `refresquito.io/version`, `supported-versions`, `used-with` y, si cambian, las de
   compatibilidad. El CI te dice cuál falta.
4. Ejecuta `python3 make-docs.py` y sube `docs/`.
5. Etiqueta `vX.Y.Z` en `main`: el CI adjunta el paquete a una *release* de GitHub.

Si cambia el número menor, publica las dos partes con el mismo y actualiza el petstore.

## Qué no debes esperar

- **El framework (`python-framework`) no se actualiza solo**: su ficha cambia con el bootstrap, no al fusionar.
- **Backstage no comprueba qué versión usa cada aplicación**: `dependsOn` dice de qué depende, no con qué versión. Eso
  está en el `pyproject.toml` y el `package.json` de la aplicación.
- **La documentación no se reconstruye al instante**: tras un cambio en `main`, la primera visita la vuelve a generar.
