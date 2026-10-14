# Aplicación nueva con el Python Framework

El **Python Framework** es la base de las aplicaciones de negocio de la plataforma: una web Angular
(`refresquito-angular`), un servicio FastAPI (`refresquito-fastapi`) y PostgreSQL, con el login y los permisos en
Keycloak. La plantilla **New application (Python Framework)** de *Create* te da una aplicación nueva ya funcionando.

Cómo está descrito el framework en el catálogo, su política de soporte y qué se actualiza al publicar una versión:
[El Python Framework en el catálogo](python-framework-catalog.md).

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
| Version of the Python Framework | `0.1` | Con qué versión del framework nace. Solo se ofrecen las mantenidas |
| Platform blocks | *Single sign-on* | Lo que usa de la plataforma. Hoy, el inicio de sesión con Keycloak (lo llevan todas), el almacenamiento de objetos y los documentos (opcionales); irán llegando gobierno del dato, gateway, procesos, dashboards y flujos |
| Object storage - buckets | `documents` | Opcional. Un bucket `<name>-documents` en SeaweedFS, solo para la aplicación, con su clave de acceso ya en el entorno del API |
| Documents (Alfresco) - sites | `records` | Opcional. Un sitio privado `<name>-records` en Alfresco, con un usuario propio de la aplicación y sus credenciales ya en el entorno del API |
| Documents (Alfresco) - groups | `finance` | Grupos de Keycloak cuyos miembros entran en los sitios de la aplicación |
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
| Publicar una versión nueva | Cambiar `image.tag` en el fichero de la aplicación por el commit cuyas imágenes quieres, en una pull request |
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

## Qué se espera de ti

- **Los permisos los decide el API**, no la web: la web solo oculta lo que un rol no puede hacer.
- **Cada cambio del API** se refleja en `backend/openapi.json`; el CI falla si no está al día.
- **El esqueleto no se edita a mano**: se regenera desde el petstore (`tools/make-python-app-skeleton.py`). Si algo
  debe cambiar para todas las aplicaciones nuevas, cámbialo en el petstore.
