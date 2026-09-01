"""
What-If Lab Decision Simulation Engine for VIGNEX (Phase 4D).
Executes deterministic mathematical simulations across campus domains and synthesizes
structured comparative trade-off explanations.
"""

import logging
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.services.simulation.schemas import (
    SimulationRunRequest,
    SimulationComparisonResponse,
    SimulationScenarioResult,
    AIExplanationResponse,
)
from app.services.simulation.transport import (
    TransportSimulationModel,
    InfrastructureSimulationModel,
    MaintenanceSimulationModel,
)

logger = logging.getLogger(__name__)

class WhatIfSimulationEngine:
    """Calculates deterministic what-if scenario models and structured trade-off explanations."""

    def run_simulation(
        self,
        request: SimulationRunRequest,
        db: Session,
    ) -> SimulationComparisonResponse:
        domain = request.domain.upper()
        scenarios = request.scenarios
        base_params = request.baseline_parameters or {}

        # -------------------------------------------------------------
        # 1. TRANSPORT SCENARIO RUNNER
        # -------------------------------------------------------------
        if domain == "TRANSPORT":
            baseline_overview = {
                "route": base_params.get("route", "Route 4 (North Gate ↔ Hostels)"),
                "current_buses": int(base_params.get("current_buses", 5)),
                "current_demand": float(base_params.get("current_demand", 420.0)),
                "capacity_per_bus": float(base_params.get("capacity_per_bus", 84.0)),
                "average_waiting_time": float(base_params.get("average_waiting_time", 22.0)),
                "current_operating_cost": float(base_params.get("current_operating_cost", 100.0)),
                "active_transit_complaints": db.query(Complaint).filter(Complaint.category.ilike("%transport%")).count(),
            }

            scenario_results: list[SimulationScenarioResult] = []
            for sc in scenarios:
                res = TransportSimulationModel.calculate_scenario(sc=sc, baseline=baseline_overview)
                scenario_results.append(res)

            best_sc = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
            summary_text = (
                f"The modeled scenario reduces estimated peak waiting time from {baseline_overview['average_waiting_time']} mins "
                f"and lowers crowding while increasing operating expenditure proportionally."
            )

            ai_explanation = AIExplanationResponse(
                summary=summary_text,
                benefits=[
                    "Drastic reduction in peak morning bus stop queues and arrival delays",
                    "Reduces passenger crowding on active fleet routes",
                    f"Alleviates an estimated {best_sc.estimated_complaint_reduction_pct}% of transit grievances",
                ],
                tradeoffs=[
                    f"Requires {best_sc.estimated_cost_monthly} additional recurring operating expenditure",
                    "Requires scheduling additional drivers and vehicle maintenance slots",
                ],
                risks=[
                    "Route bottlenecks at external North Gate during municipal traffic congestion peaks",
                    "Driver availability during early morning transit windows",
                ],
                assumptions=[
                    "Commuter demand remains steady at 420 daily peak students",
                    "Vehicle capacity fixed at 84 passengers per bus",
                    "Traffic conditions within standard campus perimeter tolerances",
                ],
                limitations=[
                    "Prototype simulation model based on simplified queuing equations.",
                    "Does not account for external city traffic volatility outside campus boundaries.",
                ],
                recommended_action=f"Adopt {best_sc.name} for the optimal balance of service reliability and cost efficiency.",
                human_authority_notice="Simulation supports decision-making. It does not make the decision.",
            )

            return SimulationComparisonResponse(
                domain="TRANSPORT",
                scenario_name=request.scenario_name or "Add buses to a route",
                baseline_overview=baseline_overview,
                scenarios=scenario_results,
                ai_explanation=ai_explanation,
                data_sources=["VIGNEX Transport Complaint Logs", "Fleet Schedule Baseline (Synthetic Prototype)"],
                assumptions_summary=[
                    "Demand remains constant at 420 daily peak students",
                    "Capacity per bus unchanged at 84 passengers",
                    "Traffic within normal campus perimeter tolerances",
                ],
                limitations_summary=[
                    "Prototype simulation model with simplified assumptions.",
                    "Not a guaranteed real-world forecast; requires administrative review before deployment.",
                ],
                is_synthetic_model=True,
                model_notice="Prototype simulation model based on documented operational parameters.",
            )

        # -------------------------------------------------------------
        # 2. INFRASTRUCTURE SCENARIO RUNNER
        # -------------------------------------------------------------
        elif domain == "INFRASTRUCTURE" or domain == "WIFI_NETWORK":
            baseline_overview = {
                "location": base_params.get("location", "Block A"),
                "current_access_points": int(base_params.get("current_access_points", 10)),
                "current_users": float(base_params.get("current_users", 450.0)),
                "current_utilization": float(base_params.get("current_utilization", 0.90)),
                "average_latency": float(base_params.get("average_latency", 65.0)),
            }

            scenario_results = []
            for sc in scenarios:
                res = InfrastructureSimulationModel.calculate_scenario(sc=sc, baseline=baseline_overview)
                scenario_results.append(res)

            best_sc = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
            summary_text = (
                f"Expanding access points in {baseline_overview['location']} drops network channel utilization "
                f"from {baseline_overview['current_utilization']} to optimal levels and improves packet latency."
            )

            ai_explanation = AIExplanationResponse(
                summary=summary_text,
                benefits=[
                    "Stabilizes wireless lecture connectivity during high-density batch classes",
                    "Reduces packet latency and frequent Wi-Fi drops",
                    "Lowers student network complaints across Block A",
                ],
                tradeoffs=[
                    f"One-time capital expenditure for enterprise hardware ({best_sc.estimated_cost_monthly})",
                    "Requires scheduled weekend downtime for ceiling wiring and AP configuration",
                ],
                risks=[
                    "Channel interference if access points are placed in close proximity without power tuning",
                ],
                assumptions=[
                    "Total simultaneous connected device load estimated at 450 users",
                    "Backbone fiber uplink bandwidth remains unconstrained",
                ],
                limitations=[
                    "Simulation assumes equal client distribution across all deployed access points.",
                ],
                recommended_action=f"Adopt {best_sc.name} to resolve chronic Wi-Fi drops in Block A.",
                human_authority_notice="Simulation supports decision-making. It does not make the decision.",
            )

            return SimulationComparisonResponse(
                domain="INFRASTRUCTURE",
                scenario_name=request.scenario_name or "Increase Wi-Fi access points in Block A",
                baseline_overview=baseline_overview,
                scenarios=scenario_results,
                ai_explanation=ai_explanation,
                data_sources=["VIGNEX Wi-Fi Issue Records", "Block A Wireless Telemetry Baseline"],
                assumptions_summary=[
                    "Connected user load steady at 450 devices",
                    "Backbone fiber throughput capacity unconstrained",
                ],
                limitations_summary=[
                    "Prototype simulation model; physical radio environment testing recommended.",
                ],
                is_synthetic_model=True,
                model_notice="Prototype simulation model based on documented wireless parameters.",
            )

        # -------------------------------------------------------------
        # 3. MAINTENANCE SCENARIO RUNNER
        # -------------------------------------------------------------
        elif domain == "MAINTENANCE":
            baseline_overview = {
                "current_technicians": int(base_params.get("current_technicians", 5)),
                "open_maintenance_cases": db.query(Complaint).filter(Complaint.status.notin_(["RESOLVED", "CLOSED"])).count(),
                "avg_resolution_capacity": float(base_params.get("avg_resolution_capacity", 4.0)),
                "current_backlog_days": float(base_params.get("current_backlog_days", 12.0)),
            }

            scenario_results = []
            for sc in scenarios:
                res = MaintenanceSimulationModel.calculate_scenario(sc=sc, baseline=baseline_overview)
                scenario_results.append(res)

            best_sc = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
            summary_text = (
                f"Increasing technician staffing accelerates ticket resolution and drains "
                f"unresolved maintenance backlog from {baseline_overview['current_backlog_days']} days."
            )

            ai_explanation = AIExplanationResponse(
                summary=summary_text,
                benefits=[
                    "Accelerates classroom projector and electrical ticket turnaround",
                    "Drains persistent maintenance backlogs across academic blocks",
                    "Improves student satisfaction with rapid on-site resolution",
                ],
                tradeoffs=[
                    f"Additional recurring technician payroll ({best_sc.estimated_cost_monthly})",
                    "Requires supervision and inventory management for maintenance tools",
                ],
                risks=[
                    "Potential bottlenecks in spare parts supply chain if procurement is delayed",
                ],
                assumptions=[
                    "Technicians maintain standard average output of 4 resolved tickets/week",
                    "Parts and tools inventory readily accessible",
                ],
                limitations=[
                    "Does not model complex emergency repair projects requiring specialized external contractors.",
                ],
                recommended_action=f"Adopt {best_sc.name} for immediate maintenance queue reduction.",
                human_authority_notice="Simulation supports decision-making. It does not make the decision.",
            )

            return SimulationComparisonResponse(
                domain="MAINTENANCE",
                scenario_name=request.scenario_name or "Increase maintenance capacity",
                baseline_overview=baseline_overview,
                scenarios=scenario_results,
                ai_explanation=ai_explanation,
                data_sources=["VIGNEX Centralized Maintenance Database"],
                assumptions_summary=[
                    "Staff productivity average at 4 cases/week/technician",
                    "Spare parts supply chain is operational",
                ],
                limitations_summary=[
                    "Prototype simulation model with simplified workforce assumptions.",
                ],
                is_synthetic_model=True,
                model_notice="Prototype simulation model based on documented maintenance parameters.",
            )

        # Default fallback to Transport
        else:
            return self.run_simulation(
                request=SimulationRunRequest(domain="TRANSPORT", scenarios=scenarios),
                db=db,
            )


simulation_engine = WhatIfSimulationEngine()
