from pydantic import BaseModel


class ExamStartBody(BaseModel):
    name: str
    school: str
    class_name: str
    token: str


class AnswerBody(BaseModel):
    participant_id: str
    token: str
    question_id: str
    selected_index: int


class SessionBody(BaseModel):
    participant_id: str
    token: str


class DiscAnswerBody(BaseModel):
    participant_id: str
    token: str
    group_index: int
    most: int
    least: int


class ScenarioAnswerBody(BaseModel):
    participant_id: str
    token: str
    scenario_id: str
    selected_index: int


class WorkDiscAnswerBody(BaseModel):
    participant_id: str
    token: str
    item_id: str
    selected_index: int


class ViolationBody(BaseModel):
    participant_id: str
    token: str
    violation_type: str
    detail: str = ""
