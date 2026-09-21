# Activepieces — automatización de flujos

Activepieces automatiza tareas con flujos. Desde Backstage **inicializas lo de alto nivel**: proyectos, sus miembros con un rol y flujos vacíos.
Lo demás —modelar el flujo, las conexiones y las variables— lo haces directamente en Activepieces.

## Qué te da

- **Página `/activepieces-manager`**: tus proyectos, sus miembros y sus flujos.
- **Ocho plantillas**:

| Objeto | Plantillas |
|---|---|
| Proyecto | crear (quedas como su **Admin**), renombrar, borrar |
| Miembros | añadir o cambiar el rol de alguien, quitar a alguien |
| Flujos | crear, renombrar, borrar |

## Quién puede hacer qué

Activepieces da permisos **por proyecto**, según el rol de cada miembro:

| Rol | Puede |
|---|---|
| Viewer | Solo leer |
| Editor | Construir flujos, conexiones y variables |
| Admin | Lo anterior, más gestionar los miembros del proyecto |

Backstage lee **tu rol real en Activepieces en el momento** y exige el permiso correspondiente: listar flujos (`READ_FLOW`), crear/renombrar/borrar
flujos (`WRITE_FLOW`), renombrar/borrar el proyecto (`WRITE_PROJECT`) y gestionar miembros (`WRITE_PROJECT_MEMBER`). Si no lo tienes, se
deniega. `backstage-admin` puede todo.

## Cómo se usa

1. *Create* → *Create Activepieces Project*. El proyecto es tuyo; añade a quien quieras con *Add or change a Project Member* y un rol.
2. *Create Activepieces Flow* crea un flujo **vacío y desactivado**, opcionalmente dentro de una carpeta (solo se indica al crearlo).
3. Construye y **publica** el flujo en Activepieces.
4. Para entrar en Activepieces necesitas el grupo `activepieces-user` en Keycloak; el alta es por invitación.

## Qué garantías tienes

- **Otro usuario no toca tus proyectos ni tus flujos.** Un flujo de otro proyecto y uno inexistente dan el mismo `403`, sin revelar si existe.
- **No se puede actuar sobre el flujo de otro proyecto nombrando el tuyo**: el flujo tiene que pertenecer al proyecto indicado.
- **Recién creado el proyecto, aunque aún no hayas entrado en Activepieces**, sigues siendo su propietario: ves el rol «Admin (until first
  Activepieces login)» hasta tu primer acceso.
- **El último miembro que puede gestionar miembros no se puede quitar.**

## Qué no debes esperar

- **Crear conexiones ni variables desde Backstage.** Contienen secretos y su forma depende de cada aplicación: se crean en Activepieces.
- **Publicar flujos ni moverlos entre carpetas desde Backstage.** Los flujos nacen vacíos y desactivados.
- **Ver aquí proyectos que no se crearon desde Backstage.** Los personales y los creados a mano quedan fuera.
- **Recuperar nada al borrar un proyecto.** Se eliminan también sus flujos, conexiones y variables.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Forbidden* al crear un flujo | Tu rol en ese proyecto es Viewer | Pide que te cambien a Editor o Admin |
| *Forbidden … not in this project* | El flujo pertenece a otro proyecto | Indica el proyecto correcto |
