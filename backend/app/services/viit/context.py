"""
Centralized VIIT Duvvada Institutional Context for VIGNAI OS.
Provides canonical catalogs, aliases, and normalization helpers.
"""

from typing import Dict, List, Any, Optional

# ==============================================================================
# 1. INSTITUTIONAL METADATA
# ==============================================================================
VIIT_METADATA: Dict[str, Any] = {
    "institution_code": "VIIT",
    "institution_name": "Vignan's Institute of Information Technology",
    "short_name": "VIIT Duvvada",
    "campus_name": "Duvvada Campus",
    "location": "Beside VSEZ, Duvvada, Vadlapudi Post, Gajuwaka",
    "city": "Visakhapatnam",
    "state": "Andhra Pradesh",
    "pincode": "530049",
    "affiliation": "JNTUGV (Autonomous Institution)",
    "accreditations": ["NAAC 'A+' Grade", "NBA Accredited Programmes", "UGC Autonomous 2(f) & 12(B)"],
    "data_provenance": "VIIT CONTEXT",
    "system_branding": "VIGNAI OS — Native AI Campus Operating System",
}

# ==============================================================================
# 2. DEPARTMENT CATALOG & ALIASES
# ==============================================================================
VIIT_DEPARTMENTS: Dict[str, Dict[str, Any]] = {
    "CSE": {
        "code": "CSE",
        "name": "Computer Science & Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech CSE", "M.Tech CSE"],
        "aliases": ["computer science", "cs", "cse dept", "computer science and engineering", "b.tech cse"],
    },
    "AI&DS": {
        "code": "AI&DS",
        "name": "Artificial Intelligence & Data Science",
        "category": "EMERGING_TECH",
        "programmes": ["B.Tech AI&DS"],
        "aliases": ["ai and ds", "ai & ds", "aids", "ai-ds", "artificial intelligence and data science", "artificial intelligence & data science"],
    },
    "CSM": {
        "code": "CSM",
        "name": "CSE (Artificial Intelligence & Machine Learning)",
        "category": "EMERGING_TECH",
        "programmes": ["B.Tech CSE-AIML"],
        "aliases": ["cse aiml", "cse ai/ml", "cse-ai&ml", "cse-aiml", "csm", "ai ml cse", "artificial intelligence and machine learning"],
    },
    "CSD": {
        "code": "CSD",
        "name": "CSE (Data Science)",
        "category": "EMERGING_TECH",
        "programmes": ["B.Tech CSE-DS"],
        "aliases": ["cse ds", "cse data science", "cse-ds", "csd", "data science cse"],
    },
    "CSC": {
        "code": "CSC",
        "name": "CSE (Cyber Security)",
        "category": "EMERGING_TECH",
        "programmes": ["B.Tech CSE-CS"],
        "aliases": ["cse cyber security", "cse cyber", "cse-cs", "csc", "cyber security cse"],
    },
    "IT": {
        "code": "IT",
        "name": "Information Technology",
        "category": "ENGINEERING",
        "programmes": ["B.Tech IT", "M.Tech IT"],
        "aliases": ["information technology", "it dept", "infotech", "b.tech it"],
    },
    "ECE": {
        "code": "ECE",
        "name": "Electronics & Communication Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech ECE", "M.Tech VLSI & Embedded Systems"],
        "aliases": ["electronics", "electronics and communication", "ece dept", "b.tech ece"],
    },
    "EEE": {
        "code": "EEE",
        "name": "Electrical & Electronics Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech EEE", "M.Tech Power Electronics"],
        "aliases": ["electrical", "electrical and electronics", "eee dept", "b.tech eee"],
    },
    "ECM": {
        "code": "ECM",
        "name": "Electronics & Computer Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech ECM"],
        "aliases": ["electronics and computer", "ecm dept", "b.tech ecm"],
    },
    "MECH": {
        "code": "MECH",
        "name": "Mechanical Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech MECH", "M.Tech CAD/CAM"],
        "aliases": ["mechanical", "mechanical engineering", "mech dept", "b.tech mech"],
    },
    "CIVIL": {
        "code": "CIVIL",
        "name": "Civil Engineering",
        "category": "ENGINEERING",
        "programmes": ["B.Tech CIVIL", "M.Tech Structural Engineering"],
        "aliases": ["civil", "civil engineering", "civil dept", "b.tech civil"],
    },
    "BS&H": {
        "code": "BS&H",
        "name": "Basic Sciences & Humanities",
        "category": "SCIENCES",
        "programmes": ["Mathematics", "Physics", "Chemistry", "English / Soft Skills"],
        "aliases": ["bsh", "bs&h", "basic sciences", "humanities", "first year", "maths department", "physics dept"],
    },
    "MCA": {
        "code": "MCA",
        "name": "Master of Computer Applications",
        "category": "POSTGRADUATE",
        "programmes": ["MCA (2-Year)"],
        "aliases": ["mca", "master of computer applications"],
    },
    "MBA": {
        "code": "MBA",
        "name": "Master of Business Administration",
        "category": "POSTGRADUATE",
        "programmes": ["MBA (2-Year)"],
        "aliases": ["mba", "management department", "business administration"],
    },
}

# Alias Map for fast normalization
DEPT_ALIAS_MAP: Dict[str, str] = {}
for code, data in VIIT_DEPARTMENTS.items():
    DEPT_ALIAS_MAP[code.lower()] = code
    for alias in data["aliases"]:
        DEPT_ALIAS_MAP[alias.lower()] = code


def normalize_department_code(raw_input: Optional[str]) -> str:
    """Normalizes any department string or alias to official VIIT department code."""
    if not raw_input:
        return "CSE"
    cleaned = raw_input.strip().lower()
    if cleaned in DEPT_ALIAS_MAP:
        return DEPT_ALIAS_MAP[cleaned]

    # Normalize '&' to 'and'
    normalized_cleaned = cleaned.replace("&", "and")

    # Sort aliases by length descending so longer descriptive names match first
    sorted_aliases = sorted(DEPT_ALIAS_MAP.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if len(alias) <= 3:
            # Word boundary check for short abbreviations like 'cs', 'it', 'ece'
            if re.search(rf"\b{re.escape(alias)}\b", cleaned) or re.search(rf"\b{re.escape(alias)}\b", normalized_cleaned):
                return DEPT_ALIAS_MAP[alias]
        else:
            if alias in cleaned or alias in normalized_cleaned:
                return DEPT_ALIAS_MAP[alias]

    return "CSE"

# ==============================================================================
# 3. EXAM TERMINOLOGY & EVALUATION SCHEME
# ==============================================================================
VIIT_EXAM_TERMINOLOGY: Dict[str, Dict[str, Any]] = {
    "CIE": {
        "code": "CIE",
        "name": "Continuous Internal Evaluation",
        "description": "Internal assessment framework comprising Mid-1, Mid-2, assignments, and subjective evaluations.",
        "weightage": "30% / 40% depending on regulation (VR20/VR22/VR23)",
        "aliases": ["cie", "internal exam", "internal evaluation", "internals", "continuous evaluation", "midterm"],
    },
    "Mid-1": {
        "code": "Mid-1",
        "name": "First Midterm Examination",
        "description": "Mid-semester examination testing Modules / Units 1 & 2 of the syllabus.",
        "aliases": ["mid-1", "mid1", "mid 1", "first mid", "first midterm", "midterm 1", "midterm-1"],
    },
    "Mid-2": {
        "code": "Mid-2",
        "name": "Second Midterm Examination",
        "description": "Mid-semester examination testing Modules / Units 3, 4 & 5 of the syllabus.",
        "aliases": ["mid-2", "mid2", "mid 2", "second mid", "second midterm", "midterm 2", "midterm-2"],
    },
    "SEE": {
        "code": "SEE",
        "name": "Semester End Examination",
        "description": "Comprehensive autonomous examination conducted at the end of each semester covering the entire syllabus.",
        "weightage": "70% / 60% depending on regulation",
        "aliases": ["see", "semester end exam", "semester end examination", "final exam", "finals", "externals", "university exam", "semester final"],
    },
    "Lab Internal": {
        "code": "Lab Internal",
        "name": "Continuous Laboratory Evaluation",
        "description": "Internal laboratory evaluation based on day-to-day work, record submission, viva-voce, and internal practical test.",
        "aliases": ["lab internal", "lab internals", "internal lab exam", "day to day lab"],
    },
    "Lab External": {
        "code": "Lab External",
        "name": "Semester End Practical Examination",
        "description": "External practical examination conducted with external examiner evaluation.",
        "aliases": ["lab external", "lab externals", "external lab exam", "lab see", "practical exam"],
    },
}

EXAM_ALIAS_MAP: Dict[str, str] = {}
for code, data in VIIT_EXAM_TERMINOLOGY.items():
    EXAM_ALIAS_MAP[code.lower()] = code
    for alias in data["aliases"]:
        EXAM_ALIAS_MAP[alias.lower()] = code


def normalize_exam_term(raw_input: Optional[str]) -> str:
    """Normalizes colloquial examination terms to official VIIT academic terminology."""
    if not raw_input:
        return "CIE"
    cleaned = raw_input.strip().lower()
    if cleaned in EXAM_ALIAS_MAP:
        return EXAM_ALIAS_MAP[cleaned]
    for alias, code in EXAM_ALIAS_MAP.items():
        if alias in cleaned or cleaned in alias:
            return code
    return "CIE"

# ==============================================================================
# 4. ACADEMIC REGULATIONS
# ==============================================================================
VIIT_REGULATIONS: Dict[str, Dict[str, Any]] = {
    "VR20": {
        "code": "VR20",
        "name": "VIIT Academic Regulation 2020",
        "effective_years": "2020–2024",
        "credit_framework": "160 Total B.Tech Credits, 30 CIE / 70 SEE",
        "description": "Autonomous regulation applicable to 2020 batch admissions.",
    },
    "VR22": {
        "code": "VR22",
        "name": "VIIT Academic Regulation 2022",
        "effective_years": "2022–2026",
        "credit_framework": "160 Total B.Tech Credits, 30 CIE / 70 SEE, Honors & Minors provision",
        "description": "Autonomous regulation applicable to current 3rd and 4th year batches with mandatory industrial internships and skill-oriented courses.",
    },
    "VR23": {
        "code": "VR23",
        "name": "VIIT Academic Regulation 2023",
        "effective_years": "2023–2027",
        "credit_framework": "160 Total B.Tech Credits aligned with APSCHE NEP 2020 framework, 40 CIE / 60 SEE",
        "description": "Latest autonomous regulation with outcome-based continuous assessments and multi-disciplinary minors.",
    },
}


def get_student_regulation_display(regulation_str: Optional[str]) -> str:
    """Returns official regulation label or strictly UNKNOWN if not determined."""
    if not regulation_str:
        return "Regulation: UNKNOWN"
    cleaned = regulation_str.strip().upper()
    if cleaned in VIIT_REGULATIONS:
        return f"Regulation: {cleaned}"
    return "Regulation: UNKNOWN"

# ==============================================================================
# 5. ATTENDANCE POLICY CONTEXT
# ==============================================================================
VIIT_ATTENDANCE_POLICY: Dict[str, Any] = {
    "normal_threshold_pct": 75.0,
    "condonation_min_pct": 65.0,
    "condonation_max_pct": 74.99,
    "detention_threshold_pct": 65.0,
    "rules": {
        "NORMAL": {
            "label": "NORMAL ATTENDANCE",
            "range": ">= 75.0%",
            "description": "Satisfies mandatory autonomous attendance requirement. Eligible to sit for Semester End Examinations (SEE).",
        },
        "CONDONATION_RANGE": {
            "label": "CONDONATION RANGE",
            "range": "65.0% – 74.9%",
            "description": "Attendance falls below normal 75% threshold. Examination eligibility is subject to institutional condonation approval with prescribed medical/extenuating documentation and condonation fee.",
        },
        "DETENTION_WARNING": {
            "label": "DETENTION WARNING",
            "range": "< 65.0%",
            "description": "Critical attendance shortage. Attendance below 65% is not eligible for condonation under academic regulations and leads to semester detention unless officially exempted by the Principal / Academic Council.",
        },
    },
    "policy_disclaimer": "Based on the configured VIIT attendance policy context. Official eligibility should be confirmed by the institution.",
}


def get_attendance_status_context(attendance_pct: float) -> Dict[str, Any]:
    """Interprets attendance percentage according to VIIT academic policy rules."""
    pct = round(attendance_pct, 1)
    if pct >= 75.0:
        tier = "NORMAL"
    elif pct >= 65.0:
        tier = "CONDONATION_RANGE"
    else:
        tier = "DETENTION_WARNING"

    info = VIIT_ATTENDANCE_POLICY["rules"][tier]
    return {
        "attendance_pct": pct,
        "status_code": tier,
        "status_label": info["label"],
        "range_str": info["range"],
        "description": info["description"],
        "policy_disclaimer": VIIT_ATTENDANCE_POLICY["policy_disclaimer"],
    }

# ==============================================================================
# 6. CAMPUS BUILDINGS & FACILITIES
# ==============================================================================
VIIT_CAMPUS_BUILDINGS: Dict[str, Dict[str, Any]] = {
    "APJ Abdul Kalam Block": {
        "name": "APJ Abdul Kalam Block",
        "code": "KALAM_BLOCK",
        "description": "Main administrative and academic block housing the Principal Office, CSE Department, and Computer Laboratories.",
        "facilities": ["Principal Office", "CSE Classrooms", "Advanced Computing Labs", "Server Room", "Dean Offices"],
        "aliases": ["kalam block", "apj block", "apj abdul kalam", "abdul kalam block", "apj", "main block", "block a"],
    },
    "Sir MV Block": {
        "name": "Sir MV Block",
        "code": "MV_BLOCK",
        "description": "Engineering block dedicated to Civil & Mechanical Engineering departments and heavy workshop labs.",
        "facilities": ["Mechanical Workshop", "CAD/CAM Lab", "Strength of Materials Lab", "Civil Survey Labs"],
        "aliases": ["sir mv block", "mv block", "visveswaraya block", "mvisveswaraya", "mech block", "civil block"],
    },
    "Ramanujan Block": {
        "name": "Ramanujan Block",
        "code": "RAMANUJAN_BLOCK",
        "description": "Academic block dedicated to Basic Sciences & Humanities (BS&H) and first-year B.Tech classrooms.",
        "facilities": ["Physics Lab", "Chemistry Lab", "English Communication Skills Lab", "First Year Lecture Halls"],
        "aliases": ["ramanujan block", "ramanujan", "first year block", "bsh block"],
    },
    "Aryabhata Block": {
        "name": "Aryabhata Block",
        "code": "ARYABHATA_BLOCK",
        "description": "Academic block housing Electronics & Communication (ECE) and Electrical & Electronics (EEE) departments.",
        "facilities": ["VLSI Design Lab", "Embedded Systems Lab", "Power Electronics Lab", "Microprocessor Lab"],
        "aliases": ["aryabhata block", "aryabhata", "ece block", "eee block", "electronics block"],
    },
    "Vignan Dhara Central Library": {
        "name": "Vignan Dhara Central Library",
        "code": "LIBRARY",
        "description": "Central Knowledge Center housing over 70,000+ volumes, digital library section with IEEE/Springer access, and reading halls.",
        "facilities": ["Digital Library", "Reference Section", "Periodicals & Journals", "Book Bank", "Discussion Rooms"],
        "aliases": ["library", "central library", "vignan dhara", "vignan dhara central library", "reading room", "digital library"],
    },
    "Dharitri Central Seminar Hall": {
        "name": "Dharitri Central Seminar Hall",
        "code": "DHARITRI",
        "description": "State-of-the-art central auditorium for institutional convocations, guest lectures, technical symposiums, and cultural events.",
        "facilities": ["Air Conditioned Auditorium", "Audio-Visual Projection", "Stage Lighting", "Guest Greenrooms"],
        "aliases": ["dharitri", "dharitri hall", "dharitri seminar hall", "central seminar hall", "auditorium", "seminar hall"],
    },
    "Priyadarshini Girls Hostel": {
        "name": "Priyadarshini Girls Hostel",
        "code": "GIRLS_HOSTEL",
        "description": "Secure on-campus residential hostel accommodation for female students with dining, Wi-Fi, and recreation rooms.",
        "facilities": ["Student Dining Hall", "Wi-Fi Connectivity", "Security Desk", "Medical Room", "Indoor Games"],
        "aliases": ["girls hostel", "priyadarshini hostel", "priyadarshini", "ladies hostel"],
    },
    "Boys Hostel Complex": {
        "name": "Boys Hostel Complex",
        "code": "BOYS_HOSTEL",
        "description": "On-campus residential facilities for male students with dining hall, sports grounds, and study areas.",
        "facilities": ["Student Dining Mess", "Study Halls", "Solar Water Heating", "Wi-Fi Hub"],
        "aliases": ["boys hostel", "mens hostel", "boys campus hostel"],
    },
    "Central Canteen & Food Court": {
        "name": "Central Canteen & Food Court",
        "code": "CANTEEN",
        "description": "Campus cafeteria providing hygienic meals, breakfast, snacks, and beverages for students, faculty, and guests.",
        "facilities": ["Hygienic Dining Area", "Juice & Snack Counters", "Coffee Lounge"],
        "aliases": ["canteen", "cafeteria", "food court", "mess"],
    },
    "Sports Complex & Open Grounds": {
        "name": "Sports Complex & Open Grounds",
        "code": "SPORTS",
        "description": "Outdoor athletic track, cricket pitch, basketball, volleyball courts, and indoor gymnasium facilities.",
        "facilities": ["Cricket Ground", "Basketball Court", "Volleyball Court", "Gymnasium", "Table Tennis"],
        "aliases": ["ground", "sports ground", "sports complex", "gym", "basketball court", "cricket ground"],
    },
    "Other / Not Listed": {
        "name": "Other / Not Listed",
        "code": "OTHER",
        "description": "General campus location or location not listed above.",
        "facilities": ["General Campus"],
        "aliases": ["other", "not listed", "unknown location", "general campus"],
    },
}

BUILDING_ALIAS_MAP: Dict[str, str] = {}
for name, data in VIIT_CAMPUS_BUILDINGS.items():
    BUILDING_ALIAS_MAP[name.lower()] = name
    for alias in data["aliases"]:
        BUILDING_ALIAS_MAP[alias.lower()] = name


def get_location_canonical_name(raw_input: Optional[str]) -> str:
    """Resolves any building alias or colloquial name to canonical VIIT building name."""
    if not raw_input:
        return "APJ Abdul Kalam Block"
    cleaned = raw_input.strip().lower()
    if cleaned in BUILDING_ALIAS_MAP:
        return BUILDING_ALIAS_MAP[cleaned]
    for alias, name in BUILDING_ALIAS_MAP.items():
        if alias in cleaned or cleaned in alias:
            return name
    return raw_input

# ==============================================================================
# 7. STATUTORY & GRIEVANCE BODIES
# ==============================================================================
VIIT_STATUTORY_CELLS: Dict[str, Dict[str, Any]] = {
    "Anti-Ragging Committee": {
        "name": "Anti-Ragging Committee & Squad",
        "code": "ANTI_RAGGING",
        "jurisdiction": "Zero-tolerance monitoring and enforcement against ragging in accordance with UGC regulations.",
        "contact_note": "Campus squad conducts surprise checks across hostel premises, transport points, and campus canteen.",
        "aliases": ["anti ragging", "anti-ragging", "ragging squad", "anti-ragging committee"],
    },
    "Internal Complaints Committee": {
        "name": "Internal Complaints Committee (ICC)",
        "code": "ICC",
        "jurisdiction": "Prevention, prohibition, and redressal of sexual harassment of women at workplace in accordance with POSH Act.",
        "contact_note": "Provides confidential, unbiased inquiry. Handled with highest privacy protocols.",
        "aliases": ["icc", "internal complaints committee", "posh", "posh committee"],
    },
    "Women Protection Cell": {
        "name": "Women Protection Cell (WPC)",
        "code": "WPC",
        "jurisdiction": "Safeguarding the rights, dignity, security, and well-being of female students and staff.",
        "contact_note": "Organizes awareness sessions, self-defense workshops, and confidential grievance counseling.",
        "aliases": ["wpc", "women protection cell", "women protection", "womens cell"],
    },
    "Central Grievance Redressal Committee": {
        "name": "Central Grievance Redressal Committee (CGRC)",
        "code": "CGRC",
        "jurisdiction": "Institutional mechanism for hearing student and staff grievances regarding academic, evaluation, or facility matters.",
        "contact_note": "Chaired by Principal / Senior Professor with student representative presence.",
        "aliases": ["grievance cell", "grievance redressal committee", "central grievance committee", "grievance committee"],
    },
    "SC/ST & Equal Opportunity Cell": {
        "name": "SC/ST & Equal Opportunity Cell",
        "code": "EQUAL_OPPORTUNITY",
        "jurisdiction": "Ensures inclusive environment, fair opportunities, scholarship facilitation, and grievance redressal for marginalized categories.",
        "aliases": ["sc st cell", "equal opportunity cell", "sc/st cell", "obc welfare cell"],
    },
    "Dean Student Affairs": {
        "name": "Dean Student Affairs (DSA)",
        "code": "DSA",
        "jurisdiction": "Oversees student welfare, campus life, clubs, technical chapters, disciplinary decorum, and student representations.",
        "aliases": ["dean student affairs", "dsa", "student affairs dean"],
    },
}

# ==============================================================================
# 8. TRANSPORT TERMINOLOGY & KEY COMMUTE HUBS
# ==============================================================================
VIIT_TRANSPORT_ROUTES: Dict[str, Any] = {
    "fleet_description": "Dedicated VIIT institutional bus fleet operating across Greater Visakhapatnam and surrounding suburbs.",
    "key_commute_areas": [
        "Maddilapalem", "MVP Colony", "Steel Plant", "Kurmannapalem",
        "Anakapalle", "Lankelapalem", "NAD Junction", "Pendurthi",
        "Gajuwaka", "Auto Nagar", "Simhachalam", "Scindia / Malkapuram",
        "Duvvada Railway Station Shuttle",
    ],
    "disclaimer": "Static route context only. Real-time GPS vehicle tracking is not connected to the development environment.",
}

# ==============================================================================
# 9. TRAINING & PLACEMENT (T&P) / CAREER CONTEXT
# ==============================================================================
VIIT_PLACEMENT_CONTEXT: Dict[str, Any] = {
    "cell_name": "Training & Placement Cell (T&P)",
    "programmes": {
        "CRT": {
            "name": "Campus Recruitment Training (CRT)",
            "description": "Structured institutional training covering quantitative aptitude, logical reasoning, verbal ability, and technical coding rounds.",
        },
        "T&P_Drives": {
            "name": "On-Campus & Pool Placement Drives",
            "description": "Recruitment drives organized by the T&P Cell for MNCs, product companies, and core engineering firms.",
        },
        "Internship_Desk": {
            "name": "Mandatory Summer & Semester Internships",
            "description": "Facilitation of academic internship credits under autonomous VR20/VR22/VR23 regulations.",
        },
    },
}
