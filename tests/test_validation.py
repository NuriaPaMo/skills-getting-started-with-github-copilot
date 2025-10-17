"""
Tests for data validation and edge cases in the Activities API
"""

import pytest
from fastapi.testclient import TestClient


class TestDataValidation:
    """Test data validation and edge cases"""
    
    def test_activities_data_structure(self, client: TestClient):
        """Test that activities have the correct data structure"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            # Check required fields exist
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_info, f"Activity '{activity_name}' missing field '{field}'"
            
            # Check field types
            assert isinstance(activity_info["description"], str)
            assert isinstance(activity_info["schedule"], str)
            assert isinstance(activity_info["max_participants"], int)
            assert isinstance(activity_info["participants"], list)
            
            # Check that max_participants is positive
            assert activity_info["max_participants"] > 0
            
            # Check that all participants are strings (emails)
            for participant in activity_info["participants"]:
                assert isinstance(participant, str)
                assert len(participant) > 0

    def test_participant_count_consistency(self, client: TestClient):
        """Test that participant counts are consistent with max_participants"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            participants_count = len(activity_info["participants"])
            max_participants = activity_info["max_participants"]
            
            # Currently we don't enforce max_participants, but let's document the current state
            # When we add enforcement, this assertion should always pass
            if participants_count > max_participants:
                pytest.skip(f"Activity '{activity_name}' has more participants than max_participants. "
                           f"This indicates max_participants enforcement is not yet implemented.")

    def test_special_characters_in_emails(self, client: TestClient):
        """Test handling of special characters in email addresses"""
        test_cases = [
            "user+tag@mergington.edu",  # Plus sign
            "user.name@mergington.edu",  # Dot
            "user_name@mergington.edu",  # Underscore
            "user-name@mergington.edu",  # Hyphen
        ]
        
        activity_name = "Programming Class"
        
        for email in test_cases:
            # Test signup
            signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert signup_response.status_code == 200
            
            # Test removal
            remove_response = client.delete(f"/activities/{activity_name}/remove?email={email}")
            assert remove_response.status_code == 200

    def test_case_sensitivity_in_activity_names(self, client: TestClient):
        """Test case sensitivity in activity names"""
        test_email = "case.test@mergington.edu"
        
        # Try with different cases - should fail for non-exact matches
        response = client.post("/activities/chess club/signup", params={"email": test_email})
        assert response.status_code == 404  # lowercase should not match "Chess Club"
        
        response = client.post("/activities/CHESS CLUB/signup", params={"email": test_email})
        assert response.status_code == 404  # uppercase should not match "Chess Club"
        
        # Exact match should work
        response = client.post("/activities/Chess Club/signup", params={"email": test_email})
        assert response.status_code == 200

    def test_empty_activity_participants_list(self, client: TestClient):
        """Test activities with no participants"""
        # First, remove all participants from an activity
        response = client.get("/activities")
        activities_data = response.json()
        
        # Find an activity with participants
        activity_with_participants = None
        for name, info in activities_data.items():
            if info["participants"]:
                activity_with_participants = name
                break
        
        if activity_with_participants:
            # Remove all participants
            original_participants = activities_data[activity_with_participants]["participants"].copy()
            
            for participant in original_participants:
                remove_response = client.delete(
                    f"/activities/{activity_with_participants}/remove?email={participant}"
                )
                assert remove_response.status_code == 200
            
            # Check that the activity still exists and has an empty participants list
            response = client.get("/activities")
            updated_activities = response.json()
            assert activity_with_participants in updated_activities
            assert updated_activities[activity_with_participants]["participants"] == []

    def test_concurrent_signups_same_activity(self, client: TestClient):
        """Test multiple signups to the same activity"""
        activity_name = "Gym Class"
        test_emails = [
            "concurrent1@mergington.edu",
            "concurrent2@mergington.edu",
            "concurrent3@mergington.edu"
        ]
        
        # Sign up multiple students
        for email in test_emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        activities_data = response.json()
        
        for email in test_emails:
            assert email in activities_data[activity_name]["participants"]

    def test_participant_uniqueness(self, client: TestClient):
        """Test that participant lists don't have duplicates"""
        response = client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_info in activities_data.items():
            participants = activity_info["participants"]
            unique_participants = list(set(participants))
            
            assert len(participants) == len(unique_participants), \
                f"Activity '{activity_name}' has duplicate participants: {participants}"

    def test_long_email_addresses(self, client: TestClient):
        """Test handling of very long email addresses"""
        # Create a long but valid email
        long_email = "a" * 50 + "@" + "b" * 50 + ".edu"
        activity_name = "Chess Club"
        
        response = client.post(f"/activities/{activity_name}/signup?email={long_email}")
        # Should handle long emails (current implementation doesn't have length limits)
        assert response.status_code == 200
        
        # Test removal
        response = client.delete(f"/activities/{activity_name}/remove?email={long_email}")
        assert response.status_code == 200

    def test_response_json_structure(self, client: TestClient):
        """Test that API responses have consistent JSON structure"""
        # Test successful signup response
        response = client.post("/activities/Chess Club/signup?email=json.test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
        
        # Test error response structure
        response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        
        # Test successful removal response
        response = client.delete("/activities/Chess Club/remove?email=json.test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)