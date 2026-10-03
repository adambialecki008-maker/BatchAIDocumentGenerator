from docx.document import Document as DocumentObject
from docx import Document
from pathlib import Path
from app.models import ClientInput, GeneratedContent


class DocxRenderer:
    def __init__(
        self,
        resume_template_path: Path,
        cover_letter_template_path: Path,
    ):
        self.resume_template_path = resume_template_path
        self.cover_letter_template_path = cover_letter_template_path

    def render_resume(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        document = Document(self.resume_template_path)
        replace_placeholder(
            document,
            "{{FULL_NAME}}",
            f"{client.first_name} {client.last_name}",
        )
        replace_placeholder(
            document,
            "{{TARGET_ROLE}}",
            client.target_role,
        )
        replace_placeholder(
            document,
            "{{PROFESSIONAL_SUMMARY}}",
            f"{content.professional_summary}",
        )
        replace_list_placeholder(
            document,
            "{{KEY_STRENGTHS}}",
            content.key_strengths,
        )
        document.save(output_path)

    def render_cover_letter(
        self,
        client: ClientInput,
        content: GeneratedContent,
        output_path: Path,
    ) -> None:
        document = Document(self.cover_letter_template_path)
        replace_placeholder(
            document,
            "{{FULL_NAME}}",
            f"{client.first_name} {client.last_name}",
        )
        replace_placeholder(
            document,
            "{{TARGET_ROLE}}",
            client.target_role,
        )
        replace_placeholder(
            document,
            "{{TARGET_COMPANY}}",
            client.target_company,
        )
        replace_placeholder(
            document,
            "{{COVER_LETTER_BODY}}",
            content.cover_letter_body,
        )
        document.save(output_path)


def replace_placeholder(
    document: DocumentObject,
    placeholder: str,
    value: str,
) -> None:
    for paragraph in document.paragraphs:
        if placeholder in paragraph.text:
            paragraph.text = paragraph.text.replace(
                placeholder,
                value,
            )


def replace_list_placeholder(
    document: DocumentObject,
    placeholder: str,
    values: list[str],
) -> None:
    text = "\n".join(f"• {value}" for value in values)
    replace_placeholder(
        document,
        placeholder,
        text,
    )
