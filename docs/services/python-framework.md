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
| GitHub owner | `javivillar` | Dueño del repositorio |

## Desplegarla en la plataforma

La plantilla crea el repositorio; el despliegue se prepara en `refresquito-services` con un comando, que la propia
plantilla te muestra al terminar con el commit ya puesto:

```bash
python3 bootstrap/add-python-app.py orders --title "Orders" --entity order --entities orders --tag <commit>
```

Genera el chart `orders-oneke`, el cliente y los roles en el fichero del realm de Keycloak, la clave del almacén de
secretos y las entradas del catálogo. Se revisa en una *pull request*; una vez fusionada, una pasada del bootstrap con
`orders-oneke` en `RQ_APPS` la instala en `<zona>-<programa>-orders-oneke`.

## Qué se espera de ti

- **Los permisos los decide el API**, no la web: la web solo oculta lo que un rol no puede hacer.
- **Cada cambio del API** se refleja en `backend/openapi.json`; el CI falla si no está al día.
- **El esqueleto no se edita a mano**: se regenera desde el petstore (`tools/make-python-app-skeleton.py`). Si algo
  debe cambiar para todas las aplicaciones nuevas, cámbialo en el petstore.
