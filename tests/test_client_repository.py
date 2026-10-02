from pathlib import Path
from app.client_repository import (
    MissingRequiredColumnsError,
    load_clients,
    _validate_required_columns,
)
import pandas as pd
import pytest

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
