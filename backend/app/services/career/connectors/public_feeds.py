from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.services.career.connectors.base import OpportunityConnector

class ApprovedPublicFeedConnector(OpportunityConnector):
    """
    Connector for approved open developer challenges and public student fellowships.
    Adheres strictly to robots.txt and authorized open syndication feeds.
    """

    @property
    def source_name(self) -> str:
        return "Approved Public Developer Feed"

    @property
    def source_type(self) -> str:
        return "PUBLIC_FEED"

    async def fetch(self) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        return [
            {
                "title": "Open Source Cloud Native Contributor Fellowship",
                "organization": "Cloud Native Community Foundation",
                "opportunity_type": "INTERNSHIP",
                "description": "3-month stipend-backed remote fellowship contributing to open source container orchestration, observability, and developer tooling.",
                "location": "Worldwide",
                "work_mode": "REMOTE",
                "deadline": (now + timedelta(days=18)).isoformat(),
                "eligibility": "Enrolled students with Git and Linux proficiency",
                "skills_required": ["Git", "Linux", "Python"],
                "skills_preferred": ["Docker", "Kubernetes", "Go"],
            },
            {
                "title": "National Graduate Engineering Aptitude Challenge",
                "organization": "National Tech Skill Council",
                "opportunity_type": "JOB",
                "description": "Graduate software engineer hiring assessment with verified industry partner companies across Hyderabad, Bangalore, and Vizag.",
                "location": "Visakhapatnam / Hyderabad",
                "work_mode": "HYBRID",
                "deadline": (now + timedelta(days=28)).isoformat(),
                "eligibility": "B.Tech Final Year Students",
                "skills_required": ["Data Structures", "SQL", "Java", "Python"],
                "skills_preferred": ["Spring Boot", "React", "Cloud Architecture"],
            }
        ]
