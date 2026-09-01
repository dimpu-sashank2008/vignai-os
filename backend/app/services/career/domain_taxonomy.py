"""
Centralized Career Domain Taxonomy & Academic-to-Domain Mapping for VIGNAI OS.
Defines supported career domains, relevant skill keywords, and subject code mappings.
"""

from typing import Dict, List, Any

CAREER_DOMAINS = {
    "DATA_SCIENCE": {
        "id": "DATA_SCIENCE",
        "name": "Data Science",
        "category": "Analytics & AI",
        "description": "Statistical modeling, machine learning pipelines, predictive analytics, and deep learning.",
        "skills": [
            "Python", "SQL", "Machine Learning", "Scikit-Learn", "TensorFlow",
            "PyTorch", "Pandas", "NumPy", "Statistics", "Deep Learning", "Data Analysis"
        ],
        "subject_codes": ["CS202", "CS302", "MA201", "CS301", "CS304"],
        "project_keywords": ["predictive", "classifier", "neural", "dataset", "regression", "nlp", "vision", "forecasting"],
    },
    "DATA_ANALYTICS": {
        "id": "DATA_ANALYTICS",
        "name": "Data Analytics",
        "category": "Business Intelligence",
        "description": "Data warehousing, dashboarding, exploratory analysis, and business metrics extraction.",
        "skills": [
            "SQL", "Python", "Power BI", "Tableau", "Excel", "Pandas",
            "NumPy", "Data Visualization", "Statistics", "R", "ETL"
        ],
        "subject_codes": ["CS202", "MA201", "CS301"],
        "project_keywords": ["dashboard", "analytics", "visualization", "bi", "metrics", "reporting", "insights", "warehouse"],
    },
    "AI_ML": {
        "id": "AI_ML",
        "name": "AI & Machine Learning",
        "category": "Artificial Intelligence",
        "description": "Computer vision, NLP, generative models, deep neural networks, and intelligent agent systems.",
        "skills": [
            "Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow",
            "Computer Vision", "NLP", "OpenCV", "FastAPI", "Docker"
        ],
        "subject_codes": ["CS302", "CS304", "CS201", "MA201"],
        "project_keywords": ["ai", "transformer", "llm", "opencv", "cnn", "bert", "gpt", "agent", "generative", "vision"],
    },
    "SOFTWARE_ENGINEERING": {
        "id": "SOFTWARE_ENGINEERING",
        "name": "Software Engineering",
        "category": "Core Engineering",
        "description": "Full-lifecycle system design, object-oriented architecture, algorithms, and robust software patterns.",
        "skills": [
            "Python", "Java", "C++", "Data Structures", "Algorithms",
            "Git", "OOP", "Design Patterns", "Linux", "REST APIs"
        ],
        "subject_codes": ["CS201", "CS203", "CS303"],
        "project_keywords": ["application", "system", "engine", "algorithm", "architecture", "microservice", "platform"],
    },
    "BACKEND": {
        "id": "BACKEND",
        "name": "Backend Development",
        "category": "Web & Cloud Services",
        "description": "Server-side architectures, API design, high-concurrency databases, caching, and microservices.",
        "skills": [
            "Python", "FastAPI", "Django", "Node.js", "SQL", "PostgreSQL",
            "MongoDB", "REST APIs", "Redis", "Docker", "Git"
        ],
        "subject_codes": ["CS202", "CS201", "CS204"],
        "project_keywords": ["api", "backend", "server", "database", "crud", "rest", "graphql", "authentication", "orm"],
    },
    "FRONTEND": {
        "id": "FRONTEND",
        "name": "Frontend Engineering",
        "category": "User Interface & Experience",
        "description": "Modern responsive web applications, state management, component architectures, and UI accessibility.",
        "skills": [
            "React", "JavaScript", "TypeScript", "HTML/CSS", "Tailwind CSS",
            "Next.js", "Vue", "Redux", "UI/UX", "REST APIs"
        ],
        "subject_codes": ["CS205", "CS201"],
        "project_keywords": ["frontend", "ui", "ux", "react", "interface", "web app", "responsive", "portal", "dashboard"],
    },
    "CLOUD_DEVOPS": {
        "id": "CLOUD_DEVOPS",
        "name": "Cloud & DevOps",
        "category": "Infrastructure & Reliability",
        "description": "Container orchestration, cloud deployment, continuous integration, infrastructure as code, and Linux administration.",
        "skills": [
            "Linux", "Docker", "Kubernetes", "AWS", "Git",
            "CI/CD", "Bash", "Terraform", "Networking", "Python"
        ],
        "subject_codes": ["CS203", "CS204", "CS305"],
        "project_keywords": ["deploy", "docker", "cloud", "aws", "kubernetes", "pipeline", "ci/cd", "infrastructure", "server"],
    },
    "CYBERSECURITY": {
        "id": "CYBERSECURITY",
        "name": "Cybersecurity & InfoSec",
        "category": "Security & Defense",
        "description": "Network security, vulnerability assessment, cryptography, packet inspection, and defensive hardening.",
        "skills": [
            "Networking", "Linux", "Cybersecurity", "Cryptography",
            "Wireshark", "Penetration Testing", "Python", "Bash"
        ],
        "subject_codes": ["CS204", "CS203", "CS306"],
        "project_keywords": ["security", "packet", "encryption", "vulnerability", "firewall", "auth", "crypto", "wireshark"],
    },
    "EMBEDDED_SYSTEMS": {
        "id": "EMBEDDED_SYSTEMS",
        "name": "Embedded Systems & IoT",
        "category": "Hardware & Firmware",
        "description": "Microcontroller programming, real-time operating systems, sensor integration, and IoT networks.",
        "skills": [
            "C++", "C", "Linux", "IoT", "Microcontrollers",
            "Arduino", "Raspberry Pi", "Sensors", "Networking"
        ],
        "subject_codes": ["CS203", "EC201", "EC202"],
        "project_keywords": ["iot", "embedded", "sensor", "arduino", "raspberry", "hardware", "firmware", "controller"],
    },
    "ELECTRONICS": {
        "id": "ELECTRONICS",
        "name": "VLSI & Electronics",
        "category": "Hardware & Circuits",
        "description": "Circuit design, VLSI architectures, digital signal processing, and hardware description languages.",
        "skills": [
            "Verilog", "VHDL", "MATLAB", "Circuit Design", "Digital Electronics", "Microprocessors"
        ],
        "subject_codes": ["EC201", "EC202", "EC301"],
        "project_keywords": ["vlsi", "fpga", "verilog", "vhdl", "circuit", "dsp", "matlab", "semiconductor"],
    },
    "RESEARCH": {
        "id": "RESEARCH",
        "name": "Academic & Applied Research",
        "category": "Research & Innovation",
        "description": "Scientific investigation, experimental benchmark design, mathematical formalisms, and academic publishing.",
        "skills": [
            "Machine Learning", "Python", "Research Methodology", "Data Analysis",
            "Statistics", "Algorithms", "Mathematics"
        ],
        "subject_codes": ["CS302", "CS304", "MA201"],
        "project_keywords": ["paper", "research", "experiment", "novel", "benchmark", "survey", "formalism", "publication"],
    },
}


def get_domains_for_subject_code(subject_code: str) -> List[str]:
    """Returns all career domain IDs mapped to a given academic subject code."""
    code_upper = subject_code.upper().strip()
    domains = []
    for d_id, data in CAREER_DOMAINS.items():
        if code_upper in data["subject_codes"]:
            domains.append(d_id)
    return domains


def get_domain_by_id(domain_id: str) -> Dict[str, Any]:
    """Returns domain details or fallback dictionary."""
    return CAREER_DOMAINS.get(domain_id.upper(), {
        "id": domain_id,
        "name": domain_id.replace("_", " ").title(),
        "category": "General",
        "description": "General domain alignment",
        "skills": [],
        "subject_codes": [],
        "project_keywords": [],
    })
