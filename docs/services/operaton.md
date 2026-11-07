# Operaton — procesos de negocio (BPM)

Operaton ejecuta los procesos BPMN y las decisiones DMN. Es el sucesor de Camunda en Refresquito: el mismo motor (es
el fork de código abierto de Camunda 7), la misma REST API y las mismas aplicaciones (Cockpit, Tasklist y Admin).
Hoy **convive con Camunda**: las plantillas de procesos de Backstage y el bloque `processes` de las aplicaciones aún
usan Camunda ([Camunda](camunda.md)) hasta que se pasen a Operaton.

## Qué te da

- **Las aplicaciones web** en `operaton.<dominio>/operaton/app/` (el enlace está en la ficha del servicio
  `operaton-oneke` del catálogo, tarjeta *Service metadata*):

| Aplicación | Para qué |
|---|---|
| *Tasklist* | Ver y completar tus tareas, y arrancar procesos |
| *Cockpit* | Seguir las instancias en ejecución, sus incidentes y su historial (administradores) |
| *Admin* | Usuarios, grupos y permisos del motor (administradores; los usuarios y grupos vienen de Keycloak, solo lectura) |

- **La REST API** en `operaton.<dominio>/engine-rest`, con HTTP Basic y tu usuario de Keycloak. Es la de Camunda 7
  (mismas rutas): su definición está en *Catálogo > APIs > Operaton REST API*.
- **Dos dashboards en Grafana** (carpeta *Services/operaton/pro*): **Operaton** (instancias, tareas, incidentes, jobs, rendimiento) y
  **Operaton Logs**.

## Quién puede hacer qué

Entras con tu **usuario y contraseña de Keycloak** en el formulario de Operaton (no hay botón de SSO). Lo que puedes
hacer dentro depende de tus grupos de Keycloak:

| Grupo de Keycloak | Qué puedes hacer en Operaton |
|---|---|
| `operaton-admin` | Todo: Cockpit, Tasklist, Admin, desplegar, ver y gestionar cualquier instancia |
| `operaton-editor` | Tasklist: ver y arrancar cualquier proceso desplegado, y trabajar **tus** instancias y tareas |
| `operaton-viewer` | Entrar, sin ver nada todavía (reservado para solo lectura) |
| ninguno | Entrar, sin ver nada |

Pide el grupo a un administrador de Keycloak. Un cambio de grupo tiene efecto **en el momento**, sin volver a entrar.

## Cómo se usa

1. Entra en `operaton.<dominio>/operaton/app/` con tu usuario de Keycloak y elige *Tasklist*.
2. *Start process*: elige el proceso y arráncalo. La tarea que te toque aparece en tu lista.
3. Abre la tarea, rellénala y pulsa *Complete*.
4. Para usar la REST API desde un programa:
   `curl -u <usuario>:<contraseña> https://operaton.<dominio>/engine-rest/process-definition`.

Los procesos los despliegan las aplicaciones y los administradores. Para desplegar los tuyos desde Backstage, sigue
usando de momento las plantillas de [Camunda](camunda.md).

## Qué garantías tienes

- **Sin credenciales no se ve nada.** La REST API responde `401` a quien no se identifica, y una contraseña errónea
  también da `401`.
- **Cada instancia es de quien la arranca**, aunque otro comparta tu grupo `operaton-editor`. Esto se cumple en los
  procesos preparados para ello: un listener de inicio da permiso a quien arranca, y la tarea se asigna a esa persona
  (el ejemplo es el proceso `authz-test-process`).
- **Los permisos de los grupos no se pierden.** Están declarados en el servicio y se vuelven a crear si faltan,
  también en una instalación nueva.
- **Las aplicaciones web solo aceptan cambios desde su propia URL.** Una página de otro sitio no puede actuar en tu
  nombre (comprobación CSRF del origen).

## Qué no debes esperar

- **Que los datos de Camunda estén en Operaton.** Operaton empieza vacío: las aplicaciones vuelven a desplegar allí
  sus procesos cuando se pasen.
- **Que todo el aislamiento venga solo.** Si un proceso no tiene el listener de inicio ni asigna la tarea a quien
  arranca, cualquier miembro de `operaton-editor` con permiso sobre la instancia la ve.
- **Ver solo tus definiciones.** Las *definiciones* de proceso las ve todo `operaton-editor`. Lo que se aísla son las
  instancias y las tareas.
- **Entrar con SSO** (sin escribir la contraseña). El formulario es el de Operaton; la contraseña la comprueba
  Keycloak.

## Si vienes de Camunda

- Los **BPMN y DMN no cambian**: las extensiones `camunda:` (`camunda:assignee`, `camunda:candidateGroups`,
  `camunda:historyTimeToLive`...) siguen funcionando.
- Los **scripts y el código Java** que nombran clases del motor sí cambian: `org.camunda.bpm...` pasa a ser
  `org.operaton.bpm...`. Si no lo cambias, el proceso falla al llegar a ese paso con *Access to host class
  org.camunda... is not allowed or does not exist*.
- La **REST API** es la misma: un cliente de la de Camunda funciona cambiando solo la URL.
- Los **grupos** son otros: `operaton-*` en lugar de `camunda-*`.

## Si algo falla

| Síntoma | Causa habitual | Qué hacer |
|---|---|---|
| *Login failed* / `401` | Usuario o contraseña de Keycloak erróneos | Prueba a entrar en Keycloak con los mismos datos |
| Entras pero no ves ninguna aplicación ni proceso | No estás en `operaton-editor` ni en `operaton-admin` | Pide el grupo a un administrador |
| Arrancas un proceso pero no ves la instancia de otro compañero | Es lo esperado: cada instancia es de quien la arranca | — |
| `403` al guardar algo en las aplicaciones web | Has entrado por otra URL (otro host, o http en lugar de https) | Usa la URL de la ficha del catálogo |
| Un proceso que funcionaba en Camunda falla con *Access to host class org.camunda...* | Un script o delegado usa clases de Camunda | Cámbialas a `org.operaton.bpm...` |
