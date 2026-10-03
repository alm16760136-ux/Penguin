# Guía del código de Aula Abierta

Esta guía explica cómo se organiza el proyecto, qué hace cada archivo y qué sucede cuando alguien usa una pantalla. No necesitas memorizar Flask: puedes seguir cada operación desde el formulario hasta el lugar donde se guardan temporalmente los datos.

## 1. El recorrido general

La aplicación funciona en este orden:

1. El navegador solicita una dirección, por ejemplo `/alumnos`.
2. Flask busca en `app.py` la función asociada con esa dirección.
3. Si es un envío de formulario (`POST`), la función lee y valida lo recibido.
4. La función llama al repositorio para consultar o cambiar los datos.
5. Flask entrega una plantilla HTML con los datos (`render_template`).
6. El navegador muestra el HTML y lo presenta con los estilos de `static/style.css`.

En resumen:

```text
Navegador -> ruta Flask (app.py) -> repositorio (classroom_store.py)
          <- plantilla HTML (templates/) <- datos
```

## 2. Archivos y carpetas

| Archivo o carpeta | Para qué sirve |
| --- | --- |
| `app.py` | Crea Flask, configura límites y archivos, define las rutas y conecta formularios con el repositorio. Es el punto de entrada al ejecutar `python app.py`. |
| `classroom_store.py` | Contiene el repositorio temporal. Conserva alumnos, entregas, avisos, actividades y asistencias mientras el servidor está encendido. |
| `templates/base.html` | Es la estructura compartida de las páginas: barra lateral, navegación, encabezado y mensajes de confirmación o error. |
| `templates/dashboard.html` | Pantalla de resumen, con contadores, alumnos, entregas recientes, avisos y actividad. |
| `templates/students.html` | Formulario de alta y directorio de alumnos. |
| `templates/assignments.html` | Formulario para adjuntar trabajos y listado con enlaces de descarga. |
| `templates/community.html` | Publicación y consulta de avisos y actividades. |
| `templates/attendance.html` | Selección de fecha y registro de asistencia por alumno. |
| `static/style.css` | Colores, tipografía, tamaños, diseño adaptable a pantallas pequeñas y estados visuales. No contiene las reglas de negocio. |
| `tests/test_app.py` | Pruebas automáticas de altas, carga de archivos, actividades y asistencia. |
| `requirements.txt` | Dependencias que pip instala; actualmente Flask. |
| `instance/uploads/` | Carpeta local donde Flask guarda los archivos de trabajos. No es una base de datos. |
| `README.md` | Requisitos, instalación y comandos básicos del proyecto. |

## 3. Cómo leer `app.py`

### Importaciones y ajustes

Al principio se importan Flask, funciones de fecha y herramientas de archivos. `ALLOWED_EXTENSIONS` enumera los tipos admitidos para entregas. `MAX_UPLOAD_BYTES` pone el límite de carga en 10 MB. `secure_filename` prepara el nombre recibido para usarlo como nombre de archivo seguro.

### `create_app(repository=None)`

Esta función construye la aplicación. Configura la clave de sesión, el límite de carga y la carpeta local de archivos. También registra el repositorio que usarán las rutas.

- En el uso normal se crea `InMemoryClassroomRepository`.
- En las pruebas se puede pasar un repositorio nuevo para que cada prueba tenga datos aislados.
- Más adelante se podrá pasar un repositorio conectado a base de datos sin reescribir las pantallas ni sus rutas.

La función pequeña `repo()` permite que las rutas obtengan siempre el repositorio configurado para esta aplicación. `shared_template_data()` comparte la fecha y el número de alumnos con todas las plantillas.

### Rutas disponibles

| Dirección y método | Función |
| --- | --- |
| `GET /` | Muestra el resumen del curso y sus datos recientes. |
| `GET /alumnos` | Muestra el formulario y el directorio. |
| `POST /alumnos` | Valida y registra a un alumno; evita correos repetidos. |
| `GET /trabajos` | Muestra el formulario de entrega y los trabajos recibidos. |
| `POST /trabajos` | Comprueba alumno, título y extensión; guarda el archivo y registra la entrega. |
| `GET /archivos/<nombre>` | Descarga como adjunto un archivo previamente cargado. |
| `GET /comunidad` | Muestra avisos y actividades existentes. |
| `POST /comunidad` | Publica un aviso o una actividad. Las actividades requieren fecha. |
| `GET /asistencia` | Muestra la lista para una fecha elegida. |
| `POST /asistencia` | Guarda el estado de asistencia de los alumnos para esa fecha. |

En las rutas que aceptan `GET` y `POST`, `GET` presenta la pantalla y `POST` procesa lo enviado por el formulario. Después de guardar, se usa `redirect(url_for(...))` para volver a cargar la página. Así, al actualizar el navegador no se vuelve a enviar accidentalmente el mismo formulario.

`flash()` prepara un mensaje temporal para confirmar una acción o indicar qué dato falta. `render_template()` elige la página HTML y le pasa los datos que necesita. `url_for()` genera direcciones a partir del nombre de una ruta, así que no hay que escribir manualmente cada enlace.

### Carga de archivos

La ruta de trabajos busca los datos de formulario y el archivo. Después:

1. Comprueba que el alumno exista y que haya título y archivo.
2. Limpia el nombre original y revisa la extensión contra `ALLOWED_EXTENSIONS`.
3. Genera un nombre de almacenamiento distinto para evitar sobrescribir otra entrega.
4. Guarda el archivo dentro de `instance/uploads/`.
5. Registra en el repositorio el alumno, título y nombres del archivo.

El manejador `too_large()` captura el error de Flask cuando se supera el límite de carga. La extensión del archivo se valida, pero en un despliegue real también conviene verificar el contenido del archivo y añadir autenticación y controles de acceso.

### Inicio del servidor

Al final, `app = create_app()` crea la aplicación que Flask sirve. El bloque `if __name__ == "__main__":` ejecuta el servidor de desarrollo cuando se ejecuta `python app.py`. `FLASK_DEBUG=1` activa el modo de depuración para desarrollo; no debe activarse en un servidor público.

## 4. Cómo leer `classroom_store.py`

`InMemoryClassroomRepository` agrupa las operaciones de datos. Las listas `students`, `assignments`, `announcements` y `activities` y el diccionario `attendance` viven en la memoria del proceso. Por eso los registros de texto vuelven a los datos de ejemplo al reiniciar la aplicación.

Los métodos se dividen por tarea:

- `list_students()` ordena y entrega alumnos; `get_student()` busca uno por identificador; `add_student()` agrega uno nuevo.
- `list_assignments()` y `add_assignment()` consultan o registran entregas. El archivo físico se guarda desde `app.py`; el repositorio conserva sus datos descriptivos.
- `list_announcements()` y `add_announcement()` consultan o crean avisos.
- `list_activities()` y `add_activity()` consultan o crean actividades con fecha de entrega.
- `get_attendance()` y `save_attendance()` leen o escriben las marcas por fecha.
- `attendance_summary()` calcula los presentes, retardos y ausentes de hoy.

La interfaz que usa `app.py` es el contrato de este repositorio. Para añadir una base de datos, se puede implementar otra clase con los mismos métodos y pasar una instancia a `create_app(repository=mi_repositorio)`. La interfaz deja preparadas las rutas para ese cambio, pero todavía no configura tablas ni guarda información en una base de datos.

## 5. Cómo se conectan las plantillas

Las plantillas usan Jinja, el motor de vistas de Flask. `base.html` define el esqueleto común. Las demás páginas comienzan con `{% extends "base.html" %}` y llenan secciones mediante `{% block ... %}`; así, el menú se mantiene igual en todas las pantallas.

En los archivos HTML:

- `{{ variable }}` inserta un valor enviado por la ruta.
- `{% for ... %}` repite un bloque para mostrar listas, como alumnos.
- `{% if ... %}` elige qué mostrar según haya datos o no.
- `url_for(...)` crea enlaces a las rutas de Flask y archivos estáticos.
- Los formularios con `method="post"` envían sus datos a la ruta actual.
- El formulario de trabajos usa `enctype="multipart/form-data"`, necesario para enviar archivos.

`style.css` aplica los estilos y los ajustes para móvil. La plantilla de comunidad incluye un pequeño JavaScript que muestra u oculta la fecha según se seleccione “Aviso” o “Actividad”; la validación definitiva sigue estando en el servidor Python.

## 6. Pruebas

`tests/test_app.py` crea una aplicación de prueba y usa el cliente de Flask para simular solicitudes web sin abrir un navegador. Comprueba que:

- se pueda registrar un alumno y verlo en el directorio;
- un trabajo admitido se guarde y descargue;
- una extensión no admitida se rechace;
- se publique una actividad y se registre asistencia.

Ejecuta todas las pruebas con:

```powershell
python -m pytest -q
```

## 7. Dónde hacer cambios comunes

- Cambiar colores, espacios o vista móvil: `static/style.css`.
- Cambiar títulos, etiquetas o estructura visual: plantilla correspondiente en `templates/`.
- Cambiar validaciones o comportamiento de formularios: ruta correspondiente en `app.py`.
- Cambiar la forma de leer y guardar datos: repositorio en `classroom_store.py` o su futura implementación con base de datos.
- Añadir una nueva sección: crea una ruta en `app.py`, una plantilla que extienda `base.html` y un enlace en la navegación de `templates/base.html`.
