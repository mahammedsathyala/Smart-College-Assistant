"""
Smart College Assistant — Database Seed Data
Populates all tables with realistic demo data for evaluation.
"""

from datetime import date, datetime, timedelta
import random

from database.models import (
    Base, Role, User, Department, Student, Faculty, Course,
    Attendance, Mark, Timetable, Admission, PlacementRecord,
    PlacementDrive, Notification, Policy, FAQ, Document, AuditLog,
    init_db, get_engine, get_session,
)
from utils.helpers import hash_password
from utils.logger import setup_logger

logger = setup_logger(__name__)


def seed_roles(session) -> dict:
    roles = {}
    for name, desc in [
        ("admin", "Full system access"),
        ("student", "Student access"),
        ("faculty", "Faculty access"),
    ]:
        r = session.query(Role).filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=desc)
            session.add(r)
            session.flush()
        roles[name] = r
    return roles


def seed_users(session, roles: dict) -> dict:
    users = {}
    # Admin
    admin_data = [
        ("admin", "admin@college.edu", "Admin@123"),
    ]
    for username, email, pwd in admin_data:
        u = session.query(User).filter_by(username=username).first()
        if not u:
            u = User(
                username=username, email=email,
                password_hash=hash_password(pwd),
                role_id=roles["admin"].id,
            )
            session.add(u)
            session.flush()
        users[username] = u

    # Students
    student_data = [
        ("cs001", "arjun.kumar@student.edu", "Student@123"),
        ("cs002", "priya.sharma@student.edu", "Student@123"),
        ("ece001", "rohit.verma@student.edu", "Student@123"),
        ("mech001", "ananya.singh@student.edu", "Student@123"),
        ("it001", "kiran.patel@student.edu", "Student@123"),
    ]
    for username, email, pwd in student_data:
        u = session.query(User).filter_by(username=username).first()
        if not u:
            u = User(
                username=username, email=email,
                password_hash=hash_password(pwd),
                role_id=roles["student"].id,
            )
            session.add(u)
            session.flush()
        users[username] = u

    # Faculty
    faculty_data = [
        ("fac001", "dr.ramesh@college.edu", "Faculty@123"),
        ("fac002", "prof.sunita@college.edu", "Faculty@123"),
        ("fac003", "dr.krishna@college.edu", "Faculty@123"),
    ]
    for username, email, pwd in faculty_data:
        u = session.query(User).filter_by(username=username).first()
        if not u:
            u = User(
                username=username, email=email,
                password_hash=hash_password(pwd),
                role_id=roles["faculty"].id,
            )
            session.add(u)
            session.flush()
        users[username] = u

    return users


def seed_departments(session) -> list:
    depts = [
        ("CS", "Computer Science & Engineering", "Dr. Ramesh Kumar", 60),
        ("ECE", "Electronics & Communication Engineering", "Dr. Sunita Patel", 60),
        ("MECH", "Mechanical Engineering", "Dr. Ajay Singh", 60),
        ("IT", "Information Technology", "Dr. Krishna Rao", 60),
        ("CIVIL", "Civil Engineering", "Dr. Meena Gupta", 60),
    ]
    dept_objs = []
    for code, name, hod, seats in depts:
        d = session.query(Department).filter_by(code=code).first()
        if not d:
            d = Department(code=code, name=name, hod_name=hod, total_seats=seats,
                           description=f"The {name} department offers cutting-edge education.")
            session.add(d)
            session.flush()
        dept_objs.append(d)
    return dept_objs


def seed_faculty(session, users: dict, depts: list) -> list:
    faculty_list = [
        ("fac001", "EMP001", "Dr. Ramesh Kumar", "dr.ramesh@college.edu", "9876543210",
         0, "Professor", "Machine Learning", 15),
        ("fac002", "EMP002", "Prof. Sunita Patel", "prof.sunita@college.edu", "9876543211",
         1, "Associate Professor", "Signal Processing", 10),
        ("fac003", "EMP003", "Dr. Krishna Rao", "dr.krishna@college.edu", "9876543212",
         3, "Assistant Professor", "Database Systems", 8),
    ]
    fac_objs = []
    for username, emp_id, name, email, phone, dept_idx, desig, spec, exp in faculty_list:
        f = session.query(Faculty).filter_by(employee_id=emp_id).first()
        if not f:
            f = Faculty(
                user_id=users[username].id, employee_id=emp_id,
                name=name, email=email, phone=phone,
                department_id=depts[dept_idx].id,
                designation=desig, specialization=spec, experience_years=exp,
            )
            session.add(f)
            session.flush()
        fac_objs.append(f)
    return fac_objs


def seed_students(session, users: dict, depts: list) -> list:
    student_data = [
        ("cs001", "CS2022001", "Arjun Kumar", "arjun.kumar@student.edu",
         "9123456780", 0, 5, "2022-2026", 8.45, 87.5),
        ("cs002", "CS2022002", "Priya Sharma", "priya.sharma@student.edu",
         "9123456781", 0, 5, "2022-2026", 9.10, 92.0),
        ("ece001", "ECE2022001", "Rohit Verma", "rohit.verma@student.edu",
         "9123456782", 1, 5, "2022-2026", 7.80, 78.0),
        ("mech001", "MECH2022001", "Ananya Singh", "ananya.singh@student.edu",
         "9123456783", 2, 5, "2022-2026", 8.20, 85.0),
        ("it001", "IT2022001", "Kiran Patel", "kiran.patel@student.edu",
         "9123456784", 3, 5, "2022-2026", 7.60, 80.5),
    ]
    stud_objs = []
    for username, roll, name, email, phone, dept_idx, sem, batch, cgpa, att in student_data:
        s = session.query(Student).filter_by(roll_number=roll).first()
        if not s:
            s = Student(
                user_id=users[username].id, roll_number=roll,
                name=name, email=email, phone=phone,
                department_id=depts[dept_idx].id,
                semester=sem, batch=batch, cgpa=cgpa,
                attendance_percentage=att,
                placement_eligible=(cgpa >= 7.5),
                joined_at=date(2022, 8, 1),
            )
            session.add(s)
            session.flush()
        stud_objs.append(s)
    return stud_objs


def seed_courses(session, depts: list, faculty_list: list) -> list:
    courses_data = [
        ("CS501", "Artificial Intelligence", 0, 0, 5, 4, 3, 0),
        ("CS502", "Machine Learning", 0, 0, 5, 4, 3, 0),
        ("CS503", "Database Management Systems", 0, 2, 5, 4, 3, 2),
        ("CS504", "Computer Networks", 0, 0, 5, 3, 3, 0),
        ("CS505", "Software Engineering", 0, 0, 5, 3, 3, 0),
        ("ECE501", "Digital Signal Processing", 1, 1, 5, 4, 3, 2),
        ("ECE502", "VLSI Design", 1, 1, 5, 4, 3, 2),
    ]
    course_objs = []
    for code, name, dept_idx, fac_idx, sem, credits, lh, lbh in courses_data:
        c = session.query(Course).filter_by(code=code).first()
        if not c:
            c = Course(
                code=code, name=name,
                department_id=depts[dept_idx].id,
                faculty_id=faculty_list[fac_idx].id,
                semester=sem, credits=credits,
                lecture_hours=lh, lab_hours=lbh,
                description=f"Core subject: {name}",
            )
            session.add(c)
            session.flush()
        course_objs.append(c)
    return course_objs


def seed_attendance(session, students: list, courses: list) -> None:
    today = date.today()
    for student in students[:2]:  # Seed for CS students only
        for course in courses[:5]:
            for delta in range(30):
                d = today - timedelta(days=delta)
                if d.weekday() < 5:  # Weekday only
                    existing = session.query(Attendance).filter_by(
                        student_id=student.id, course_id=course.id, date=d
                    ).first()
                    if not existing:
                        status = "present" if random.random() > 0.15 else "absent"
                        att = Attendance(
                            student_id=student.id, course_id=course.id,
                            date=d, status=status,
                        )
                        session.add(att)


def seed_marks(session, students: list, courses: list) -> None:
    grade_data = [
        ("O", 10.0), ("A+", 9.0), ("A", 8.0), ("B+", 7.0), ("B", 6.0),
    ]
    for student in students:
        for course in courses[:5]:
            existing = session.query(Mark).filter_by(
                student_id=student.id, course_id=course.id, exam_type="internal"
            ).first()
            if not existing:
                grade, gp = random.choice(grade_data)
                max_m = 100.0
                obtained = gp * 10
                m = Mark(
                    student_id=student.id, course_id=course.id,
                    exam_type="internal", marks_obtained=obtained,
                    max_marks=max_m, grade=grade, grade_point=gp,
                    semester=5, exam_date=date.today() - timedelta(days=60),
                )
                session.add(m)


def seed_timetable(session, depts: list, courses: list, faculty_list: list) -> None:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = [("09:00", "10:00"), ("10:00", "11:00"), ("11:15", "12:15"),
             ("12:15", "13:15"), ("14:00", "15:00")]
    rooms = ["LH101", "LH102", "LH103", "LAB201", "LAB202"]
    for i, course in enumerate(courses[:5]):
        existing = session.query(Timetable).filter_by(course_id=course.id).first()
        if not existing:
            day = days[i % 5]
            start, end = slots[i % 5]
            t = Timetable(
                department_id=depts[0].id, course_id=course.id,
                faculty_id=faculty_list[0].id, semester=5,
                day=day, start_time=start, end_time=end,
                room=rooms[i % 5], type="lecture",
            )
            session.add(t)


def seed_notifications(session, admin_user) -> None:
    notifs = [
        ("End Semester Examination Schedule Released", "examination",
         "The End Semester Examination for Semester V will commence from 15th October 2026. "
         "Hall tickets will be distributed from 1st October 2026.", "high"),
        ("TCS Recruitment Drive — 20th August 2026", "placement",
         "TCS is conducting a campus recruitment drive. Eligible students with CGPA ≥ 7.0 "
         "can register by 10th August 2026.", "high"),
        ("Hackathon 2026 Registration Open", "event",
         "Smart India Hackathon 2026 registrations are open. Form teams of 6 and register "
         "on the official portal.", "normal"),
        ("Annual Sports Meet — September 2026", "event",
         "The Annual Sports Meet will be held from 5th to 8th September 2026. "
         "Register with your respective Department Sports Coordinator.", "normal"),
        ("Workshop on AI & Machine Learning", "event",
         "A 3-day hands-on workshop on AI and Machine Learning is scheduled for 25–27 Aug 2026. "
         "Registration is free for all students.", "normal"),
        ("Library Fine Waiver Scheme", "general",
         "The library is offering a one-time fine waiver for overdue books. "
         "Return books by 31st August to avail the waiver.", "low"),
        ("Scholarship Applications Open", "general",
         "Merit-cum-Means scholarship applications for academic year 2026-27 are now open. "
         "Apply through the student portal before 15th September.", "high"),
    ]
    for title, category, content, priority in notifs:
        existing = session.query(Notification).filter_by(title=title).first()
        if not existing:
            n = Notification(
                title=title, content=content, category=category,
                target_role="all", created_by=admin_user.id,
                priority=priority,
            )
            session.add(n)


def seed_policies(session, admin_user) -> None:
    policies = [
        ("Attendance Policy", "attendance",
         "Students must maintain a minimum of 75% attendance in each subject to be eligible "
         "for End Semester Examinations. Students with attendance between 65%-74% may apply "
         "for medical condonation with valid medical certificate. Students below 65% will be "
         "detained and not permitted to appear in examinations."),
        ("Examination Rules", "exam",
         "1. Students must carry their Hall Ticket and College ID for all examinations. "
         "2. Mobile phones and electronic devices are strictly prohibited in the exam hall. "
         "3. Students must arrive 15 minutes before the exam. "
         "4. Use of unfair means will result in immediate cancellation and disciplinary action. "
         "5. Revaluation applications must be submitted within 15 days of result declaration."),
        ("Library Rules", "library",
         "1. Students can borrow up to 3 books for 14 days. "
         "2. A fine of Rs. 2/- per day will be charged for overdue books. "
         "3. Silence must be maintained inside the library. "
         "4. Reference books, journals, and newspapers are for in-library use only. "
         "5. Damaged or lost books must be replaced or the cost paid by the student."),
        ("Hostel Rules", "hostel",
         "1. Hostel in-time is 9:00 PM on weekdays and 10:00 PM on weekends. "
         "2. Visitors are allowed only in the visitor's room during permitted hours. "
         "3. Consumption of alcohol, tobacco, or drugs is strictly prohibited. "
         "4. Ragging in any form is a criminal offense and will be dealt with accordingly. "
         "5. Students must vacate during vacations unless prior permission is obtained."),
        ("Anti-Ragging Policy", "anti_ragging",
         "The institution has a zero-tolerance policy towards ragging in any form. "
         "Any act of ragging will lead to immediate suspension and legal action under the "
         "UGC Anti-Ragging Regulations 2009. Students experiencing ragging should contact "
         "the Anti-Ragging Committee immediately. All complaints will be treated confidentially."),
        ("Dress Code", "dress_code",
         "1. Students must wear the college uniform on all working days. "
         "2. ID card must be worn visibly at all times within the campus. "
         "3. Formal dress code applies during special events, seminars, and campus drives. "
         "4. Laboratory personnel must wear lab coats during all lab sessions. "
         "5. Footwear must be appropriate and safe for the campus environment."),
        ("Code of Conduct", "conduct",
         "Students are expected to maintain high standards of academic integrity and personal conduct. "
         "Plagiarism, cheating, and academic dishonesty will not be tolerated. "
         "Respectful behavior towards faculty, staff, and fellow students is mandatory. "
         "Violation of the code of conduct may result in disciplinary action including suspension."),
    ]
    for title, category, content in policies:
        existing = session.query(Policy).filter_by(title=title).first()
        if not existing:
            p = Policy(
                title=title, category=category, content=content,
                updated_by=admin_user.id,
            )
            session.add(p)


def seed_faqs(session) -> None:
    faqs = [
        ("What is the minimum attendance required?",
         "Students must maintain a minimum of 75% attendance in each subject to be eligible for End Semester Examinations.",
         "attendance"),
        ("How do I apply for medical leave?",
         "Submit a medical certificate from a registered doctor to the class advisor within 7 days of return. The advisor will forward it to the attendance committee.",
         "attendance"),
        ("What documents are required for admission?",
         "Required documents: 10th and 12th mark sheets, Transfer Certificate, Migration Certificate, Conduct Certificate, 6 passport photos, Aadhar Card, Caste Certificate (if applicable), Income Certificate.",
         "admission"),
        ("When are the entrance exam results announced?",
         "Entrance exam results are typically announced within 30 days of the exam. Check the official college website for exact dates.",
         "admission"),
        ("How is CGPA calculated?",
         "CGPA = Sum of (Grade Points × Credits) / Sum of Credits. The 10-point grading scale is: O=10, A+=9, A=8, B+=7, B=6, C=5, F=0.",
         "academics"),
        ("What is the revaluation process?",
         "Apply for revaluation within 15 days of result declaration. Pay the prescribed fee, submit the application to the exam section. Results are declared within 30 days.",
         "exam"),
        ("How do I register for placement drives?",
         "Log in to the student portal, navigate to Placement Cell > Upcoming Drives, and register for eligible drives. Ensure your profile is complete with an updated resume.",
         "placement"),
        ("What is the minimum CGPA for placement eligibility?",
         "The minimum CGPA requirement varies by company. Generally, 6.0 CGPA is the minimum. Premium companies like TCS, Infosys require 7.0+, while top-tier companies require 8.0+.",
         "placement"),
        ("How do I access my hall ticket?",
         "Log in to the student portal 10 days before the exam. Go to Examination > Hall Ticket. Download and print your hall ticket. Carry it to every examination.",
         "exam"),
        ("What are the hostel fee details?",
         "Hostel fees for the academic year 2026-27: Single room Rs. 45,000/year, Double sharing Rs. 35,000/year, Triple sharing Rs. 28,000/year. Includes meals and utilities.",
         "hostel"),
        ("Are there any scholarships available?",
         "Yes, several scholarships are available: State Government Merit Scholarship, Central Government SC/ST Scholarship, College Merit Scholarship (top 10% students), and various private scholarships.",
         "admission"),
        ("How can I track my attendance?",
         "Log in to the student portal and go to Dashboard > Attendance. You can see subject-wise attendance percentage and date-wise records.",
         "attendance"),
    ]
    for question, answer, category in faqs:
        existing = session.query(FAQ).filter_by(question=question).first()
        if not existing:
            f = FAQ(question=question, answer=answer, category=category)
            session.add(f)


def seed_placement_drives(session) -> None:
    today = date.today()
    drives = [
        ("Tata Consultancy Services", today + timedelta(days=18),
         "Systems Engineer", 3.5, 7.0, "CS,IT,ECE",
         today + timedelta(days=10),
         "TCS is conducting a campus recruitment drive for Systems Engineer role. "
         "Package: 3.5 LPA. Eligible branches: CS, IT, ECE."),
        ("Infosys", today + timedelta(days=25),
         "Software Engineer", 4.5, 7.5, "CS,IT",
         today + timedelta(days=18),
         "Infosys PowerProgrammer role. Package: 4.5 LPA. Eligible: CS, IT only. "
         "Selection: Online Test + Technical Interview + HR Interview."),
        ("Wipro", today + timedelta(days=35),
         "Project Engineer", 3.5, 6.5, "CS,IT,ECE,MECH",
         today + timedelta(days=28),
         "Wipro ELITE National Talent Hunt. All branches eligible with CGPA ≥ 6.5."),
        ("Google (Internship)", today + timedelta(days=45),
         "Software Engineering Intern", 0.0, 8.5, "CS,IT",
         today + timedelta(days=30),
         "Google Summer Internship 2026. Stipend: 1.5 LPM. Pre-final year students preferred."),
        ("Amazon", today + timedelta(days=60),
         "SDE-1", 24.0, 8.0, "CS,IT",
         today + timedelta(days=50),
         "Amazon campus hiring for SDE-1 position. Package: 24 LPA. "
         "Selection: 2 Coding Rounds + 3 Technical Interviews + Bar Raiser."),
    ]
    for company, drive_date, role, pkg, cgpa_req, depts, reg_dl, desc in drives:
        existing = session.query(PlacementDrive).filter_by(
            company_name=company, drive_date=drive_date
        ).first()
        if not existing:
            d = PlacementDrive(
                company_name=company, drive_date=drive_date, role=role,
                package_lpa=pkg, eligibility_cgpa=cgpa_req,
                departments=depts, registration_deadline=reg_dl,
                description=desc, status="upcoming",
            )
            session.add(d)


def seed_admissions(session, depts: list) -> None:
    applicants = [
        ("Rahul Mehta", "rahul.mehta@gmail.com", "9111222333", 0, 95.5, "General"),
        ("Sneha Reddy", "sneha.reddy@gmail.com", "9111222334", 0, 98.2, "OBC"),
        ("Vikram Nair", "vikram.nair@gmail.com", "9111222335", 1, 91.0, "General"),
        ("Pooja Iyer", "pooja.iyer@gmail.com", "9111222336", 2, 88.5, "SC"),
        ("Amit Das", "amit.das@gmail.com", "9111222337", 3, 93.0, "General"),
    ]
    statuses = ["approved", "approved", "pending", "approved", "waitlisted"]
    for i, (name, email, phone, dept_idx, score, category) in enumerate(applicants):
        existing = session.query(Admission).filter_by(email=email).first()
        if not existing:
            a = Admission(
                applicant_name=name, email=email, phone=phone,
                department_id=depts[dept_idx].id,
                entrance_score=score, category=category,
                status=statuses[i],
                applied_date=datetime.utcnow() - timedelta(days=30 - i * 5),
            )
            session.add(a)


def seed_placements(session, students: list) -> None:
    placement_data = [
        (0, "TCS", 3.5, "Systems Engineer", date(2026, 3, 15), "campus", "placed"),
        (1, "Infosys", 4.5, "Software Engineer", date(2026, 3, 20), "campus", "placed"),
        (2, None, 0.0, None, None, None, "not_placed"),
        (3, "Wipro", 3.5, "Project Engineer", date(2026, 4, 1), "campus", "placed"),
        (4, "TCS", 3.5, "Systems Engineer", date(2026, 3, 15), "campus", "placed"),
    ]
    for i, (stud_idx, company, pkg, role, placed_date, ptype, status) in enumerate(placement_data):
        s = students[stud_idx]
        existing = session.query(PlacementRecord).filter_by(student_id=s.id).first()
        if not existing:
            r = PlacementRecord(
                student_id=s.id, company_name=company,
                package_lpa=pkg, role=role,
                placed_date=placed_date, placement_type=ptype,
                status=status,
            )
            session.add(r)


def run_seed() -> None:
    """Run all seed functions in correct order."""
    logger.info("Starting database seeding...")
    engine = get_engine()
    init_db(engine)
    session = get_session(engine)

    try:
        roles = seed_roles(session)
        session.commit()

        users = seed_users(session, roles)
        session.commit()

        depts = seed_departments(session)
        session.commit()

        faculty_list = seed_faculty(session, users, depts)
        session.commit()

        students = seed_students(session, users, depts)
        session.commit()

        courses = seed_courses(session, depts, faculty_list)
        session.commit()

        seed_attendance(session, students, courses)
        seed_marks(session, students, courses)
        seed_timetable(session, depts, courses, faculty_list)
        session.commit()

        admin_user = users["admin"]
        seed_notifications(session, admin_user)
        seed_policies(session, admin_user)
        seed_faqs(session)
        seed_placement_drives(session)
        seed_admissions(session, depts)
        seed_placements(session, students)
        session.commit()

        logger.info("✅ Database seeding complete!")

    except Exception as e:
        session.rollback()
        logger.error("Seeding failed: %s", e)
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
