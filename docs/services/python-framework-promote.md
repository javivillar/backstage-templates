# Promocionar una aplicación (Python Framework)

Un cluster sirve las tres etapas de una aplicación del Python Framework, cada una en su propio namespace:

| Etapa | Namespace | URL | Keycloak |
|---|---|---|---|
| `dev` | `<zona>-<programa>-<nombre>-dev-oneke` | `https://<nombre>-dev.<dominio>` | cliente `<nombre>-dev`, roles `<nombre>-<rol>` **de ese cliente** |
| `pre` | `<zona>-<programa>-<nombre>-pre-oneke` | `https://<nombre>-pre.<dominio>` | cliente `<nombre>-pre`, roles de ese cliente |
| `pro` | `<zona>-<programa>-<nombre>-oneke` | `https://<nombre>.<dominio>` | cliente `<nombre>`, roles del realm |

Los roles se llaman igual en todas las etapas, así que el código de la aplicación no cambia; un rol dado en dev no
vale en pro. En dev y pre, de momento, solo está el bloque `sso`.

Qué versión corre en cada etapa lo dice el fichero de la aplicación en refresquito-services
(`bootstrap/app-of-apps/apps/<nombre>.yaml`):

```yaml
stages:
  dev: { tag: "9f3c2a1..." }
  pro: { tag: "c714056..." }
```

## La plantilla

**Promote an application (Python Framework)**, en *Create*:

| Campo | Qué es |
|---|---|
| Application | el nombre de la aplicación (`orders`) |
| From | la versión de `dev`, la de `pre`, o **un commit** de su repositorio (para llevar una versión nueva, normalmente a dev; su CI tiene que haber publicado las imágenes) |
| To | la etapa que la recibe: `dev`, `pre` o `pro` |

Abre un pull request a refresquito-services que cambia **solo** la línea `stages.<etapa>.tag` (el fichero conserva sus
comentarios). Al hacer merge, Argo CD despliega esa versión en esa etapa en unos minutos, sin pasada del bootstrap.

- Una aplicación que solo tenía pro (`image.tag`) pasa a `stages` la primera vez que se promociona a dev o pre,
  conservando la versión de pro.
- Si la etapa de origen no tiene versión, no se abre ningún pull request y la plantilla lo dice.
- El CI del pull request renderiza el stack completo: si algo no cuadra, falla antes del merge.

El recorrido habitual: un commit → **dev**; lo pruebas en `https://<nombre>-dev.<dominio>` con los usuarios
`<nombre>-dev-admin` y `<nombre>-dev-viewer`; dev → **pre**; pre → **pro**.
