#!/usr/bin/env python3
"""
Unit tests for get_team_info.py

This test suite provides comprehensive coverage of the Make.com team and organization
ID retrieval functionality using mocked API responses.

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
from unittest.mock import patch, Mock, call
import json
import os
import requests
from make_blueprint_creator.utils.team_info import (
    make_api_request,
    get_teams_for_organization,
    get_user_teams,
    get_organizations,
    get_user_info
)
from make_blueprint_creator.cli.team_info import main


class TestMakeApiRequest(unittest.TestCase):
    """Test cases for make_api_request function."""

    @patch('make_blueprint_creator.utils.team_info.requests.get')
    def test_successful_api_request(self, mock_get):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_get.return_value = mock_response

        result = make_api_request("/test", "test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, {"success": True, "data": "test"})
        mock_get.assert_called_once_with(
            "https://test.make.com/api/v2/test",
            headers={
                'Authorization': 'Token test_token',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )

    @patch('make_blueprint_creator.utils.team_info.requests.get')
    def test_api_request_with_http_error(self, mock_get):
        """Test API request with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_response.json.return_value = {"error": "Not found"}
        mock_get.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            make_api_request("/test", "test_token")

    @patch('make_blueprint_creator.utils.team_info.requests.get')
    def test_api_request_with_connection_error(self, mock_get):
        """Test API request with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with self.assertRaises(requests.exceptions.ConnectionError):
            make_api_request("/test", "test_token")

    @patch('make_blueprint_creator.utils.team_info.requests.get')
    def test_api_request_strips_leading_slash(self, mock_get):
        """Test that leading slash is properly handled in endpoint."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"success": True}
        mock_get.return_value = mock_response

        make_api_request("/test", "test_token", "https://test.make.com/api/v2")

        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://test.make.com/api/v2/test")


class TestGetTeamsForOrganization(unittest.TestCase):
    """Test cases for get_teams_for_organization function."""

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_successful_teams_retrieval(self, mock_request):
        """Test successful teams retrieval for organization."""
        mock_teams = [
            {"id": 1, "name": "Team 1", "organizationId": 123},
            {"id": 2, "name": "Team 2", "organizationId": 123}
        ]
        mock_request.return_value = {"teams": mock_teams}

        result = get_teams_for_organization("test_token", "https://test.make.com/api/v2", 123)

        self.assertEqual(result, mock_teams)
        mock_request.assert_called_once_with(
            '/teams?organizationId=123',
            "test_token",
            "https://test.make.com/api/v2"
        )

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_teams_retrieval_with_api_error(self, mock_request):
        """Test teams retrieval with API error."""
        mock_request.side_effect = Exception("API Error")

        result = get_teams_for_organization("test_token", "https://test.make.com/api/v2", 123)

        self.assertEqual(result, [])

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_teams_retrieval_empty_response(self, mock_request):
        """Test teams retrieval with empty response."""
        mock_request.return_value = {}

        result = get_teams_for_organization("test_token", "https://test.make.com/api/v2", 123)

        self.assertEqual(result, [])


class TestGetUserInfo(unittest.TestCase):
    """Test cases for get_user_info function."""

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_successful_user_info_retrieval(self, mock_request):
        """Test successful user info retrieval."""
        mock_user = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com"
        }
        mock_request.return_value = {"authUser": mock_user}

        result = get_user_info("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, mock_user)
        mock_request.assert_called_once_with(
            '/users/me',
            "test_token",
            "https://test.make.com/api/v2"
        )

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_user_info_retrieval_with_api_error(self, mock_request):
        """Test user info retrieval with API error."""
        mock_request.side_effect = Exception("API Error")

        result = get_user_info("test_token", "https://test.make.com/api/v2")

        self.assertIsNone(result)

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_user_info_retrieval_empty_response(self, mock_request):
        """Test user info retrieval with empty response."""
        mock_request.return_value = {}

        result = get_user_info("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, {})


class TestGetOrganizations(unittest.TestCase):
    """Test cases for get_organizations function."""

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_successful_organizations_retrieval(self, mock_request):
        """Test successful organizations retrieval."""
        mock_orgs = [
            {"id": 1, "name": "Org 1", "role": "admin"},
            {"id": 2, "name": "Org 2", "role": "member"}
        ]
        mock_request.return_value = {"organizations": mock_orgs}

        result = get_organizations("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, mock_orgs)
        mock_request.assert_called_once_with(
            '/organizations',
            "test_token",
            "https://test.make.com/api/v2"
        )

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_organizations_retrieval_with_api_error(self, mock_request):
        """Test organizations retrieval with API error."""
        mock_request.side_effect = Exception("API Error")

        result = get_organizations("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, [])


class TestGetUserTeams(unittest.TestCase):
    """Test cases for get_user_teams function."""

    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    @patch('make_blueprint_creator.utils.team_info.get_teams_for_organization')
    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_successful_user_teams_retrieval(self, mock_request, mock_get_teams, mock_get_orgs, mock_get_user):
        """Test successful user teams retrieval."""
        # Mock user info
        mock_get_user.return_value = {"id": 123, "name": "Test User"}
        
        # Mock organizations
        mock_get_orgs.return_value = [{"id": 1, "name": "Test Org"}]
        
        # Mock teams for organization
        mock_get_teams.return_value = [
            {"id": 10, "name": "Team 1", "organizationId": 1},
            {"id": 11, "name": "Team 2", "organizationId": 1}
        ]
        
        # Mock team role requests
        mock_request.side_effect = [
            {"userTeamRole": {"usersRoleId": 1, "changeable": True}},  # User has role in team 10
            Exception("404 Not Found")  # User doesn't have role in team 11
        ]

        result = get_user_teams("test_token", "https://test.make.com/api/v2")

        # Should return only the team where user has a role
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 10)
        self.assertEqual(result[0]["userRole"], 1)
        self.assertTrue(result[0]["changeable"])

    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    def test_user_teams_no_user_id(self, mock_get_user):
        """Test user teams retrieval when user ID cannot be obtained."""
        mock_get_user.return_value = None

        result = get_user_teams("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, [])

    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    def test_user_teams_no_organizations(self, mock_get_orgs, mock_get_user):
        """Test user teams retrieval when no organizations found."""
        mock_get_user.return_value = {"id": 123, "name": "Test User"}
        mock_get_orgs.return_value = []

        result = get_user_teams("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, [])

    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    def test_user_teams_with_exception(self, mock_get_user):
        """Test user teams retrieval with exception."""
        mock_get_user.side_effect = Exception("API Error")

        result = get_user_teams("test_token", "https://test.make.com/api/v2")

        self.assertEqual(result, [])


class TestMainFunction(unittest.TestCase):
    """Test cases for main function."""

    @patch.dict(os.environ, {}, clear=True)
    @patch('make_blueprint_creator.cli.team_info.load_dotenv')
    def test_main_missing_api_token(self, mock_load_dotenv):
        """Test main function when API token is missing."""
        with patch('builtins.print') as mock_print:
            main()
            mock_load_dotenv.assert_called_once()
            # Check that error message was printed
            mock_print.assert_any_call("❌ Error: MAKE_API_TOKEN environment variable is required")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'})
    @patch('make_blueprint_creator.cli.team_info.load_dotenv')
    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    @patch('make_blueprint_creator.utils.team_info.get_user_teams')
    @patch('make_blueprint_creator.utils.team_info.get_teams_for_organization')
    def test_main_successful_execution(self, mock_get_teams_org, mock_get_user_teams, 
                                     mock_get_orgs, mock_get_user_info, mock_load_dotenv):
        """Test main function successful execution."""
        # Mock all the API responses
        mock_get_user_info.return_value = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com"
        }
        
        mock_get_orgs.return_value = [
            {"id": 1, "name": "Test Org", "role": "admin", "status": "active"}
        ]
        
        mock_get_user_teams.return_value = [
            {"id": 10, "name": "Test Team", "userRole": 1, "organizationId": 1}
        ]
        
        mock_get_teams_org.return_value = [
            {"id": 10, "name": "Test Team"}
        ]

        with patch('builtins.print') as mock_print:
            main()
            
            # Verify load_dotenv was called
            mock_load_dotenv.assert_called_once()
            
            # Check that success messages were printed
            mock_print.assert_any_call("   ✅ User: Test User (test@example.com)")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'})
    @patch('make_blueprint_creator.cli.team_info.load_dotenv')
    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    @patch('make_blueprint_creator.utils.team_info.get_user_teams')
    def test_main_with_no_data(self, mock_get_user_teams, mock_get_orgs, 
                              mock_get_user_info, mock_load_dotenv):
        """Test main function when no data is returned."""
        # Mock empty responses
        mock_get_user_info.return_value = None
        mock_get_orgs.return_value = []
        mock_get_user_teams.return_value = []

        with patch('builtins.print') as mock_print:
            main()
            
            # Check that appropriate messages were printed
            mock_print.assert_any_call("   ❌ No organizations found or unable to retrieve organizations")
            mock_print.assert_any_call("   ❌ No teams found or unable to retrieve teams")

    @patch.dict(os.environ, {
        'MAKE_API_TOKEN': 'test_token',
        'MAKE_API_BASE_URL': 'https://custom.make.com/api/v2'
    })
    @patch('make_blueprint_creator.cli.team_info.load_dotenv')
    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    @patch('make_blueprint_creator.utils.team_info.get_user_teams')
    def test_main_with_custom_base_url(self, mock_get_user_teams, mock_get_orgs, 
                                      mock_get_user_info, mock_load_dotenv):
        """Test main function with custom base URL."""
        mock_get_user_info.return_value = {"id": 123, "name": "Test User"}
        mock_get_orgs.return_value = []
        mock_get_user_teams.return_value = []

        with patch('builtins.print') as mock_print:
            main()
            
            # Check that custom base URL was used
            mock_print.assert_any_call("🌍 Using API endpoint: https://custom.make.com/api/v2")


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True) 