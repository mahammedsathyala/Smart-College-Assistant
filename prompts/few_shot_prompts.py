"""
Smart College Assistant — Few-Shot Prompt Examples
Demonstrates desired response format for each agent.
"""

ADMISSION_FEW_SHOTS = [
    {
        "question": "What documents are needed for admission?",
        "answer": (
            "For admission to Smart Engineering College, you need to submit the following documents:\n\n"
            "**Mandatory Documents:**\n"
            "• 10th Standard Mark Sheet (Original + 2 copies)\n"
            "• 12th Standard Mark Sheet (Original + 2 copies)\n"
            "• Transfer Certificate (TC) from previous institution\n"
            "• Migration Certificate\n"
            "• Character/Conduct Certificate\n"
            "• 6 Recent Passport-Size Photographs\n"
            "• Aadhar Card (Original + 2 copies)\n\n"
            "**For Reserved Categories:**\n"
            "• Caste Certificate (SC/ST/OBC)\n"
            "• Income Certificate (for fee concession)\n\n"
            "All documents should be self-attested. Originals will be returned after verification."
        ),
    },
    {
        "question": "What is the fee structure?",
        "answer": (
            "**Fee Structure for Academic Year 2026-27:**\n\n"
            "| Fee Type | Amount |\n"
            "|----------|--------|\n"
            "| Tuition Fee | Rs. 85,000/year |\n"
            "| Development Fee | Rs. 15,000/year |\n"
            "| Examination Fee | Rs. 2,500/semester |\n"
            "| Library Fee | Rs. 1,000/year |\n"
            "| Sports Fee | Rs. 500/year |\n"
            "| **Total** | **Rs. 1,04,000/year** |\n\n"
            "**Hostel (Optional):**\n"
            "• Single Room: Rs. 45,000/year\n"
            "• Double Sharing: Rs. 35,000/year\n\n"
            "Scholarships and fee waivers are available for eligible students."
        ),
    },
]

EXAM_FEW_SHOTS = [
    {
        "question": "How is CGPA calculated?",
        "answer": (
            "**CGPA Calculation Formula:**\n\n"
            "```\nCGPA = Σ (Grade Point × Credits) / Σ Credits\n```\n\n"
            "**Grading Scale (10-point):**\n"
            "| Grade | Grade Point | Marks Range |\n"
            "|-------|-------------|-------------|\n"
            "| O | 10.0 | 91-100 |\n"
            "| A+ | 9.0 | 81-90 |\n"
            "| A | 8.0 | 71-80 |\n"
            "| B+ | 7.0 | 61-70 |\n"
            "| B | 6.0 | 51-60 |\n"
            "| C | 5.0 | 40-50 |\n"
            "| F | 0.0 | Below 40 |\n\n"
            "**Example:**\nIf you scored A(8.0) in a 4-credit subject and B+(7.0) in a 3-credit subject:\n"
            "CGPA = (8.0×4 + 7.0×3) / (4+3) = (32+21) / 7 = **7.57**\n\n"
            "Use our **CGPA Calculator** in Smart Tools for instant calculation! 🎓"
        ),
    },
]

PLACEMENT_FEW_SHOTS = [
    {
        "question": "How can I prepare for TCS campus placement?",
        "answer": (
            "**TCS Campus Placement Preparation Guide:**\n\n"
            "**Selection Process:**\n"
            "1. 🖥️ Online Test (TCS NQT)\n"
            "2. 💻 Technical Interview\n"
            "3. 👔 HR Interview\n\n"
            "**Online Test Topics:**\n"
            "• Quantitative Aptitude\n"
            "• Verbal Ability & Reading Comprehension\n"
            "• Reasoning & Logical Ability\n"
            "• Coding (1-2 problems in Python/Java/C++)\n\n"
            "**Technical Interview Preparation:**\n"
            "• Data Structures & Algorithms\n"
            "• DBMS basics (SQL queries)\n"
            "• OOP concepts\n"
            "• Projects from your resume\n\n"
            "**HR Interview Tips:**\n"
            "• Research TCS — history, services, values\n"
            "• Prepare: 'Tell me about yourself', 'Why TCS?'\n"
            "• Dress professionally\n\n"
            "**Eligibility:** CGPA ≥ 7.0, No active backlogs\n\n"
            "Visit the Placement Cell for mock interviews and practice materials! 🚀"
        ),
    },
]
