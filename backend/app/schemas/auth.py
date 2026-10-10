from pydantic import BaseModel


class LoginBody(BaseModel):
    email: str
    password: str
