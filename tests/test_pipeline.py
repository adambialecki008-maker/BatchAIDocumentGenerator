import json
from pathlib import Path

from app.models import ClientInput, GeneratedContent
from app.pipeline import (
    process_client_documents,
    process_clients_documents,
)


def valid_client_data() -> dict:
    return {
        "client_id": "C001",
        "first_name": "Adam",
        "last_name": "Kowalski",
        "email": "adam@example.com",
        "target_role": "Automation Engineer",
        "years_experience": 5,
        "skills": "PLC, Python",
        "current_company": "ABC",
        "current_role": "Automation Engineer",
        "location": "Kraków",
        "key_achievement": "Commissioned production line",
        "tone": "professional",
    }


class FakeGenerator:
    def generate(
        self,
        client: ClientInput,
    ) -> GeneratedContent:
        return GeneratedContent(
            professional_summary="Generated summary",
            key_strengths=["PLC", "Python"],
            cover_letter_body="Generated cover letter",
        )


class FakeRenderer:
    def render_resume(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        output_path.write_text(
            content.professional_summary,
            encoding="utf-8",
        )

    def render_cover_letter(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        output_path.write_text(
            content.cover_letter_body,
            encoding="utf-8",
        )


def test_process_client_documents_generates_and_renders_documents(tmp_path):
    client = ClientInput(**valid_client_data())
    process_client_documents(
        client,
        FakeGenerator(),
        FakeRenderer(),
        tmp_path,
    )

    client_dir = tmp_path / "C001_Adam_Kowalski"

    resume_path = client_dir / "resume.docx"
    cover_letter_path = client_dir / "cover_letter.docx"
    assert resume_path.exists()
    assert cover_letter_path.exists()
    assert (
        resume_path.read_text(
            encoding="utf-8",
        )
        == "Generated summary"
    )

    assert (
        cover_letter_path.read_text(
            encoding="utf-8",
        )
        == "Generated cover letter"
    )


def test_process_clients_documents_continues_after_client_failure(tmp_path):
    clients = [
        ClientInput(**valid_client_data()),
        ClientInput(
            **{
                **valid_client_data(),
                "client_id": "C002",
                "first_name": "Broken",
            }
        ),
        ClientInput(
            **{
                **valid_client_data(),
                "client_id": "C003",
                "first_name": "Anna",
            }
        ),
    ]

    class FailingGenerator:
        def generate(
            self,
            client: ClientInput,
        ) -> GeneratedContent:
            if client.client_id == "C002":
                raise RuntimeError("LLM failed")

            return GeneratedContent(
                professional_summary="Summary",
                key_strengths=["PLC"],
                cover_letter_body="Cover letter",
            )

    summary = process_clients_documents(
        clients,
        FailingGenerator(),
        FakeRenderer(),
        tmp_path,
    )
    assert summary.processed == 3
    assert summary.succeeded == 2
    assert summary.failed == 1
    assert summary.skipped == 0
    assert (tmp_path / "C001_Adam_Kowalski").exists()
    assert not (tmp_path / "C002_Broken_Kowalski").exists()
    assert (tmp_path / "C003_Anna_Kowalski").exists()
    summary_path = tmp_path / "run_summary.json"
    assert summary_path.exists()
    saved_summary = json.loads(
        summary_path.read_text(
            encoding="utf-8",
        )
    )

    assert saved_summary == {
        "processed": 3,
        "succeeded": 2,
        "failed": 1,
        "skipped": 0,
    }
