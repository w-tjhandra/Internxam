from app.seed_data import (
    SCENARIO_ASSESSMENT_VERSION,
    SCENARIO_INDICATORS,
    SCENARIO_ITEMS,
)
from app.services.scenario_assessment import compute_scenario_result


def test_scenario_bank_has_balanced_versioned_rubric():
    assert len(SCENARIO_ITEMS) == 8
    assert {item["indicator"] for item in SCENARIO_ITEMS} == {
        indicator["id"] for indicator in SCENARIO_INDICATORS
    }
    assert all(
        len([item for item in SCENARIO_ITEMS if item["indicator"] == indicator["id"]]) == 2
        for indicator in SCENARIO_INDICATORS
    )
    assert all(
        len(item["options"]) == 4
        and all(0 <= option["score"] <= 3 and option["rationale"] for option in item["options"])
        for item in SCENARIO_ITEMS
    )


def test_scenario_scoring_reports_observed_answers_without_pass_fail():
    items = SCENARIO_ITEMS
    answers = {item["id"]: 0 for item in items}
    result = compute_scenario_result(items, answers, SCENARIO_ASSESSMENT_VERSION)

    assert result["version"] == SCENARIO_ASSESSMENT_VERSION
    assert result["status"] == "pilot"
    assert result["answered_scenarios"] == result["total_scenarios"] == 8
    assert len(result["responses"]) == 8
    assert "pass" not in result
    assert "fail" not in result
    assert all(indicator["average"] == 3 for indicator in result["indicators"].values())


def test_unanswered_scenarios_are_not_scored_as_zero():
    item = SCENARIO_ITEMS[0]
    result = compute_scenario_result(SCENARIO_ITEMS, {}, SCENARIO_ASSESSMENT_VERSION)

    indicator = result["indicators"][item["indicator"]]
    assert result["answered_scenarios"] == 0
    assert indicator["answered"] == 0
    assert indicator["average"] is None


def test_invalid_saved_choice_is_ignored():
    item = SCENARIO_ITEMS[0]
    result = compute_scenario_result(
        SCENARIO_ITEMS, {item["id"]: len(item["options"])}, SCENARIO_ASSESSMENT_VERSION
    )

    assert result["answered_scenarios"] == 0
