# Aplicación nueva con el Python Framework

El **Python Framework** es la base de las aplicaciones de negocio de la plataforma: una web Angular
(`refresquito-angular`), un servicio FastAPI (`refresquito-fastapi`) y PostgreSQL, con el login y los permisos en
Keycloak. La plantilla **New application (Python Framework)** de *Create* te da una aplicación nueva ya funcionando.

Cómo está descrito el framework en el catálogo, su política de soporte y qué se actualiza al publicar una versión:
[El Python Framework en el catálogo](python-framework-catalog.md). El recorrido completo, campo a campo y con todo lo
que se crea (grupos, roles y usuarios incluidos): [Manual: crear una aplicación paso a paso](python-framework-manual.md).

## Qué te da

Un repositorio privado `<owner>/<nombre>` con:

- **API** (`backend/`): un CRUD completo de tu primera entidad en `/api/<entidades>`, con migraciones, errores en formato
  estándar, logs en JSON, métricas y validación del token de Keycloak.
- **Web** (`frontend/`): la lista con filtros y paginación, el formulario, y entrar y salir con Keycloak.
- **Pruebas** de las dos partes, que pasan desde el primer commit, y un **CI** que las ejecuta y publica las dos imágenes.
- Su entrada en el **catálogo**, en el system `business-systems`, dependiendo de `python-framework`.

Es una copia del [petstore](https://github.com/javivillar/petstore), la aplicación de referencia, con los nombres que
indiques. La entidad nace con nombre, categoría, estado y fecha de inicio: cámbiala por lo que necesite tu aplicación.

## Qué te pide

| Campo | Ejemplo | Para qué |
|---|---|---|
| Name | `orders` | Repositorio, paquete Python, cliente de Keycloak, roles `orders-viewer` y `orders-admin`, y después el namespace. Solo minúsculas y cifras, sin guiones |
| Title | `Orders` | Cómo se lee |
| Description | `Orders of the shop` | Una frase |
| Entity, singular / plural | `order` / `orders` | La tabla y la clase (`Order`), y la ruta del API (`/api/orders`) |
| Environments | `nato-sirtap` | Los clusters donde se despliega, como `<zona>-<programa>` |
| Version of the Python Framework | `2.0` | Con qué versión del framework nace. Solo se ofrecen las mantenidas: la **2.0** (añade la traza de auditoría) y la **0.1** (mantenida hasta el 15-04-2027) |
| Platform blocks | *Single sign-on* | Lo que usa de la plataforma. Hoy, el inicio de sesión con Keycloak (lo llevan todas), el almacenamiento de objetos, los documentos, el catálogo de datos, el gateway de APIs, los procesos de Camunda, los dashboards de Superset y los flujos de Activepieces (opcionales) |
| Object storage - buckets | `documents` | Opcional. Un bucket `<name>-documents` en SeaweedFS, solo para la aplicación, con su clave de acceso ya en el entorno del API |
| Documents (Alfresco) - sites | `records` | Opcional. Un sitio privado `<name>-records` en Alfresco, con un usuario propio de la aplicación y sus credenciales ya en el entorno del API |
| Documents (Alfresco) - groups | `finance` | Grupos de Keycloak cuyos miembros entran en los sitios de la aplicación |
| Data catalog (DataHub) - register its data | sí / no | Opcional. Un producto de datos `<name>` en DataHub con las tablas de su base de datos |
| Data catalog (DataHub) - people / groups who own its data | `ana` / `finance` | Responsables de negocio de sus datos. Tu equipo es siempre el responsable técnico |
| API gateway (Gravitee) - publish its API | sí / no | Opcional. Su API en el gateway, en `/gateway/<name>/`, pública en el portal de desarrolladores |
| API gateway (Gravitee) - team | `gravitee-team-alpha` | Opcional. El grupo cuyos miembros ven la API en Backstage |
| Processes (Camunda) - deploy its processes | sí / no | Opcional. Los BPMN de `platform/processes/` se despliegan en Camunda con cada versión |
| Processes (Camunda) - groups | `finance` | Grupos cuyos miembros inician los procesos y trabajan sus tareas en Tasklist |
| Dashboards (Superset) - import its dashboards | sí / no | Opcional. El export de Superset de `platform/dashboards/` se importa en Superset con cada versión |
| Flows (Activepieces) - import its flows | sí / no | Opcional. Los flujos de `platform/flows/` se importan en un proyecto propio de Activepieces y se publican |
| Flows (Activepieces) - groups that edit them | `finance` | Grupos cuyos miembros editan los flujos en su proyecto de Activepieces |
| People who get the role `<name>-admin` | `javi` | Usuarios del realm que serán administradores de la aplicación (deben existir) |
| GitHub owner | `javivillar` | Dueño del repositorio |

## Cómo se despliega

**La plantilla no toca ningún cluster.** Además de crear el repositorio, abre una *pull request* en
`refresquito-services` con dos ficheros: el de la aplicación (`bootstrap/app-of-apps/apps/<nombre>.yaml`: qué es, en qué
entornos va, qué imágenes y qué bloques usa) y la definición de su API para el catálogo. Al terminar te da el enlace.

**Fusionar esa pull request es lo que despliega**: Argo CD crea el namespace `<zona>-<programa>-<nombre>-oneke` y
arranca la web, el API y la base de datos. En unos minutos la aplicación responde en `https://<nombre>.<dominio>`, con
su cliente de Keycloak, sus roles y los usuarios de prueba `<nombre>-admin` y `<nombre>-viewer`. No hay comandos que
ejecutar ni pasadas del bootstrap.

| Para | Qué se hace |
|---|---|
| Publicar una versión nueva | La plantilla [Promote an application](python-framework-promote.md), o cambiar `image.tag` (`stages.<etapa>.tag` si tiene etapas) por el commit cuyas imágenes quieres, en una pull request |
| Llevarla a otro entorno | Añadir su `<zona>-<programa>` a `environments` |
| Dar el rol de administrador a alguien | Añadirlo a `users` del rol `admin` |
| Dejar de usar un bloque | Ponerlo a `enabled: false`: deja de gestionarse, y lo que creó se queda |

Espera a que termine el CI del repositorio nuevo antes de fusionar: es el que publica las imágenes de ese commit. Si
fusionas antes, los pods quedan en `ImagePullBackOff` hasta que existan.

## Lo que usa de la plataforma (bloques)

Cada bloque que eliges se crea al desplegar, aparece en el catálogo como un **recurso de la aplicación** (por ejemplo
`orders-sso-client`) y hace que dependa del **servicio que lo presta** (`iam-oneke`): en la ficha de la aplicación ves
todo lo que usa, y en la del servicio, todas las aplicaciones a las que afecta. Lo que declares se mantiene: si alguien
lo cambia a mano en el servicio, vuelve a su sitio en unos minutos. Quitar un bloque nunca borra lo que creó.

### Almacenamiento de objetos (S3)

Si indicas buckets, la aplicación recibe cada uno como `<nombre>-<bucket>` en SeaweedFS, con una identidad propia que
solo puede usar los suyos. El API lo encuentra todo en su entorno, con los nombres que lee cualquier cliente S3:

| Variable | Valor |
|---|---|
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | La clave de acceso de la aplicación |
| `AWS_ENDPOINT_URL_S3`, `AWS_DEFAULT_REGION` | Dónde está el S3 de la plataforma |
| `S3_BUCKETS` | Todos sus buckets, separados por comas |
| `S3_BUCKET_<BUCKET>` | El nombre completo de cada uno, por ejemplo `S3_BUCKET_DOCUMENTS=orders-documents` |

El framework **no trae cliente S3**: añade a tu aplicación el que prefieras (por ejemplo `boto3`), que funcionará con
esas variables tal cual. Puedes añadir buckets después en el fichero de la aplicación; quitar uno de la lista no lo
borra.

### Documentos (Alfresco)

Si indicas sitios, la aplicación recibe cada uno como un sitio privado `<nombre>-<sitio>` en Alfresco. El API de
Alfresco no acepta los tokens de Keycloak, así que la aplicación entra con un usuario propio de Alfresco,
`app-<nombre>`, colaborador de sus sitios (lee, crea y edita en ellos) y de ningún otro. El API lo encuentra todo en su
entorno:

| Variable | Valor |
|---|---|
| `ALFRESCO_URL` | El repositorio de Alfresco dentro del cluster (API REST en `/alfresco/api/-default-/public/alfresco/versions/1`) |
| `ALFRESCO_USERNAME`, `ALFRESCO_PASSWORD` | El usuario de la aplicación (autenticación HTTP Basic) |
| `ALFRESCO_SITES` | Todos sus sitios, separados por comas |
| `ALFRESCO_SITE_<SITIO>` | El id de cada uno, por ejemplo `ALFRESCO_SITE_RECORDS=orders-records` |

Las personas entran por Keycloak: cada sitio tiene un grupo `alfrescodms-site-<nombre>-<sitio>`, y quien está en él
entra en el sitio como lector (Consumer) la primera vez; después su rol se cambia en el propio Alfresco. Los miembros
de los grupos que indiques en el formulario se añaden a ese grupo, también quien entre en ellos más adelante. Nunca se
saca a nadie: quien deba salir se quita del grupo a mano. Una persona aparece en el sitio después de haber entrado una
vez en Alfresco.

El framework **no trae cliente de Alfresco**: usa su API REST con el cliente HTTP que prefieras. Puedes añadir sitios
después en el fichero de la aplicación; quitar uno de la lista no lo borra.

### Catálogo de datos (DataHub)

Si lo marcas, la aplicación tiene en DataHub un producto de datos con su nombre y, dentro, un dataset por cada tabla
de su base de datos, con sus columnas y tipos. Las tablas se leen del esquema de la base de datos cada pocos minutos,
así que lo que cambien tus migraciones (una tabla o una columna nueva) aparece solo. Los comentarios de tablas y
columnas (`COMMENT ON TABLE ...`, `COMMENT ON COLUMN ...`, o `comment=` en SQLAlchemy) son sus descripciones en
DataHub: es la forma de documentar tus datos desde el código.

Responsables: tu equipo (`<segmento>-team`) como responsable técnico, y las personas y grupos que indiques como
responsables de negocio. Solo se añaden: lo que alguien añada en DataHub (responsables, descripciones, etiquetas,
términos del glosario) se queda. Los dominios, etiquetas y términos los crean los stewards; el fichero de la aplicación
puede indicar un dominio que ya exista (`domain:`). En Backstage, la aplicación muestra la tarjeta de DataHub y la
pestaña *Data governance*.

La aplicación no recibe nada en su entorno: esto es para quien busca o gobierna los datos, no para el código.

### Gateway de APIs (Gravitee)

Si lo marcas, tu API se publica en el gateway, en `https://gravitee.<dominio>/gateway/<nombre>/`. Una llamada a
`/gateway/<nombre>/orders` llega a `/api/orders` de tu aplicación. Aparece pública en el portal de desarrolladores, con
tu OpenAPI como documentación. Se lee de tu API cada pocos minutos, así que una versión nueva actualiza el portal sola.

Para llamarla por el gateway hace falta un token del realm de Keycloak de un cliente suscrito. El gateway lo comprueba
y se lo pasa a tu API, que sigue mirando los roles como siempre. El cliente de tu propia web ya está suscrito. Quien
quiera consumir tu API desde otra aplicación la registra en el portal, con su cliente de Keycloak, y se suscribe; la
suscripción se acepta sola.

Tu aplicación no recibe nada en su entorno: sigue sirviendo su API en `/api` como siempre, y el gateway es una puerta
más para otros consumidores.

### Procesos (Camunda)

Tus procesos son parte de tu código: los BPMN (y DMN y formularios) van en `platform/processes/` de tu repositorio, y el
Dockerfile del API los copia a la imagen. Así, Camunda tiene siempre los procesos de la versión que corre: al desplegar
un commit nuevo, lo que cambió pasa a ser una versión nueva del proceso. La aplicación nace con uno de ejemplo,
`<nombre>-review`, que puedes cambiar o borrar.

**Regla:** el `id` de cada proceso y decisión empieza por el nombre de la aplicación y un guion (`orders-approval`).
Uno con otro id no se despliega, y el despliegue de ese commit te lo dice en el log del provisioner.

Tu API habla con Camunda como ella misma: `CAMUNDA_URL` (la API REST, `engine-rest`), `CAMUNDA_USERNAME` y
`CAMUNDA_PASSWORD` (autenticación HTTP Basic). Puede iniciar sus procesos y leer, reclamar y completar sus tareas, nada
de otras aplicaciones. Las personas de los grupos que indiques los inician y trabajan sus tareas en Tasklist
(`https://bpm.<dominio>`). El framework no trae cliente de Camunda: usa su API REST con el cliente HTTP que prefieras.

### Dashboards (Superset)

Tus dashboards también son parte de tu código. Créalos en Superset sobre cualquier base de datos con tus mismas tablas,
expórtalos (Dashboards, ⋮, Export) y descomprime el fichero en `platform/dashboards/` tal como viene. La aplicación nace
con uno de ejemplo sobre su tabla principal.

Con cada versión desplegada se importan en Superset sobre **tu base de datos de ese clúster**, sea cual sea la conexión
que traiga el export, con un rol de **solo lectura** (`<nombre>_reader`): puede leer todas tus tablas, también las que
creen migraciones futuras, y no puede escribir en ninguna. Los ven los grupos `superset-editor` y `superset-admin`.
Tu aplicación no recibe nada en su entorno.

### Flujos (Activepieces)

Tus flujos también son parte de tu código. Créalos en Activepieces, expórtalos (menú del flujo, Export) y guarda cada uno
en `platform/flows/<flujo>.json`: un flujo por fichero, y el nombre del fichero (minúsculas, dígitos y guiones) da nombre
a su webhook. La aplicación nace con uno de ejemplo, `new-<entidad>.json`: un webhook que responde con un saludo.

Con cada versión desplegada se importan en un **proyecto de Activepieces propio de tu aplicación** (con su título) los
flujos cuyo fichero cambió, y se publican en cuanto están completos (activados la primera vez; después conservan el
estado que les haya dado alguien). Lo que edites en Activepieces se pierde con el siguiente cambio del fichero: el
flujo es el fichero. Un flujo que use conexiones (`{{connections['<nombre>']}}`) espera como borrador hasta que alguien
cree esas conexiones en el proyecto, con esos nombres: las credenciales nunca van al repositorio. Los miembros de los
grupos que indiques son editores del proyecto.

Tu API recibe la URL de cada flujo que empieza con un webhook en `ACTIVEPIECES_FLOW_<FLUJO>_URL` (el nombre del fichero
en mayúsculas, guiones como `_`): un POST lo arranca, y a `<url>/sync` espera su respuesta (la del paso *Return
Response*). Llega tras la primera pasada del provisioner, que reinicia el API para dársela.

### Logs y auditoría (versión 2.0)

Con la 2.0 tu API escribe dos flujos, ambos JSON por stdout y distinguidos por `log_type`: `application` (sus logs y
una línea por petición) y `audit` (quién hizo qué). Toda escritura (`POST`, `PUT`, `PATCH`, `DELETE`) y toda petición
rechazada (401, 403) se audita sola, con el usuario, la ruta, el resultado y el `request_id`; lo que importe al
negocio lo registras tú con `audit("<entidad>.<acción>", resource=...)`.

En la plataforma cada flujo es un stream propio de Loki (`{kubernetes_namespace_name="<namespace>", log_type="audit"}`) y cada
evento cuenta en `audit_events_total{action, outcome}` del `/metrics`, que Prometheus ya rasca. En Grafana tienes los
dos en el dashboard *Python Framework - Audit*. Nunca metas secretos ni datos personales innecesarios en un evento.

## Qué se espera de ti

- **Los permisos los decide el API**, no la web: la web solo oculta lo que un rol no puede hacer.
- **Cada cambio del API** se refleja en `backend/openapi.json`; el CI falla si no está al día.
- **El esqueleto no se edita a mano**: se regenera desde el petstore (`tools/make-python-app-skeleton.py`). Si algo
  debe cambiar para todas las aplicaciones nuevas, cámbialo en el petstore.
