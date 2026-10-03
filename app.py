from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from classroom_store import InMemoryClassroomRepository


ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "png", "jpg", "jpeg", "zip"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def create_app(repository: InMemoryClassroomRepository | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "desarrollo-cambiar-antes-de-publicar"),
        MAX_CONTENT_LENGTH=MAX_UPLOAD_BYTES,
        UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"),
    )
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    app.extensions["classroom_repository"] = repository or InMemoryClassroomRepository()

    def repo() -> InMemoryClassroomRepository:
        return app.extensions["classroom_repository"]

    @app.context_processor
    def shared_template_data():
        return {"today": date.today(), "nav_counts": {"students": len(repo().students)}}

    @app.get("/")
    def dashboard():
        data = repo()
        return render_template(
            "dashboard.html",
            students=data.list_students(),
            assignments=data.list_assignments()[:4],
            announcements=data.list_announcements()[:3],
            activities=data.list_activities()[:3],
            attendance=data.attendance_summary(),
        )

    @app.route("/alumnos", methods=["GET", "POST"])
    def students():
        data = repo()
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            group = request.form.get("group", "").strip()
            if not name or not email or not group:
                flash("Completa nombre, correo y grupo para dar de alta al alumno.", "error")
            elif any(student["email"].casefold() == email.casefold() for student in data.list_students()):
                flash("Ya existe un alumno registrado con ese correo.", "error")
            else:
                data.add_student(name=name, email=email, group=group)
                flash(f"{name} ya forma parte del curso.", "success")
                return redirect(url_for("students"))
        return render_template("students.html", students=data.list_students())

    @app.route("/trabajos", methods=["GET", "POST"])
    def assignments():
        data = repo()
        if request.method == "POST":
            student_id = request.form.get("student_id", type=int)
            title = request.form.get("title", "").strip()
            upload = request.files.get("file")
            student = data.get_student(student_id) if student_id else None
            if not student or not title or not upload or not upload.filename:
                flash("Selecciona al alumno y agrega el nombre y el archivo del trabajo.", "error")
            else:
                original_name = secure_filename(upload.filename)
                extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
                if extension not in ALLOWED_EXTENSIONS:
                    flash("Tipo de archivo no admitido. Usa PDF, Office, imagen o ZIP.", "error")
                else:
                    stored_name = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{original_name}"
                    upload.save(Path(app.config["UPLOAD_FOLDER"]) / stored_name)
                    data.add_assignment(student_id, title, original_name, stored_name)
                    flash("Trabajo entregado correctamente.", "success")
                    return redirect(url_for("assignments"))
        return render_template("assignments.html", students=data.list_students(), assignments=data.list_assignments())

    @app.get("/archivos/<path:filename>")
    def uploaded_file(filename: str):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)

    @app.route("/comunidad", methods=["GET", "POST"])
    def community():
        data = repo()
        if request.method == "POST":
            kind = request.form.get("kind", "announcement")
            title = request.form.get("title", "").strip()
            body = request.form.get("body", "").strip()
            due_date = request.form.get("due_date", "").strip()
            if not title or not body:
                flash("Escribe un título y el detalle antes de publicar.", "error")
            elif kind == "activity" and not due_date:
                flash("Indica la fecha de la actividad.", "error")
            else:
                if kind == "activity":
                    data.add_activity(title, body, due_date)
                    flash("Actividad publicada.", "success")
                else:
                    data.add_announcement(title, body)
                    flash("Aviso publicado.", "success")
                return redirect(url_for("community"))
        return render_template("community.html", announcements=data.list_announcements(), activities=data.list_activities())

    @app.route("/asistencia", methods=["GET", "POST"])
    def attendance():
        data = repo()
        selected_date = request.values.get("date", date.today().isoformat())
        if request.method == "POST":
            marks = {int(key.removeprefix("student_")): value for key, value in request.form.items() if key.startswith("student_")}
            if not marks:
                flash("No hay alumnos para registrar. Da de alta al grupo primero.", "error")
            else:
                data.save_attendance(selected_date, marks)
                flash("Asistencia guardada.", "success")
                return redirect(url_for("attendance", date=selected_date))
        return render_template(
            "attendance.html",
            students=data.list_students(),
            selected_date=selected_date,
            attendance=data.get_attendance(selected_date),
            summary=data.attendance_summary(),
        )

    @app.errorhandler(413)
    def too_large(_error):
        flash("El archivo supera el límite de 10 MB.", "error")
        return redirect(url_for("assignments"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")