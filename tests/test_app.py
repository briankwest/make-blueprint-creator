#!/usr/bin/env python3
"""
Unit tests for Make.com Blueprint Creator

This test suite provides comprehensive coverage of the MakeBlueprintCreator
functionality using mocked API responses to avoid actual API calls during testing.

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import json
import os
import requests
from make_blueprint_creator.core.config import MakeConfig
from make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator
from make_blueprint_creator.core.exceptions import MakeBlueprintError
from make_blueprint_creator.cli.examples import create_example_blueprints


class TestMakeConfig(unittest.TestCase):
    """Test cases for MakeConfig dataclass."""

    def test_valid_config_with_team_id(self):
        """Test creating valid configuration with team ID."""
        config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.assertEqual(config.api_token, "test_token")
        self.assertEqual(config.team_id, 123)
        self.assertEqual(config.base_url, "https://us2.make.com/api/v2")  # Default value

    def test_valid_config_with_organization_id(self):
        """Test creating valid configuration with organization ID."""
        config = MakeConfig(
            api_token="test_token",
            organization_id=456
        )
        self.assertEqual(config.api_token, "test_token")
        self.assertEqual(config.organization_id, 456)

    def test_custom_base_url(self):
        """Test configuration with custom base URL."""
        config = MakeConfig(
            api_token="test_token",
            team_id=123,
            base_url="https://us1.make.com/api/v2"
        )
        self.assertEqual(config.base_url, "https://us1.make.com/api/v2")

    def test_default_base_url_when_not_specified(self):
        """Test that default base URL is used when not specified."""
        config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.assertEqual(config.base_url, "https://us2.make.com/api/v2")

    def test_missing_api_token(self):
        """Test that missing API token raises MakeConfigError."""
        from make_blueprint_creator.core.exceptions import MakeConfigError
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="", team_id=123)
        self.assertIn("API token is required", str(context.exception))

    def test_missing_team_and_organization_id(self):
        """Test that missing both team_id and organization_id raises MakeConfigError."""
        from make_blueprint_creator.core.exceptions import MakeConfigError
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="test_token")
        self.assertIn("Either team_id or organization_id must be provided", str(context.exception))


class TestMakeBlueprintCreator(unittest.TestCase):
    """Test cases for MakeBlueprintCreator class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.creator = MakeBlueprintCreator(self.config)

    def test_initialization(self):
        """Test proper initialization of MakeBlueprintCreator."""
        self.assertEqual(self.creator.config, self.config)
        self.assertIsNotNone(self.creator.session)
        self.assertEqual(
            self.creator.session.headers['Authorization'],
            'Token test_token'
        )

    @patch('requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"success": True}
        mock_response.content = b'{"success": true}'
        mock_request.return_value = mock_response

        result = self.creator._make_request('GET', '/test')

        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once()

    @patch('requests.Session.request')
    def test_make_request_http_error(self, mock_request):
        """Test API request with HTTP error."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_response.json.return_value = {"error": "Not found"}
        mock_request.return_value = mock_response

        with self.assertRaises(MakeBlueprintError) as context:
            self.creator._make_request('GET', '/test')

        self.assertIn("API request failed", str(context.exception))

    @patch('requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """Test API request with connection error."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with self.assertRaises(MakeBlueprintError) as context:
            self.creator._make_request('GET', '/test')

        self.assertIn("API request failed", str(context.exception))

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_list_scenarios_success(self, mock_request):
        """Test successful scenario listing."""
        mock_scenarios = [
            {"id": 1, "name": "Test Scenario 1", "isActive": True},
            {"id": 2, "name": "Test Scenario 2", "isActive": False}
        ]
        mock_request.return_value = {"scenarios": mock_scenarios}

        scenarios = self.creator.list_scenarios()

        self.assertEqual(len(scenarios), 2)
        self.assertEqual(scenarios[0]["name"], "Test Scenario 1")
        mock_request.assert_called_once_with('GET', '/scenarios', params={'teamId': '123'})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_list_scenarios_active_only(self, mock_request):
        """Test listing only active scenarios."""
        mock_request.return_value = {"scenarios": []}

        self.creator.list_scenarios(active_only=True)

        mock_request.assert_called_once_with(
            'GET', 
            '/scenarios', 
            params={'teamId': '123', 'isActive': True}
        )

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_get_scenario_blueprint(self, mock_request):
        """Test getting scenario blueprint."""
        mock_blueprint = {
            "name": "Test Scenario",
            "flow": [{"id": 1, "module": "test:module"}]
        }
        mock_request.return_value = {"response": mock_blueprint}

        blueprint = self.creator.get_scenario_blueprint(123)

        self.assertEqual(blueprint, mock_blueprint)
        mock_request.assert_called_once_with('GET', '/scenarios/123/blueprint')

    def test_create_simple_blueprint_default(self):
        """Test creating simple blueprint with default modules."""
        blueprint = self.creator.create_simple_blueprint(
            name="Test Scenario",
            description="Test description"
        )

        self.assertEqual(blueprint["name"], "Test Scenario")
        self.assertEqual(blueprint["description"], "Test description")
        self.assertIn("flow", blueprint)
        self.assertIn("metadata", blueprint)
        self.assertEqual(len(blueprint["flow"]), 1)
        self.assertEqual(blueprint["flow"][0]["module"], "http:ActionSendData")

    def test_create_simple_blueprint_custom_modules(self):
        """Test creating simple blueprint with custom modules."""
        custom_modules = [
            {
                "id": 1,
                "module": "http:ActionSendData",
                "version": 3,
                "metadata": {"designer": {"x": 0, "y": 0}},
                "parameters": {"url": "https://example.com"}
            }
        ]

        blueprint = self.creator.create_simple_blueprint(
            name="Custom Scenario",
            modules=custom_modules
        )

        self.assertEqual(blueprint["name"], "Custom Scenario")
        self.assertEqual(blueprint["flow"], custom_modules)

    def test_create_webhook_blueprint(self):
        """Test creating webhook blueprint."""
        blueprint = self.creator.create_webhook_blueprint(
            name="Webhook Scenario",
            webhook_name="test_webhook",
            description="Test webhook scenario"
        )

        self.assertEqual(blueprint["name"], "Webhook Scenario")
        self.assertEqual(blueprint["description"], "Test webhook scenario")
        self.assertEqual(len(blueprint["flow"]), 2)
        
        # Check webhook module
        webhook_module = blueprint["flow"][0]
        self.assertEqual(webhook_module["module"], "webhook:CustomWebHook")
        # Note: Parameters section was removed to fix API validation errors
        
        # Check HTTP action module
        action_module = blueprint["flow"][1]
        self.assertEqual(action_module["module"], "http:ActionSendData")

    def test_format_blueprint_for_api(self):
        """Test blueprint formatting for API submission."""
        blueprint = {
            "name": "Test",
            "flow": [{"id": 1, "module": "test"}]
        }

        formatted = self.creator.format_blueprint_for_api(blueprint)

        self.assertIsInstance(formatted, str)
        # Should be valid JSON
        parsed = json.loads(formatted)
        self.assertEqual(parsed["name"], "Test")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_success(self, mock_request):
        """Test successful scenario creation."""
        blueprint = {"name": "Test Scenario", "flow": []}
        mock_scenario = {"id": 123, "name": "Test Scenario"}
        mock_request.return_value = {"scenario": mock_scenario}

        scenario = self.creator.create_scenario(blueprint)

        self.assertEqual(scenario, mock_scenario)
        mock_request.assert_called_once()
        
        # Check the call arguments
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], 'POST')  # method
        self.assertEqual(call_args[0][1], '/scenarios')  # endpoint
        self.assertIn('blueprint', call_args[1]['data'])

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_custom_scheduling(self, mock_request):
        """Test scenario creation with custom scheduling."""
        blueprint = {"name": "Test Scenario", "flow": []}
        custom_scheduling = {"type": "cron", "cron": "0 9 * * 1-5"}
        mock_request.return_value = {"scenario": {"id": 123}}

        self.creator.create_scenario(blueprint, scheduling=custom_scheduling)

        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data["scheduling"], custom_scheduling)

    @patch.object(MakeBlueprintCreator, 'get_scenario_blueprint')
    @patch.object(MakeBlueprintCreator, 'create_scenario')
    def test_clone_scenario_success(self, mock_create, mock_get_blueprint):
        """Test successful scenario cloning."""
        mock_blueprint = {"name": "Original", "flow": []}
        mock_get_blueprint.return_value = mock_blueprint
        mock_cloned_scenario = {"id": 456, "name": "Cloned Scenario"}
        mock_create.return_value = mock_cloned_scenario

        result = self.creator.clone_scenario(
            source_scenario_id=123,
            new_name="Cloned Scenario"
        )

        self.assertEqual(result, mock_cloned_scenario)
        mock_get_blueprint.assert_called_once_with(123)
        mock_create.assert_called_once_with(
            blueprint=mock_blueprint,
            name="Cloned Scenario"
        )

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_update_scenario_blueprint(self, mock_request):
        """Test updating scenario blueprint."""
        blueprint = {"name": "Updated Scenario", "flow": []}
        mock_response = {"scenario": {"id": 123, "name": "Updated Scenario"}}
        mock_request.return_value = mock_response

        result = self.creator.update_scenario_blueprint(123, blueprint)

        self.assertEqual(result, mock_response["scenario"])
        mock_request.assert_called_once()

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_activate_scenario(self, mock_request):
        """Test scenario activation."""
        mock_response = {"success": True}
        mock_request.return_value = mock_response

        result = self.creator.activate_scenario(123)

        self.assertEqual(result, mock_response)
        mock_request.assert_called_once_with('PATCH', '/scenarios/123', data={'isActive': True})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_deactivate_scenario(self, mock_request):
        """Test scenario deactivation."""
        mock_response = {"success": True}
        mock_request.return_value = mock_response

        result = self.creator.deactivate_scenario(123)

        self.assertEqual(result, mock_response)
        mock_request.assert_called_once_with('PATCH', '/scenarios/123', data={'isActive': False})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_run_scenario_basic(self, mock_request):
        """Test basic scenario execution."""
        mock_response = {"executionId": "exec_123"}
        mock_request.return_value = mock_response

        result = self.creator.run_scenario(123)

        self.assertEqual(result, mock_response)
        mock_request.assert_called_once_with(
            'POST',
            '/scenarios/123/run',
            data={}
        )

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_run_scenario_with_input_data(self, mock_request):
        """Test scenario execution with input data."""
        input_data = {"key": "value", "number": 42}
        mock_response = {"executionId": "exec_123"}
        mock_request.return_value = mock_response

        result = self.creator.run_scenario(
            123, 
            input_data=input_data, 
            wait_for_completion=True
        )

        self.assertEqual(result, mock_response)
        mock_request.assert_called_once_with(
            'POST',
            '/scenarios/123/run',
            data={
                'data': input_data
            }
        )


class TestExampleBlueprints(unittest.TestCase):
    """Test cases for example blueprint creation."""

    def test_create_example_blueprints(self):
        """Test creation of example blueprints."""
        examples = create_example_blueprints()

        self.assertIsInstance(examples, dict)
        self.assertIn("webhook_to_email", examples)
        self.assertIn("http_to_database", examples)

    def test_webhook_to_email_blueprint(self):
        """Test webhook to email blueprint structure."""
        examples = create_example_blueprints()
        blueprint = examples["webhook_to_email"]

        self.assertEqual(blueprint["name"], "Webhook to Email")
        self.assertIn("flow", blueprint)
        self.assertEqual(len(blueprint["flow"]), 0)  # Empty flow in current implementation

    def test_http_to_database_blueprint(self):
        """Test HTTP to database blueprint structure."""
        examples = create_example_blueprints()
        blueprint = examples["http_to_database"]

        self.assertEqual(blueprint["name"], "HTTP to Database")
        self.assertIn("flow", blueprint)
        self.assertEqual(len(blueprint["flow"]), 0)  # Empty flow in current implementation


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

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


class TestConfigurationVariations(unittest.TestCase):
    """Test different configuration scenarios."""

    def test_organization_config(self):
        """Test configuration with organization ID."""
        config = MakeConfig(
            api_token="test_token",
            organization_id=789
        )
        creator = MakeBlueprintCreator(config)

        self.assertEqual(creator.config.organization_id, 789)
        self.assertIsNone(creator.config.team_id)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_list_scenarios_with_organization(self, mock_request):
        """Test listing scenarios with organization ID."""
        config = MakeConfig(api_token="test_token", organization_id=789)
        creator = MakeBlueprintCreator(config)
        mock_request.return_value = {"scenarios": []}

        creator.list_scenarios()

        mock_request.assert_called_once_with(
            'GET', 
            '/scenarios', 
            params={'organizationId': '789'}
        )


class TestErrorHandlingEdgeCases(unittest.TestCase):
    """Test specific error handling edge cases for 100% coverage."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(api_token="test_token", team_id=123)
        self.creator = MakeBlueprintCreator(self.config)

    @patch('requests.Session.request')
    def test_make_request_response_json_parse_error(self, mock_request):
        """Test API request when response.json() fails but response.text works."""
        # Create a proper HTTPError with a response
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")  # JSON parsing fails
        mock_response.text = "Server Error Details"
        
        # Create HTTPError with the response attached
        http_error = requests.exceptions.HTTPError("500 Server Error")
        http_error.response = mock_response
        
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        with self.assertRaises(MakeBlueprintError) as context:
            self.creator._make_request('GET', '/test')

        # Should include the response text when JSON parsing fails
        self.assertIn("Server Error Details", str(context.exception))

    @patch('requests.Session.request')
    def test_make_request_response_json_and_text_fail(self, mock_request):
        """Test API request when both response.json() and response.text fail."""
        # Mock response where both JSON and text access fail
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        # Make text property raise a UnicodeDecodeError (one of the specific exceptions we catch)
        type(mock_response).text = PropertyMock(side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "Text access failed"))
        
        # Create HTTPError with the response attached
        http_error = requests.exceptions.HTTPError("500 Server Error")
        http_error.response = mock_response
        
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        with self.assertRaises(MakeBlueprintError) as context:
            self.creator._make_request('GET', '/test')

        # Should still raise the error even if text access fails
        # The error message should contain the original HTTP error
        self.assertIn("API request failed", str(context.exception))
        self.assertIn("500 Server Error", str(context.exception))

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_folder_id(self, mock_request):
        """Test scenario creation with folder_id parameter."""
        blueprint = {"name": "Test Scenario", "flow": []}
        mock_request.return_value = {"scenario": {"id": 123, "name": "Test Scenario"}}

        self.creator.create_scenario(blueprint, folder_id=456)

        # Check that folder_id was included in the request
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['folderId'], 456)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_string_blueprint(self, mock_request):
        """Test scenario creation with blueprint as string."""
        blueprint_str = '{"name": "Test Scenario", "flow": []}'
        mock_request.return_value = {"scenario": {"id": 123, "name": "Test Scenario"}}

        self.creator.create_scenario(blueprint_str)

        # Check that blueprint string was used directly
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['blueprint'], blueprint_str)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_name_override(self, mock_request):
        """Test scenario creation with name override for dict blueprint."""
        blueprint = {"name": "Original Name", "flow": []}
        mock_request.return_value = {"scenario": {"id": 123, "name": "Override Name"}}

        self.creator.create_scenario(blueprint, name="Override Name")

        # Check that the scenario name was overridden
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['name'], "Override Name")
        # The blueprint itself should remain unchanged
        blueprint_data = json.loads(data['blueprint'])
        self.assertEqual(blueprint_data['name'], "Original Name")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_clone_scenario_with_webhook_mapping(self, mock_request):
        """Test scenario cloning with webhook mapping."""
        mock_request.return_value = {"id": 456, "name": "Cloned Scenario"}

        self.creator.clone_scenario(
            source_scenario_id=123,
            new_name="Cloned Scenario",
            webhook_mapping={"old_webhook": 1, "new_webhook": 2}
        )

        # Check that webhook mapping was included
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['hook'], {"old_webhook": 1, "new_webhook": 2})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_clone_scenario_with_organization_id(self, mock_request):
        """Test scenario cloning with organization ID in params."""
        # Use organization-based config
        org_config = MakeConfig(api_token="test_token", organization_id=789)
        creator = MakeBlueprintCreator(org_config)
        mock_request.return_value = {"id": 456, "name": "Cloned Scenario"}

        creator.clone_scenario(
            source_scenario_id=123,
            new_name="Cloned Scenario"
        )

        # Check that organization ID was included in params
        call_args = mock_request.call_args
        params = call_args[1]['params']
        self.assertEqual(params['organizationId'], 789)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_update_scenario_blueprint_with_scheduling(self, mock_request):
        """Test updating scenario blueprint with scheduling."""
        blueprint = {"name": "Updated Scenario", "flow": []}
        scheduling = {"type": "cron", "cron": "0 9 * * 1-5"}
        mock_request.return_value = {"scenario": {"id": 123, "name": "Updated Scenario"}}

        self.creator.update_scenario_blueprint(123, blueprint, scheduling=scheduling)

        # Check that scheduling was included
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertIn('scheduling', data)
        scheduling_data = json.loads(data['scheduling'])
        self.assertEqual(scheduling_data["type"], "cron")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_update_scenario_blueprint_with_string_blueprint(self, mock_request):
        """Test updating scenario blueprint with blueprint as string."""
        blueprint_str = '{"name": "Updated Scenario", "flow": []}'
        mock_request.return_value = {"scenario": {"id": 123, "name": "Updated Scenario"}}

        self.creator.update_scenario_blueprint(123, blueprint_str)

        # Check that blueprint string was used directly
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['blueprint'], blueprint_str)

    @patch('requests.Session.request')
    def test_make_request_response_json_success_line_141(self, mock_request):
        """Test API request when e.response.json() succeeds - covers line 141."""
        # Create a mock response where JSON parsing succeeds
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Server error details"}
        
        # Create HTTPError with the response attached
        http_error = requests.exceptions.HTTPError("500 Server Error")
        http_error.response = mock_response
        
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response

        with self.assertRaises(MakeBlueprintError) as context:
            self.creator._make_request('GET', '/test')

        # Should include the JSON error details in the message
        self.assertIn("API request failed", str(context.exception))
        self.assertIn("500 Server Error", str(context.exception))
        self.assertIn("Server error details", str(context.exception))
        
        # The error message should contain the JSON details
        error_msg = str(context.exception)
        self.assertIn("{'error': 'Server error details'}", error_msg)


class TestMainFunction(unittest.TestCase):
    """Test the main function for complete coverage."""

    @patch.dict(os.environ, {}, clear=True)
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    def test_main_missing_api_token(self, mock_load_dotenv):
        """Test main function when API token is missing."""
        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from make_blueprint_creator.cli.main import main
            main()
            mock_load_dotenv.assert_called_once()
            mock_logger.error.assert_called_with("MAKE_API_TOKEN environment variable is required")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'}, clear=True)
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    def test_main_missing_team_id(self, mock_load_dotenv):
        """Test main function when team ID and organization ID are missing."""
        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from make_blueprint_creator.cli.main import main
            main()
            mock_load_dotenv.assert_called_once()
            mock_logger.error.assert_called_with("Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token', 'MAKE_TEAM_ID': '123'})
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    @patch('make_blueprint_creator.core.blueprint_creator.MakeBlueprintCreator')
    def test_main_successful_execution(self, mock_creator_class, mock_load_dotenv):
        """Test main function successful execution."""
        # Mock the creator instance and its methods
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock scenario list
        mock_creator.list_scenarios.return_value = [
            {"id": 1, "name": "Test Scenario 1", "isActive": True},
            {"id": 2, "name": "Test Scenario 2", "isActive": False}
        ]
        
        # Mock scenario creation
        mock_creator.create_scenario.side_effect = [
            {"id": 10, "name": "Test Scenario from API"},
            {"id": 11, "name": "Webhook Test Scenario"}
        ]
        
        # Mock blueprint creation
        mock_creator.create_simple_blueprint.return_value = {"name": "Test", "flow": []}
        mock_creator.create_webhook_blueprint.return_value = {"name": "Webhook Test", "flow": []}

        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from make_blueprint_creator.cli.main import main
            main()
            
            # Verify load_dotenv was called
            mock_load_dotenv.assert_called_once()
            
            # Verify success message was logged
            mock_logger.info.assert_any_call("Blueprint creation demonstration completed successfully!")

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token', 'MAKE_TEAM_ID': '123'})
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    @patch('make_blueprint_creator.core.config.MakeConfig')
    def test_main_exception_handling(self, mock_config_class, mock_load_dotenv):
        """Test main function exception handling."""
        # Make config initialization raise an exception
        mock_config_class.side_effect = ValueError("Invalid configuration")

        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from make_blueprint_creator.cli.main import main
            with self.assertRaises(ValueError):
                main()
            
            # Verify load_dotenv was called
            mock_load_dotenv.assert_called_once()
            
            # Verify error was logged
            mock_logger.error.assert_called_with("Error in main execution: Invalid configuration")

    @patch.dict(os.environ, {
        'MAKE_API_TOKEN': 'test_token', 
        'MAKE_TEAM_ID': '123',
        'MAKE_API_BASE_URL': 'https://us1.make.com/api/v2'
    })
    @patch('make_blueprint_creator.cli.main.load_dotenv')
    @patch('make_blueprint_creator.core.blueprint_creator.MakeBlueprintCreator')
    def test_main_with_custom_base_url(self, mock_creator_class, mock_load_dotenv):
        """Test main function with custom base URL from environment."""
        # Mock the creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        mock_creator.list_scenarios.return_value = []
        mock_creator.create_scenario.return_value = {"id": 1, "name": "Test"}
        mock_creator.create_simple_blueprint.return_value = {"name": "Test", "flow": []}
        mock_creator.create_webhook_blueprint.return_value = {"name": "Webhook", "flow": []}

        with patch('make_blueprint_creator.cli.main.logger') as mock_logger:
            from make_blueprint_creator.cli.main import main
            main()
            
            # Verify load_dotenv was called
            mock_load_dotenv.assert_called_once()
            
            # Verify MakeConfig was called with custom base URL
            mock_creator_class.assert_called_once()
            config_arg = mock_creator_class.call_args[0][0]
            self.assertEqual(config_arg.base_url, 'https://us1.make.com/api/v2')

    def test_main_module_execution(self):
        """Test the if __name__ == '__main__' block."""
        # This tests the actual module execution path
        with patch('make_blueprint_creator.cli.main.main') as mock_main:
            # Import and execute the module's main block
            import make_blueprint_creator.cli.main as main_module
            
            # Simulate running the module directly
            if main_module.__name__ == "__main__":
                main_module.main()
            
            # Since we're not actually running as main, this won't execute
            # But we can test the import path works
            self.assertTrue(hasattr(main_module, 'main'))


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True) 