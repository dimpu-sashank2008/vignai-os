"""
VIIT Integration Connector Interfaces & Mock Development Connectors (Phase 8B).
Defines abstract connector interfaces for future institutional ERP/LMS integrations
and provides the static development context connector.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

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
)


class IEcapConnector(ABC):
    """Abstract connector interface for future eCAP Institutional ERP integration."""
    connector_id: str = "ECAP_ERP"
    status: str = "NOT CONFIGURED"

    @abstractmethod
    def fetch_student_record(self, roll_number: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def fetch_attendance_feed(self, roll_number: str) -> Dict[str, Any]:
        pass


class ICoeConnector(ABC):
    """Abstract connector interface for future Controller of Examinations (COE) portal integration."""
    connector_id: str = "COE_EXAMS"
    status: str = "NOT CONFIGURED"

    @abstractmethod
    def fetch_exam_timetables(self, regulation: str, branch: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def fetch_results(self, roll_number: str, semester: int) -> Dict[str, Any]:
        pass


class ILmsConnector(ABC):
    """Abstract connector interface for future Learning Management System (LMS) integration."""
    connector_id: str = "VIIT_LMS"
    status: str = "NOT CONFIGURED"

    @abstractmethod
    def fetch_course_materials(self, subject_code: str) -> List[Dict[str, Any]]:
        pass


class ILibraryConnector(ABC):
    """Abstract connector interface for future Vignan Dhara Central Library ILMS integration."""
    connector_id: str = "VIGNAN_DHARA_LIBRARY"
    status: str = "NOT CONFIGURED"

    @abstractmethod
    def search_books(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def check_book_availability(self, accession_number: str) -> Dict[str, Any]:
        pass


class ITransportConnector(ABC):
    """Abstract connector interface for future Live Transit & GPS fleet integration."""
    connector_id: str = "VIIT_TRANSPORT_GPS"
    status: str = "NOT CONFIGURED"

    @abstractmethod
    def get_live_bus_positions(self) -> List[Dict[str, Any]]:
        pass


class MockVIITContextConnector:
    """
    Mock / Development Context Connector for VIIT Duvvada.
    Serves static institutional knowledge, catalogs, and policy definitions clearly labeled as development context.
    """
    source_name: str = "MockVIITContextConnector"
    source_type: str = "SYNTHETIC_DEVELOPMENT"
    provenance: str = "VIIT CONTEXT"
    is_live_connection: bool = False

    def get_institutional_context(self) -> Dict[str, Any]:
        return {
            "metadata": VIIT_METADATA,
            "departments_count": len(VIIT_DEPARTMENTS),
            "departments": list(VIIT_DEPARTMENTS.values()),
            "regulations": list(VIIT_REGULATIONS.values()),
            "exam_terms": list(VIIT_EXAM_TERMINOLOGY.values()),
            "attendance_policy": VIIT_ATTENDANCE_POLICY,
            "campus_buildings": list(VIIT_CAMPUS_BUILDINGS.values()),
            "statutory_cells": list(VIIT_STATUTORY_CELLS.values()),
            "transport_routes": VIIT_TRANSPORT_ROUTES,
            "placement_context": VIIT_PLACEMENT_CONTEXT,
            "connector_statuses": {
                "ECAP_ERP": "NOT CONFIGURED",
                "COE_EXAMS": "NOT CONFIGURED",
                "VIIT_LMS": "NOT CONFIGURED",
                "VIGNAN_DHARA_LIBRARY": "NOT CONFIGURED",
                "VIIT_TRANSPORT_GPS": "NOT CONFIGURED",
            },
            "provenance": self.provenance,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instance
mock_viit_connector = MockVIITContextConnector()
