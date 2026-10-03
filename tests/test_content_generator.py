from app.content_generator import (
    FakeGenerator,
    OllamaGenerator,
    OpenAIGenerator,
    build_prompt,
)
from app.models import ClientInput, GeneratedContent


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


class FakeResponses:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed
        self.kwargs = None

    def parse(self, **kwargs):
        self.kwargs = kwargs

        class FakeResponse:
            pass

        response = FakeResponse()
        response.output_parsed = self.output_parsed
        return response


class FakeAPIClient:
    def __init__(self, output_parsed):
        self.responses = FakeResponses(output_parsed)


def test_fake_generator_returns_generated_content():
    client = ClientInput(**valid_client_data())
    generator = FakeGenerator()
    result = generator.generate(client)
    assert isinstance(result, GeneratedContent)


def test_build_prompt_contains_client_data():
    client = ClientInput(**valid_client_data())
    prompt = build_prompt(client)
    assert client.first_name in prompt
    assert client.last_name in prompt
    assert client.target_role in prompt
    assert client.skills in prompt
    assert client.tone in prompt


def test_build_prompt_contains_generation_instructions():
    client = ClientInput(**valid_client_data())
    prompt = build_prompt(client)
    assert "professional summary" in prompt.lower()
    assert "key strengths" in prompt.lower()
    assert "cover letter" in prompt.lower()


def test_openai_generator_returns_parsed_content():
    expected = GeneratedContent(
        professional_summary="Experienced automation engineer.",
        key_strengths=["PLC", "Python"],
        cover_letter_body="I am interested in the position.",
    )
    api_client = FakeAPIClient(expected)
    generator = OpenAIGenerator(
        api_client,
        model="test-model",
    )
    client = ClientInput(**valid_client_data())
    result = generator.generate(client)
    assert result == expected
    assert api_client.responses.kwargs["model"] == "test-model"
    assert api_client.responses.kwargs["text_format"] is GeneratedContent
    assert client.target_role in api_client.responses.kwargs["input"]


def test_ollama_generator_returns_generated_content(monkeypatch):
    expected_json = """
    {
        "professional_summary": "Experienced automation engineer.",
        "key_strengths": ["PLC", "Python"],
        "cover_letter_body": "I am interested in the position."
    }
    """

    class FakeMessage:
        content = expected_json

    class FakeResponse:
        message = FakeMessage()

    def fake_chat(**kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "app.content_generator.ollama.chat",
        fake_chat,
    )
    client = ClientInput(**valid_client_data())
    generator = OllamaGenerator("qwen2.5:3b")
    result = generator.generate(client)
    assert isinstance(result, GeneratedContent)
    assert result.key_strengths == ["PLC", "Python"]
