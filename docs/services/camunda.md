# Camunda — procesos de negocio (BPM)

Camunda ejecuta los procesos BPMN. Desde Backstage **despliegas y gestionas tus definiciones de proceso**; los procesos en ejecución y sus
tareas se trabajan en las aplicaciones de Camunda (Cockpit y Tasklist).

## Qué te da

- **Página `/camunda-manager`**: tus definiciones de proceso (los administradores ven todas, con columna *Owner*).
- **Tres plantillas**:

| Plantilla | Qué hace |
|---|---|
| *Provision Camunda Process* | Despliega un proceso mínimo (inicio → una tarea de usuario → fin), ya preparado para el aislamiento por usuario, y te da **derechos exclusivos** sobre él. Descargas el BPMN y lo modelas en el *Camunda Modeler* de escritorio. |
| *Update Camunda Process* | Vuelve a desplegar una **nueva versión** del BPMN bajo una clave que ya posees. |
| *Delete Camunda Process* | Borra la definición (**todas** las versiones y todas las instancias) de un proceso tuyo. |

## Quién puede hacer qué

- **Desplegar**: cualquier usuario que haya entrado en Backstage; el proceso queda a tu nombre.
- **Actualizar y borrar**: solo el propietario o `backstage-admin`.
- **En Camunda** (Cockpit, Tasklist), los grupos son `camunda-admin`, `camunda-editor` y `camunda-viewer` (este último reservado para solo lectura).

## Cómo se usa

1. *Create* → *Provision Camunda Process*, y descarga el BPMN resultante.
2. Modélalo en el *Camunda Modeler*.
3. *Update Camunda Process*: pega el XML actualizado. **El identificador del proceso dentro del BPMN no debe cambiar**, o la propiedad no se traslada.

## Qué garantías tienes

- **Otro editor no puede borrar ni redesplegar tu proceso.** Además de la comprobación de Backstage, Camunda lo impide por sí mismo: una
  petición directa con las credenciales de otro editor recibe un `403` nativo.
- **Cada instancia y su tarea son de quien la arrancó.** Con el proceso que genera la plantilla, solo el usuario que arranca una instancia la
  ve, y su tarea queda asignada a él, aunque otro comparta tu grupo `camunda-editor`.

## Qué no debes esperar

- **Que todo el aislamiento venga solo.** Depende del listener de arranque y de la asignación de la tarea que trae el proceso de la plantilla:
  si al modelar los quitas, la instancia deja de estar aislada.
- **Ver solo tus definiciones dentro de Camunda.** La *definición* es visible para todo el grupo `camunda-editor` (lo que se aísla es editarla,
  borrarla, y las instancias y tareas).
- **Gestionar instancias o tareas desde Backstage.** Se hace en Cockpit y Tasklist con tu SSO.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Forbidden* al actualizar o borrar | La clave del proceso es de otro usuario | Pide al propietario o a un administrador |
| Una actualización no conserva la propiedad | Cambió el id del proceso dentro del BPMN | Mantén el mismo id |
