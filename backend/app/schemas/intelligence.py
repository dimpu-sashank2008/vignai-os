from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any

class EmergingPatternSchema(BaseModel):
    id: int
    title: str
    description: str
    pattern_type: str
    severity: str
    case_count: int
    affected_estimate: str
    trend: str
    evidence_case_ids: list[str]
    confidence: float
    primary_department: str | None = None
    primary_location: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CampusIntelligenceSummary(BaseModel):
    total_cases: int
    open_cases_count: int = 0
    emerging_patterns_count: int
    high_impact_risks: int
    recommended_actions_count: int
    campus_intelligence_score: int
    score_status: str # OPTIMAL, GOOD, MODERATE, CRITICAL
    score_breakdown: dict[str, Any]
    is_sufficient_data: bool

class AIPriorityItem(BaseModel):
    case_id: str
    title: str
    category: str | None = None
    location: str | None = None
    department: str | None = None
    ai_suggested_priority: str
    current_status: str
    calculated_score: int
    score_factors: list[str]
    created_at: datetime

class DomainHealthItem(BaseModel):
    domain: str
    health_status: str # Healthy, Watch, Elevated, High Risk
    active_cases: int
    critical_cases: int
    patterns_count: int
    trend: str
    primary_issue_summary: str
    supporting_case_ids: list[str]

class CampusTrendAnalytics(BaseModel):
    volume_timeline: list[dict[str, Any]]
    category_distribution: list[dict[str, Any]]
    department_distribution: list[dict[str, Any]]
    status_distribution: list[dict[str, Any]]
    priority_distribution: list[dict[str, Any]]
    resolution_rate: float
    time_range: str

class AIActivityEvent(BaseModel):
    id: str
    event_type: str # ANALYSIS, ROUTING, PATTERN_DISCOVERY, ACTION_LOG, ESCALATION
    case_id: str | None = None
    title: str
    description: str
    timestamp: datetime
    tag: str

# Phase 4B: Relationship Graph & Explainability Schemas
class GraphNode(BaseModel):
    id: str
    label: str
    type: str # CASE, LOCATION, CATEGORY, DEPARTMENT, PATTERN
    data: dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    type: str # LOCATION_LINK, CATEGORY_LINK, DEPT_LINK, PATTERN_LINK, CASE_SIMILARITY

class IntelligenceGraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    metrics: dict[str, int]

class WhyInsightSignal(BaseModel):
    name: str
    weight: str
    evidence: str

class WhyInsightResponse(BaseModel):
    insight_id: str
    insight_type: str # PATTERN, PRIORITY_CASE, DOMAIN_HEALTH
    title: str
    supporting_case_count: int
    supporting_case_ids: list[str]
    locations: list[str]
    categories: list[str]
    departments: list[str]
    data_window: str
    signals: list[WhyInsightSignal]
    interpretation: str
    limitations: str

# Phase 4C: Ask VIGNEX Schemas
class AskVignexPayload(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    context_filters: dict[str, Any] | None = None

class AskVignexEvidenceCase(BaseModel):
    case_id: str
    title: str
    category: str | None = None
    location: str | None = None
    priority: str
    status: str

class AskVignexResponse(BaseModel):
    query: str
    answer: str
    intent: str
    supporting_cases: list[AskVignexEvidenceCase]
    patterns_referenced: list[str]
    data_grounding: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Phase 4D: What-If Lab Simulation Schemas
class SimulationScenarioConfig(BaseModel):
    scenario_id: str
    name: str
    parameters: dict[str, Any]

class SimulationRunRequest(BaseModel):
    domain: str # TRANSPORT, INFRASTRUCTURE, WIFI_NETWORK
    scenarios: list[SimulationScenarioConfig]

class SimulationMetricResult(BaseModel):
    name: str
    baseline_value: float
    scenario_value: float
    difference: float
    unit: str
    trend_direction: str # BETTER, WORSE, NEUTRAL

class SimulationScenarioResult(BaseModel):
    scenario_id: str
    name: str
    metrics: list[SimulationMetricResult]
    estimated_complaint_reduction_pct: float
    estimated_cost_monthly: str
    estimated_affected_users: str
    operational_risk: str # LOW, MEDIUM, HIGH
    assumptions: list[str]
    ai_scenario_explanation: str

class AIRecommendationPayload(BaseModel):
    recommended_scenario_id: str
    recommended_action: str
    why: str
    supporting_signals: list[str]
    trade_offs: str
    limitations: str
    authority_notice: str

class SimulationComparisonResponse(BaseModel):
    domain: str
    baseline_overview: dict[str, Any]
    scenarios_results: list[SimulationScenarioResult]
    ai_recommendation: AIRecommendationPayload
