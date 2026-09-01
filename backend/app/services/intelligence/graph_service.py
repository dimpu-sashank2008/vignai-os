"""
Knowledge Graph Construction Service for VIGNEX (Phase 4B).
Builds a unified relational graph linking complaints, categories, locations,
departments, and detected emerging patterns from the centralized database.
"""

import logging
import re
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.schemas.intelligence import (
    GraphNode,
    GraphEdge,
    IntelligenceGraphResponse,
)

logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """Create a safe clean identifier for graph node IDs."""
    return re.sub(r'[^a-zA-Z0-9]', '_', text.strip().lower())

class GraphService:
    """Constructs real relationship knowledge graph from centralized records."""

    def build_intelligence_graph(
        self,
        db: Session,
        limit_cases: int = 40,
        filter_dept: str | None = None,
        filter_category: str | None = None,
    ) -> IntelligenceGraphResponse:
        """Query real complaint & pattern data and assemble unified graph nodes and edges."""
        complaints_query = db.query(Complaint).order_by(Complaint.created_at.desc())
        all_complaints = complaints_query.limit(limit_cases).all()

        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()

        nodes_map: dict[str, GraphNode] = {}
        edges_list: list[GraphEdge] = []
        edge_set: set[str] = set()

        def add_edge(source_id: str, target_id: str, label: str, edge_type: str):
            edge_id = f"{source_id}->{target_id}:{label}"
            if edge_id not in edge_set and source_id in nodes_map and target_id in nodes_map:
                edge_set.add(edge_id)
                edges_list.append(
                    GraphEdge(
                        id=edge_id,
                        source=source_id,
                        target=target_id,
                        label=label,
                        type=edge_type,
                    )
                )

        # 1. Pattern Nodes
        for p in patterns:
            pat_id = f"pat-{p.id}"
            nodes_map[pat_id] = GraphNode(
                id=pat_id,
                label=p.title,
                type="PATTERN",
                data={
                    "pattern_id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "pattern_type": p.pattern_type,
                    "severity": p.severity,
                    "case_count": p.case_count,
                    "affected_estimate": p.affected_estimate,
                    "trend": p.trend,
                    "primary_location": p.primary_location,
                    "primary_department": p.primary_department,
                    "confidence": p.confidence,
                },
            )

        # 2. Process Complaints
        for c in all_complaints:
            ai = c.ai_analysis
            cat = c.category or (ai.category if ai else "General") or "General"
            loc = (c.location or (ai.location if ai else "") or "").strip()
            dept = (ai.department if ai and ai.department else None) or "CSE"

            # Filter if requested
            if filter_dept and filter_dept.upper() != "ALL" and dept.upper() != filter_dept.upper():
                continue
            if filter_category and filter_category.upper() != "ALL" and cat.upper() != filter_category.upper():
                continue

            case_node_id = f"case-{c.case_id}"

            # Create Case Node
            nodes_map[case_node_id] = GraphNode(
                id=case_node_id,
                label=c.case_id,
                type="CASE",
                data={
                    "case_id": c.case_id,
                    "title": ai.issue_summary if (ai and ai.issue_summary) else (c.title or c.description[:45]),
                    "description": c.description,
                    "category": cat,
                    "location": loc or "Campus",
                    "priority": c.priority,
                    "status": c.status,
                    "department": dept,
                    "identity_protected": c.identity_protected,
                    "created_at": c.created_at.strftime("%Y-%m-%d"),
                },
            )

            # Create / Update Category Node
            if cat:
                cat_node_id = f"cat-{slugify(cat)}"
                if cat_node_id not in nodes_map:
                    nodes_map[cat_node_id] = GraphNode(
                        id=cat_node_id,
                        label=cat,
                        type="CATEGORY",
                        data={"category_name": cat, "count": 1},
                    )
                else:
                    nodes_map[cat_node_id].data["count"] = nodes_map[cat_node_id].data.get("count", 0) + 1

                add_edge(case_node_id, cat_node_id, "categorized_as", "CATEGORY_LINK")

            # Create / Update Location Node
            if loc and loc.lower() != "campus" and loc.lower() != "not specified":
                loc_node_id = f"loc-{slugify(loc)}"
                if loc_node_id not in nodes_map:
                    nodes_map[loc_node_id] = GraphNode(
                        id=loc_node_id,
                        label=loc.title(),
                        type="LOCATION",
                        data={"location_name": loc.title(), "count": 1},
                    )
                else:
                    nodes_map[loc_node_id].data["count"] = nodes_map[loc_node_id].data.get("count", 0) + 1

                add_edge(case_node_id, loc_node_id, "located_at", "LOCATION_LINK")

            # Create / Update Department Node
            if dept:
                dept_node_id = f"dept-{slugify(dept)}"
                if dept_node_id not in nodes_map:
                    nodes_map[dept_node_id] = GraphNode(
                        id=dept_node_id,
                        label=dept,
                        type="DEPARTMENT",
                        data={"department_name": dept, "count": 1},
                    )
                else:
                    nodes_map[dept_node_id].data["count"] = nodes_map[dept_node_id].data.get("count", 0) + 1

                add_edge(case_node_id, dept_node_id, "routed_to", "DEPT_LINK")

            # Link Case to Matching Patterns
            for p in patterns:
                if isinstance(p.evidence_case_ids, list) and c.case_id in p.evidence_case_ids:
                    pat_node_id = f"pat-{p.id}"
                    add_edge(case_node_id, pat_node_id, "part_of_cluster", "PATTERN_LINK")

        # 3. Link Pattern Nodes to Departments and Locations
        for p in patterns:
            pat_node_id = f"pat-{p.id}"
            if p.primary_department:
                dept_node_id = f"dept-{slugify(p.primary_department)}"
                if dept_node_id in nodes_map:
                    add_edge(pat_node_id, dept_node_id, "impacts_dept", "DEPT_LINK")

            if p.primary_location:
                loc_node_id = f"loc-{slugify(p.primary_location)}"
                if loc_node_id in nodes_map:
                    add_edge(pat_node_id, loc_node_id, "centered_at", "LOCATION_LINK")

        nodes_list = list(nodes_map.values())

        metrics = {
            "total_nodes": len(nodes_list),
            "total_edges": len(edges_list),
            "cases_count": sum(1 for n in nodes_list if n.type == "CASE"),
            "patterns_count": sum(1 for n in nodes_list if n.type == "PATTERN"),
            "locations_count": sum(1 for n in nodes_list if n.type == "LOCATION"),
            "categories_count": sum(1 for n in nodes_list if n.type == "CATEGORY"),
            "departments_count": sum(1 for n in nodes_list if n.type == "DEPARTMENT"),
        }

        return IntelligenceGraphResponse(
            nodes=nodes_list,
            edges=edges_list,
            metrics=metrics,
        )


graph_service = GraphService()
