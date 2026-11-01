# Harbor: imágenes curadas

Harbor es el registro de contenedores de la zona. Los proyectos **curados** (`common`, `framework-python`,
`framework-spring`) tienen las imágenes que un sistema de la PaaS puede usar: endurecidas (Docker Hardened Images
siempre que existen), firmadas, con SBOM y VEX, escaneadas a diario. Las ves en la página **Images** de Backstage.

## Qué te da

- **Ver** qué imágenes hay, para qué sirve cada una, su versión, su fin de vida, sus vulnerabilidades y su firma:
  página *Images* y la pestaña *Image* de cada una.
- **Pedir** una imagen nueva, o un tag nuevo de una que ya está: plantilla **Request a curated image**.
- **Avisos**: si un sistema tuyo usa una imagen que llega a su fin de vida, queda obsoleta o tiene un CVE crítico
  nuevo, `support` abre una incidencia a ese sistema (alertas `Workload…` de la plataforma).

## Quién puede hacer qué

| Quién | Qué |
|---|---|
| Cualquier persona con acceso a Backstage | Ver las imágenes; pedir una con la plantilla |
| El equipo de plataforma | Revisar y aprobar (fusionar) la petición; retirar imágenes |
| Nadie | Subir una imagen a mano a un proyecto curado: todo entra por el catálogo y la cuarentena |

## Cómo se pide una imagen

1. Mira antes la página *Images*: puede que ya esté, o que haya otra para lo mismo (p. ej. Valkey en lugar de Redis).
2. *Create* → **Request a curated image**. Rellena:
   - **Source**: registro y repositorio, sin tag. Primero Docker Hardened Images (`dhi.io/<nombre>`); una imagen
     de la comunidad solo con un escaneo limpio.
   - **Tags**: uno o varios, fijos (nunca `latest`). Comprueba que existen.
   - **Project**: `common` (piezas para los sistemas y la plataforma) o el del framework que la usa.
   - **Category**, **Who may use it** (`apps`: cualquier sistema; `platform`: solo los servicios de la plataforma,
     p. ej. por su licencia), **Summary** (una línea: se ve en *Images*) y **Why it is needed** (quién la
     necesita y el escaneo que hiciste).
3. La plantilla abre un **pull request en `opennebula`** con un fichero `harbor/catalog.d/<proyecto>-<nombre>-<tags>.toml`.
   Su CI comprueba que el catálogo sigue siendo válido.
4. El equipo de plataforma lo revisa (imagen endurecida o escaneo limpio, tags que existen, licencia permitida) y
   lo fusiona.
5. El siguiente *sync* de Harbor (cada día a las 04:00) la copia a la **cuarentena**, la escanea y la promociona
   al proyecto, firmada, **solo si pasa el filtro** (ningún CVE crítico sin una declaración VEX que lo descarte).
   Entonces aparece en *Images*. Si se queda retenida, el *sync* dice por qué.

## Qué garantías tienes

- Lo que está en un proyecto curado pasó el filtro de la cuarentena y lleva la **firma de Refresquito**.
- Cada imagen se vuelve a escanear a diario; su fin de vida y sus CVE críticos generan avisos al equipo de
  plataforma y a los sistemas que la usan.
- En una zona sin internet llega lo mismo, por bundles firmados.

## Qué no debes esperar

- Que la imagen esté al momento: depende de la revisión y del *sync* diario.
- Que entre una imagen con CVE críticos abiertos: se queda en la cuarentena hasta que su origen la corrija.
- `latest`, ni tags que cambian sin control: los tags son fijos (Docker Hardened Images reconstruye el mismo tag
  cuando lo parchea, y esa reconstrucción también pasa por la cuarentena).

Detalle técnico: `opennebula/harbor/README.md` (*Request an image*, *Quarantine*, *Retention and end of life*).
