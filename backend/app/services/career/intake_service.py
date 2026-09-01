import re
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.career import Opportunity, OpportunitySkill, OpportunityMatch
from app.models.user import User
from app.services.career.matching_engine import CareerMatchingEngine

class CoordinatorIntakeService:
    """
    Parses pasted/forwarded opportunity circulars from authorized coordinators
    into structured DRAFT opportunities, requiring verification before publishing.
    """

    KNOWN_SKILLS = [
        "Python", "React", "SQL", "Git", "Docker", "Kubernetes", "AWS", "Linux",
        "Machine Learning", "FastAPI", "TypeScript", "JavaScript", "Java", "C++",
        "HTML/CSS", "Tailwind CSS", "MongoDB", "Data Structures", "OpenCV", "PyTorch",
        "REST APIs", "Node.js", "Django", "Flask", "Cybersecurity", "Networking"
    ]

    @classmethod
    def extract_from_text(cls, text: str) -> Dict[str, Any]:
        """Heuristic rule-based extractor for pasted college circulars."""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        first_line = lines[0] if lines else "New Opportunity Announcement"

        # 1. Title Extraction
        title = first_line
        title_match = re.search(r"(?:hiring|opportunity|internship|role|position|announcement)[:\-]?\s*(.+)", first_line, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        elif len(lines) > 1 and len(lines[0]) < 60:
            title = lines[0]

        # 2. Organization Extraction
        org = "VIIT Placement Partner"
        org_match = re.search(r"(?:at|company|organization|recruiter|by)[:\-]?\s*([A-Za-z0-9\s&]+)", text, re.IGNORECASE)
        if org_match:
            candidate_org = org_match.group(1).strip().splitlines()[0].split(".")[0]
            if len(candidate_org) < 60 and candidate_org.lower() not in ["the", "all", "our"]:
                org = candidate_org

        # 3. Opportunity Type
        opp_type = "INTERNSHIP"
        text_lower = text.lower()
        if "hackathon" in text_lower or "competition" in text_lower:
            opp_type = "HACKATHON"
        elif "research" in text_lower or "fellowship" in text_lower:
            opp_type = "RESEARCH"
        elif "certification" in text_lower or "course" in text_lower:
            opp_type = "CERTIFICATION"
        elif "full time" in text_lower or "job" in text_lower or "fresher" in text_lower:
            opp_type = "JOB"

        # 4. Work Mode & Location
        work_mode = "HYBRID"
        loc = "Visakhapatnam (VIIT Campus)"
        if "remote" in text_lower or "work from home" in text_lower or "wfh" in text_lower:
            work_mode = "REMOTE"
            loc = "Remote"
        elif "on-site" in text_lower or "onsite" in text_lower or "in-office" in text_lower:
            work_mode = "ON_SITE"

        loc_match = re.search(r"(?:location|city)[:\-]?\s*([A-Za-z\s,]+)", text, re.IGNORECASE)
        if loc_match:
            loc = loc_match.group(1).strip().splitlines()[0]

        # 5. Skills Extraction
        skills_required = []
        skills_preferred = []
        for sk in cls.KNOWN_SKILLS:
            pattern = rf"\b{re.escape(sk)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                if len(skills_required) < 4:
                    skills_required.append(sk)
                else:
                    skills_preferred.append(sk)

        if not skills_required:
            skills_required = ["Python", "Problem Solving"]

        # 6. Eligibility
        eligibility = "B.Tech All Branches"
        elig_match = re.search(r"(?:eligibility|branches|eligible|criteria)[:\-]?\s*([^\r\n]+)", text, re.IGNORECASE)
        if elig_match:
            eligibility = elig_match.group(1).strip()

        # 7. Deadline Extraction
        deadline = datetime.utcnow() + timedelta(days=14)
        deadline_match = re.search(r"(?:deadline|last date|apply by|closing)[:\-]?\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{1,2}\s+[A-Za-z]+\s+\d{2,4})", text, re.IGNORECASE)
        if deadline_match:
            try:
                date_str = deadline_match.group(1)
                for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d %B %Y", "%d %b %Y"]:
                    try:
                        deadline = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        pass
            except Exception:
                pass

        return {
            "title": title[:250],
            "organization": org[:250],
            "opportunity_type": opp_type,
            "description": text.strip()[:1000],
            "location": loc[:100],
            "work_mode": work_mode,
            "deadline": deadline,
            "eligibility": eligibility[:250],
            "skills_required": skills_required,
            "skills_preferred": skills_preferred,
        }

    @classmethod
    def create_draft(
        cls,
        db: Session,
        user: User,
        announcement_text: str,
        source_name: str = "VIIT Placement Coordinator",
        source_type: str = "AUTHORIZED_COORDINATOR"
    ) -> Opportunity:
        extracted = cls.extract_from_text(announcement_text)
        opp_id = f"OPP-INTAKE-{uuid.uuid4().hex[:6].upper()}"

        # Deterministic fingerprint for deduplication
        deadline_str = extracted["deadline"].strftime("%Y-%m-%d") if extracted.get("deadline") else ""
        fp_str = f"{extracted['title'].lower()}|{extracted['organization'].lower()}|{extracted['opportunity_type'].lower()}|{deadline_str}"
        fingerprint = hashlib.sha256(fp_str.encode()).hexdigest()

        # Check for existing fingerprint
        existing = db.query(Opportunity).filter(Opportunity.fingerprint == fingerprint).first()
        if existing:
            return existing

        opp = Opportunity(
            opportunity_id=opp_id,
            title=extracted["title"],
            organization=extracted["organization"],
            opportunity_type=extracted["opportunity_type"],
            description=extracted["description"],
            location=extracted["location"],
            work_mode=extracted["work_mode"],
            deadline=extracted["deadline"],
            eligibility=extracted["eligibility"],
            source_name=source_name,
            source_type=source_type,
            verification_status="DRAFT", # Starts as DRAFT
            lifecycle_status="NEW",
            submitted_by_id=user.id,
            submitted_at=datetime.utcnow(),
            fingerprint=fingerprint,
            raw_content=announcement_text,
            data_source=f"SUBMISSION FROM {source_name.upper()}",
            is_active=True,
        )
        db.add(opp)
        db.flush()

        for s in extracted["skills_required"]:
            db.add(OpportunitySkill(opportunity_id=opp.id, skill_name=s, is_required=True))
        for s in extracted["skills_preferred"]:
            db.add(OpportunitySkill(opportunity_id=opp.id, skill_name=s, is_required=False))

        db.commit()
        db.refresh(opp)
        return opp

    @classmethod
    def verify_opportunity(
        cls,
        db: Session,
        opportunity_id: int,
        user: User,
        action: str = "VERIFY",
        review_notes: Optional[str] = None
    ) -> Opportunity:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError(f"Opportunity with ID {opportunity_id} not found.")

        if action.upper() == "VERIFY":
            opp.verification_status = "VERIFIED"
            opp.lifecycle_status = "ACTIVE"
            opp.verified_by_id = user.id
            opp.verified_at = datetime.utcnow()
            opp.data_source = f"VERIFIED BY {user.role.upper()} ({opp.source_name})"
            opp.is_active = True
        elif action.upper() == "REJECT":
            opp.verification_status = "REJECTED"
            opp.lifecycle_status = "EXPIRED"
            opp.is_active = False

        db.commit()
        db.refresh(opp)
        return opp
