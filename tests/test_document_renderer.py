from docx import Document

from app.document_renderer import replace_placeholder, DocxRenderer
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


def test_replace_placeholder_replaces_full_name():
    document = Document()
    document.add_paragraph("{{FULL_NAME}}")

    replace_placeholder(
        document,
        "{{FULL_NAME}}",
        "Adam Kowalski",
    )
    assert document.paragraphs[0].text == "Adam Kowalski"


def test_render_resume_replaces_placeholders_and_saves_file(tmp_path):
    template_path = tmp_path / "resume_template.docx"
    output_path = tmp_path / "resume.docx"
    cover_template_path = tmp_path / "cover_letter_template.docx"
    template = Document()
    template.add_paragraph("{{FULL_NAME}}")
    template.add_paragraph("{{TARGET_ROLE}}")
    template.add_paragraph("{{PROFESSIONAL_SUMMARY}}")
    template.add_paragraph("{{KEY_STRENGTHS}}")
    template.save(template_path)
    client = ClientInput(
        client_id="C001",
        first_name="Adam",
        last_name="Kowalski",
        email="adam@example.com",
        target_role="Automation Engineer",
        years_experience=5,
        skills="PLC, Python",
        current_company="ABC",
        current_role="Automation Engineer",
        location="Kraków",
        key_achievement="Commissioned production line",
        tone="professional",
    )
    content = GeneratedContent(
        professional_summary="Automation Engineer with 5 years of experience.",
        key_strengths=["PLC", "Python"],
        cover_letter_body="Cover letter body.",
    )
    renderer = DocxRenderer(template_path, cover_template_path)
    renderer.render_resume(
        client,
        content,
        output_path,
    )
    assert output_path.exists()
    rendered_document = Document(output_path)
    paragraphs = [paragraph.text for paragraph in rendered_document.paragraphs]
    assert "Adam Kowalski" in paragraphs
    assert "Automation Engineer" in paragraphs
    assert "Automation Engineer with 5 years of experience." in paragraphs
    assert "• PLC\n• Python" in paragraphs


def test_render_cover_letter_replaces_placeholders_and_saves_file(tmp_path):
    resume_template_path = tmp_path / "resume_template.docx"
    cover_template_path = tmp_path / "cover_letter_template.docx"
    output_path = tmp_path / "cover_letter.docx"

    Document().save(resume_template_path)

    template = Document()
    template.add_paragraph("{{FULL_NAME}}")
    template.add_paragraph("{{TARGET_ROLE}}")
    template.add_paragraph("{{TARGET_COMPANY}}")
    template.add_paragraph("{{COVER_LETTER_BODY}}")
    template.save(cover_template_path)
    client = ClientInput(**valid_client_data())
    content = GeneratedContent(
        professional_summary="Summary",
        key_strengths=["PLC", "Python"],
        cover_letter_body="I am interested in this position.",
    )
    renderer = DocxRenderer(
        resume_template_path,
        cover_template_path,
    )
    renderer.render_cover_letter(
        client,
        content,
        output_path,
    )
    assert output_path.exists()
    document = Document(output_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Adam Kowalski" in text
    assert "Automation Engineer" in text
    assert "Your organization" in text
    assert "I am interested in this position." in text
