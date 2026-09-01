"""
VIIT Duvvada Context Layer for VIGNAI OS (Phase 8B).
Centralizes institutional identity, departments, exam terminology, regulations,
campus buildings, statutory grievance cells, transport hubs, and future connector interfaces.
"""

from app.services.viit.context import (
    VIIT_METADATA,
    VIIT_DEPARTMENTS,
    VIIT_EXAM_TERMINOLOGY,
    VIIT_REGULATIONS,
    VIIT_ATTENDANCE_POLICY,
    VIIT_CAMPUS_BUILDINGS,
    VIIT_STATUTORY_CELLS,
    VIIT_TRANSPORT_ROUTES,
    VIIT_PLACEMENT_CONTEXT,
    normalize_department_code,
    normalize_exam_term,
    get_location_canonical_name,
    get_attendance_status_context,
    get_student_regulation_display,
)
from app.services.viit.connectors import (
    IEcapConnector,
    ICoeConnector,
    ILmsConnector,
    ILibraryConnector,
    ITransportConnector,
    MockVIITContextConnector,
    mock_viit_connector,
)

__all__ = [
    "VIIT_METADATA",
    "VIIT_DEPARTMENTS",
    "VIIT_EXAM_TERMINOLOGY",
    "VIIT_REGULATIONS",
    "VIIT_ATTENDANCE_POLICY",
    "VIIT_CAMPUS_BUILDINGS",
    "VIIT_STATUTORY_CELLS",
    "VIIT_TRANSPORT_ROUTES",
    "VIIT_PLACEMENT_CONTEXT",
    "normalize_department_code",
    "normalize_exam_term",
    "get_location_canonical_name",
    "get_attendance_status_context",
    "get_student_regulation_display",
    "IEcapConnector",
    "ICoeConnector",
    "ILmsConnector",
    "ILibraryConnector",
    "ITransportConnector",
    "MockVIITContextConnector",
    "mock_viit_connector",
]
