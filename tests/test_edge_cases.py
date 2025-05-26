#!/usr/bin/env python3
"""
Edge Cases and Coverage Tests for Make.com Blueprint Creator

This test suite consolidates all edge cases, error conditions, and specific
coverage targets to achieve comprehensive test coverage. It combines tests
from multiple previous test files into one organized suite.

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock
import os
import json
import requests
from make_blueprint_creator.core.config import MakeConfig
from make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator
from make_blueprint_creator.core.exceptions import MakeBlueprintError
from make_blueprint_creator.cli.examples import (
    example_basic_usage, example_webhook_scenario, example_custom_blueprint,
    example_scenario_cloning, example_blueprint_update, example_using_templates,
    example_bulk_operations, cleanup_scenarios, main as example_main
)
from make_blueprint_creator.utils.team_info import (
    make_api_request, get_user_info, get_organizations, get_user_teams
)
from make_blueprint_creator.cli.team_info import main as get_team_info_main


class TestSpecificMissingLines(unittest.TestCase):
    """Tests specifically targeting the 16 missing lines for maximum coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(api_token="test_token", team_id=123)
        self.creator = MakeBlueprintCreator(self.config)

    # ===== get_team_info.py missing lines =====
    
    @patch('make_blueprint_creator.utils.team_info.requests.get')
    def test_get_team_info_line_70_71(self, mock_get):
        """Test lines 70-71: JSON decode error with accessible text response."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Bad Request")
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Bad request error details"
        mock_get.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            make_api_request("/test", "test_token")

    @patch('make_blueprint_creator.utils.team_info.get_user_info')
    @patch('make_blueprint_creator.utils.team_info.get_organizations')
    @patch('make_blueprint_creator.utils.team_info.get_user_teams')
    @patch('builtins.print')
    def test_get_team_info_line_311(self, mock_print, mock_get_user_teams, mock_get_orgs, mock_get_user_info):
        """Test line 311: No teams found message."""
        mock_get_user_info.return_value = {"id": 123, "name": "Test User", "email": "test@example.com"}
        mock_get_orgs.return_value = [{"id": 1, "name": "Test Org"}]
        mock_get_user_teams.return_value = []  # Empty teams list
        
        with patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'}):
            get_team_info_main()
            
        # Check that the specific print statement was called
        mock_print.assert_any_call("   ❌ No teams found or unable to retrieve teams")

    @patch('make_blueprint_creator.utils.team_info.make_api_request')
    def test_get_team_info_line_340(self, mock_request):
        """Test line 340: Missing authUser key in response."""
        # Return response without 'authUser' key
        mock_request.return_value = {"someOtherKey": "value", "user": {"id": 123}}
        
        result = get_user_info("test_token", "https://test.make.com/api/v2")
        
        # Should return empty dict when 'authUser' key is missing
        self.assertEqual(result, {})

    # ===== example.py missing lines =====
    
    @patch('make_blueprint_creator.cli.examples.create_example_blueprints')
    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_example_lines_387_391(self, mock_creator_class, mock_get_config, mock_create_examples):
        """Test lines 387-391: General exception in example_using_templates."""
        # Set up successful config and creator
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Make create_example_blueprints raise a general Exception (not MakeBlueprintError)
        mock_create_examples.side_effect = Exception("Unexpected error in blueprints")
        
        result = example_using_templates()
        self.assertIsNone(result)

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_example_lines_431_432(self, mock_creator_class, mock_get_config):
        """Test lines 431-432: General exception in example_bulk_operations."""
        # Set up successful config
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Make MakeBlueprintCreator initialization raise a general Exception
        mock_creator_class.side_effect = Exception("Creator initialization failed")
        
        result = example_bulk_operations()
        self.assertIsNone(result)

    # ===== app.py missing lines =====
    
    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_app_line_426(self, mock_request):
        """Test line 426: Re-raise in delete_scenario error handling."""
        # Make _make_request raise MakeBlueprintError
        mock_request.side_effect = MakeBlueprintError("Delete failed")
        
        # This should catch the error, log it, and re-raise it (line 426)
        with self.assertRaises(MakeBlueprintError):
            self.creator.delete_scenario(123)

    @patch('requests.Session.request')
    def test_app_lines_563_564(self, mock_request):
        """Test lines 563-564: Both JSON and text access fail."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        # Make text property raise AttributeError (one of the caught exceptions)
        type(mock_response).text = PropertyMock(side_effect=AttributeError("No text attribute"))
        
        http_error = requests.exceptions.HTTPError("500 Server Error")
        http_error.response = mock_response
        
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        with self.assertRaises(MakeBlueprintError):
            self.creator._make_request('GET', '/test')

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token', 'MAKE_TEAM_ID': '123'})
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    @patch('make_blueprint_creator.core.config.MakeConfig')
    def test_app_line_760(self, mock_config_class, mock_load_dotenv):
        """Test line 760: Re-raise in main function exception handling."""
        # Make MakeConfig raise an exception
        mock_config_class.side_effect = ValueError("Invalid configuration")

        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from app import main
            # This should catch the exception, log it, and re-raise it (line 760)
            with self.assertRaises(ValueError):
                main()

    # ===== example.py line 514 =====
    
    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.cleanup_scenarios')
    def test_example_line_514(self, mock_cleanup, mock_get_config):
        """Test line 514: Cleanup exception in main function."""
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock all example functions to return None (no scenarios created)
        with patch('example.example_basic_usage', return_value=None), \
             patch('example.example_webhook_scenario', return_value=None), \
             patch('example.example_custom_blueprint', return_value=None), \
             patch('example.example_scenario_cloning', return_value=None), \
             patch('example.example_blueprint_update', return_value=None), \
             patch('example.example_using_templates', return_value=None), \
             patch('example.example_bulk_operations', return_value=None):
            
            # Make cleanup_scenarios raise an exception
            mock_cleanup.side_effect = Exception("Cleanup failed")
            
            # This should catch the cleanup exception and log it (line 514)
            example_main()


class TestAdditionalEdgeCases(unittest.TestCase):
    """Additional edge cases for comprehensive coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(api_token="test_token", team_id=123)
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_empty_scenarios_list(self, mock_request):
        """Test handling of empty scenarios list."""
        mock_request.return_value = {"scenarios": []}

        scenarios = self.creator.list_scenarios()

        self.assertEqual(scenarios, [])

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_missing_scenarios_key(self, mock_request):
        """Test handling of response without scenarios key."""
        mock_request.return_value = {}

        scenarios = self.creator.list_scenarios()

        self.assertEqual(scenarios, [])

    def test_create_blueprint_empty_name(self):
        """Test creating blueprint with empty name."""
        blueprint = self.creator.create_simple_blueprint(name="")

        self.assertEqual(blueprint["name"], "")
        self.assertIn("flow", blueprint)

    def test_format_blueprint_empty_dict(self):
        """Test formatting empty blueprint dictionary."""
        formatted = self.creator.format_blueprint_for_api({})

        self.assertEqual(formatted, "{}")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_clone_scenario_no_mappings(self, mock_request):
        """Test cloning scenario without connection/webhook mappings."""
        mock_request.return_value = {"id": 456}

        self.creator.clone_scenario(123, "New Name")

        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertNotIn('account', data)
        self.assertNotIn('hook', data)

    def test_organization_config(self):
        """Test configuration with organization ID."""
        config = MakeConfig(
            api_token="test_token",
            organization_id=789
        )
        creator = MakeBlueprintCreator(config)

        self.assertEqual(creator.config.organization_id, 789)
        self.assertIsNone(creator.config.team_id)

    @patch.dict(os.environ, {}, clear=True)
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    def test_main_missing_api_token(self, mock_load_dotenv):
        """Test main function when API token is missing."""
        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from app import main
            main()
            mock_load_dotenv.assert_called_once()
            mock_logger.error.assert_called_with("MAKE_API_TOKEN environment variable is required")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'}, clear=True)
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    def test_main_missing_team_id(self, mock_load_dotenv):
        """Test main function when team ID and organization ID are missing."""
        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from app import main
            main()
            mock_load_dotenv.assert_called_once()
            mock_logger.error.assert_called_with("Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required")


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True) 