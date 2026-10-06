from app.content_generator import (
    FakeGenerator,
    OllamaGenerator,
    OpenAIGenerator,
    build_prompt,
)
from app.models import ClientInput, GeneratedContent


def valid_client_data() -> dict:
    return {
        "client_id": "C001",
        "first_name": "Adam",
        "last_name": "Kowalski",
        "email": "adam@example.com",
        "target_role": "Automation Engineer",
        "years_experience": 5,
        "skills": "Python, PLC",
        "current_company": "ABC Automation",
        "current_role": "Automation Engineer",
        "location": "Kraków",
        "key_achievement": "Commissioned production line",
        "tone": "professional",
        "target_company": "Target Company",
    }


class FakeResponses:
    def __init__(self, expected):
        self.expected = expected
        self.kwargs = None

    def parse(self, **kwargs):
        self.kwargs = kwargs

        class Response:
            output_parsed = self.expected

        return Response()


class FakeAPIClient:
    def __init__(self, expected):
        self.responses = FakeResponses(expected)


def test_fake_generator_returns_generated_content():
    client = ClientInput(**valid_client_data())

    generator = FakeGenerator()

    result = generator.generate(client)

    assert isinstance(result, GeneratedContent)

    assert result.key_strengths == [
        "Python",
        "PLC",
    ]

    assert result.achievement_paragraph == ("Commissioned production line")

    assert result.closing_paragraph == (
        "I would welcome the opportunity to discuss " "my application further."
    )


def test_build_prompt_contains_client_data():
    client = ClientInput(**valid_client_data())

    prompt = build_prompt(client)

    assert "Adam" in prompt
    assert "Kowalski" in prompt
    assert "Automation Engineer" in prompt
    assert "Python, PLC" in prompt
    assert "ABC Automation" in prompt
    assert "Kraków" in prompt
    assert "Commissioned production line" in prompt
    assert "Target Company" in prompt


def test_build_prompt_contains_generation_instructions():
    client = ClientInput(**valid_client_data())

    prompt = build_prompt(client).lower()

    assert "professional summary" in prompt
    assert "key strengths" in prompt
    assert "opening paragraph" in prompt
    assert "fit paragraph" in prompt
    assert "achievement paragraph" in prompt
    assert "closing paragraph" in prompt
    assert "candidate data" in prompt


def test_openai_generator_returns_parsed_content():
    expected = GeneratedContent(
        professional_summary="Experienced automation engineer.",
        key_strengths=["Generated skill"],
        opening_paragraph="Generated opening.",
        fit_paragraph="Generated fit.",
        achievement_paragraph="Generated achievement.",
        closing_paragraph="Generated closing.",
    )

    api_client = FakeAPIClient(expected)

    client = ClientInput(**valid_client_data())

    generator = OpenAIGenerator(
        api_client,
        "test-model",
    )

    result = generator.generate(client)

    assert isinstance(result, GeneratedContent)

    assert result.professional_summary == ("Experienced automation engineer.")

    # Deterministic fields override LLM output.
    assert result.key_strengths == [
        "Python",
        "PLC",
    ]

    assert result.achievement_paragraph == ("Commissioned production line")

    assert result.fit_paragraph == (
        "My experience as Automation Engineer at ABC Automation, "
        "together with my skills in Python, PLC, "
        "is relevant to the Automation Engineer role."
    )

    assert result.closing_paragraph == (
        "I would welcome the opportunity to discuss " "my application further."
    )

    assert api_client.responses.kwargs["model"] == "test-model"
    assert api_client.responses.kwargs["text_format"] is GeneratedContent

    assert "Adam" in api_client.responses.kwargs["input"]


def test_ollama_generator_returns_generated_content(monkeypatch):
    expected_json = """
    {
        "professional_summary": "Experienced automation engineer.",
        "key_strengths": ["Generated skill"],
        "opening_paragraph": "Generated opening.",
        "fit_paragraph": "Generated fit.",
        "achievement_paragraph": "Generated achievement.",
        "closing_paragraph": "Generated closing."
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

    generator = OllamaGenerator(
        "qwen2.5:3b",
    )

    result = generator.generate(client)

    assert isinstance(result, GeneratedContent)

    assert result.professional_summary == ("Experienced automation engineer.")

    assert result.key_strengths == [
        "Python",
        "PLC",
    ]

    assert result.achievement_paragraph == ("Commissioned production line")

    assert result.fit_paragraph == (
        "My experience as Automation Engineer at ABC Automation, "
        "together with my skills in Python, PLC, "
        "is relevant to the Automation Engineer role."
    )

    assert result.closing_paragraph == (
        "I would welcome the opportunity to discuss " "my application further."
    )
