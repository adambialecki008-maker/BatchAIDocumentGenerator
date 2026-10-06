import json
from pathlib import Path

import pandas as pd

from app.models import (
    ClientInput,
    GeneratedContent,
    SkippedRecord,
)
from app.pipeline import (
    REPORT_FILENAME,
    process_client_documents,
    process_clients_documents,
    process_excel_batch,
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
            key_strengths=[
                "PLC",
                "Python",
            ],
            opening_paragraph="Opening",
            fit_paragraph="Fit",
            achievement_paragraph="Achievement",
            closing_paragraph="Closing",
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
            content.opening_paragraph,
            encoding="utf-8",
        )


def test_process_client_documents_generates_and_renders_documents(
    tmp_path,
):
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
        == "Opening"
    )


def test_process_clients_documents_continues_after_client_failure(
    tmp_path,
):
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
                professional_summary=("Summary"),
                key_strengths=["PLC"],
                opening_paragraph=("Opening"),
                fit_paragraph="Fit",
                achievement_paragraph=("Achievement"),
                closing_paragraph=("Closing"),
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

    report_path = tmp_path / REPORT_FILENAME

    assert report_path.exists()

    saved_report = json.loads(
        report_path.read_text(
            encoding="utf-8",
        )
    )

    assert saved_report == {
        "processed": 3,
        "succeeded": 2,
        "failed": 1,
        "skipped": 0,
        "failures": [
            {
                "client_id": "C002",
                "error": "LLM failed",
            }
        ],
        "skipped_records": [],
    }

    assert len(summary.failures) == 1

    assert summary.failures[0].client_id == "C002"

    assert summary.failures[0].error == "LLM failed"


def test_process_clients_documents_includes_skipped_records_in_report(
    tmp_path,
):
    clients = [
        ClientInput(**valid_client_data()),
    ]

    skipped_records = [
        SkippedRecord(
            row_number=3,
            client_id="C002",
            error=("field 'email': " "invalid value"),
        ),
        SkippedRecord(
            row_number=4,
            client_id="C001",
            error=("duplicate client_id"),
        ),
    ]

    summary = process_clients_documents(
        clients,
        FakeGenerator(),
        FakeRenderer(),
        tmp_path,
        skipped_records=(skipped_records),
    )

    assert summary.processed == 3
    assert summary.succeeded == 1
    assert summary.failed == 0
    assert summary.skipped == 2

    assert len(summary.skipped_records) == 2

    report_path = tmp_path / REPORT_FILENAME

    assert report_path.exists()

    saved_report = json.loads(
        report_path.read_text(
            encoding="utf-8",
        )
    )

    assert saved_report["processed"] == 3

    assert saved_report["succeeded"] == 1

    assert saved_report["failed"] == 0

    assert saved_report["skipped"] == 2

    assert saved_report["skipped_records"][0]["client_id"] == "C002"

    assert saved_report["skipped_records"][1]["error"] == "duplicate client_id"


def test_process_excel_batch_loads_clients_and_processes_them(
    tmp_path,
):
    input_path = tmp_path / "clients.xlsx"

    dataframe = pd.DataFrame(
        [
            valid_client_data(),
            {
                **valid_client_data(),
                "client_id": "C002",
                "first_name": "Anna",
            },
        ]
    )

    dataframe.to_excel(
        input_path,
        index=False,
    )

    output_path = tmp_path / "output"

    summary = process_excel_batch(
        input_path,
        FakeGenerator(),
        FakeRenderer(),
        output_path,
    )

    assert summary.processed == 2
    assert summary.succeeded == 2
    assert summary.failed == 0
    assert summary.skipped == 0

    assert (output_path / "C001_Adam_Kowalski" / "resume.docx").exists()

    assert (output_path / "C002_Anna_Kowalski" / "resume.docx").exists()

    assert (output_path / REPORT_FILENAME).exists()
