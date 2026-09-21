# SeaweedFS — almacenamiento de objetos (S3)

SeaweedFS es el almacenamiento compatible con S3. Desde Backstage creas y gestionas **tus buckets, table buckets, grupos y políticas**.

## Qué te da

- **Página `/seaweedfs-manager`** con cuatro pestañas (buckets, table buckets, grupos, políticas), filtradas por propietario (los
  administradores ven todo, con columna *Owner*).
- **Ocho plantillas**: crear y borrar, para cada uno de estos objetos:

| Objeto | Detalle |
|---|---|
| Bucket | Bucket S3 |
| Table bucket | Bucket de tablas S3. Para borrarlo se identifica por su **ARN**, que ves en la página de gestión. |
| Grupo IAM | Grupo del que eres propietario |
| Política IAM | Se crea a partir de un documento de política en JSON (misma forma que AWS IAM) |

## Quién puede hacer qué

- **Crear**: cualquier usuario que haya entrado en Backstage; pasas a ser el propietario.
- **Ver, usar y borrar**: solo el propietario o `backstage-admin`.

## Cómo se usa

1. *Create* → *Create SeaweedFS Bucket* (o el objeto que necesites).
2. Al crear un bucket se te concede automáticamente **acceso completo** a él, también desde el *File Browser* del Admin UI de SeaweedFS.
3. Para **adjuntar políticas a un grupo**, edita el grupo en `/seaweedfs-manager`: el selector te ofrece **solo las políticas que has creado tú**.

## Qué garantías tienes

- **Tu bucket es inaccesible para otros usuarios no administradores**, tanto en Backstage como en el *File Browser* (que deniega por defecto).
- **No puedes adjuntar políticas ajenas** a un grupo tuyo: el servidor lo comprueba, no solo el desplegable.

## Qué no debes esperar

- **Aislamiento de grupos y políticas dentro del Admin UI de SeaweedFS.** Ese Admin UI no oculta grupos ni políticas por propietario; el
  aislamiento lo hace la capa de Backstage. Un administrador que lo mire directamente ve todo.
- **Gestionar las políticas desde una plantilla al editar un grupo.** Adjuntar y quitar políticas es una función de la página, no un formulario.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Forbidden* al borrar un objeto | Es de otro usuario | Pide al propietario o a un administrador |
| No ves una política al editar un grupo | No la has creado tú | Crea la tuya con *Create SeaweedFS Policy* |
