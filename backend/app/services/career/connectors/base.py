import abc
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class OpportunityConnector(abc.ABC):
    """Abstract base class for all opportunity connectors."""

    @property
    @abc.abstractmethod
    def source_name(self) -> str:
        """Name of the source (e.g., 'VIIT Placement Cell')."""
        pass

    @property
    @abc.abstractmethod
    def source_type(self) -> str:
        """Type of source (INSTITUTION_CURATED, AUTHORIZED_COORDINATOR, APPROVED_API, PUBLIC_FEED)."""
        pass

    @abc.abstractmethod
    async def fetch(self) -> List[Dict[str, Any]]:
        """Fetches raw opportunity items from the underlying source."""
        pass

    def normalize(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministically normalizes raw fields into standard opportunity format:
        title, organization, opportunity_type, description, location, work_mode,
        deadline, eligibility, skills_required, skills_preferred.
        """
        title = (raw_item.get("title") or "Opportunity").strip()
        org = (raw_item.get("organization") or self.source_name).strip()
        opp_type = (raw_item.get("opportunity_type") or "INTERNSHIP").strip().upper()
        if opp_type not in ["INTERNSHIP", "JOB", "RESEARCH", "HACKATHON", "COURSE", "CERTIFICATION"]:
            opp_type = "INTERNSHIP"

        desc = (raw_item.get("description") or "").strip()
        loc = (raw_item.get("location") or "Remote").strip()
        work_mode = (raw_item.get("work_mode") or "REMOTE").strip().upper()
        if work_mode not in ["REMOTE", "HYBRID", "ON_SITE"]:
            work_mode = "REMOTE"

        eligibility = (raw_item.get("eligibility") or "B.Tech All Years / Branches").strip()
        
        # Parse skills
        raw_req_skills = raw_item.get("skills_required", [])
        raw_pref_skills = raw_item.get("skills_preferred", [])

        skills_required = [s.strip() for s in raw_req_skills if s and s.strip()]
        skills_preferred = [s.strip() for s in raw_pref_skills if s and s.strip()]

        deadline = raw_item.get("deadline")
        if isinstance(deadline, str):
            try:
                deadline = datetime.fromisoformat(deadline)
            except Exception:
                deadline = None

        return {
            "title": title,
            "organization": org,
            "opportunity_type": opp_type,
            "description": desc,
            "location": loc,
            "work_mode": work_mode,
            "deadline": deadline,
            "eligibility": eligibility,
            "skills_required": skills_required,
            "skills_preferred": skills_preferred,
            "source_name": self.source_name,
            "source_type": self.source_type,
            "data_source": f"VERIFIED FROM {self.source_name.upper()}",
            "verification_status": "VERIFIED",
            "lifecycle_status": "ACTIVE",
            "is_active": True,
        }
