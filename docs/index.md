# Servicios Refresquito desde Backstage

Esta documentación es para **quien desarrolla** en la plataforma: qué puedes hacer desde Backstage con cada servicio,
qué permisos necesitas y qué debes esperar cuando lo haces. No cubre cómo se opera o se despliega la plataforma
(eso vive en el repositorio `refresquito-services`).

## Qué encuentras en Backstage

| Dónde | Para qué |
|---|---|
| **Create** (plantillas) | Iniciar recursos en un servicio: un proyecto, un bucket, un producto de datos… Cada plantilla es un formulario. |
| **Páginas de servicio** (por ejemplo `/datahub`) | Ver y gestionar lo tuyo sin salir del portal. |
| **Catálogo** | Las entidades registradas; algunas muestran tarjetas de los servicios (por ejemplo la de DataHub). |
| **Esta documentación** | Qué esperar de cada servicio. |

## Reglas comunes

- **Un solo inicio de sesión.** Entras con tu cuenta de Keycloak; el portal no guarda contraseñas.
- **Lo tuyo es tuyo.** Lo que creas queda a tu nombre (o al de tu grupo) y **otros usuarios no pueden editarlo**.
  Las cuentas con el grupo `backstage-admin` pueden gestionarlo todo.
- **Los permisos vienen de grupos de Keycloak**, no de roles sueltos. Si un botón no aparece o recibes un *Forbidden*, casi
  siempre falta un grupo: pídelo al administrador del servicio.
- **Backstage inicia; el servicio modela.** Desde el portal se crean los objetos de alto nivel (proyectos, productos,
  buckets, sitios…). El trabajo detallado —flujos, dashboards, columnas, procesos— se hace en la herramienta del servicio.
- **Los secretos no pasan por Backstage.** Contraseñas, claves y conexiones se configuran en el propio servicio.
- **Las plantillas que crean algo empiezan en «solo validar»** cuando lo ofrecen: te muestran qué harían sin crear nada.

## Servicios documentados

| Servicio | Para qué | Página |
|---|---|---|
| Keycloak | Crear y gestionar tus usuarios, grupos y clientes OIDC | [Keycloak](services/keycloak.md) |
| Superset | Conexiones, datasets, gráficos y dashboards propios | [Superset](services/superset.md) |
| Camunda | Desplegar y gestionar tus procesos BPMN | [Camunda](services/camunda.md) |
| SeaweedFS | Buckets S3, table buckets, grupos y políticas propios | [SeaweedFS](services/seaweedfs.md) |
| Alfresco | Crear y gestionar tus sites de documentos | [Alfresco](services/alfresco.md) |
| Activepieces | Proyectos, miembros y flujos de automatización | [Activepieces](services/activepieces.md) |
| DataHub | Dar de alta y gobernar los datos de un producto (dueños, clasificación, retención, linaje) | [DataHub](services/datahub.md) |

## Cómo se documenta cada servicio

Cada página sigue el mismo orden: **qué te da**, **quién puede hacer qué**, **cómo se usa**, **qué garantías tienes** y **qué no
debes esperar**. Si algo de lo que ves difiere de lo que aquí se dice, es un error de la documentación o del servicio:
avisa a un administrador.
