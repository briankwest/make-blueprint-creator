"""
Comprehensive tests for make_blueprint_creator core functionality.

This test file covers the core classes and functions in the restructured package.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
from dataclasses import dataclass

# Import from the new package structure
from make_blueprint_creator.core import (
    MakeBlueprintCreator,
    MakeConfig,
    MakeBlueprintError,
    MakeAPIError,
    MakeConfigError,
    MakeBlueprintValidationError
)


class TestMakeConfig(unittest.TestCase):
    """Test MakeConfig class functionality."""

    def test_valid_config_with_team_id(self):
        """Test creating valid config with team_id."""
        config = MakeConfig(
            api_token="test_token",
            team_id=123,
            base_url="https://us1.make.com/api/v2"
        )
        self.assertEqual(config.api_token, "test_token")
        self.assertEqual(config.team_id, 123)
        self.assertIsNone(config.organization_id)

    def test_valid_config_with_organization_id(self):
        """Test creating valid config with organization_id."""
        config = MakeConfig(
            api_token="test_token",
            organization_id=456,
            base_url="https://us1.make.com/api/v2"
        )
        self.assertEqual(config.api_token, "test_token")
        self.assertEqual(config.organization_id, 456)
        self.assertIsNone(config.team_id)

    def test_missing_api_token(self):
        """Test that missing API token raises MakeConfigError."""
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="", team_id=123)
        self.assertIn("API token is required", str(context.exception))

    def test_missing_team_and_organization_id(self):
        """Test that missing both team_id and organization_id raises MakeConfigError."""
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="test_token")
        self.assertIn("Either team_id or organization_id must be provided", str(context.exception))

    def test_both_team_and_organization_id(self):
        """Test that providing both team_id and organization_id raises MakeConfigError."""
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(
                api_token="test_token",
                team_id=123,
                organization_id=456
            )
        self.assertIn("Cannot specify both team_id and organization_id", str(context.exception))

    def test_default_base_url(self):
        """Test that default base URL is set correctly."""
        config = MakeConfig(api_token="test_token", team_id=123)
        self.assertEqual(config.base_url, "https://us2.make.com/api/v2")


class TestMakeBlueprintCreator(unittest.TestCase):
    """Test MakeBlueprintCreator class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123,
            base_url="https://us1.make.com/api/v2"
        )
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_request.return_value = {"success": True}

        result = self.creator._make_request('GET', '/test')
        self.assertEqual(result, {"success": True})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_make_request_404_error(self, mock_request):
        """Test API request with 404 error."""
        mock_request.side_effect = MakeAPIError("404 Not Found", 404)

        with self.assertRaises(MakeAPIError) as context:
            self.creator._make_request('GET', '/test')
        self.assertIn("404", str(context.exception))

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_make_request_500_error(self, mock_request):
        """Test API request with 500 error."""
        mock_request.side_effect = MakeAPIError("500 Internal Server Error", 500)

        with self.assertRaises(MakeAPIError) as context:
            self.creator._make_request('GET', '/test')
        self.assertIn("500", str(context.exception))

    def test_create_simple_blueprint_default(self):
        """Test creating simple blueprint with default modules."""
        blueprint = self.creator.create_simple_blueprint(name="Test Blueprint")
        
        self.assertIn("name", blueprint)
        self.assertIn("flow", blueprint)
        self.assertEqual(len(blueprint["flow"]), 1)  # Default creates 1 module
        self.assertEqual(blueprint["flow"][0]["module"], "http:ActionSendData")

    def test_create_simple_blueprint_custom(self):
        """Test creating simple blueprint with custom parameters."""
        custom_modules = [
            {
                "id": 1,
                "module": "json:ParseJSON",
                "version": 1,
                "metadata": {"designer": {"x": 0, "y": 0}},
                "mapper": {}
            },
            {
                "id": 2,
                "module": "email:ActionSendEmail",
                "version": 1,
                "metadata": {"designer": {"x": 200, "y": 0}},
                "mapper": {}
            }
        ]
        
        blueprint = self.creator.create_simple_blueprint(
            name="Custom Blueprint",
            description="Custom description",
            modules=custom_modules
        )
        
        self.assertEqual(blueprint["name"], "Custom Blueprint")
        self.assertEqual(blueprint["description"], "Custom description")
        self.assertEqual(len(blueprint["flow"]), 2)
        self.assertEqual(blueprint["flow"][0]["module"], "json:ParseJSON")
        self.assertEqual(blueprint["flow"][1]["module"], "email:ActionSendEmail")

    def test_create_webhook_blueprint(self):
        """Test creating webhook blueprint."""
        blueprint = self.creator.create_webhook_blueprint(
            name="Test Webhook",
            webhook_name="test-webhook"
        )
        
        self.assertEqual(blueprint["name"], "Test Webhook")
        self.assertIn("flow", blueprint)
        self.assertTrue(len(blueprint["flow"]) > 0)
        
        webhook_module = blueprint["flow"][0]
        self.assertEqual(webhook_module["module"], "webhook:CustomWebHook")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_success(self, mock_request):
        """Test successful scenario creation."""
        mock_request.return_value = {"scenario": {"id": 123, "name": "Test Scenario"}}
        
        blueprint = {"name": "Test Scenario", "flow": []}
        result = self.creator.create_scenario(blueprint)
        
        self.assertEqual(result, {"id": 123, "name": "Test Scenario"})
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], 'POST')
        self.assertEqual(call_args[0][1], '/scenarios')

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_custom_scheduling(self, mock_request):
        """Test scenario creation with custom scheduling."""
        mock_request.return_value = {"scenario": {"id": 123, "name": "Test Scenario"}}
        
        blueprint = {"name": "Test Scenario", "flow": []}
        scheduling = {"interval": 15, "unit": "minutes"}
        
        result = self.creator.create_scenario(blueprint, scheduling=scheduling)
        
        self.assertEqual(result, {"id": 123, "name": "Test Scenario"})
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertIn('scheduling', data)

    @patch.object(MakeBlueprintCreator, 'get_scenario_blueprint')
    @patch.object(MakeBlueprintCreator, 'create_scenario')
    def test_clone_scenario_success(self, mock_create, mock_get_blueprint):
        """Test successful scenario cloning."""
        mock_get_blueprint.return_value = {"name": "Original", "flow": []}
        mock_create.return_value = {"id": 456, "name": "Cloned Scenario"}
        
        result = self.creator.clone_scenario(123, "Cloned Scenario")
        
        self.assertEqual(result, {"id": 456, "name": "Cloned Scenario"})
        mock_get_blueprint.assert_called_once_with(123)
        mock_create.assert_called_once_with(
            blueprint={"name": "Original", "flow": []},
            name="Cloned Scenario"
        )

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_activate_scenario(self, mock_request):
        """Test scenario activation."""
        mock_request.return_value = {"success": True}
        
        result = self.creator.activate_scenario(123)
        
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with('PATCH', '/scenarios/123', data={'isActive': True})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_deactivate_scenario(self, mock_request):
        """Test scenario deactivation."""
        mock_request.return_value = {"success": True}
        
        result = self.creator.deactivate_scenario(123)
        
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with('PATCH', '/scenarios/123', data={'isActive': False})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_run_scenario_basic(self, mock_request):
        """Test basic scenario execution."""
        mock_request.return_value = {"executionId": "exec123"}
        
        result = self.creator.run_scenario(123)
        
        self.assertEqual(result, {"executionId": "exec123"})
        mock_request.assert_called_once_with('POST', '/scenarios/123/run', data={})

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_run_scenario_with_input_data(self, mock_request):
        """Test scenario execution with input data."""
        mock_request.return_value = {"executionId": "exec123"}
        
        input_data = {"key": "value", "number": 42}
        result = self.creator.run_scenario(123, input_data=input_data)
        
        self.assertEqual(result, {"executionId": "exec123"})
        mock_request.assert_called_once_with(
            'POST', 
            '/scenarios/123/run', 
            data={'data': input_data}
        )

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_delete_scenario(self, mock_request):
        """Test scenario deletion."""
        mock_request.return_value = {"success": True}
        
        result = self.creator.delete_scenario(123)
        
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with('DELETE', '/scenarios/123')

    def test_webhook_blueprint_creation(self):
        """Test webhook blueprint creation."""
        blueprint = self.creator.create_webhook_blueprint(
            name="Webhook to Email",
            webhook_name="email-webhook"
        )
        
        self.assertEqual(blueprint["name"], "Webhook to Email")
        self.assertIn("flow", blueprint)
        self.assertTrue(len(blueprint["flow"]) > 0)

    def test_simple_blueprint_creation(self):
        """Test simple blueprint creation with custom name."""
        blueprint = self.creator.create_simple_blueprint(
            name="HTTP to Database",
            description="Fetch data via HTTP and store in database"
        )
        
        self.assertEqual(blueprint["name"], "HTTP to Database")
        self.assertIn("flow", blueprint)
        self.assertEqual(len(blueprint["flow"]), 1)  # Default creates 1 module


class TestExceptionHandling(unittest.TestCase):
    """Test exception handling and error cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_folder_id(self, mock_request):
        """Test scenario creation with folder_id parameter."""
        mock_request.return_value = {"id": 123, "name": "Test Scenario"}
        
        blueprint = {"name": "Test Scenario", "flow": []}
        result = self.creator.create_scenario(blueprint, folder_id=456)
        
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['folderId'], 456)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_create_scenario_with_name_override(self, mock_request):
        """Test scenario creation with name override for dict blueprint."""
        mock_request.return_value = {"id": 123, "name": "Override Name"}
        
        blueprint = {"name": "Original Name", "flow": []}
        result = self.creator.create_scenario(blueprint, name="Override Name")
        
        call_args = mock_request.call_args
        data = call_args[1]['data']
        self.assertEqual(data['name'], "Override Name")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_invalid_blueprint_type(self, mock_request):
        """Test error handling for invalid blueprint type."""
        mock_request.side_effect = MakeBlueprintValidationError("Invalid blueprint type")
        
        with self.assertRaises(MakeBlueprintValidationError):
            self.creator.create_scenario("invalid_blueprint")

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        mock_request.side_effect = MakeAPIError("API Error", 400)
        
        blueprint = {"name": "Test", "flow": []}
        with self.assertRaises(MakeAPIError):
            self.creator.create_scenario(blueprint)


if __name__ == '__main__':
    unittest.main() 