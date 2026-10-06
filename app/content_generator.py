import re
from typing import Protocol
import ollama
from app.models import ClientInput, GeneratedContent


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

        content = GeneratedContent.model_validate_json(response.message.content)

        return apply_deterministic_content(
            client,
            content,
        )


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

        content = response.output_parsed

        return apply_deterministic_content(
            client,
            content,
        )


class FakeGenerator:
    def generate(self, client: ClientInput) -> GeneratedContent:
        content = GeneratedContent(
            professional_summary=(
                f"{client.first_name} {client.last_name} is a "
                f"{client.current_role} with {client.years_experience} years "
                f"of experience, currently working at {client.current_company} "
                f"in {client.location}."
            ),
            key_strengths=["placeholder"],
            opening_paragraph="placeholder",
            fit_paragraph="placeholder",
            achievement_paragraph="placeholder",
            closing_paragraph="placeholder",
        )

        return apply_deterministic_content(
            client,
            content,
        )


def build_prompt(client: ClientInput) -> str:
    return f"""
Respond in English only.

Your primary task is to generate a concise professional summary.

STRICT FACTUALITY RULES:
- Use only facts explicitly present in the candidate data.
- Do not infer additional skills, responsibilities, seniority, achievements,
  impact, leadership, or business results.
- Do not invent facts about the target company.
- Preserve skill names exactly as provided.
- Do not add proficiency levels or qualifiers such as proficient, expert,
  advanced, strong, proven, demonstrated, seasoned, highly skilled,
  experienced, or specialized unless explicitly present in the candidate data.
- Do not invent efficiency gains, optimization, troubleshooting,
  data analysis, project management, or similar claims unless explicitly present.
- Do not include the key achievement in the professional summary.
- Do not invent soft skills.
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
- an opening paragraph,
- a fit paragraph,
- an achievement paragraph,
- a closing paragraph.

The professional summary must contain only factual candidate information.

Return each section separately according to the required structured output schema.
"""


def apply_deterministic_content(
    client: ClientInput,
    content: GeneratedContent,
) -> GeneratedContent:
    content.key_strengths = parse_skills(client.skills)

    content.opening_paragraph = (
        f"I am applying for the {client.target_role} position "
        f"at {client.target_company}. "
        f"I have {client.years_experience} years of experience and "
        f"currently work as {client.current_role} at "
        f"{client.current_company}."
    )

    content.fit_paragraph = (
        f"My experience as {client.current_role} at "
        f"{client.current_company}, together with my skills in "
        f"{client.skills}, is relevant to the "
        f"{client.target_role} role."
    )

    content.achievement_paragraph = client.key_achievement

    content.closing_paragraph = (
        "I would welcome the opportunity to discuss " "my application further."
    )

    return content


def parse_skills(skills: str) -> list[str]:
    values = re.split(
        r"[;,]",
        skills,
    )

    return [value.strip() for value in values if value.strip()]
