from typing import List

from pydantic import BaseModel, Field


class TokenGenBody(BaseModel):
    count: int = Field(ge=1, le=500)
    type: str = "single"
    max_uses: int = 1


class QuestionBody(BaseModel):
    text: str
    options: List[str] = Field(min_length=2, max_length=6)
    correct_index: int
    category: str = "Umum"
    difficulty: str = "sedang"


class DiscItemsBody(BaseModel):
    items: List[dict]


class ConfigBody(BaseModel):
    tkj_duration_minutes: int
    disc_duration_minutes: int
    tkj_question_count: int
    violation_threshold: int
    require_seb: bool
    seb_browser_exam_key: str = ""
    work_disc_enabled: bool = True
    work_disc_duration_minutes: int = Field(default=60, ge=60, le=60)
