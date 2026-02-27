import copy
import pytest

from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app, activities


# keep an original deep copy of activities for resetting
_original_activities = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict before each test."""
    activities.clear()
    activities.update(copy.deepcopy(_original_activities))
    yield


@pytest.fixture

def client():
    return TestClient(app)


# -------------- happy paths --------------

def test_get_activities(client):
    # Arrange: nothing special, client fixture ready

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success(client):
    # Arrange
    email = "test@student.edu"
    activity_name = "Chess Club"

    # Act
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in resp.json()["message"]


def test_signup_duplicate(client):
    # Arrange
    email = "michael@mergington.edu"  # already in initial data
    activity_name = "Chess Club"

    # Act: attempt to sign up again
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 400


def test_signup_not_found(client):
    # Act
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404


# ------------- unregister tests -------------

def test_unregister_success(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    assert email in activities[activity_name]["participants"]

    # Act
    resp = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Unregistered" in resp.json()["message"]


def test_unregister_not_registered(client):
    # Arrange
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"

    # Act
    resp = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert resp.status_code == 400


def test_unregister_not_found(client):
    # Act
    resp = client.post("/activities/Nope/unregister", params={"email": "a@b.com"})

    # Assert
    assert resp.status_code == 404
