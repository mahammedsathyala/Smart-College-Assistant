"""
Smart College Assistant — Student Service
Data access layer for student-related operations.
"""

from __future__ import annotations
from datetime import date

from database.models import (
    Student, Attendance, Mark, Course, Timetable,
    Notification, PlacementRecord, PlacementDrive,
    get_session,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class StudentService:
    """Service for student data operations."""

    @staticmethod
    def get_student_by_user(user_id: int) -> dict | None:
        """Get student profile by user ID."""
        session = get_session()
        try:
            s = session.query(Student).filter_by(user_id=user_id).first()
            if not s:
                return None
            dept = s.department
            return {
                "id": s.id,
                "roll_number": s.roll_number,
                "name": s.name,
                "email": s.email,
                "phone": s.phone,
                "department": dept.name if dept else "N/A",
                "department_code": dept.code if dept else "N/A",
                "semester": s.semester,
                "batch": s.batch,
                "cgpa": s.cgpa,
                "attendance_percentage": s.attendance_percentage,
                "placement_eligible": s.placement_eligible,
                "photo_url": s.photo_url or "/static/images/default_avatar.png",
            }
        finally:
            session.close()

    @staticmethod
    def get_attendance_summary(student_id: int) -> dict:
        """Get subject-wise attendance summary."""
        session = get_session()
        try:
            records = (
                session.query(Attendance)
                .filter_by(student_id=student_id)
                .all()
            )
            summary: dict[int, dict] = {}
            for r in records:
                cid = r.course_id
                if cid not in summary:
                    summary[cid] = {"present": 0, "absent": 0, "total": 0, "course_id": cid}
                summary[cid]["total"] += 1
                if r.status == "present":
                    summary[cid]["present"] += 1
                else:
                    summary[cid]["absent"] += 1

            result = []
            for cid, data in summary.items():
                course = session.query(Course).filter_by(id=cid).first()
                pct = round(data["present"] / data["total"] * 100, 1) if data["total"] else 0
                result.append({
                    "course": course.name if course else "Unknown",
                    "course_code": course.code if course else "N/A",
                    "present": data["present"],
                    "absent": data["absent"],
                    "total": data["total"],
                    "percentage": pct,
                    "status": "Safe" if pct >= 75 else ("Warning" if pct >= 65 else "Detained"),
                })
            return {"subjects": result}
        finally:
            session.close()

    @staticmethod
    def get_marks_summary(student_id: int) -> dict:
        """Get subject-wise marks for the student."""
        session = get_session()
        try:
            marks = (
                session.query(Mark)
                .filter_by(student_id=student_id)
                .all()
            )
            result = []
            for m in marks:
                course = session.query(Course).filter_by(id=m.course_id).first()
                result.append({
                    "course": course.name if course else "Unknown",
                    "course_code": course.code if course else "N/A",
                    "exam_type": m.exam_type,
                    "marks_obtained": m.marks_obtained,
                    "max_marks": m.max_marks,
                    "percentage": round(m.marks_obtained / m.max_marks * 100, 1) if m.max_marks else 0,
                    "grade": m.grade,
                    "grade_point": m.grade_point,
                    "credits": course.credits if course else 0,
                })
            return {"marks": result}
        finally:
            session.close()

    @staticmethod
    def get_timetable(student_id: int) -> dict:
        """Get timetable for the student's department and semester."""
        session = get_session()
        try:
            student = session.query(Student).filter_by(id=student_id).first()
            if not student:
                return {"timetable": []}

            slots = (
                session.query(Timetable)
                .filter_by(
                    department_id=student.department_id,
                    semester=student.semester,
                )
                .order_by(Timetable.day, Timetable.start_time)
                .all()
            )

            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            by_day: dict[str, list] = {d: [] for d in days_order}

            for slot in slots:
                course = slot.course
                faculty = slot.faculty
                by_day[slot.day].append({
                    "time": f"{slot.start_time} - {slot.end_time}",
                    "course": course.name if course else "N/A",
                    "course_code": course.code if course else "N/A",
                    "faculty": faculty.name if faculty else "N/A",
                    "room": slot.room,
                    "type": slot.type,
                })

            return {"timetable": {day: slots for day, slots in by_day.items() if slots}}
        finally:
            session.close()

    @staticmethod
    def get_dashboard_stats(student_id: int) -> dict:
        """Get aggregated dashboard statistics for a student."""
        attendance_data = StudentService.get_attendance_summary(student_id)
        marks_data = StudentService.get_marks_summary(student_id)

        # Overall attendance
        subjects = attendance_data.get("subjects", [])
        if subjects:
            overall_att = round(sum(s["percentage"] for s in subjects) / len(subjects), 1)
        else:
            overall_att = 0.0

        # At-risk subjects
        at_risk = [s for s in subjects if s["percentage"] < 75]

        return {
            "overall_attendance": overall_att,
            "at_risk_subjects": len(at_risk),
            "total_subjects": len(subjects),
            "subjects_data": subjects,
            "marks_data": marks_data.get("marks", []),
        }
