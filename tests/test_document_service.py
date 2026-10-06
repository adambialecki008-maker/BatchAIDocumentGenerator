from pathlib import Path

from app.document_service import render_client_documents
from app.models import ClientInput, GeneratedContent


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


class FakeRenderer:
    def render_resume(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        output_path.write_text("resume")

    def render_cover_letter(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        output_path.write_text("cover letter")


def test_render_client_documents_creates_client_directory_and_files(tmp_path):
    client = ClientInput(**valid_client_data())

    content = GeneratedContent(
        professional_summary="Summary",
        key_strengths=["PLC", "Python"],
        opening_paragraph="Opening",
        fit_paragraph="Fit",
        achievement_paragraph="Achievement",
        closing_paragraph="Closing",
    )

    renderer = FakeRenderer()

    render_client_documents(
        client,
        content,
        renderer,
        tmp_path,
    )

    client_dir = tmp_path / "C001_Adam_Kowalski"

    assert client_dir.exists()
    assert (client_dir / "resume.docx").exists()
    assert (client_dir / "cover_letter.docx").exists()
