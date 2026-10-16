# Manual: crear una aplicación con el Python Framework, paso a paso

Este manual acompaña a la plantilla **New application (Python Framework)** de *Create* en Backstage. Explica qué
significa cada campo del formulario, qué hace cada paso de la plantilla, qué se crea en cada servicio de la plataforma
(incluidos los **grupos, roles y usuarios** de Keycloak) y cómo comprobar que todo ha quedado bien.

Si solo quieres la referencia rápida de los bloques, está en [Aplicación nueva (Python Framework)](python-framework.md).
Para mover versiones entre dev, pre y pro: [Promocionar una aplicación](python-framework-promote.md).

## 1. El recorrido completo

| # | Quién | Qué pasa | Cuánto tarda |
|---|---|---|---|
| 1 | Tú | Rellenas el formulario de la plantilla en *Create* | 2-5 minutos |
| 2 | Backstage | Genera el código, crea el repositorio, lo registra en el catálogo y abre la *pull request* de despliegue | 1 minuto |
| 3 | GitHub Actions | El CI del repositorio nuevo pasa las pruebas y publica las imágenes `<nombre>-api` y `<nombre>-web` | 5-10 minutos |
| 4 | Tú (o quien revise) | Haces *merge* de la pull request en `refresquito-services`, **cuando el CI del paso 3 ha terminado** | — |
| 5 | Argo CD | Crea el namespace y arranca la web, el API y la base de datos | 2-3 minutos |
| 6 | El provisioner | Crea en Keycloak, SeaweedFS, Alfresco, etc. lo que declaraste (un CronJob que pasa cada 5 minutos) | hasta 5 minutos |
| 7 | Tú | Entras en `https://<nombre>.<dominio>` y compruebas | — |

**La plantilla nunca toca un cluster.** Lo único que despliega es el *merge* de la pull request (GitOps): todo queda
escrito en Git, revisado y repetible.

## 2. Antes de empezar

- Tienes que poder entrar en Backstage con tu usuario del realm.
- Elige un **nombre corto**: es la pieza de la que cuelgan casi todos los demás nombres (ver la tabla de la sección 5).
  No se puede cambiar después sin crear otra aplicación.
- Las **personas y grupos** que vayas a indicar en el formulario **deben existir ya** en Keycloak. La plantilla no crea
  personas ni grupos de personas; los que no existen se ignoran y el log del provisioner lo dice.
- Si vas a publicar en el gateway con un equipo, el grupo `gravitee-team-<equipo>` debe existir.

## 3. El formulario, página a página

### Página 1 · The application

| Campo | Ejemplo | Qué significa y qué consecuencias tiene |
|---|---|---|
| **Name** | `orders` | El identificador de la aplicación. Solo minúsculas y cifras, empezando por letra, 3 a 31 caracteres, **sin guiones**. Da nombre al repositorio, al paquete Python, al cliente de Keycloak, a los roles, al host, al namespace y a todo lo que la aplicación crea en otros servicios |
| **Title** | `Orders` | Cómo lo leen las personas: en la web, en el catálogo, en el portal del gateway, en el proyecto de Activepieces |
| **Description** | `Orders of the shop` | Una frase. Aparece en el catálogo y en la descripción de la pull request |

### Página 2 · Its first entity

La aplicación nace con un CRUD completo de una entidad (como el petstore con sus mascotas).

| Campo | Ejemplo | Qué significa |
|---|---|---|
| **Entity, singular** | `order` | La tabla y la clase Python (`Order`) |
| **Entity, plural** | `orders` | La ruta del API (`/api/orders`) y la página de la web |

La entidad nace con nombre, categoría, estado y fecha de inicio: cámbiala por lo que necesites (con una migración).

### Página 3 · Where it runs

| Campo | Ejemplo | Qué significa |
|---|---|---|
| **Environments** | `nato-sirtap` | Los clusters donde se despliega, como `<zona>-<programa>`. Se pueden añadir más después en el fichero de la aplicación |
| **Version of the Python Framework** | `2.0` | La línea del framework con la que nace. Solo se ofrecen las **mantenidas**: **2.0** (la actual, con traza de auditoría) y **0.1** (en retirada, mantenida hasta el 15-04-2027). En el catálogo la aplicación dependerá de esa línea (`python-framework-2-0` o `python-framework-0-1`) |

| **Initial stage** | `dev` | La etapa en la que nace: **dev** por defecto (`<nombre>-dev`, su propio cliente de Keycloak y sus usuarios de prueba). Después pasa a pre y a pro con la plantilla **Promote an application**. Elige `pro` solo si debe nacer ya en producción. DataHub solo existe en pro |

Lo que cambia según la etapa (nombres, Keycloak, DataHub): sección 8.

### Página 4 · Platform blocks

Cada bloque es algo que la aplicación usa de la plataforma. Todos son opcionales salvo el inicio de sesión.

| Campo | Qué significa |
|---|---|
| **Single sign-on (Keycloak)** | Siempre activo. El login con Keycloak, los roles y los usuarios de prueba |
| **Object storage - buckets** | Una entrada por bucket (`documents`). Cada una se convierte en `<nombre>-documents` en SeaweedFS |
| **Documents (Alfresco) - sites** | Una entrada por sitio (`records`). Cada una se convierte en el sitio privado `<nombre>-records` |
| **Documents (Alfresco) - groups** | Grupos de Keycloak cuyos miembros entran en **todos** los sitios de la aplicación |
| **Data catalog (DataHub) - register its data** | Publica sus tablas como un producto de datos en DataHub |
| **Data catalog - people / groups who own its data** | Responsables **de negocio** del producto de datos. El técnico es siempre el equipo de la aplicación |
| **API gateway (Gravitee) - publish its API** | Publica el API en `/gateway/<nombre>/` y en el portal de desarrolladores |
| **API gateway - team** | Grupo `gravitee-team-<equipo>` cuyos miembros ven el API en Backstage |
| **Processes (Camunda) - deploy its processes** | Despliega en Camunda los BPMN de `platform/processes/` del repositorio |
| **Processes - groups** | Grupos cuyos miembros inician los procesos y trabajan sus tareas en Tasklist |
| **Dashboards (Superset) - import its dashboards** | Importa en Superset los dashboards de `platform/dashboards/` |
| **Flows (Activepieces) - import its flows** | Importa en un proyecto propio de Activepieces los flujos de `platform/flows/` |
| **Flows - groups that edit them** | Grupos cuyos miembros son editores de ese proyecto |
| **People who get the role `<nombre>-admin`** | Usuarios del realm que serán administradores de la aplicación. Vacío: solo el usuario de prueba |

Qué crea exactamente cada uno: sección 5.

### Página 5 · Repository

| Campo | Ejemplo | Qué significa |
|---|---|---|
| **GitHub owner** | `javivillar` | Usuario u organización dueña del repositorio `<owner>/<nombre>`, que se crea **privado** |

Al final, Backstage muestra un resumen. Revísalo y pulsa **Create**.

## 4. Qué hace la plantilla al pulsar Create

La pantalla muestra cinco pasos. Esto es lo que significa cada uno:

| Paso | Qué hace | Si falla |
|---|---|---|
| **Generate the application from the skeleton** | Copia el esqueleto de la línea elegida (una copia del petstore) y sustituye los nombres por los tuyos: paquete, entidad, rutas, roles, cliente de Keycloak, títulos | Es casi siempre un valor del formulario fuera de su patrón |
| **Create the repository** | Crea el repositorio privado `<owner>/<nombre>` en GitHub con ese código en `main`, en un primer commit `<nombre> 0.1.0`. Ese commit dispara el CI, que publica las imágenes | Un repositorio con ese nombre ya existe |
| **Register in the Backstage catalog** | Registra su `catalog-info.yaml`: aparece en el catálogo como componente, con su documentación y dependiendo del framework | Se puede registrar a mano después desde *Register existing component* |
| **Prepare the deployment** | Escribe el fichero de la aplicación (`bootstrap/app-of-apps/apps/<nombre>.yaml`: dónde va, qué imágenes, qué bloques) y la definición de su API para el catálogo (`catalog/apis/<nombre>.json`) | — |
| **Open the deployment pull request** | Abre una pull request en `refresquito-services` con esos dos ficheros, en la rama `deploy-<nombre>` | Ya existe una pull request abierta de esa aplicación |

Al terminar tienes tres enlaces: el **repositorio**, la **pull request de despliegue** y la **ficha en el catálogo**.

**Antes de hacer merge**, espera a que el CI del repositorio nuevo termine en verde (pestaña *Actions*): es el que
publica las imágenes del commit que la pull request despliega. Si haces merge antes, los pods quedan en
`ImagePullBackOff` hasta que existan; no se rompe nada, solo esperan.

## 5. Qué se crea, servicio por servicio

En la tabla, `orders` es el nombre de la aplicación y los nombres son los de **pro**. En dev y pre llevan la etapa
detrás del nombre (`orders-dev-oneke`, `https://orders-dev.<dominio>`, cliente `orders-dev`, `app-orders-dev`...): la tabla
completa está en la sección 8. Lo que **no** se crea (personas, grupos de personas, dominios de
DataHub) aparece marcado como *debe existir*.

### Kubernetes (Argo CD)

| Qué | Nombre |
|---|---|
| Aplicación de Argo CD | `orders-oneke` (se sincroniza sola con cada cambio del fichero) |
| Namespace | `<zona>-<programa>-orders-oneke`, con las etiquetas `refresquito.io/segment=business-support`, `refresquito.io/stage=pro`, zona y programa |
| Web, API y PostgreSQL | `orders-oneke-web`, `orders-oneke-api`, `orders-oneke-db` (disco en Longhorn) |
| URL | `https://orders.<dominio>`; `/api` va al API, el resto a la web |
| Contraseña de la base de datos | generada una vez en el namespace por External Secrets |
| Provisioner | CronJob `orders-oneke-provisioner`, cada 5 minutos: crea y alinea lo de los bloques; **nunca borra** |

### Keycloak (siempre)

| Qué | Nombre | Notas |
|---|---|---|
| Cliente | `orders` | Público, con PKCE. Lo usan la web y el API |
| Rol de lectura | `orders-viewer` | Rol del realm. Lee los datos |
| Rol de administración | `orders-admin` | Rol del realm. Además crea, edita y borra |
| Usuarios de prueba | `orders-viewer`, `orders-admin` | Uno por rol, con la contraseña de prueba del cluster (pregúntala al equipo de plataforma) |
| Administradores | los de *People who get the role orders-admin* | *Deben existir*. Se les da `orders-admin` |

Los permisos los comprueba el API: un usuario sin `orders-viewer` ni `orders-admin` recibe 403.

### Grupos de Keycloak: cuáles se crean y cuáles se usan

| Grupo | Lo crea | Para qué | Quién entra |
|---|---|---|---|
| `alfrescodms-site-orders-<sitio>` | El provisioner, uno por sitio de Alfresco | Quien está en él entra en el sitio `orders-<sitio>` | Los miembros de los grupos indicados en *Documents - groups*, al momento y también los que entren después. **Nunca se saca a nadie** |
| `activepieces-user` | *Debe existir* (lo trae la plataforma) | Sin él, Keycloak no deja entrar en Activepieces | Se añade a las personas de *Flows - groups* |
| Los grupos de *Documents*, *Processes*, *Flows* y *Data catalog* | *Deben existir* | Dicen quién usa cada cosa | Los gestiona quien administra las personas |
| `gravitee-team-<equipo>` | *Debe existir* | Quién ve el API en Backstage | — |
| `superset-editor`, `superset-admin` | *Deben existir* (los trae la plataforma) | Quién ve los dashboards en Superset | — |
| `<segmento>-team` (`business-support-team`) | Es del catálogo | Equipo propietario de la aplicación y responsable técnico de sus datos | — |

### SeaweedFS · bloque *Object storage*

| Qué | Nombre |
|---|---|
| Buckets | `orders-<bucket>` |
| Identidad de la aplicación | `app-orders`, solo con permiso sobre sus buckets (política `App-orders-S3`) |
| En el entorno del API | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ENDPOINT_URL_S3`, `AWS_DEFAULT_REGION`, `S3_BUCKETS`, `S3_BUCKET_<BUCKET>` |

### Alfresco · bloque *Documents*

| Qué | Nombre |
|---|---|
| Sitios | `orders-<sitio>`, privados |
| Persona de la aplicación | `app-orders`, colaboradora (SiteCollaborator) de sus sitios y de ningún otro |
| Personas | entran como lectoras (Consumer) a través del grupo `alfrescodms-site-orders-<sitio>`, **después de haber entrado una vez en Alfresco** |
| En el entorno del API | `ALFRESCO_URL`, `ALFRESCO_USERNAME`, `ALFRESCO_PASSWORD`, `ALFRESCO_SITES`, `ALFRESCO_SITE_<SITIO>` |

### DataHub · bloque *Data catalog*

| Qué | Nombre |
|---|---|
| Producto de datos | `orders` (`urn:li:dataProduct:orders`) |
| Datasets | uno por tabla de su base de datos, con columnas, tipos y los comentarios como descripción; se releen cada pocos minutos |
| Responsables | `business-support-team` (técnico) y las personas y grupos que indicaste (negocio). Solo se añaden |
| Dominio | opcional (`domain:` en el fichero); *debe existir*, lo crean los stewards |

### Gravitee · bloque *API gateway*

| Qué | Nombre |
|---|---|
| API | `Orders`, en `https://gravitee.<dominio>/gateway/orders/`, pública en el portal, con su OpenAPI |
| Plan | JWT: exige un token del realm de un cliente suscrito |
| Aplicación de Gravitee | `Orders (web)`, con el cliente `orders`, ya suscrita |
| Equipo | metadato `backstage-team` = el grupo indicado |

### Camunda · bloque *Processes*

| Qué | Nombre |
|---|---|
| Despliegue | `orders`, con los BPMN/DMN de `platform/processes/`; cada cambio es una versión nueva |
| Regla | el `id` de cada proceso o decisión empieza por `orders-` (si no, no se despliega) |
| Usuario de la aplicación | `app-orders` en Keycloak, con permiso solo sobre sus procesos |
| Personas | los grupos de *Processes - groups*: inician sus procesos y trabajan sus tareas en Tasklist (`https://bpm.<dominio>`) |
| En el entorno del API | `CAMUNDA_URL`, `CAMUNDA_USERNAME`, `CAMUNDA_PASSWORD`, `CAMUNDA_KEY_PREFIX` (`orders-`) |

### Superset · bloque *Dashboards*

| Qué | Nombre |
|---|---|
| Base de datos | `Orders (orders)`: la de la aplicación en ese cluster, leída con el rol de **solo lectura** `orders_reader` |
| Dashboards | los de `platform/dashboards/`, con su dirección (slug) empezando por `orders` |
| Quién los ve | `superset-editor` y `superset-admin` |

### Activepieces · bloque *Flows*

| Qué | Nombre |
|---|---|
| Proyecto | `Orders` (identificador `platform:orders`) |
| Flujos | uno por fichero de `platform/flows/`, publicados cuando están completos |
| Personas | los miembros de *Flows - groups*, invitados como **Editor** (y añadidos a `activepieces-user`) |
| En el entorno del API | `ACTIVEPIECES_FLOW_<FLUJO>_URL` por cada flujo que empieza con un webhook |

### Catálogo de Backstage

| Entidad | Nombre | Relaciones |
|---|---|---|
| Componente del repositorio | `orders` | parte de `business-systems`, dependiendo del framework |
| Servicio desplegado | `orders-oneke` | depende de `orders`, de su línea del framework (`python-framework-2-0`) y de un recurso por bloque |
| API | `orders` | la proporciona `orders-oneke` |
| Recursos de los bloques | `orders-sso-client`, `orders-<bucket>`, `orders-<sitio>`, `orders-data-product`, `orders-gateway-api`, `orders-processes`, `orders-dashboards`, `orders-flows` | cada uno depende del servicio que lo presta (`iam-oneke`, `seaweedfs-oneke`...) |

En la ficha del servicio ves todo lo que usa la aplicación; en la ficha de cada servicio de la plataforma, todas las
aplicaciones a las que afecta.

### Observabilidad

Los logs del API llegan a Loki y sus métricas a Prometheus sin hacer nada. Con la 2.0, la auditoría (quién escribió
qué y qué peticiones se rechazaron) es un stream aparte, `{kubernetes_namespace_name="<namespace>", log_type="audit"}`,
y se ve en el dashboard de Grafana *Python Framework - Audit*.

### SBOM de las imágenes

Al hacer merge en `main`, el CI genera el **SBOM** de cada imagen que publica (CycloneDX JSON, con
[Syft](https://github.com/anchore/syft)): los paquetes del sistema operativo y de la aplicación, sea cual sea su
lenguaje. Lo adjunta a la imagen en ghcr.io como artefacto OCI ligado a su digest, así que el SBOM viaja con el tag
desplegado, y también lo guarda como artefacto del run (pestaña **CI/CD**, `<nombre>-api.cdx.json` y
`<nombre>-web.cdx.json`). Para leerlo: `oras discover ghcr.io/<owner>/<nombre>-api:<commit>`. El framework
(`refresquito-fastapi`, `refresquito-angular`) aparece en él con su versión y su licencia. Las vulnerabilidades de las
imágenes las recoge Wazuh.

## 6. Comprobar que todo ha ido bien

1. **Argo CD**: la aplicación `orders-oneke` está *Synced* y *Healthy* (en Backstage, pestaña de Kubernetes o de Argo CD
   de la ficha `orders-oneke`).
2. **La web**: `https://orders.<dominio>` abre y te lleva al login de Keycloak.
3. **Los roles**: con el usuario de prueba `orders-viewer` ves la lista pero no puedes crear; con `orders-admin`, sí.
4. **El provisioner**: el log del último Job de `orders-oneke-provisioner` termina en `orders: done`. Cada bloque dice
   en una línea qué ha creado o que está *as declared*.
5. **El catálogo**: la ficha `orders-oneke` muestra sus recursos y su línea del framework en *Dependencies*.

## 7. Cambios habituales después

Todo se hace con una pull request a `bootstrap/app-of-apps/apps/<nombre>.yaml` de `refresquito-services`:

| Para | Qué cambias |
|---|---|
| Publicar una versión nueva | La plantilla **Promote an application**, o `image.tag` (o `stages.<etapa>.tag`) con el commit cuyas imágenes quieres |
| Dar el rol de administrador a alguien | Añadirlo a `users` del rol `admin` |
| Añadir un bucket, un sitio o un grupo | Añadirlo a la lista de su bloque |
| Activar un bloque más | Su sección en `platform:` con `enabled: true` |
| Dejar de usar un bloque | `enabled: false`: deja de gestionarse y **lo que creó se queda** |
| Llevarla a otro cluster | Añadir su `<zona>-<programa>` a `environments` |
| Pasar a otra línea del framework | Cambiar las versiones de los paquetes en el repositorio y luego `framework:` en el fichero |

**Nada se borra solo.** Quitar un bloque, un bucket, un sitio o una persona de una lista deja lo creado como estaba;
borrarlo es una decisión a mano en el propio servicio.

### Retirar una aplicación

El catálogo recibe la aplicación por dos vías, y hay que cerrar las dos: el **componente** `<nombre>` viene de su
repositorio (Backstage descubre cada 30 minutos los `catalog-info.yaml` de los repositorios del owner), y el **servicio**
`<nombre>-oneke`, su API y sus recursos vienen del fichero de despliegue. En este orden:

1. **El despliegue.** Una pull request a `refresquito-services` que borre `bootstrap/app-of-apps/apps/<nombre>.yaml`,
   `catalog/apis/<nombre>.json` y su línea en `catalog/apis/README.md`. Al hacer merge, Argo CD elimina la aplicación y
   sus objetos, y del catálogo desaparecen `<nombre>-oneke`, su API y sus recursos.
2. **El namespace.** Argo CD no lo borra, y con él se queda el disco de la base de datos: `kubectl delete ns
   <zona>-<programa>-<nombre>-oneke` borra los dos. **Los datos se pierden**: haz copia antes si los necesitas.
3. **El repositorio.** Bórralo en GitHub (o archívalo y quítale `catalog-info.yaml`). Mientras exista con ese fichero,
   el descubrimiento vuelve a meter el componente en el catálogo.
4. **El componente.** En su ficha, menú ⋮, *Unregister entity*, *Unregister location*. Después del paso 3; antes,
   vuelve a aparecer.
5. **Lo de fuera, que nunca se borra solo.** En Keycloak, el cliente `<nombre>`, los roles `<nombre>-viewer` y
   `<nombre>-admin` y los usuarios de prueba (plantillas *keycloak-delete-client* y *keycloak-delete-user* de *Create*;
   los roles, en la consola de Keycloak). Lo de los demás bloques también tiene su plantilla de borrado:
   *seaweedfs-delete-bucket*, *alfresco-delete-site*, *camunda-delete-process*, *activepieces-delete-project* y, en
   DataHub, *datahub-deprecate-asset*. Opcional: las imágenes `<nombre>-api` y `<nombre>-web` en GitHub Packages.

## 8. Etapas: dev, pre y pro

Un cluster puede tener las tres etapas de la aplicación, cada una en su namespace y con su versión. La aplicación nace
en **dev** (campo *Initial stage*): su fichero tiene `stages: { dev: { tag: ... } }`. Con la plantilla **Promote an
application** pasa a pre y a pro, y cada paso es una pull request que copia el tag de una etapa a la siguiente:

| | pro | dev / pre |
|---|---|---|
| Namespace | `<zona>-<programa>-orders-oneke` | `<zona>-<programa>-orders-dev-oneke` |
| URL | `https://orders.<dominio>` | `https://orders-dev.<dominio>` |
| Cliente de Keycloak | `orders` | `orders-dev` |
| Roles | `orders-viewer`, `orders-admin` del **realm** | los mismos nombres, como roles **del cliente** `orders-dev`: un rol dado en dev no vale en pro |
| Usuarios de prueba | `orders-viewer`, `orders-admin` | `orders-dev-viewer`, `orders-dev-admin` |
| Lo que crean los bloques | `orders-...`, `app-orders` | `orders-dev-...`, `app-orders-dev`; los ids de Camunda pasan a `orders-dev-...` |
| DataHub | sí | no: hay un único DataHub y el producto de datos es el de pro |
| En el catálogo | `orders-oneke` (production) | `orders-dev-oneke` (experimental) |

El código de la aplicación no cambia entre etapas. Cómo mover versiones: [Promocionar una aplicación](python-framework-promote.md).

## 9. Cómo trabajar en el repositorio con dev, pre y pro

**Las etapas no son ramas.** En el repositorio de la aplicación hay una sola rama principal, `main`. Qué versión corre en
cada etapa no está en tu repositorio, sino en el fichero de despliegue de `refresquito-services`:

```yaml
stages:
  dev: { tag: "c3..." }   # lo último de main
  pre: { tag: "c2..." }   # en validación
  pro: { tag: "c1..." }   # en producción
```

### El ciclo de un cambio

1. Trabajas en una rama corta (`feature/...`) y abres una pull request hacia `main`. Su CI pasa las pruebas, pero **no
   publica imágenes**.
2. Al hacer merge en `main`, el CI publica `<nombre>-api` y `<nombre>-web` con la etiqueta del **hash del commit**: esa
   es la versión. Lo ves en la pestaña **CI/CD** del componente de tu repositorio.
3. Con la plantilla **Promote an application** llevas ese commit a **dev** (*From*: a commit of its repository).
4. Cuando dev está bien, **dev → pre** y luego **pre → pro**, con la misma plantilla. Cada paso es una pull request a
   `refresquito-services` que copia el tag de una etapa a la siguiente.

**Se construye una vez y se despliega muchas.** Pre y pro no reconstruyen nada: reciben exactamente la imagen que se
probó antes. Una etapa nunca cambia por promocionar otra: llevar algo a pre no toca dev ni pro.

### Qué cambia entre etapas sin tocar el código

| | Cómo llega a cada etapa |
|---|---|
| **Configuración** (cliente de Keycloak, buckets, sitios, Camunda, base de datos...) | Variables de entorno con los nombres de esa etapa. El código **no debe tener nada escrito a mano** que dependa de la etapa |
| **Contenido de `platform/`** (procesos, dashboards, flujos) | Viaja dentro de la imagen: cada etapa tiene el de su versión. Si pro corre `c1`, tiene los procesos de `c1` |
| **Base de datos** | Cada etapa tiene la suya; las migraciones se aplican solas al arrancar el API. Los datos no pasan de una etapa a otra |
| **Personas** | Los grupos que declaras son los mismos en todas las etapas; los usuarios de prueba y los roles de dev y pre son propios |

En el código, usa siempre las variables de entorno:

| En lugar de escribir | Usa | Que vale en pre |
|---|---|---|
| `"orders-documents"` | `S3_BUCKET_DOCUMENTS` | `orders-pre-documents` |
| `"orders-records"` | `ALFRESCO_SITE_RECORDS` | `orders-pre-records` |
| `"orders-review"` | `CAMUNDA_KEY_PREFIX + "review"` | `orders-pre-review` |
| la URL de un flujo | `ACTIVEPIECES_FLOW_<FLUJO>_URL` | la del proyecto `Orders (pre)` |

Si un nombre está escrito a mano, en dev y pre falla: cada etapa solo tiene permiso sobre lo suyo.

### Lo que crean los bloques: una copia por etapa

Cada etapa tiene **su propia copia** de cada bloque, para que probar en dev nunca toque lo que usa pro: el proceso de
Camunda (`orders-dev-review`), el sitio de Alfresco (`orders-dev-records`, que nace vacío), el bucket, los dashboards
(sobre la base de datos de dev) y el proyecto de Activepieces (`Orders (dev)`, cuyas **conexiones hay que crear en cada
proyecto**: las credenciales nunca van al repositorio). DataHub es la excepción: hay uno solo y el producto de datos es
el de pro.

**Lo que diseñas a mano en dev no se guarda solo en el repositorio.** Un proceso, un dashboard o un flujo hecho en la
web de dev hay que exportarlo y guardarlo en `platform/` con un commit (sección *Lo que usa de la plataforma* de
[Aplicación nueva](python-framework.md)); si no, se pierde cuando el provisioner vuelve a importar el del repositorio.

### Migraciones compatibles hacia atrás

Una versión pasa por dev y pre antes de llegar a pro, y cada etapa migra su base de datos al arrancar. Prefiere cambios
que la versión anterior siga entendiendo: **añadir antes que borrar o renombrar** (una columna nueva primero; quitar la
vieja en una versión posterior, cuando ninguna etapa la use).

### Trabajo a medias y arreglos urgentes

- **Mantén `main` promocionable.** Lo que tenga que entrar en `main` sin estar terminado, déjalo desactivado (una
  variable de entorno o un *flag*) hasta que lo esté. Así cualquier commit de `main` puede llegar a pro.
- **Un arreglo urgente en pro** se hace en `main` y se promociona dev → pre → pro como siempre (son minutos). Si `main`
  tiene algo que no puede salir todavía, crea una rama desde el commit de pro (`git checkout -b hotfix/x <commit de pro>`)
  y llévalo después también a `main`. Ojo: **el CI solo publica imágenes desde `main`**, así que una rama `hotfix/*` no
  tiene imágenes que desplegar mientras su CI no lo permita (pídeselo al equipo de plataforma).

## 10. Problemas frecuentes

| Síntoma | Causa | Qué hacer |
|---|---|---|
| Pods en `ImagePullBackOff` | Se hizo merge antes de que el CI publicara las imágenes | Esperar al CI; los pods arrancan solos |
| La web da 401 o vuelve al login en bucle | El provisioner aún no ha creado el cliente | Esperar a su siguiente pasada (máximo 5 minutos) |
| Un administrador no tiene permisos | Su usuario no existía en el realm cuando se declaró | Crear el usuario; la siguiente pasada le da el rol |
| Alguien de un grupo no ve el sitio de Alfresco | Nunca ha entrado en Alfresco | Que entre una vez; después aparece en el sitio |
| Un flujo se queda en borrador | Usa conexiones que no existen en el proyecto | Crear las conexiones en Activepieces con esos nombres |
| Un proceso no se despliega | Su `id` no empieza por `<nombre>-` | Renombrarlo en el BPMN y publicar una versión nueva |
| Una pasada del provisioner falla | Un servicio no responde o rechaza algo | El log del Job dice qué bloque y por qué; los demás bloques siguen funcionando |

## 11. Lo que se espera de ti

- **Los permisos los decide el API**, no la web: la web solo oculta lo que un rol no puede hacer.
- **Cada cambio del API** se refleja en `backend/openapi.json`; el CI falla si no está al día.
- **Nunca pongas secretos** en el repositorio ni en los eventos de auditoría: las credenciales llegan por el entorno.
- **Mantén la aplicación en una línea mantenida** del framework: en el catálogo, una dependencia de una línea
  `deprecated` es un aviso de que hay que migrar.
