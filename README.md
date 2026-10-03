# Aula Abierta

Portal web sencillo para administrar un curso: altas de alumnos, recepción local de trabajos, avisos, actividades y asistencia.

Para entender el propósito de cada archivo y el recorrido de los datos, consulta la [Guía del código](GUIA_DEL_CODIGO.md).

## Requisitos

- Python 3.13.5 (también funciona con Python 3.11 o posterior)

## Ejecutar en Windows

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000 en el navegador.

## Probar

```powershell
python -m pip install pytest
python -m pytest
```

## Persistencia

Los registros se guardan solo en memoria y se reinician al cerrar la aplicación. La capa `InMemoryClassroomRepository` en `classroom_store.py` concentra el acceso a alumnos, trabajos, avisos, actividades y asistencia. Para incorporar una base de datos, implementa la misma interfaz con el motor elegido y pásala a `create_app(repository=...)`; las rutas no necesitan conocer los detalles de persistencia. Los archivos cargados se guardan localmente en `instance/uploads`.

La carga admite PDF, documentos y hojas de cálculo de Office, imágenes JPG/PNG y ZIP, con un límite de 10 MB. Configura `SECRET_KEY` como variable de entorno antes de desplegarla en un servidor.