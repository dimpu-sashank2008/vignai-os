"""
What-If Lab Deterministic Simulation Engine for VIGNEX (Phase 4D).
Computes transparent mathematical scenario models for campus transport, infrastructure staffing,
and Wi-Fi upgrades, combined with AI-assisted comparative trade-off explanations.
"""

import logging
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.schemas.intelligence import (
    SimulationRunRequest,
    SimulationScenarioConfig,
    SimulationMetricResult,
    SimulationScenarioResult,
    AIRecommendationPayload,
    SimulationComparisonResponse,
)

logger = logging.getLogger(__name__)

class SimulationEngine:
    """Calculates deterministic what-if campus scenario projections."""

    def run_simulation(
        self,
        request: SimulationRunRequest,
        db: Session,
    ) -> SimulationComparisonResponse:
        domain = request.domain.upper()

        if domain == "TRANSPORT":
            return self._simulate_transport(request, db)
        elif domain == "INFRASTRUCTURE":
            return self._simulate_infrastructure(request, db)
        elif domain == "WIFI_NETWORK":
            return self._simulate_wifi(request, db)
        else:
            return self._simulate_transport(request, db)

    def _simulate_transport(
        self,
        request: SimulationRunRequest,
        db: Session,
    ) -> SimulationComparisonResponse:
        complaints = db.query(Complaint).all()
        transit_complaints = [c for c in complaints if "bus" in c.description.lower() or "transport" in (c.category or "").lower()]
        active_transit_count = len(transit_complaints)

        baseline_overview = {
            "active_fleet_buses": 4,
            "avg_peak_wait_time_mins": 28.0,
            "daily_commuter_demand": 650,
            "active_transit_complaints": active_transit_count,
            "current_monthly_cost": "₹1,20,000",
        }

        scenario_results: list[SimulationScenarioResult] = []

        for sc in request.scenarios:
            params = sc.parameters
            add_buses = int(params.get("additional_buses", 1))
            interval_mins = int(params.get("interval_minutes", 20))
            is_express = bool(params.get("express_route", False))

            total_buses = 4 + add_buses
            express_factor = 0.75 if is_express else 1.0

            # Deterministic Formulas
            new_wait_time = round((112.0 / total_buses) * (interval_mins / 30.0) * express_factor, 1)
            capacity_per_hour = round(total_buses * 55 * (60.0 / interval_mins))
            complaint_reduction_pct = round(min(88.0, max(15.0, ((28.0 - new_wait_time) / 28.0) * 100.0)), 1)
            monthly_cost_val = 120000 + (add_buses * 35000) + (15000 if is_express else 0)

            metrics = [
                SimulationMetricResult(
                    name="Peak Waiting Time",
                    baseline_value=28.0,
                    scenario_value=new_wait_time,
                    difference=round(new_wait_time - 28.0, 1),
                    unit="mins",
                    trend_direction="BETTER" if new_wait_time < 28.0 else "NEUTRAL",
                ),
                SimulationMetricResult(
                    name="Transit Fleet Size",
                    baseline_value=4.0,
                    scenario_value=float(total_buses),
                    difference=float(add_buses),
                    unit="buses",
                    trend_direction="BETTER" if add_buses > 0 else "NEUTRAL",
                ),
                SimulationMetricResult(
                    name="Hourly Passenger Capacity",
                    baseline_value=440.0,
                    scenario_value=float(capacity_per_hour),
                    difference=float(capacity_per_hour - 440),
                    unit="passengers/hr",
                    trend_direction="BETTER" if capacity_per_hour > 440 else "NEUTRAL",
                ),
            ]

            assumptions = [
                f"Fleet expanded by {add_buses} chartered vehicle(s) operating at {interval_mins}-min frequency.",
                "Peak morning commuter demand estimated at 650 students daily.",
                "Route traffic congestion index assumed within normal campus perimeter tolerances.",
            ]
            if is_express:
                assumptions.append("Express direct routing skips non-core intermediate campus gates.")

            explanation = (
                f"Deploying {add_buses} additional bus(es) at {interval_mins}-minute intervals "
                f"reduces estimated peak waiting time from 28.0 mins to {new_wait_time} mins (-{round(28.0 - new_wait_time, 1)} mins), "
                f"projected to alleviate ~{complaint_reduction_pct}% of student transit complaints."
            )

            scenario_results.append(
                SimulationScenarioResult(
                    scenario_id=sc.scenario_id,
                    name=sc.name,
                    metrics=metrics,
                    estimated_complaint_reduction_pct=complaint_reduction_pct,
                    estimated_cost_monthly=f"₹{monthly_cost_val:,}",
                    estimated_affected_users=f"~{min(650, total_buses * 140)} students daily",
                    operational_risk="LOW" if add_buses <= 2 else "MEDIUM",
                    assumptions=assumptions,
                    ai_scenario_explanation=explanation,
                )
            )

        # AI Recommendation Synthesis
        best_scenario = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
        ai_recommendation = AIRecommendationPayload(
            recommended_scenario_id=best_scenario.scenario_id,
            recommended_action=f"Adopt {best_scenario.name} for optimal transit balance.",
            why=(
                f"{best_scenario.name} delivers an estimated {best_scenario.estimated_complaint_reduction_pct}% reduction "
                f"in campus transit delays while maintaining sustainable operational expenditure at {best_scenario.estimated_cost_monthly}/mo."
            ),
            supporting_signals=[
                f"{active_transit_count} active transit complaints in SQLite records",
                f"Peak passenger capacity increases significantly",
                "High student impact across morning lecture batches",
            ],
            trade_offs="Increases recurring monthly operating expenses offset by drastic reduction in student arrival delays.",
            limitations="Assumes driver availability and zero unscheduled mechanical breakdowns on active routes.",
            authority_notice="Final decision authority remains exclusively with authorized campus management.",
        )

        return SimulationComparisonResponse(
            domain="TRANSPORT",
            baseline_overview=baseline_overview,
            scenarios_results=scenario_results,
            ai_recommendation=ai_recommendation,
        )

    def _simulate_infrastructure(
        self,
        request: SimulationRunRequest,
        db: Session,
    ) -> SimulationComparisonResponse:
        complaints = db.query(Complaint).all()
        infra_complaints = [
            c for c in complaints
            if any(k in (c.category or "").lower() for k in ["laboratory", "infrastructure", "electrical", "classroom"])
        ]

        baseline_overview = {
            "on_site_technicians": 1,
            "avg_mttr_hours": 96.0,
            "open_hardware_complaints": len(infra_complaints),
            "current_monthly_cost": "₹30,000",
        }

        scenario_results: list[SimulationScenarioResult] = []

        for sc in request.scenarios:
            params = sc.parameters
            add_techs = int(params.get("additional_technicians", 1))
            pm_hours = int(params.get("preventive_maintenance_hours", 10))

            total_techs = 1 + add_techs
            new_mttr = round(max(8.0, (96.0 / total_techs) - (pm_hours * 0.7)), 1)
            reduction_pct = round(min(90.0, max(20.0, ((96.0 - new_mttr) / 96.0) * 100.0)), 1)
            monthly_cost = 30000 + (add_techs * 25000) + (pm_hours * 400)

            metrics = [
                SimulationMetricResult(
                    name="Mean Time to Repair (MTTR)",
                    baseline_value=96.0,
                    scenario_value=new_mttr,
                    difference=round(new_mttr - 96.0, 1),
                    unit="hours",
                    trend_direction="BETTER" if new_mttr < 96.0 else "NEUTRAL",
                ),
                SimulationMetricResult(
                    name="Dedicated Staffing",
                    baseline_value=1.0,
                    scenario_value=float(total_techs),
                    difference=float(add_techs),
                    unit="technicians",
                    trend_direction="BETTER" if add_techs > 0 else "NEUTRAL",
                ),
            ]

            assumptions = [
                f"Maintenance team expanded by {add_techs} technician(s) with {pm_hours} hrs/week scheduled preventive inspection.",
                "Essential spare projector bulbs and cable adapters stocked in department inventory.",
            ]

            explanation = (
                f"Adding {add_techs} technician(s) and {pm_hours} hrs/week preventive inspections "
                f"reduces equipment downtime from 96.0 hrs to {new_mttr} hrs (-{round(96.0 - new_mttr, 1)} hrs)."
            )

            scenario_results.append(
                SimulationScenarioResult(
                    scenario_id=sc.scenario_id,
                    name=sc.name,
                    metrics=metrics,
                    estimated_complaint_reduction_pct=reduction_pct,
                    estimated_cost_monthly=f"₹{monthly_cost:,}",
                    estimated_affected_users=f"~{total_techs * 8} lab sessions weekly",
                    operational_risk="LOW",
                    assumptions=assumptions,
                    ai_scenario_explanation=explanation,
                )
            )

        best_scenario = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
        ai_recommendation = AIRecommendationPayload(
            recommended_scenario_id=best_scenario.scenario_id,
            recommended_action=f"Implement {best_scenario.name} to minimize lab downtime.",
            why=f"{best_scenario.name} cuts average defect resolution time down to ~{best_scenario.metrics[0].scenario_value} hours.",
            supporting_signals=[
                f"{len(infra_complaints)} open lab/infrastructure complaints in database",
                "Projector defect recurrence affecting practical lab sessions",
            ],
            trade_offs="Increases technician staffing budget by ₹25,000/head with immediate payoff in class continuity.",
            limitations="Assumes replacement parts are readily sourced through existing campus vendors.",
            authority_notice="Final decision authority remains exclusively with authorized campus management.",
        )

        return SimulationComparisonResponse(
            domain="INFRASTRUCTURE",
            baseline_overview=baseline_overview,
            scenarios_results=scenario_results,
            ai_recommendation=ai_recommendation,
        )

    def _simulate_wifi(
        self,
        request: SimulationRunRequest,
        db: Session,
    ) -> SimulationComparisonResponse:
        complaints = db.query(Complaint).all()
        wifi_complaints = [c for c in complaints if "wi-fi" in (c.category or "").lower() or "wifi" in c.description.lower()]

        baseline_overview = {
            "active_access_points": 10,
            "signal_coverage_pct": 65.0,
            "open_network_complaints": len(wifi_complaints),
            "current_monthly_cost": "₹50,000",
        }

        scenario_results: list[SimulationScenarioResult] = []

        for sc in request.scenarios:
            params = sc.parameters
            add_aps = int(params.get("new_access_points", 4))
            bw_mult = float(params.get("bandwidth_multiplier", 2.0))

            coverage = round(min(98.0, 65.0 + (add_aps * 4.2)), 1)
            reduction_pct = round(min(92.0, max(25.0, (add_aps * 5.5) + ((bw_mult - 1.0) * 12.0))), 1)
            monthly_cost = 50000 + (add_aps * 4000) + int((bw_mult - 1.0) * 15000)

            metrics = [
                SimulationMetricResult(
                    name="Zone Signal Coverage",
                    baseline_value=65.0,
                    scenario_value=coverage,
                    difference=round(coverage - 65.0, 1),
                    unit="%",
                    trend_direction="BETTER" if coverage > 65.0 else "NEUTRAL",
                ),
                SimulationMetricResult(
                    name="Access Point Density",
                    baseline_value=10.0,
                    scenario_value=float(10 + add_aps),
                    difference=float(add_aps),
                    unit="APs",
                    trend_direction="BETTER" if add_aps > 0 else "NEUTRAL",
                ),
            ]

            assumptions = [
                f"Installed {add_aps} enterprise dual-band APs across Academic Block A and Central Library.",
                f"Campus gateway bandwidth multiplier set to {bw_mult}x.",
            ]

            explanation = (
                f"Adding {add_aps} Access Points and increasing bandwidth by {bw_mult}x "
                f"boosts reliable zone coverage from 65.0% to {coverage}% (+{round(coverage - 65.0, 1)}%), "
                f"projected to resolve ~{reduction_pct}% of authentication and signal drop tickets."
            )

            scenario_results.append(
                SimulationScenarioResult(
                    scenario_id=sc.scenario_id,
                    name=sc.name,
                    metrics=metrics,
                    estimated_complaint_reduction_pct=reduction_pct,
                    estimated_cost_monthly=f"₹{monthly_cost:,}",
                    estimated_affected_users="Entire Academic Block & Library",
                    operational_risk="LOW",
                    assumptions=assumptions,
                    ai_scenario_explanation=explanation,
                )
            )

        best_scenario = max(scenario_results, key=lambda s: s.estimated_complaint_reduction_pct)
        ai_recommendation = AIRecommendationPayload(
            recommended_scenario_id=best_scenario.scenario_id,
            recommended_action=f"Proceed with {best_scenario.name} for high-density coverage.",
            why=f"{best_scenario.name} resolves network bottlenecks across lecture blocks with ~{best_scenario.estimated_complaint_reduction_pct}% complaint reduction.",
            supporting_signals=[
                f"{len(wifi_complaints)} active Wi-Fi complaints recorded",
                "High student device density during lecture hours",
            ],
            trade_offs="One-time AP deployment hardware cost with ongoing ISP bandwidth tier fee.",
            limitations="Assumes building electrical power stability without extended blackout surges.",
            authority_notice="Final decision authority remains exclusively with authorized campus management.",
        )

        return SimulationComparisonResponse(
            domain="WIFI_NETWORK",
            baseline_overview=baseline_overview,
            scenarios_results=scenario_results,
            ai_recommendation=ai_recommendation,
        )


simulation_engine = SimulationEngine()
