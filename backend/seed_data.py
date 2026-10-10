"""Backward-compatible imports for seed data used by legacy scripts and tests."""

from app.seed_data import (
    DISC_GROUPS,
    DISC_INTERPRETATIONS,
    SCENARIO_ASSESSMENT_DISCLAIMER,
    SCENARIO_ASSESSMENT_VERSION,
    SCENARIO_INDICATORS,
    SCENARIO_ITEMS,
    TKJ_QUESTIONS,
    build_disc_items,
)

__all__ = [
    "DISC_GROUPS",
    "DISC_INTERPRETATIONS",
    "SCENARIO_ASSESSMENT_DISCLAIMER",
    "SCENARIO_ASSESSMENT_VERSION",
    "SCENARIO_INDICATORS",
    "SCENARIO_ITEMS",
    "TKJ_QUESTIONS",
    "build_disc_items",
]
