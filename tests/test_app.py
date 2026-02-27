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
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # verify some known activities exist
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success(client):
    email = "test@student.edu"
    activity_name = "Chess Club"
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert "Signed up" in resp.json()["message"]


def test_signup_duplicate(client):
    email = "michael@mergington.edu"  # already in initial data
    activity_name = "Chess Club"
    # first attempt (already present) should fail
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert resp.status_code == 400


def test_signup_not_found(client):
    resp = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


# ------------- unregister tests -------------

def test_unregister_success(client):
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    # ensure it's there to begin with
    assert email in activities[activity_name]["participants"]
    resp = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert "Unregistered" in resp.json()["message"]


def test_unregister_not_registered(client):
    email = "nobody@mergington.edu"
    activity_name = "Chess Club"
    resp = client.post(f"/activities/{activity_name}/unregister", params={"email": email})
    assert resp.status_code == 400


def test_unregister_not_found(client):
    resp = client.post("/activities/Nope/unregister", params={"email": "a@b.com"})
    assert resp.status_code == 404
