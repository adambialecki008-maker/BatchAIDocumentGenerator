from app.models import ClientInput
from app.service import process_client, process_clients
from app.content_generator import FakeGenerator, GeneratedContent


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


def test_process_client_uses_generator():
    client = ClientInput(**valid_client_data())
    generator = FakeGenerator()
    result = process_client(client, generator)
    assert isinstance(result, GeneratedContent)


def test_process_clients_returns_two_generated_results():
    client_data = valid_client_data()
    client_1 = ClientInput(**client_data)
    client_data["client_id"] = "C002"
    client_data["first_name"] = "Jan"
    client_data["last_name"] = "Kowalski"
    client_2 = ClientInput(**client_data)
    generator = FakeGenerator()
    clients = [client_1, client_2]
    results = process_clients(clients, generator)
    assert len(results) == 2
    assert all(isinstance(result, GeneratedContent) for result in results)
