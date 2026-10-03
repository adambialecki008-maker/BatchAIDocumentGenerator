from app.models import ClientInput, GeneratedContent
from app.document_renderer import DocxRenderer
from pathlib import Path


def render_client_documents(
    client: ClientInput,
    content: GeneratedContent,
    renderer: DocxRenderer,
    output_dir: Path,
) -> None:
    client_dir = output_dir / (
        f"{client.client_id}_{client.first_name}_{client.last_name}"
    )
    client_dir.mkdir(parents=True, exist_ok=True)
    resume_output_path = client_dir / "resume.docx"
    cover_letter_output_path = client_dir / "cover_letter.docx"
    renderer.render_resume(client, content, resume_output_path)
    renderer.render_cover_letter(client, content, cover_letter_output_path)
