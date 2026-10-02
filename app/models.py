from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    client_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
    first_name: str
    last_name: str
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    target_role: str
    years_experience: int = Field(ge=0, le=80)
    skills: str
    current_company: str
    current_role: str
    location: str
    key_achievement: str
    tone: Literal["professional", "technical", "concise"]
    target_company: str = "Your organization"

    @field_validator("*")
    @classmethod
    def nonempty(cls, value):
        if isinstance(value, str) and not value:
            raise ValueError("must not be blank")
        return value

