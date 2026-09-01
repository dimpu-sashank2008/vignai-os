from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.models.emerging_pattern import EmergingPattern
from app.schemas.intelligence import (
    CampusIntelligenceSummary,
    EmergingPatternSchema,
    AIPriorityItem,
    DomainHealthItem,
    CampusTrendAnalytics,
    AIActivityEvent,
    IntelligenceGraphResponse,
    WhyInsightResponse,
    SimulationRunRequest,
    SimulationComparisonResponse,
)
from app.services.ask_vignex.schemas import (
    AskVignexQueryPayload,
    AskVignexAnswerResponse,
)
from app.services.intelligence.pattern_detection import pattern_detection_service
from app.services.intelligence.analytics_engine import analytics_engine
from app.services.intelligence.graph_service import graph_service
from app.services.intelligence.explainability_service import explainability_service
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.simulation.engine import simulation_engine

router = APIRouter(prefix="/intelligence", tags=["intelligence"])

@router.get("/summary", response_model=CampusIntelligenceSummary)
async def get_campus_intelligence_summary(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve top-level KPI metrics, active patterns count, high impact risks, and transparent score."""
    return analytics_engine.get_summary(db)

@router.get("/patterns", response_model=list[EmergingPatternSchema])
async def list_emerging_patterns(
    status_filter: str | None = Query("ACTIVE", alias="status"),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve all detected emerging patterns and clusters with supporting evidence case IDs."""
    query = db.query(EmergingPattern)
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(EmergingPattern.status == status_filter.upper())

    patterns = query.order_by(EmergingPattern.created_at.desc()).all()
    if not patterns and status_filter.upper() == "ACTIVE":
        patterns = pattern_detection_service.detect_and_save_patterns(db)

    return patterns

@router.post("/patterns/refresh", response_model=list[EmergingPatternSchema])
async def refresh_emerging_patterns(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Trigger real-time re-evaluation of clustering algorithms across all database complaint records."""
    return pattern_detection_service.detect_and_save_patterns(db)

@router.get("/priorities", response_model=list[AIPriorityItem])
async def list_ai_priorities(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve AI-assisted prioritized cases ranked with transparent score calculation."""
    return analytics_engine.get_ai_priorities(db, limit=limit)

@router.get("/health", response_model=list[DomainHealthItem])
async def get_domain_health_matrix(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve campus operational health breakdown across standard functional domains."""
    return analytics_engine.get_domain_health(db)

@router.get("/trends", response_model=CampusTrendAnalytics)
async def get_trend_analytics(
    time_range: str = Query("30d"),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve complaint volume timeline, category, department, and status distributions."""
    return analytics_engine.get_trend_analytics(db, time_range=time_range)

@router.get("/activity", response_model=list[AIActivityEvent])
async def get_ai_activity_stream(
    limit: int = Query(15, ge=1, le=50),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve real-time processing, routing, and pattern discovery activity stream."""
    return analytics_engine.get_activity_stream(db, limit=limit)

# Phase 4B Endpoints: Relationship Graph & Explainability
@router.get("/graph", response_model=IntelligenceGraphResponse)
async def get_intelligence_graph(
    limit: int = Query(40, ge=5, le=100),
    department: str | None = Query(None),
    category: str | None = Query(None),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve unified knowledge graph linking cases, locations, categories, departments, and patterns."""
    return graph_service.build_intelligence_graph(
        db=db,
        limit_cases=limit,
        filter_dept=department,
        filter_category=category,
    )

@router.get("/explain/{insight_type}/{insight_id}", response_model=WhyInsightResponse)
async def explain_insight(
    insight_type: str,
    insight_id: str,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve structured 'Why this insight?' explanation with supporting evidence, signals, and limitations."""
    try:
        return explainability_service.explain_insight(
            db=db,
            insight_type=insight_type,
            insight_id=insight_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/patterns/{pattern_id}/explanation", response_model=WhyInsightResponse)
async def explain_pattern_by_id(
    pattern_id: str,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve structured explanation for an emerging pattern by pattern ID."""
    try:
        return explainability_service.explain_insight(
            db=db,
            insight_type="PATTERN",
            insight_id=pattern_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# Phase 4C Endpoint: Ask VIGNEX Natural Language Q&A
@router.post("/ask", response_model=AskVignexAnswerResponse)
@router.post("/ask-vignex", response_model=AskVignexAnswerResponse)
async def ask_vignex(
    payload: AskVignexQueryPayload,
    current_user: User = Depends(require_role("management", "student", "faculty")),
    db: Session = Depends(get_db),
):
    """Answer natural language administrative & academic queries strictly grounded in SQLite database records."""
    return ask_vignex_answer_service.process_query(
        payload=payload,
        db=db,
        user=current_user,
    )

# Phase 4D Endpoints: What-If Lab Simulations
@router.post("/simulations/run", response_model=SimulationComparisonResponse)
async def run_what_if_simulation(
    payload: SimulationRunRequest,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Run deterministic what-if scenario simulations with multi-scenario comparison and AI trade-off analysis."""
    return simulation_engine.run_simulation(
        request=payload,
        db=db,
    )
