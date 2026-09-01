"""
Deterministic Simulation Models for What-If Lab (Phase 4D).
All numerical outputs are calculated purely from documented mathematical relationships.
The LLM never calculates or modifies these numbers.
"""

from typing import Any
from app.services.simulation.schemas import (
    SimulationScenarioConfig,
    SimulationScenarioResult,
    SimulationMetricResult,
)

class TransportSimulationModel:
    """
    Deterministic model for campus bus route expansions.
    Relationship:
      effective_capacity = total_buses * capacity_per_bus
      utilization = demand / effective_capacity
      waiting_time = baseline_wait_time * (baseline_buses / total_buses)
      operating_cost = baseline_cost * (total_buses / baseline_buses)
    """

    @staticmethod
    def calculate_scenario(
        sc: SimulationScenarioConfig,
        baseline: dict[str, Any],
    ) -> SimulationScenarioResult:
        base_buses = int(baseline.get("current_buses", 5))
        base_demand = float(baseline.get("current_demand", 420.0))
        cap_per_bus = float(baseline.get("capacity_per_bus", 84.0))
        base_wait_time = float(baseline.get("average_waiting_time", 22.0))
        base_cost = float(baseline.get("current_operating_cost", 100.0))

        params = sc.parameters
        add_buses = int(params.get("additional_buses", 1))
        total_buses = max(1, base_buses + add_buses)

        # 1. Effective Capacity & Crowding
        base_capacity = base_buses * cap_per_bus
        new_capacity = total_buses * cap_per_bus
        base_crowding = round(min(1.5, base_demand / base_capacity), 2)
        new_crowding = round(min(1.5, base_demand / new_capacity), 2)
        crowding_delta_pct = round(((new_crowding - base_crowding) / base_crowding) * 100.0, 1)

        # 2. Waiting Time
        new_wait_time = round(base_wait_time * (base_buses / total_buses), 1)
        wait_diff = round(new_wait_time - base_wait_time, 1)
        wait_delta_pct = round(((new_wait_time - base_wait_time) / base_wait_time) * 100.0, 1)

        # 3. Operating Cost
        new_cost = round(base_cost * (total_buses / base_buses), 1)
        cost_diff = round(new_cost - base_cost, 1)
        cost_delta_pct = round(((new_cost - base_cost) / base_cost) * 100.0, 1)

        # 4. Metrics Array
        metrics = [
            SimulationMetricResult(
                name="Average Waiting Time",
                baseline_value=base_wait_time,
                scenario_value=new_wait_time,
                difference=wait_diff,
                percentage_change=wait_delta_pct,
                unit="mins",
                trend_direction="BETTER" if new_wait_time < base_wait_time else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Bus Fleet Crowding",
                baseline_value=base_crowding,
                scenario_value=new_crowding,
                difference=round(new_crowding - base_crowding, 2),
                percentage_change=crowding_delta_pct,
                unit="utilization ratio",
                trend_direction="BETTER" if new_crowding < base_crowding else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Operating Cost Index",
                baseline_value=base_cost,
                scenario_value=new_cost,
                difference=cost_diff,
                percentage_change=cost_delta_pct,
                unit="cost units",
                trend_direction="WORSE" if new_cost > base_cost else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Total Active Fleet",
                baseline_value=float(base_buses),
                scenario_value=float(total_buses),
                difference=float(add_buses),
                percentage_change=round((add_buses / base_buses) * 100.0, 1),
                unit="buses",
                trend_direction="BETTER" if add_buses > 0 else "NEUTRAL",
            ),
        ]

        complaint_reduct_pct = round(min(85.0, abs(wait_delta_pct) * 1.1), 1)
        affected_users = f"~{int(base_demand)} daily commuters"

        assumptions = [
            f"Fleet expanded by {add_buses} bus(es) (Total active: {total_buses}).",
            f"Commuter demand remains constant at {int(base_demand)} students during peak hours.",
            f"Capacity per bus fixed at {int(cap_per_bus)} passengers.",
            "Model does not account for external city traffic volatility outside campus gates.",
        ]

        explanation = (
            f"Adding {add_buses} bus(es) to the route reduces average waiting time from {base_wait_time} mins to {new_wait_time} mins ({wait_delta_pct}%) "
            f"and lowers bus crowding from {base_crowding} to {new_crowding} ({crowding_delta_pct}%), "
            f"with an operating cost increase of {cost_delta_pct}%."
        )

        return SimulationScenarioResult(
            scenario_id=sc.scenario_id,
            name=sc.name,
            metrics=metrics,
            estimated_complaint_reduction_pct=complaint_reduct_pct,
            estimated_cost_monthly=f"+{cost_delta_pct}% operating expense",
            estimated_affected_users=affected_users,
            operational_risk="LOW" if add_buses <= 2 else "MEDIUM",
            assumptions=assumptions,
            ai_scenario_explanation=explanation,
            data_source_label="Prototype simulation model (Synthetic Baseline)",
        )


class InfrastructureSimulationModel:
    """
    Deterministic model for Wi-Fi Access Point expansions.
    """

    @staticmethod
    def calculate_scenario(
        sc: SimulationScenarioConfig,
        baseline: dict[str, Any],
    ) -> SimulationScenarioResult:
        base_aps = int(baseline.get("current_access_points", 10))
        base_users = float(baseline.get("current_users", 450.0))
        base_utilization = float(baseline.get("current_utilization", 0.90))
        base_latency = float(baseline.get("average_latency", 65.0))

        params = sc.parameters
        add_aps = int(params.get("additional_access_points", 3))
        total_aps = max(1, base_aps + add_aps)

        # Calculations
        new_utilization = round(base_utilization * (base_aps / total_aps), 2)
        util_delta_pct = round(((new_utilization - base_utilization) / base_utilization) * 100.0, 1)

        new_latency = round(max(22.0, base_latency * (base_aps / total_aps)), 1)
        lat_delta_pct = round(((new_latency - base_latency) / base_latency) * 100.0, 1)

        metrics = [
            SimulationMetricResult(
                name="Network Channel Utilization",
                baseline_value=base_utilization,
                scenario_value=new_utilization,
                difference=round(new_utilization - base_utilization, 2),
                percentage_change=util_delta_pct,
                unit="utilization ratio",
                trend_direction="BETTER" if new_utilization < base_utilization else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Average Ping Latency",
                baseline_value=base_latency,
                scenario_value=new_latency,
                difference=round(new_latency - base_latency, 1),
                percentage_change=lat_delta_pct,
                unit="ms",
                trend_direction="BETTER" if new_latency < base_latency else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Deployed Access Points",
                baseline_value=float(base_aps),
                scenario_value=float(total_aps),
                difference=float(add_aps),
                percentage_change=round((add_aps / base_aps) * 100.0, 1),
                unit="APs",
                trend_direction="BETTER" if add_aps > 0 else "NEUTRAL",
            ),
        ]

        assumptions = [
            f"Installed {add_aps} enterprise dual-band Wi-Fi access points in high-density corridors.",
            f"Active connected user load estimated at {int(base_users)} simultaneous devices.",
            "Backbone fiber uplink bandwidth remains unconstrained.",
        ]

        explanation = (
            f"Deploying {add_aps} additional access point(s) in Block A decreases channel utilization from {base_utilization} to {new_utilization} ({util_delta_pct}%) "
            f"and improves packet latency from {base_latency} ms to {new_latency} ms ({lat_delta_pct}%)."
        )

        return SimulationScenarioResult(
            scenario_id=sc.scenario_id,
            name=sc.name,
            metrics=metrics,
            estimated_complaint_reduction_pct=round(abs(util_delta_pct) * 0.9, 1),
            estimated_cost_monthly=f"₹{add_aps * 8500:,} hardware setup",
            estimated_affected_users=f"~{int(base_users)} students and faculty in Block A",
            operational_risk="LOW",
            assumptions=assumptions,
            ai_scenario_explanation=explanation,
            data_source_label="Prototype simulation model (Block A Wireless Telemetry)",
        )


class MaintenanceSimulationModel:
    """
    Deterministic model for maintenance technician capacity and ticket backlog drain.
    """

    @staticmethod
    def calculate_scenario(
        sc: SimulationScenarioConfig,
        baseline: dict[str, Any],
    ) -> SimulationScenarioResult:
        base_techs = int(baseline.get("current_technicians", 5))
        open_cases = int(baseline.get("open_maintenance_cases", 34))
        capacity_per_tech = float(baseline.get("avg_resolution_capacity", 4.0)) # cases/week
        base_backlog_days = float(baseline.get("current_backlog_days", 12.0))

        params = sc.parameters
        add_techs = int(params.get("additional_technicians", 2))
        total_techs = max(1, base_techs + add_techs)

        base_weekly_capacity = base_techs * capacity_per_tech
        new_weekly_capacity = total_techs * capacity_per_tech
        cap_delta_pct = round(((new_weekly_capacity - base_weekly_capacity) / base_weekly_capacity) * 100.0, 1)

        new_backlog_days = round(max(1.5, base_backlog_days * (base_techs / total_techs)), 1)
        backlog_diff = round(new_backlog_days - base_backlog_days, 1)
        backlog_delta_pct = round(((new_backlog_days - base_backlog_days) / base_backlog_days) * 100.0, 1)

        metrics = [
            SimulationMetricResult(
                name="Average Ticket Resolution Backlog",
                baseline_value=base_backlog_days,
                scenario_value=new_backlog_days,
                difference=backlog_diff,
                percentage_change=backlog_delta_pct,
                unit="days",
                trend_direction="BETTER" if new_backlog_days < base_backlog_days else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Weekly Case Resolution Capacity",
                baseline_value=base_weekly_capacity,
                scenario_value=new_weekly_capacity,
                difference=float(new_weekly_capacity - base_weekly_capacity),
                percentage_change=cap_delta_pct,
                unit="tickets/week",
                trend_direction="BETTER" if new_weekly_capacity > base_weekly_capacity else "NEUTRAL",
            ),
            SimulationMetricResult(
                name="Active Maintenance Staff",
                baseline_value=float(base_techs),
                scenario_value=float(total_techs),
                difference=float(add_techs),
                percentage_change=round((add_techs / base_techs) * 100.0, 1),
                unit="technicians",
                trend_direction="BETTER" if add_techs > 0 else "NEUTRAL",
            ),
        ]

        assumptions = [
            f"Contracted {add_techs} additional qualified field technician(s) across campus electrical & civil teams.",
            f"Average output maintained at {capacity_per_tech} tickets per technician per week.",
            "Spare parts supply chain assumes uninterrupted parts availability.",
        ]

        explanation = (
            f"Increasing maintenance staff by {add_techs} technicians expands weekly resolution capacity from {base_weekly_capacity} to {new_weekly_capacity} tickets/wk (+{cap_delta_pct}%) "
            f"and cuts average case backlog turnaround from {base_backlog_days} days to {new_backlog_days} days ({backlog_delta_pct}%)."
        )

        return SimulationScenarioResult(
            scenario_id=sc.scenario_id,
            name=sc.name,
            metrics=metrics,
            estimated_complaint_reduction_pct=round(min(80.0, abs(backlog_delta_pct) * 1.05), 1),
            estimated_cost_monthly=f"+₹{add_techs * 25000:,}/month staff payroll",
            estimated_affected_users=f"~{open_cases} open student & faculty maintenance cases",
            operational_risk="LOW",
            assumptions=assumptions,
            ai_scenario_explanation=explanation,
            data_source_label="Prototype simulation model (Centralized Maintenance Queues)",
        )
