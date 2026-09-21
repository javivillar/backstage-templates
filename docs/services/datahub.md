# DataHub — gobierno del dato

DataHub es el catálogo de metadatos de Refresquito: dice **qué datos existen, de quién son, cómo se clasifican y de dónde
vienen**. Desde Backstage no lo sustituyes: **das de alta y consultas** lo que importa para gobernar un producto de datos.

## Qué te da

- **Página `/datahub`** en Backstage: busca activos, filtra los que tienen huecos de gobierno y ve la **completitud** de cada uno.
- **Tarjeta y pestaña *Data governance*** en las entidades del catálogo que están enlazadas a un activo de DataHub.
- **Plantillas y botones** para registrar un producto de datos, añadirle activos, deprecar un activo, ver el impacto de un cambio y
  pedir vocabulario.
- **Un enlace directo a DataHub** desde las entidades que genera la plantilla de producto y un acceso rápido en la página de inicio.

## Quién puede hacer qué

El acceso lo dan los **grupos de Keycloak** `datahub-admin`, `datahub-editor` y `datahub-viewer`. Sin ninguno de ellos recibes
*Forbidden* y el mensaje te dice que pidas a un administrador de DataHub que te añada.

| Quién | Puede |
|---|---|
| `datahub-viewer` | Leer: página `/datahub`, tarjetas, impacto de un cambio y solicitud de vocabulario. **No** escribe. |
| `datahub-editor` | Lo anterior, **más** dar de alta un producto nuevo (te conviertes en su propietario técnico) y editar o deprecar los activos de **los productos de los que eres propietario**, directamente o por un grupo tuyo. |
| Steward (`datahub-admin`) y `backstage-admin` | Todo, incluido corregir clasificaciones de cualquier producto. |

Los botones que **no** puedes usar no se muestran; si no puedes crear, la página lo explica.

## Cómo se usa

### Dar de alta un producto de datos — **New data product**

Un formulario con el «brief de datos»: nombre y dominio del producto, responsables (negocio, técnico y, si toca, *steward*),
almacenes (base de datos, topic, prefijo S3 o sitio de Alfresco) con su clasificación y retención, procesos opcionales con lo que
leen y escriben (esto crea el **linaje previsto**) y enlaces.

Reglas que verás aplicadas:

- **Nunca se crean dominios, términos ni etiquetas nuevos** desde la plantilla: eliges de listas que vienen de DataHub. Si te falta uno, usa *Request vocabulary*.
- Si una columna es **dato personal**: la **base legal** RGPD, la retención y una clasificación de al menos *Confidential* pasan a ser obligatorias.
- Desde *Confidential*, el **steward** es obligatorio.
- El **propietario técnico** por defecto eres tú.

La plantilla arranca en **«Validate only»**: comprueba el formulario y te enseña el plan **sin escribir nada**. Para crear de verdad,
desmarca esa opción. Opcionalmente, elige un repositorio (privado) donde publicar el `catalog-info.yaml` del producto: la plantilla lo
registra en el catálogo con las anotaciones que hacen aparecer la tarjeta y la pestaña de gobierno. Sin repositorio, no se publica nada.

### Añadir activos a un producto, o deprecar uno

Solo sobre productos **de los que eres propietario**. Deprecar es un **borrado suave**: el activo deja de aparecer y se puede deshacer.

### Ver el impacto de cambiar un dataset — **Check impact**

Antes de cambiar un esquema, te dice **qué activos dependen de él aguas abajo** según el linaje: cuántos por tipo, quién los consume,
cuáles están marcados `dq-critical` y **a qué propietarios avisar**. Está abierto a cualquier usuario con acceso a DataHub.
Cubre hasta 100 resultados por consulta (te avisa si hay más) y trabaja a nivel de activo, no de columna.

### Pedir vocabulario — **Request vocabulary**

Si necesitas un dominio, término o etiqueta que no existe, lo pides y **un steward lo crea**. La petición es una *issue* de GitHub en
`javivillar/refresquito-services` con la etiqueta `datahub-vocabulary`. La plantilla:

- se niega a pedir algo que **ya existe** (sin distinguir mayúsculas, espacios ni guiones);
- no duplica una issue **abierta** con el mismo título;
- exige definición y justificación;
- por defecto **solo te enseña la previsualización**.

## Qué garantías tienes

- **Nadie recibe permiso para crear vocabulario**, ni siquiera el propio plugin: solo los stewards, en DataHub.
- **Relanzar una plantilla no duplica** lo ya creado, y si un alta falla a mitad **no queda un estado a medias**: se deshace.
- **Lo que no eres propietario, no lo editas**: la comprobación se hace en el servidor, no solo escondiendo botones.
- Todo lo que crea el portal queda **marcado** como creado desde Backstage y con **quién lo pidió**.

## Qué no debes esperar

- **Modelar el detalle no se hace aquí.** Descripciones de columnas, calidad, incidentes o el glosario se trabajan en la propia UI de DataHub.
- **No ves solo «lo tuyo» en las búsquedas de lectura.** Cualquier usuario con grupo `datahub-*` puede leer el catálogo; la propiedad
  restringe **quién escribe**, no quién lee.
- **La completitud es una guía, no una nota.** Un activo se considera «gobernado» a partir del **80 %** de las comprobaciones que le aplican.
- **Publicar el repositorio del producto** (*Backstage catalog*) y **crear de verdad la issue de vocabulario** dependen de los permisos del
  token de GitHub de Backstage y todavía no se han comprobado extremo a extremo; usa la previsualización mientras tanto.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Forbidden … is not in any DataHub access group* | No estás en `datahub-viewer/editor/admin` | Pide el grupo a un administrador |
| *Forbidden … is not in a DataHub write group* | Eres *viewer* e intentas crear | Pide `datahub-editor` |
| *Forbidden … is not an owner of this data product* | El producto es de otro equipo | Pide al propietario que lo haga o que te añada como propietario |
| No aparece la tarjeta de gobierno en una entidad | La entidad no lleva la anotación `datahub.io/…` | Genérala con la plantilla de producto |
