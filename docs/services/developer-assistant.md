# Implementar un cambio (Developer Assistant)

El **Developer Assistant** es el tercer asistente de la cadena funcional → arquitecto → **desarrollador**. Implementa
un **cambio** de una especificación aprobada en la aplicación del Python Framework que instanció su arquitectura
aprobada, y lo deja en **pull requests en borrador** para que una persona los revise y los mergee.

## Antes de usarlo

1. La **especificación** del sistema aprobada (su pull request `spec/<sistema>` mergeado; la escribe el Functional
   Assistant).
2. La **arquitectura** aprobada (su pull request `arch/<sistema>` mergeado; la escribe el Architect Assistant).
3. La **aplicación instanciada**, con la sección 5.6 de su Architecture Design: el repositorio creado con la plantilla
   *New application (Python Framework)* y `add-python-app.py --from` mergeado. El asistente no instancia.

## Cómo se usa

*Create* → **Implement a change (Developer Assistant)**:

| Campo | Qué |
|---|---|
| System | el sistema de refresquito-specs |
| Change | la carpeta del cambio, `docs/openspec/changes/<cambio>` |
| Mode | **plan**: propone `tasks.md` del cambio (grupos de tareas, cada uno un pull request); **implement**: construye las tareas no hechas |
| Group | solo ese grupo de `tasks.md` (recomendado: un pull request revisable cada vez) |
| Model | `claude-opus-5-5` por defecto |

El asistente corre en GitHub Actions (workflow `develop` de refresquito-specs): lee el cambio, la especificación y la
arquitectura, escribe el código y los tests de cada escenario, pasa los tests, y marca las tareas hechas. Al
terminar, el propio workflow comprueba lo que ha dejado (nada en `.github/`, `vendor/`, Dockerfiles, `compose.yaml` ni
excepciones de seguridad; en las especificaciones, solo `tasks.md`; ningún secreto) y abre los pull requests:

- en el **repositorio de la aplicación**: el código (rama `dev/<cambio>-…`);
- en **refresquito-specs**: las tareas hechas (rama `tasks/<sistema>-<cambio>-…`).

Su descripción dice lo que hizo, los tests y las preguntas que deja. **Mergear es aprobar**: luego el CI de la
aplicación construye las imágenes y el template *Promote* las lleva de dev a pre y pro. Cuando el cambio está en
producción, el Functional Assistant lo archiva.

## Quién puede usarlo

Por ahora solo el operador: corre con su suscripción de Claude. Detalles, instalación (dos secretos del repositorio
refresquito-specs), seguridad y el paso a un modelo local:
[developer/README.md](https://github.com/javivillar/refresquito-specs/blob/main/developer/README.md).
