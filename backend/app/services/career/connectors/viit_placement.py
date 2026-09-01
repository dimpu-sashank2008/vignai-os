import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.services.career.connectors.base import OpportunityConnector

class MockVIITPlacementConnector(OpportunityConnector):
    """
    Development connector for VIIT Training & Placement Cell.
    Supplies curated campus hiring, pre-placement internships, and lab research opportunities.
    """

    @property
    def source_name(self) -> str:
        return "VIIT Training & Placement Cell"

    @property
    def source_type(self) -> str:
        return "INSTITUTION_CURATED"

    async def fetch(self) -> List[Dict[str, Any]]:
        now = datetime.utcnow()
        return [
            {
                "title": "VIIT Autonomous Systems & AI Research Internship",
                "organization": "VIIT Center for Artificial Intelligence",
                "opportunity_type": "RESEARCH",
                "description": "Engage in funded computer vision and robotics research on autonomous navigation systems at VIIT Duvvada Campus AI Lab.",
                "location": "Visakhapatnam (VIIT Campus)",
                "work_mode": "HYBRID",
                "deadline": (now + timedelta(days=20)).isoformat(),
                "eligibility": "B.Tech 2nd/3rd Year CSE, IT, AIML, ECE (Min CGPA 7.5)",
                "skills_required": ["Python", "Machine Learning", "Data Structures", "OpenCV"],
                "skills_preferred": ["PyTorch", "ROS", "Linux"],
            },
            {
                "title": "VIIT Campus Recruitment Training (CRT) Full-Stack Internship",
                "organization": "VIIT Placement & Industry Relations",
                "opportunity_type": "INTERNSHIP",
                "description": "Pre-placement industry internship program with corporate development partner focusing on enterprise web development and microservices.",
                "location": "Visakhapatnam / Remote",
                "work_mode": "HYBRID",
                "deadline": (now + timedelta(days=12)).isoformat(),
                "eligibility": "B.Tech 3rd & 4th Year All Branches",
                "skills_required": ["Python", "React", "SQL", "Git"],
                "skills_preferred": ["FastAPI", "Docker", "REST APIs"],
            },
            {
                "title": "National Smart Campus Innovation Hackathon 2026",
                "organization": "VIIT Institution's Innovation Council (IIC)",
                "opportunity_type": "HACKATHON",
                "description": "Official college-wide innovation hackathon tackling smart energy, campus transport optimization, and AI academic assistance.",
                "location": "VIIT Campus Auditorium",
                "work_mode": "ON_SITE",
                "deadline": (now + timedelta(days=5)).isoformat(),
                "eligibility": "All VIIT Undergraduate & Postgraduate Students",
                "skills_required": ["Python", "React", "Git", "Problem Solving"],
                "skills_preferred": ["Docker", "Tailwind CSS", "UI/UX"],
            },
            {
                "title": "VIIT Cyber Security & Cloud Infrastructure Certification Track",
                "organization": "VIIT Dept of Computer Science & Engineering",
                "opportunity_type": "CERTIFICATION",
                "description": "Hands-on guided certification covering Linux server administration, network defense, container security, and AWS fundamentals.",
                "location": "Online / VIIT Lab 3",
                "work_mode": "REMOTE",
                "deadline": (now + timedelta(days=25)).isoformat(),
                "eligibility": "Open to all enrolled engineering students",
                "skills_required": ["Linux", "Git", "Networking Basics"],
                "skills_preferred": ["Docker", "AWS", "Bash"],
            },
        ]


class LiveVIITPlacementConnector(OpportunityConnector):
    """
    Production connector for live VIIT Placement Portal API.
    Gracefully degrades if external API key/endpoint is not configured in environment.
    """

    @property
    def source_name(self) -> str:
        return "Live VIIT Placement Portal"

    @property
    def source_type(self) -> str:
        return "APPROVED_API"

    async def fetch(self) -> List[Dict[str, Any]]:
        api_url = os.getenv("VIIT_PLACEMENT_API_URL")
        api_key = os.getenv("VIIT_PLACEMENT_API_KEY")

        if not api_url or not api_key:
            # Not configured in current dev environment -> raise informative error
            raise ConnectionError("Live VIIT Placement Portal credentials not configured in environment.")

        # In production with credentials, makes authorized HTTPS request
        # (Adhering strictly to authorized endpoints and tokens)
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
            res = await client.get(f"{api_url}/v1/opportunities", headers=headers)
            res.raise_for_status()
            return res.json().get("items", [])
