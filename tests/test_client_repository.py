from app.client_repository import (
    InvalidClientRecordError,
    MissingRequiredColumnsError,
    load_clients,
    _validate_required_columns,
)
import pandas as pd
import pytest
from pathlib import Path

path = Path("fixtures/clients.xlsx")


def test_load_clients_returns_expected_records():
    clients = load_clients(path)
    assert len(clients) == 12
    assert clients[0].client_id == "C001"
    assert clients[0].target_role == "Automation Engineer"


def test_validate_required_columns_raises_when_header_is_missing(tmp_path):
    dataframe = pd.DataFrame(
        {
            "client_id": ["C001"],
            "first_name": ["Anna"],
        }
    )

    path = tmp_path / "clients.xlsx"
    dataframe.to_excel(path, index=False)

    dataframe = pd.read_excel(path)

    with pytest.raises(MissingRequiredColumnsError):
        _validate_required_columns(dataframe)


def test_load_clients_reports_excel_row_and_field_for_invalid_record(tmp_path):
    dataframe = pd.DataFrame(
        [
            {
                "client_id": "C001",
                "first_name": "Anna",
                "last_name": "Kowalska",
                "email": "anna@example.com",
                "target_role": "Automation Engineer",
                "years_experience": 3,
                "skills": "PLC, Python",
                "current_company": "ABC",
                "current_role": "Automation Engineer",
                "location": "Kraków",
                "key_achievement": "Commissioned production line",
                "tone": "professional",
            },
            {
                "client_id": "C002",
                "first_name": "Jan",
                "last_name": "Nowak",
                "email": "jan@example.com",
                "target_role": "Python Developer",
                "years_experience": 2,
                "skills": "Python",
                "current_company": "XYZ",
                "current_role": "Developer",
                "location": "Warszawa",
                "key_achievement": "Built automation tool",
                "tone": "wrong",
            },
        ]
    )
    path = tmp_path / "clients.xlsx"
    dataframe.to_excel(path, index=False)
    with pytest.raises(InvalidClientRecordError) as exc_info:
        load_clients(path)
    message = str(exc_info.value)
    assert "Excel row 3" in message
    assert "tone" in message
