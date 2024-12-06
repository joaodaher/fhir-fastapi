from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from fhir.resources.patient import Patient

from main import app

client = TestClient(app)


@pytest.fixture
def valid_fhir_data():
    return {
        "resourceType": "Patient",
        "id": "example",
        "name": [{"use": "official", "family": "Doe", "given": ["John"]}],
        "gender": "male",
        "birthDate": "2000-01-01",
    }


@pytest.fixture
def invalid_fhir_data():
    return {
        "resourceType": "Patient",
        "name": "Invalid format for name field",  # Should be a list of objects
    }


def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_receive_fhir_resource_success(valid_fhir_data):
    with patch("faststream.rabbit.RabbitBroker.publish") as publish:
        response = client.post("/fhir/Patient", json=valid_fhir_data)

    assert response.status_code == status.HTTP_200_OK
    expected_data = Patient(**valid_fhir_data).dict()
    publish.assert_called_once_with(
        message=expected_data, queue="patient"
    )


def test_receive_fhir_resource_not_found():
    invalid_resource = "InvalidResource"
    with patch("faststream.rabbit.RabbitBroker.publish") as publish:
        response = client.post(f"/fhir/{invalid_resource}", json={})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": f"Resource {invalid_resource} not found"}
    publish.assert_not_called()


def test_receive_fhir_resource_validation_error(invalid_fhir_data):
    with patch("faststream.rabbit.RabbitBroker.publish") as publish:
        response = client.post("/fhir/Patient", json=invalid_fhir_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()
    assert "value is not a valid list" in response.json()["detail"][0]["msg"]
    publish.assert_not_called()
