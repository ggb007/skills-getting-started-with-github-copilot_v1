from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
BASE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities = deepcopy(BASE_ACTIVITIES)
    yield


def test_get_activities_returns_all_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant():
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up test@mergington.edu for Chess Club"}
    assert "test@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_duplicate_signup_returns_bad_request():
    response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
    assert app_module.activities["Chess Club"]["participants"].count("michael@mergington.edu") == 1


def test_remove_participant_from_activity():
    response = client.delete("/activities/Gym%20Class/participants?email=john@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {"message": "Removed john@mergington.edu from Gym Class"}
    assert "john@mergington.edu" not in app_module.activities["Gym Class"]["participants"]


def test_remove_nonexistent_participant_returns_not_found():
    response = client.delete("/activities/Gym%20Class/participants?email=missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
