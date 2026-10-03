from app.models import GeneratedContent, ClientInput
from app.content_generator import FakeGenerator


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


def test_fake_generator_returns_generated_content():
    client = ClientInput(**valid_client_data())

    generator = FakeGenerator()

    result = generator.generate(client)

    assert isinstance(result, GeneratedContent)
