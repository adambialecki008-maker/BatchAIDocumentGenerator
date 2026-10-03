from app.models import ClientInput, GeneratedContent
from typing import Protocol
import ollama


class ContentGenerator(Protocol):
    def generate(self, client: ClientInput) -> GeneratedContent: ...


class OllamaGenerator:
    def __init__(self, model: str):
        self.model = model

    def generate(self, client: ClientInput) -> GeneratedContent:
        prompt = build_prompt(client)
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            format=GeneratedContent.model_json_schema(),
            options={
                "temperature": 0,
            },
        )
        return GeneratedContent.model_validate_json(response.message.content)


class OpenAIGenerator:
    def __init__(self, api_client, model: str):
        self.api_client = api_client
        self.model = model

    def generate(self, client: ClientInput) -> GeneratedContent:
        prompt = build_prompt(client)
        response = self.api_client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=GeneratedContent,
        )
        return response.output_parsed


class FakeGenerator:
    def generate(self, client: ClientInput) -> GeneratedContent:
        return GeneratedContent(
            professional_summary=(
                f"{client.first_name} {client.last_name} is an experienced "
                f"{client.target_role}"
            ),
            key_strengths=(
                [
                    client.skills,
                    client.key_achievement,
                ]
            ),
            cover_letter_body=(
                f"I am intereseted in {client.target_role} position"
                f"at {client.target_company}"
            ),
        )


def build_prompt(client: ClientInput) -> str:
    return f"""
        Respond in English only.

        STRICT FACTUALITY RULES:
        - Use only facts explicitly present in the candidate data.
        - Do not infer additional skills, responsibilities, seniority, achievements, impact, leadership, or business results.
        - Do not convert singular achievements into plural achievements.
        - Do not invent facts about the target company.
        - Preserve skill names exactly as provided.
        - Do not add proficiency levels or qualifiers such as proficient, expert, advanced, strong, proven, demonstrated, experienced, or specialized unless explicitly present in the candidate data.
        - Do not invent efficiency gains, optimization, troubleshooting, data analysis, project management, or similar claims unless explicitly present.
        - If a claim cannot be directly traced to the candidate data, omit it.

        Candidate data:
        First name: {client.first_name}
        Last name: {client.last_name}
        Target role: {client.target_role}
        Years of experience: {client.years_experience}
        Skills: {client.skills}
        Current company: {client.current_company}
        Current role: {client.current_role}
        Location: {client.location}
        Key achievement: {client.key_achievement}
        Tone: {client.tone}
        Target company: {client.target_company}

        Generate:
        - a concise professional summary,
        - 3 to 5 key strengths,
        - a professional cover letter body.

        Base every statement only on the candidate data above.
        """
