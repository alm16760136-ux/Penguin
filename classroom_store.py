from __future__ import annotations

from datetime import date
from typing import Any


class InMemoryClassroomRepository:
    """Repositorio temporal; puede sustituirse por uno SQL conservando esta interfaz."""

    def __init__(self) -> None:
        self.students: list[dict[str, Any]] = [
            {"id": 1, "name": "Lucía Mendoza", "email": "lucia.mendoza@escuela.edu", "group": "3° A"},
            {"id": 2, "name": "Mateo Salas", "email": "mateo.salas@escuela.edu", "group": "3° A"},
            {"id": 3, "name": "Valentina Cruz", "email": "valentina.cruz@escuela.edu", "group": "3° B"},
            {"id": 4, "name": "Diego Navarro", "email": "diego.navarro@escuela.edu", "group": "3° A"},
        ]
        self.assignments: list[dict[str, Any]] = []
        self.announcements: list[dict[str, Any]] = [
            {"id": 1, "title": "Bienvenidos al espacio del curso", "body": "Aquí encontrarás avisos, fechas importantes y materiales de clase.", "created_at": date.today().isoformat()},
        ]
        self.activities: list[dict[str, Any]] = [
            {"id": 1, "title": "Lectura: ecosistemas locales", "body": "Lee el capítulo 4 y anota tres observaciones para la discusión.", "due_date": date.today().isoformat()},
        ]
        self.attendance: dict[str, dict[int, str]] = {}
        self._next_student_id = 5
        self._next_assignment_id = 1
        self._next_announcement_id = 2
        self._next_activity_id = 2

    def list_students(self) -> list[dict[str, Any]]:
        return sorted(self.students, key=lambda student: (student["group"], student["name"]))

    def get_student(self, student_id: int) -> dict[str, Any] | None:
        return next((student for student in self.students if student["id"] == student_id), None)

    def add_student(self, name: str, email: str, group: str) -> dict[str, Any]:
        student = {"id": self._next_student_id, "name": name, "email": email, "group": group}
        self._next_student_id += 1
        self.students.append(student)
        return student

    def add_assignment(self, student_id: int, title: str, filename: str, stored_name: str) -> dict[str, Any]:
        student = self.get_student(student_id)
        assignment = {
            "id": self._next_assignment_id,
            "student_id": student_id,
            "student_name": student["name"] if student else "Alumno eliminado",
            "group": student["group"] if student else "",
            "title": title,
            "filename": filename,
            "stored_name": stored_name,
            "submitted_at": date.today().isoformat(),
        }
        self._next_assignment_id += 1
        self.assignments.insert(0, assignment)
        return assignment

    def list_assignments(self) -> list[dict[str, Any]]:
        return list(self.assignments)

    def add_announcement(self, title: str, body: str) -> dict[str, Any]:
        notice = {"id": self._next_announcement_id, "title": title, "body": body, "created_at": date.today().isoformat()}
        self._next_announcement_id += 1
        self.announcements.insert(0, notice)
        return notice

    def list_announcements(self) -> list[dict[str, Any]]:
        return list(self.announcements)

    def add_activity(self, title: str, body: str, due_date: str) -> dict[str, Any]:
        activity = {"id": self._next_activity_id, "title": title, "body": body, "due_date": due_date}
        self._next_activity_id += 1
        self.activities.insert(0, activity)
        return activity

    def list_activities(self) -> list[dict[str, Any]]:
        return list(self.activities)

    def save_attendance(self, attendance_date: str, marks: dict[int, str]) -> None:
        self.attendance[attendance_date] = marks

    def get_attendance(self, attendance_date: str) -> dict[int, str]:
        return self.attendance.get(attendance_date, {})

    def attendance_summary(self) -> dict[str, int]:
        today_marks = self.get_attendance(date.today().isoformat())
        return {
            "students": len(self.students),
            "present": sum(mark == "present" for mark in today_marks.values()),
            "late": sum(mark == "late" for mark in today_marks.values()),
            "absent": sum(mark == "absent" for mark in today_marks.values()),
        }