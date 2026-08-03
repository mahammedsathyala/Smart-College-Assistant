"""
Smart College Assistant — Database Models (SQLAlchemy)
Defines all normalized database tables with relationships.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    DateTime, Date, ForeignKey, Enum, create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


# ── 1. Roles ─────────────────────────────────────────────────
class Role(Base):
    """User role for RBAC."""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)   # admin / student / faculty
    description = Column(String(200))
    users = relationship("User", back_populates="role")


# ── 2. Users ─────────────────────────────────────────────────
class User(Base):
    """Unified authentication table for all user types."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    student = relationship("Student", back_populates="user", uselist=False)
    faculty = relationship("Faculty", back_populates="user", uselist=False)
    chat_sessions = relationship("ChatHistory", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


# ── 3. Departments ───────────────────────────────────────────
class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)   # e.g., CS, ECE
    name = Column(String(100), nullable=False)
    hod_name = Column(String(100))
    total_seats = Column(Integer, default=60)
    description = Column(Text)

    students = relationship("Student", back_populates="department")
    faculty = relationship("Faculty", back_populates="department")
    courses = relationship("Course", back_populates="department")
    timetables = relationship("Timetable", back_populates="department")


# ── 4. Students ──────────────────────────────────────────────
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    roll_number = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(200))
    phone = Column(String(15))
    department_id = Column(Integer, ForeignKey("departments.id"))
    semester = Column(Integer, default=1)
    batch = Column(String(10))           # e.g., 2022-2026
    cgpa = Column(Float, default=0.0)
    attendance_percentage = Column(Float, default=0.0)
    placement_eligible = Column(Boolean, default=False)
    photo_url = Column(String(300))
    address = Column(Text)
    guardian_name = Column(String(100))
    guardian_phone = Column(String(15))
    joined_at = Column(Date)

    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    attendance = relationship("Attendance", back_populates="student")
    marks = relationship("Mark", back_populates="student")
    placement = relationship("PlacementRecord", back_populates="student", uselist=False)


# ── 5. Faculty ───────────────────────────────────────────────
class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(200))
    phone = Column(String(15))
    department_id = Column(Integer, ForeignKey("departments.id"))
    designation = Column(String(100))
    specialization = Column(String(200))
    experience_years = Column(Integer, default=0)
    photo_url = Column(String(300))

    user = relationship("User", back_populates="faculty")
    department = relationship("Department", back_populates="faculty")
    courses = relationship("Course", back_populates="faculty")
    timetables = relationship("Timetable", back_populates="faculty")


# ── 6. Courses ───────────────────────────────────────────────
class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    faculty_id = Column(Integer, ForeignKey("faculty.id"))
    semester = Column(Integer)
    credits = Column(Integer, default=3)
    lecture_hours = Column(Integer, default=3)
    lab_hours = Column(Integer, default=0)
    description = Column(Text)

    department = relationship("Department", back_populates="courses")
    faculty = relationship("Faculty", back_populates="courses")
    attendance = relationship("Attendance", back_populates="course")
    marks = relationship("Mark", back_populates="course")
    timetables = relationship("Timetable", back_populates="course")


# ── 7. Attendance ────────────────────────────────────────────
class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    date = Column(Date, nullable=False)
    status = Column(Enum("present", "absent", "late", name="att_status"), default="present")
    recorded_by = Column(Integer, ForeignKey("faculty.id"))

    student = relationship("Student", back_populates="attendance")
    course = relationship("Course", back_populates="attendance")


# ── 8. Marks ─────────────────────────────────────────────────
class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    exam_type = Column(String(50))   # internal / external / lab
    marks_obtained = Column(Float)
    max_marks = Column(Float)
    grade = Column(String(5))
    grade_point = Column(Float)
    semester = Column(Integer)
    exam_date = Column(Date)

    student = relationship("Student", back_populates="marks")
    course = relationship("Course", back_populates="marks")


# ── 9. Timetable ─────────────────────────────────────────────
class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    faculty_id = Column(Integer, ForeignKey("faculty.id"))
    semester = Column(Integer)
    day = Column(String(10))         # Monday … Saturday
    start_time = Column(String(10))  # 09:00
    end_time = Column(String(10))    # 10:00
    room = Column(String(20))
    type = Column(String(20), default="lecture")  # lecture / lab

    department = relationship("Department", back_populates="timetables")
    course = relationship("Course", back_populates="timetables")
    faculty = relationship("Faculty", back_populates="timetables")


# ── 10. Admissions ───────────────────────────────────────────
class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True)
    applicant_name = Column(String(100), nullable=False)
    email = Column(String(200))
    phone = Column(String(15))
    department_id = Column(Integer, ForeignKey("departments.id"))
    applied_date = Column(DateTime, default=datetime.utcnow)
    status = Column(
        Enum("pending", "approved", "rejected", "waitlisted", name="adm_status"),
        default="pending",
    )
    entrance_score = Column(Float)
    category = Column(String(20))    # General / OBC / SC / ST
    notes = Column(Text)


# ── 11. Placements ───────────────────────────────────────────
class PlacementRecord(Base):
    __tablename__ = "placements"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    company_name = Column(String(150))
    package_lpa = Column(Float)
    role = Column(String(100))
    placed_date = Column(Date)
    placement_type = Column(String(50))  # campus / off-campus / internship
    status = Column(String(30), default="not_placed")  # placed / not_placed / in_process

    student = relationship("Student", back_populates="placement")


class PlacementDrive(Base):
    """Upcoming placement drives."""
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(150), nullable=False)
    drive_date = Column(Date)
    role = Column(String(100))
    package_lpa = Column(Float)
    eligibility_cgpa = Column(Float, default=6.0)
    departments = Column(String(200))   # Comma-separated dept codes
    registration_deadline = Column(Date)
    description = Column(Text)
    status = Column(String(20), default="upcoming")


# ── 12. Notifications ────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    category = Column(String(50))    # exam / event / placement / general
    target_role = Column(String(20), default="all")  # all / student / faculty
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    priority = Column(String(10), default="normal")  # low / normal / high


# ── 13. Policies ─────────────────────────────────────────────
class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))    # attendance / exam / hostel / library
    content = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"))


# ── 14. FAQs ─────────────────────────────────────────────────
class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(50))
    helpful_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ── 15. Documents (RAG) ──────────────────────────────────────
class Document(Base):
    """Uploaded documents indexed in FAISS."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(300), nullable=False)
    file_path = Column(String(500))
    category = Column(String(50))
    description = Column(Text)
    chunk_count = Column(Integer, default=0)
    indexed = Column(Boolean, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# ── 16. Chat History ─────────────────────────────────────────
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(100))
    role = Column(String(10))        # user / assistant
    content = Column(Text)
    agent_used = Column(String(50))  # Which agent handled the query
    confidence = Column(Float)
    sources = Column(Text)           # JSON-encoded source citations
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")


# ── 17. Audit Logs ───────────────────────────────────────────
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100))
    resource = Column(String(100))
    details = Column(Text)
    ip_address = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")


def get_engine(db_url: str | None = None):
    from config.settings import ActiveConfig
    url = db_url or ActiveConfig.DATABASE_URL
    return create_engine(url, connect_args={"check_same_thread": False}, echo=False)


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db(engine=None) -> None:
    """Create all tables."""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
