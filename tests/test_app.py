"""
Tests for the High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that all expected activities are present"""
        response = client.get("/activities")
        activities = response.json()
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Ensemble",
            "Debate Club",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"{field} not found in {activity_name}"


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_valid_activity_and_email(self):
        """Test successful signup for a valid activity with new email"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_already_registered_email(self):
        """Test that registering the same email twice returns 400"""
        email = "duplicate@mergington.edu"
        activity = "Chess%20Club"
        
        # First signup should succeed
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_updates_participant_list(self):
        """Test that signup actually adds the email to participants"""
        email = "testupdate@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial participants
        response_before = client.get("/activities")
        participants_before = response_before.json()[activity_name]["participants"].copy()
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Check participants were updated
        response_after = client.get("/activities")
        participants_after = response_after.json()[activity_name]["participants"]
        assert email in participants_after
        assert len(participants_after) == len(participants_before) + 1


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        # First, get current participants in an activity
        response = client.get("/activities")
        activity = "Gym Class"
        initial_participants = response.json()[activity]["participants"].copy()
        
        if initial_participants:
            email_to_remove = initial_participants[0]
            
            # Unregister the participant
            response = client.delete(
                f"/activities/{activity}/unregister?email={email_to_remove}"
            )
            assert response.status_code == 200
            assert "Unregistered" in response.json()["message"]
            
            # Verify participant was removed
            response_after = client.get("/activities")
            participants_after = response_after.json()[activity]["participants"]
            assert email_to_remove not in participants_after

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant not in the activity returns 400"""
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_updates_participant_list(self):
        """Test that unregister actually removes the email from participants"""
        # First signup a user
        email = "unregistertest@mergington.edu"
        activity_name = "Tennis Club"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify they're registered
        response = client.get("/activities")
        assert email in response.json()[activity_name]["participants"]
        
        # Unregister them
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify they're no longer registered
        response_after = client.get("/activities")
        assert email not in response_after.json()[activity_name]["participants"]


class TestRootRedirect:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
