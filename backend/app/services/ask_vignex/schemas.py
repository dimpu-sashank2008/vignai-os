"""
Pydantic Schemas for Ask VIGNEX Data-Grounded Campus AI Engine (Phase 4C).
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class AskVignexQueryPayload(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    session_id: str | None = None
    conversation_context: list[dict[str, Any]] | None = None

class IntentClassificationResult(BaseModel):
    intent: str
    query_mode: str = "VIGNEX_DATA"  # GENERAL_KNOWLEDGE, VIGNEX_DATA, HYBRID
    domain: str = "CAMPUS_INTELLIGENCE"  # GENERAL_KNOWLEDGE, ACADEMIC, COMPLAINTS, CAMPUS_INTELLIGENCE, SIMULATIONS, HYBRID
    context_badge: str = "🏛️ VIGNEX CAMPUS DATA"
    department: str | None = None
    location: str | None = None
    category: str | None = None
    time_window: str = "30d"
    follow_up_target_index: int | None = None
    confidence: float = 0.90

class RetrievalContext(BaseModel):
    data_window: str = "last_30_days"
    case_count: int = 0
    open_cases_count: int = 0
    resolved_cases_count: int = 0
    locations: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    departments: list[str] = Field(default_factory=list)
    department_aggregates: dict[str, int] = Field(default_factory=dict)
    trend: str = "STABLE"
    patterns: list[dict[str, Any]] = Field(default_factory=list)
    supporting_cases: list[dict[str, Any]] = Field(default_factory=list)
    supporting_case_ids: list[str] = Field(default_factory=list)
    is_sufficient_data: bool = True
    special_safety_flag: str | None = None # PRIVACY_ATTEMPT, ALLEGATION_TRUTH_ATTEMPT, UNKNOWN_DATA

class AskVignexActionLink(BaseModel):
    label: str
    url: str
    action_type: str # VIEW_CASES, OPEN_PATTERN, OPEN_INTELLIGENCE, VIEW_GRAPH, VIEW_ACADEMICS, VIEW_SIMULATIONS

class AskVignexAnswerResponse(BaseModel):
    query: str
    intent: str
    query_mode: str = "VIGNEX_DATA"  # GENERAL_KNOWLEDGE, VIGNEX_DATA, HYBRID
    domain: str = "CAMPUS_INTELLIGENCE"  # GENERAL_KNOWLEDGE, ACADEMIC, COMPLAINTS, CAMPUS_INTELLIGENCE, SIMULATIONS, HYBRID
    context_badge: str = "🏛️ VIGNEX CAMPUS DATA"  # 📖 GENERAL KNOWLEDGE, 📚 ACADEMIC, 🏛️ VIGNEX CAMPUS DATA, 🛠️ SIMULATION, ⚡ HYBRID
    answer: str
    key_findings: list[str] = Field(default_factory=list)
    supporting_case_ids: list[str] = Field(default_factory=list)
    supporting_cases: list[dict[str, Any]] = Field(default_factory=list)
    data_window: str = "Last 30 days"
    provenance: dict[str, Any] = Field(default_factory=dict)
    interpretation: str = ""
    limitations: list[str] = Field(default_factory=list)
    action_links: list[AskVignexActionLink] = Field(default_factory=list)
    ai_assisted: bool = True
    provider: str = "local_heuristic"
    model: str = "vignex-nlp-rules-v2"
    provider_status: str = "fallback"  # "live", "fallback", "error"
    tools_called: list[str] = Field(default_factory=list)
    latency_ms: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
