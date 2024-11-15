from fastapi.testclient import TestClient
from starlette import status

from ..main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Healthy"}
