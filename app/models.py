from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ClientInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    client_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")

    first_name: str = Field(max_length=100)

    last_name: str = Field(max_length=100)

    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

    target_role: str = Field(max_length=200)

    years_experience: int = Field(
        ge=0,
        le=80,
    )

    skills: str
    current_company: str
    current_role: str
    location: str

    key_achievement: str = Field(max_length=1000)

    tone: Literal[
        "professional",
        "technical",
        "concise",
    ]

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

    opening_paragraph: str
    fit_paragraph: str
    achievement_paragraph: str
    closing_paragraph: str

    @field_validator(
        "professional_summary",
        "opening_paragraph",
        "fit_paragraph",
        "achievement_paragraph",
        "closing_paragraph",
    )
    @classmethod
    def nonempty_text(
        cls,
        value: str,
    ) -> str:
        if not value.strip():
            raise ValueError("must not be blank")

        return value

    @field_validator("key_strengths")
    @classmethod
    def nonempty_strengths(
        cls,
        values: list[str],
    ) -> list[str]:
        for value in values:
            if not value.strip():
                raise ValueError("must not be blank")

        return values


class ClientFailure(BaseModel):
    client_id: str
    error: str


class SkippedRecord(BaseModel):
    row_number: int

    client_id: str | None = None

    error: str


class ClientLoadResult(BaseModel):
    total_records: int

    clients: list[ClientInput] = Field(default_factory=list)

    skipped_records: list[SkippedRecord] = Field(default_factory=list)


class RunSummary(BaseModel):
    processed: int
    succeeded: int
    failed: int
    skipped: int = 0

    failures: list[ClientFailure] = Field(default_factory=list)

    skipped_records: list[SkippedRecord] = Field(default_factory=list)
