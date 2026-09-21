# Alfresco — gestión documental (sites)

Alfresco guarda y comparte documentos. Desde Backstage **creas y borras tus sites**; el trabajo con los documentos se hace en Alfresco.

## Qué te da

- **Página `/alfresco-manager`**: tus sites y la gestión de sus miembros.
- **Dos plantillas**: *Create Alfresco Site* y *Delete Alfresco Site*.

## Quién puede hacer qué

- **Crear un site**: cualquier usuario que haya entrado en Backstage; **no hace falta ser administrador global de Alfresco**. Pasas a ser el
  **SiteManager** del site.
- **Editarlo, borrarlo y gestionar sus miembros**: solo tú como SiteManager, o `backstage-admin`.

Los permisos dentro de Alfresco son **de tres capas**, cada una en su sitio:

| Capa | Qué controla | Dónde se gestiona |
|---|---|---|
| Administrador global | La administración completa del repositorio | Dentro de Alfresco, a mano, por usuario |
| Acceso a un site | Si puedes entrar en él | Grupos de Keycloak por site (los sincroniza un proceso automático) o desde Share |
| Rol dentro del site | Qué puedes hacer en él | *Site Members* de Share; el proceso automático concede el rol base una vez y nunca lo sobrescribe |

## Cómo se usa

1. *Create* → *Create Alfresco Site*. Quedas como SiteManager.
2. Añade miembros y asigna roles desde Share (*Site Members*), o desde `/alfresco-manager`.
3. Los permisos sobre un fichero o carpeta concretos se ajustan en Share con *Manage Permissions*.

## Qué garantías tienes

- Nadie más que tú (y `backstage-admin`) puede editar o borrar tu site ni gestionar sus miembros desde Backstage.

## Qué no debes esperar

- **Que un grupo de Keycloak baste para dar permisos de administrador.** Pertenecer a `alfrescodms-admin` no hace nada por sí solo: el permiso
  de administrador global se concede a mano dentro de Alfresco.
- **Que la sincronización de miembros funcione antes del primer acceso.** Quien nunca ha iniciado sesión en Alfresco se omite hasta que entre.
- **Que el proceso automático te quite o cambie roles.** Es solo aditivo: los cambios manuales de un SiteManager en Share se respetan.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| Un miembro nuevo no aparece en el site | Nunca ha entrado en Alfresco | Que inicie sesión una vez y espera a la siguiente sincronización |
| *Forbidden* al borrar un site | No eres su SiteManager | Pídeselo al SiteManager o a un administrador |
