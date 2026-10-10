from app.services.work_disc import (
    DIMENSIONS,
    WORK_DISC_VERSION,
    build_work_disc_items,
    score_work_disc,
)


def test_work_disc_bank_has_thirty_realistic_four_choice_items():
    items = build_work_disc_items()

    assert len(items) == 30
    assert len({item["id"] for item in items}) == 30
    assert all(item["situation"] and len(item["options"]) == 4 for item in items)
    assert all(
        {option["dimension"] for option in item["options"]} == set(DIMENSIONS)
        for item in items
    )


def test_work_disc_scoring_summarizes_all_dimensions_without_pass_fail():
    items = build_work_disc_items()
    answers = {item["id"]: 0 for item in items}

    result = score_work_disc(items, answers)

    assert result["version"] == WORK_DISC_VERSION
    assert result["status"] == "complete"
    assert result["answered_items"] == result["total_items"] == 30
    assert result["counts"] == {"D": 30, "I": 0, "S": 0, "C": 0}
    assert result["scores"] == {"D": 100, "I": 0, "S": 0, "C": 0}
    assert "pass" not in result
    assert "fail" not in result


def test_partial_timeout_keeps_unanswered_items_out_of_dimension_scores():
    items = build_work_disc_items()
    answers = {item["id"]: 2 for item in items[:7]}

    result = score_work_disc(items, answers, auto_submitted=True)

    assert result["status"] == "partial"
    assert result["answered_items"] == 7
    assert result["total_items"] == 30
    assert result["auto_submitted"] is True
    assert sum(result["counts"].values()) == 7
    assert sum(result["scores"].values()) == 100


def test_empty_disc_answers_return_zero_scores_not_a_fabricated_profile():
    result = score_work_disc(build_work_disc_items(), {})

    assert result["status"] == "partial"
    assert result["answered_items"] == 0
    assert result["scores"] == {"D": 0, "I": 0, "S": 0, "C": 0}

