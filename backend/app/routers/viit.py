"""
VIIT Context Router for VIGNAI OS (Phase 8B).
Serves institutional metadata, normalized departments, campus locations, regulations,
and future connector health statuses to authenticated and public consumers.
"""

from fastapi import APIRouter, Depends
from typing import Dict, List, Any
from app.services.viit.connectors import mock_viit_connector
from app.services.viit.context import (
    VIIT_METADATA,
    VIIT_DEPARTMENTS,
    VIIT_CAMPUS_BUILDINGS,
    VIIT_EXAM_TERMINOLOGY,
    VIIT_REGULATIONS,
    VIIT_ATTENDANCE_POLICY,
    VIIT_STATUTORY_CELLS,
    VIIT_TRANSPORT_ROUTES,
    VIIT_PLACEMENT_CONTEXT,
)

router = APIRouter(prefix="/viit", tags=["VIIT Institutional Context"])


@router.get("/context", response_model=Dict[str, Any])
def get_viit_context() -> Dict[str, Any]:
    """Returns complete institutional context and connector status payload."""
    return mock_viit_connector.get_institutional_context()


@router.get("/locations", response_model=List[Dict[str, Any]])
def get_viit_locations() -> List[Dict[str, Any]]:
    """Returns canonical campus buildings and facilities for grievance location selection."""
    return list(VIIT_CAMPUS_BUILDINGS.values())


@router.get("/departments", response_model=List[Dict[str, Any]])
def get_viit_departments() -> List[Dict[str, Any]]:
    """Returns normalized VIIT departments catalog."""
    return list(VIIT_DEPARTMENTS.values())


@router.get("/regulations", response_model=List[Dict[str, Any]])
def get_viit_regulations() -> List[Dict[str, Any]]:
    """Returns official academic regulation frameworks."""
    return list(VIIT_REGULATIONS.values())


@router.get("/exam-terminology", response_model=List[Dict[str, Any]])
def get_viit_exam_terms() -> List[Dict[str, Any]]:
    """Returns official evaluation and exam terminology."""
    return list(VIIT_EXAM_TERMINOLOGY.values())
