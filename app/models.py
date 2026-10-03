from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    client_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    target_role: str = Field(max_length=200)
    years_experience: int = Field(ge=0, le=80)
    skills: str
    current_company: str
    current_role: str
    location: str
    key_achievement: str = Field(max_length=1000)
    tone: Literal["professional", "technical", "concise"]
    target_company: str = "Your organization"

    @field_validator("*")
    @classmethod
    def nonempty(cls, value):
        if isinstance(value, str) and not value:
            raise ValueError("must not be blank")
        return value


class GeneratedContent(BaseModel):
    professional_summary: str
    key_strengths: list[str] = Field(min_length=1)
    cover_letter_body: str

    @field_validator("professional_summary", "cover_letter_body")
    @classmethod
    def nonempty_text(cls, value):
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("key_strengths")
    @classmethod
    def validate_key_strengths(cls, values):
        for value in values:
            if not value.strip():
                raise ValueError("must not be blank")
        return values


class RunSummary(BaseModel):
    processed: int
    succeeded: int
    failed: int
    skipped: int = 0
