import io

from app import create_app
from classroom_store import InMemoryClassroomRepository


def make_client(tmp_path):
    app = create_app(InMemoryClassroomRepository())
    app.config.update(TESTING=True, UPLOAD_FOLDER=str(tmp_path))
    return app.test_client()


def test_register_student_and_show_in_directory(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/alumnos", data={"name": "Andrea López", "email": "andrea@example.edu", "group": "2° B"}, follow_redirects=True)
    assert response.status_code == 200
    assert "Andrea López" in response.get_data(as_text=True)


def test_assignment_upload_is_available_for_download(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/trabajos", data={"student_id": "1", "title": "Práctica de ciencias", "file": (io.BytesIO(b"contenido"), "practica.pdf")}, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert "Práctica de ciencias" in response.get_data(as_text=True)
    assert b"contenido" in client.get("/archivos/" + next(tmp_path.iterdir()).name).data


def test_reject_unsupported_assignment_type(tmp_path):
    client = make_client(tmp_path)
    response = client.post("/trabajos", data={"student_id": "1", "title": "Archivo", "file": (io.BytesIO(b"contenido"), "script.exe")}, content_type="multipart/form-data", follow_redirects=True)
    assert "Tipo de archivo no admitido" in response.get_data(as_text=True)


def test_publish_activity_and_take_attendance(tmp_path):
    client = make_client(tmp_path)
    activity = client.post("/comunidad", data={"kind": "activity", "title": "Lectura", "body": "Capítulo dos", "due_date": "2026-10-12"}, follow_redirects=True)
    attendance = client.post("/asistencia", data={"date": "2026-10-03", "student_1": "present", "student_2": "absent"}, follow_redirects=True)
    assert "Lectura" in activity.get_data(as_text=True)
    assert "Asistencia guardada" in attendance.get_data(as_text=True)