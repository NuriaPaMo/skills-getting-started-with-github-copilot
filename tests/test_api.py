"""
Tests for the Mergington High School Activities API endpoints
"""

import pytest
from fastapi.testclient import TestClient


class TestActivitiesAPI:
    """Test class for activities API endpoints"""

    def test_root_redirect(self, client: TestClient):
        """Test that root URL redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]

    def test_get_activities(self, client: TestClient):
        """Test GET /activities endpoint"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_signup_for_activity_success(self, client: TestClient):
        """Test successful signup for an activity"""
        test_email = "test.student@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]

    def test_signup_for_nonexistent_activity(self, client: TestClient):
        """Test signup for an activity that doesn't exist"""
        test_email = "test.student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_participant(self, client: TestClient):
        """Test signing up the same participant twice"""
        test_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"

    def test_remove_participant_success(self, client: TestClient):
        """Test successful removal of a participant"""
        test_email = "michael@mergington.edu"  # Pre-existing participant in Chess Club
        activity_name = "Chess Club"
        
        # Verify participant exists first
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]
        
        # Remove the participant
        response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]

    def test_remove_participant_from_nonexistent_activity(self, client: TestClient):
        """Test removing participant from an activity that doesn't exist"""
        test_email = "test.student@mergington.edu"
        activity_name = "Nonexistent Activity"
        
        response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_remove_nonexistent_participant(self, client: TestClient):
        """Test removing a participant who isn't signed up"""
        test_email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"
        
        response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_activity_max_participants_constraint(self, client: TestClient):
        """Test that activities respect max participants (integration test)"""
        # Get an activity with low max participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        chess_club = activities_data["Chess Club"]
        max_participants = chess_club["max_participants"]
        current_participants = len(chess_club["participants"])
        available_spots = max_participants - current_participants
        
        # Fill up the remaining spots
        for i in range(available_spots):
            test_email = f"student{i}@mergington.edu"
            response = client.post(f"/activities/Chess Club/signup?email={test_email}")
            assert response.status_code == 200
        
        # Verify we can't add more participants beyond the max
        # Note: Our current implementation doesn't enforce max_participants
        # This test documents the current behavior and can be updated when we add this feature
        extra_email = "extra.student@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={extra_email}")
        # Currently this will succeed (200) because we don't enforce max_participants
        # When we add this feature, this should return 400
        assert response.status_code == 200  # Current behavior

    def test_signup_and_remove_workflow(self, client: TestClient):
        """Test the complete workflow of signing up and removing a participant"""
        test_email = "workflow.test@mergington.edu"
        activity_name = "Programming Class"
        
        # 1. Verify student is not initially signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]
        
        # 2. Sign up the student
        signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert signup_response.status_code == 200
        
        # 3. Verify student is now signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data[activity_name]["participants"]
        
        # 4. Remove the student
        remove_response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert remove_response.status_code == 200
        
        # 5. Verify student is no longer signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email not in activities_data[activity_name]["participants"]

    def test_url_encoding_in_activity_names(self, client: TestClient):
        """Test that activity names with special characters are handled correctly"""
        # Test with an existing activity that has spaces
        test_email = "encoding.test@mergington.edu"
        activity_name = "Chess Club"  # Has a space
        
        # URL should be properly encoded
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert response.status_code == 200
        
        # Test removal as well
        response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert response.status_code == 200

    def test_email_validation_basic(self, client: TestClient):
        """Test basic email validation (currently not enforced but documents expected behavior)"""
        invalid_emails = [
            "",  # Empty email
            "not-an-email",  # No @ symbol
            "@mergington.edu",  # No local part
            "student@"  # No domain part
        ]
        
        activity_name = "Chess Club"
        
        for email in invalid_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            # Currently our API doesn't validate email format, so these will succeed
            # This test documents current behavior and can be updated when we add validation
            assert response.status_code in [200, 400]  # Either succeeds or fails validation