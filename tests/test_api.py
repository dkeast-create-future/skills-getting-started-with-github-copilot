"""
Tests for High School Management System API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team with games and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "liam@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events for all skill levels",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "william@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, sculpture, and mixed media",
            "schedule": "Wednesdays, 3:00 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debate",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "alexander@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for competitions",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        }
    })
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 8
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_activity_participants(self, client):
        """Test that participants are included in activities"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_successful_signup(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to activity"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]

    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice returns an error"""
        email = "michael@mergington.edu"  # Already registered
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_url_encoding(self, client):
        """Test that activity names with spaces work correctly"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=coder@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_successful_unregister(self, client):
        """Test successfully unregistering from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess%20Club/participants/{email}")
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who isn't registered"""
        response = client.delete(
            "/activities/Chess%20Club/participants/notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_url_encoding(self, client):
        """Test that activity names and emails with special chars work"""
        response = client.delete(
            "/activities/Programming%20Class/participants/emma@mergington.edu"
        )
        assert response.status_code == 200


class TestIntegration:
    """Integration tests for complete workflows"""

    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant is in list
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # Verify participant is removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity]["participants"]

    def test_multiple_signups_different_activities(self, client):
        """Test signing up for multiple activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        activities_list = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities_list:
            assert email in data[activity]["participants"]
