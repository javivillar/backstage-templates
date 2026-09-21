# Keycloak — identidades (usuarios, grupos y clientes)

Keycloak es el proveedor de identidad de toda la plataforma (realm `RefresquitoTime`). Desde Backstage puedes **crear y gestionar
tus propios** usuarios, grupos y clientes OIDC, sin pedírselo a un administrador.

## Qué te da

- **Página `/keycloak-manager`**: lista **solo lo que has creado tú** (los administradores ven todo, con una columna *Owner*).
- **Nueve plantillas** en *Create*: crear, actualizar y borrar, para cada uno de estos tres tipos:

| Tipo | Crear | Actualizar | Borrar |
|---|---|---|---|
| Usuario | email, nombre, contraseña **temporal** y grupos existentes a los que unirlo | email, nombre y pertenencia a grupos | sí |
| Grupo | nombre, opcionalmente como subgrupo de otro | renombrar | sí |
| Cliente OIDC | los datos de una aplicación que quiera entrar con SSO | ajustes del cliente (no cambian el `clientId` ni el tipo público/confidencial) | sí |

## Quién puede hacer qué

- **Entrar en Backstage** exige el rol de acceso `backstage.access`, que dan los grupos `backstage-admin`, `backstage-editor` y
  `backstage-viewer`. Sin él, Keycloak deniega el login (también si ya tenías sesión en otra aplicación).
- **Crear**: cualquier usuario que haya entrado. Pasas a ser el **propietario** del objeto.
- **Actualizar y borrar**: solo su propietario o `backstage-admin`.

## Cómo se usa

1. *Create* → elige la plantilla del tipo de objeto.
2. Rellena el formulario. Un usuario nuevo recibe una **contraseña temporal** y tendrá que cambiarla en su primer acceso.
3. Consulta y gestiona lo tuyo en `/keycloak-manager`.

## Qué garantías tienes

- **Lo que creas solo lo editas tú.** Cada objeto queda marcado con su creador; otro usuario recibe *Forbidden* al intentar modificarlo y ni
  siquiera lo ve en la lista.
- **Los objetos anteriores a este sistema** (sin propietario registrado) **solo los puede tocar un administrador**: falla cerrado, no abierto.

## Qué no debes esperar

- **Tener acceso a una aplicación por crear un usuario.** El acceso a cada aplicación lo dan los **grupos** de Keycloak (por ejemplo `datahub-*`,
  `camunda-*`); pídeselos al administrador de esa aplicación.
- **Que el aislamiento cubra todo el portal.** La comprobación de propietario protege estos objetos de Keycloak; no restringe la lectura del
  catálogo de Backstage ni otras plantillas.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| Login denegado al entrar en Backstage | Tu usuario no tiene el rol `backstage.access` | Pide uno de los grupos `backstage-*` |
| *Forbidden … may not modify this Keycloak object* | El objeto es de otro usuario, o es anterior al sistema de propietarios | Pide al propietario o a un administrador que lo haga |
