"""
Pydantic Schemas for VIGNEX What-If Lab Decision Simulation Engine (Phase 4D).
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class SimulationMetricResult(BaseModel):
    name: str
    baseline_value: float
    scenario_value: float
    difference: float
    percentage_change: float
    unit: str
    trend_direction: str  # BETTER, WORSE, NEUTRAL

class SimulationScenarioConfig(BaseModel):
    scenario_id: str
    name: str
    parameters: dict[str, Any]

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
    data_source_label: str = "Prototype simulation model"

class AIExplanationResponse(BaseModel):
    summary: str
    benefits: list[str] = Field(default_factory=list)
    tradeoffs: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    recommended_action: str = ""
    human_authority_notice: str = "Simulation supports decision-making. It does not make the decision."

class SimulationRunRequest(BaseModel):
    domain: str = "TRANSPORT"  # TRANSPORT, INFRASTRUCTURE, MAINTENANCE, RESOURCE_ALLOCATION
    scenario_name: str = "Add buses to a route"
    baseline_parameters: dict[str, Any] = Field(default_factory=dict)
    scenarios: list[SimulationScenarioConfig]

class SimulationComparisonResponse(BaseModel):
    domain: str
    scenario_name: str
    baseline_overview: dict[str, Any]
    scenarios: list[SimulationScenarioResult]
    ai_explanation: AIExplanationResponse
    data_sources: list[str]
    assumptions_summary: list[str]
    limitations_summary: list[str]
    is_synthetic_model: bool = True
    model_notice: str = "Estimated prototype simulation model based on documented operational assumptions."

class SavedSimulationPayload(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    scenario_type: str = "TRANSPORT"
    input_data: dict[str, Any]
    result_data: dict[str, Any]

class SavedSimulationResponse(BaseModel):
    id: int
    user_id: int | None
    name: str
    scenario_type: str
    input_data: dict[str, Any]
    result_data: dict[str, Any]
    created_at: datetime
