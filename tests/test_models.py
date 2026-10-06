from app.models import ClientInput, GeneratedContent
import pytest
from pydantic import ValidationError


def valid_client_data():
    return {
        "client_id": "C001",
        "first_name": "Adam",
        "last_name": "Kowalski",
        "email": "adam@example.com",
        "target_role": "Automation Engineer",
        "years_experience": 1,
        "skills": "Python, PLC",
        "current_company": "ABC",
        "current_role": "Automation Engineer",
        "location": "Kraków",
        "key_achievement": "Commissioned production line",
        "tone": "professional",
    }


@pytest.mark.parametrize("invalid_years", [-1, 81])
def test_client_input_rejects_negative_years_experience(invalid_years):
    data = valid_client_data()
    data["years_experience"] = invalid_years
    with pytest.raises(ValidationError):
        ClientInput(**data)


def test_client_input_rejects_wrong_tone():
    data = valid_client_data()
    data["tone"] = "test"
    with pytest.raises(ValidationError):
        ClientInput(**data)


def test_client_input_rejects_empty_name():
    data = valid_client_data()
    data["first_name"] = "    "
    with pytest.raises(ValidationError):
        ClientInput(**data)


def test_client_input_uses_default_target_company():
    data = valid_client_data()
    client = ClientInput(**data)
    assert client.target_company == "Your organization"


@pytest.mark.parametrize(
    "invalid_email",
    [
        "annaexample.com",  # brak @
        "anna example.com",  # spacja
        "anna@@example.com",  # dwa @
    ],
)
def test_client_input_rejects_invalid_email(invalid_email):
    data = valid_client_data()
    data["email"] = invalid_email
    with pytest.raises(ValidationError):
        ClientInput(**data)


def test_client_input_accepts_valid_email():
    data = valid_client_data()
    data["email"] = "anna.kowalska@example.com"
    client = ClientInput(**data)
    assert client.email == "anna.kowalska@example.com"


@pytest.mark.parametrize(
    "invalid_client_id",
    [
        "_C001",  # nie może zaczynać się od _
        "-C001",  # nie może zaczynać się od -
        "C 001",  # spacja
        "C@001",  # niedozwolony znak
    ],
)
def test_client_input_rejects_invalid_client_id(invalid_client_id):
    data = valid_client_data()
    data["client_id"] = invalid_client_id
    with pytest.raises(ValidationError):
        ClientInput(**data)


def test_client_input_accepts_valid_client_id():
    data = valid_client_data()
    data["client_id"] = "CLIENT_01-A"
    client = ClientInput(**data)
    assert client.client_id == "CLIENT_01-A"


def test_generated_content_rejects_blank_key_strength():
    with pytest.raises(ValidationError):
        GeneratedContent(
            professional_summary="Experienced automation engineer.",
            key_strengths=["", "PLC"],
            cover_letter_body="I am interested in this position.",
        )


def test_generated_content_accepts_valid_data():
    content = GeneratedContent(
        professional_summary="Experienced automation engineer.",
        key_strengths=["PLC", "Python"],
        opening_paragraph="I am applying for the position.",
        fit_paragraph="My experience matches the role requirements.",
        achievement_paragraph="I commissioned a production line.",
        closing_paragraph="I would welcome the opportunity to discuss the role.",
    )

    assert content.opening_paragraph == "I am applying for the position."
    assert content.fit_paragraph == "My experience matches the role requirements."
    assert content.achievement_paragraph == "I commissioned a production line."
    assert content.closing_paragraph == (
        "I would welcome the opportunity to discuss the role."
    )


@pytest.mark.parametrize(
    "field_name",
    [
        "professional_summary",
        "opening_paragraph",
        "fit_paragraph",
        "achievement_paragraph",
        "closing_paragraph",
    ],
)
def test_generated_content_rejects_blank_text(field_name):
    data = {
        "professional_summary": "Summary",
        "key_strengths": ["PLC"],
        "opening_paragraph": "Opening",
        "fit_paragraph": "Fit",
        "achievement_paragraph": "Achievement",
        "closing_paragraph": "Closing",
    }

    data[field_name] = "   "

    with pytest.raises(ValidationError):
        GeneratedContent(**data)
