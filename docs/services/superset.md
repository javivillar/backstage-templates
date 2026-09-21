# Superset — conexiones, datasets, gráficos y dashboards

Superset es la herramienta de análisis y visualización. Desde Backstage inicializas **lo tuyo** y lo terminas de construir en Superset.

## Qué te da

- **Página `/superset-manager`**: tus conexiones, datasets, gráficos y dashboards (los administradores ven todo, con columna *Owner*).
- **Seis plantillas**:

| Recurso | En Backstage | Por qué |
|---|---|---|
| Conexión a base de datos | Crear y actualizar (con las opciones reales de Superset) | En Superset también es un formulario |
| Dataset | Crear y actualizar | Igual: elegir conexión y tabla, o SQL para uno virtual |
| Gráfico | **Aprovisionar** un gráfico vacío a tu nombre + enlace al editor de Superset | Construir un gráfico es un editor visual, no un formulario |
| Dashboard | **Aprovisionar** un dashboard vacío a tu nombre + enlace al editor de Superset | Igual |

## Quién puede hacer qué

- **Crear**: cualquier usuario que haya entrado en Backstage; pasas a ser el propietario.
- **Actualizar**: solo el propietario o `backstage-admin`.
- **Dentro de Superset**, tus permisos los dan los grupos `superset-admin`, `superset-editor` y `superset-viewer`; el *viewer* no puede crear nada.
- **Datasets sobre una conexión**: solo el propietario de esa conexión puede construirlos.
- «Admin de Superset» y «admin de Backstage» son **dos cosas distintas**: ser una no te hace la otra.

## Cómo se usa

1. *Create* → *Create Superset Connection* (y después *Create Superset Dataset* sobre ella).
2. Para un gráfico o dashboard, usa *Provision*: te devuelve el enlace al editor de Superset para terminarlo allí.
3. Revisa lo tuyo en `/superset-manager`.

## Qué garantías tienes

- **No ves ni tocas lo de otros.** La propiedad se comprueba en el servidor de Backstage y las listas se filtran por propietario.
- En Superset, un dashboard **sin publicar** solo lo ven sus propietarios (y un administrador); dos usuarios con el mismo rol no se ven los
  dashboards del otro salvo que uno lo publique.

## Qué no debes esperar

- **Un gráfico o dashboard terminado desde Backstage.** Solo se crea el objeto vacío y correcto; el diseño se hace en Superset.
- **Seguridad por filas.** Este modelo protege *objetos* (dashboards, gráficos…), no qué filas de datos se ven dentro de un mismo gráfico
  (*Row Level Security* es otra capa de Superset que no está configurada aquí).
- **Borrar desde Backstage.** No hay plantillas de borrado para estos recursos.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Forbidden … may not modify this Superset object* | El recurso es de otro usuario | Pide al propietario o a un administrador |
| No puedes crear un dataset sobre una conexión | La conexión es de otro usuario | Crea la tuya o pide que se la cree quien la posee |
