import asyncio
import sys
from app.services.ai.examples.dataset import SYNTHETIC_EVALUATION_EXAMPLES
from app.services.ai.policy.rules import (
    CONFIGURED_DEPARTMENTS,
    ROUTE_TYPES,
    SENSITIVITY_LEVELS,
    VIGNEX_AI_POLICY_VERSION,
)
from app.services.ai.provider import get_ai_provider, VALID_CATEGORIES
from app.services.routing.routing_policy import evaluate_routing_policy
from app.models.complaint import Complaint
from app.models.ai_analysis import ComplaintAIAnalysis

async def run_evaluation():
    print("==================================================")
    print(f"VIGNEX AI POLICY EVALUATION (Policy Version: {VIGNEX_AI_POLICY_VERSION})")
    print("==================================================")
    provider = get_ai_provider()
    print(f"Evaluating with Provider: {provider.get_provider_name()} (Model: {provider.get_model_name()})")
    print(f"Total Benchmark Cases: {len(SYNTHETIC_EVALUATION_EXAMPLES)}\n")

    passed_count = 0
    failed_count = 0

    for ex in SYNTHETIC_EVALUATION_EXAMPLES:
        case_id = ex["id"]
        name = ex["name"]
        desc = ex["description"]
        loc = ex.get("location")
        cat = ex.get("category_hint")

        try:
            # 1. Analyze with provider
            analysis = await provider.analyze_complaint(description=desc, location=loc, category=cat)

            # 2. Validate Schema & Constraints
            assert analysis.category in VALID_CATEGORIES, f"Invalid category '{analysis.category}'"
            assert analysis.department is None or analysis.department in CONFIGURED_DEPARTMENTS, f"Invalid department '{analysis.department}'"
            assert analysis.suggested_priority in ["LOW", "MEDIUM", "HIGH", "CRITICAL"], f"Invalid priority '{analysis.suggested_priority}'"
            assert analysis.sensitivity in SENSITIVITY_LEVELS, f"Invalid sensitivity '{analysis.sensitivity}'"
            assert analysis.suggested_route_type in ROUTE_TYPES, f"Invalid route type '{analysis.suggested_route_type}'"
            assert 0.0 <= analysis.confidence <= 1.0, f"Invalid confidence '{analysis.confidence}'"

            # 3. Simulate Policy Engine Evaluation
            mock_complaint = Complaint(
                case_id=case_id,
                description=desc,
                location=loc,
                category=cat,
            )
            mock_ai = ComplaintAIAnalysis(
                category=analysis.category,
                subcategory=analysis.subcategory,
                issue_summary=analysis.issue_summary,
                location=analysis.location,
                department=analysis.department,
                suggested_route_type=analysis.suggested_route_type,
                sensitivity=analysis.sensitivity,
                suggested_priority=analysis.suggested_priority,
                routing_reason=analysis.routing_reason,
            )
            routing_decision = evaluate_routing_policy(mock_complaint, mock_ai)

            # 4. Check specific safety/policy constraints
            if case_id == "SYN-03":  # Faculty Conduct Allegation
                assert analysis.sensitivity == "HIGH_SENSITIVITY", "Allegation must be tagged HIGH_SENSITIVITY"
                assert routing_decision.policy_validation_result == "RESTRICTED_OVERRIDE", "Must trigger RESTRICTED_OVERRIDE"
                assert "SUBJECT_FACULTY" in routing_decision.restricted_recipients, "Subject faculty must be restricted"

            print(f"[{case_id}] PASS: {name}")
            print(f"       Category: {analysis.category} | Dept: {analysis.department} | Sensitivity: {analysis.sensitivity}")
            print(f"       AI Route: {analysis.suggested_route_type} -> Policy: {routing_decision.policy_validation_result} ({routing_decision.final_route})")
            passed_count += 1

        except Exception as e:
            print(f"[{case_id}] FAIL: {name} - Error: {e}")
            failed_count += 1

    print("\n==================================================")
    print(f"EVALUATION SUMMARY: {passed_count}/{len(SYNTHETIC_EVALUATION_EXAMPLES)} Passed ({failed_count} Failed)")
    print("==================================================")

    if failed_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_evaluation())
