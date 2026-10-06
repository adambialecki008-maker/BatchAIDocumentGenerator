from pathlib import Path

from app.content_generator import OllamaGenerator
from app.document_renderer import DocxRenderer
from app.pipeline import process_excel_batch


def main() -> None:
    input_path = Path("fixtures/clients.xlsx")
    output_dir = Path("output")
    renderer = DocxRenderer(
        Path("templates/resume_template.docx"),
        Path("templates/cover_letter_template.docx"),
    )
    generator = OllamaGenerator(
        "qwen2.5:3b",
    )
    summary = process_excel_batch(
        input_path,
        generator,
        renderer,
        output_dir,
    )
    print(summary.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
