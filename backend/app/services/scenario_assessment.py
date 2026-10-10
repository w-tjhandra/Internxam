from app.seed_data import SCENARIO_ASSESSMENT_DISCLAIMER, SCENARIO_INDICATORS


def compute_scenario_result(items: list, answers: dict, version: str) -> dict:
    indicator_scores = {
        indicator["id"]: {
            "label": indicator["label"],
            "description": indicator["description"],
            "total_score": 0,
            "answered": 0,
            "total": 0,
            "average": None,
        }
        for indicator in SCENARIO_INDICATORS
    }
    responses = []
    for item in items:
        indicator = indicator_scores.get(item["indicator"])
        if indicator is None:
            continue
        indicator["total"] += 1
        selected_index = answers.get(item["id"])
        if not isinstance(selected_index, int) or not 0 <= selected_index < len(item["options"]):
            continue
        option = item["options"][selected_index]
        indicator["total_score"] += option["score"]
        indicator["answered"] += 1
        responses.append({
            "scenario_id": item["id"],
            "indicator": item["indicator"],
            "indicator_label": indicator["label"],
            "selected_index": selected_index,
            "selected_option": option["text"],
            "score": option["score"],
            "rationale": option["rationale"],
        })
    for indicator in indicator_scores.values():
        if indicator["answered"]:
            indicator["average"] = round(indicator["total_score"] / indicator["answered"], 2)
    return {
        "version": version,
        "status": "pilot",
        "indicators": indicator_scores,
        "responses": responses,
        "answered_scenarios": len(responses),
        "total_scenarios": len(items),
        "disclaimer": SCENARIO_ASSESSMENT_DISCLAIMER,
    }
