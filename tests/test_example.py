#!/usr/bin/env python3
"""
Unit tests for example.py

This test suite provides comprehensive coverage of the example usage
functionality using mocked API responses.

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import os
from make_blueprint_creator.cli.examples import (
    get_make_config,
    example_basic_usage,
    example_webhook_scenario,
    example_custom_blueprint,
    example_scenario_cloning,
    example_blueprint_update,
    example_using_templates,
    example_bulk_operations,
    cleanup_scenarios,
    main
)
from make_blueprint_creator.core.config import MakeConfig
from make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator


class TestGetMakeConfig(unittest.TestCase):
    """Test cases for get_make_config function."""

    @patch.dict(os.environ, {
        'MAKE_API_TOKEN': 'test_token',
        'MAKE_TEAM_ID': '123'
    }, clear=True)
    def test_get_config_with_team_id(self):
        """Test getting configuration with team ID."""
        config = get_make_config()
        
        self.assertEqual(config.api_token, 'test_token')
        self.assertEqual(config.team_id, 123)
        self.assertIsNone(config.organization_id)

    @patch.dict(os.environ, {
        'MAKE_API_TOKEN': 'test_token',
        'MAKE_ORGANIZATION_ID': '456'
    }, clear=True)
    def test_get_config_with_organization_id(self):
        """Test getting configuration with organization ID."""
        config = get_make_config()
        
        self.assertEqual(config.api_token, 'test_token')
        self.assertEqual(config.organization_id, 456)
        self.assertIsNone(config.team_id)

    @patch.dict(os.environ, {
        'MAKE_API_TOKEN': 'test_token',
        'MAKE_TEAM_ID': '123',
        'MAKE_API_BASE_URL': 'https://custom.make.com/api/v2'
    })
    def test_get_config_with_custom_base_url(self):
        """Test getting configuration with custom base URL."""
        config = get_make_config()
        
        self.assertEqual(config.base_url, 'https://custom.make.com/api/v2')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_missing_api_token(self):
        """Test getting configuration when API token is missing."""
        with self.assertRaises(ValueError) as context:
            get_make_config()
        
        self.assertIn("MAKE_API_TOKEN environment variable is required", str(context.exception))

    @patch.dict(os.environ, {'MAKE_API_TOKEN': 'test_token'}, clear=True)
    def test_get_config_missing_team_and_org_id(self):
        """Test getting configuration when both team and org ID are missing."""
        with self.assertRaises(ValueError) as context:
            get_make_config()
        
        self.assertIn("Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required", str(context.exception))


class TestExampleBasicUsage(unittest.TestCase):
    """Test cases for example_basic_usage function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_basic_usage_success(self, mock_creator_class, mock_get_config):
        """Test successful basic usage example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.list_scenarios.return_value = [
            {"id": 1, "name": "Existing Scenario", "isActive": True}
        ]
        mock_creator.create_simple_blueprint.return_value = {
            "name": "API Test Scenario",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 123,
            "name": "API Test Scenario"
        }

        result = example_basic_usage()

        self.assertEqual(result, 123)
        mock_creator.list_scenarios.assert_called_once()
        mock_creator.create_simple_blueprint.assert_called_once()
        mock_creator.create_scenario.assert_called_once()

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_basic_usage_with_exception(self, mock_creator_class, mock_get_config):
        """Test basic usage example with exception."""
        mock_get_config.side_effect = Exception("Configuration error")

        result = example_basic_usage()

        self.assertIsNone(result)


class TestExampleWebhookScenario(unittest.TestCase):
    """Test cases for example_webhook_scenario function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_webhook_scenario_success(self, mock_creator_class, mock_get_config):
        """Test successful webhook scenario example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.create_webhook_blueprint.return_value = {
            "name": "Data Processing Webhook",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 456,
            "name": "Data Processing Webhook"
        }
        mock_creator.activate_scenario.return_value = {"success": True}

        result = example_webhook_scenario()

        self.assertEqual(result, 456)
        mock_creator.create_webhook_blueprint.assert_called_once()
        mock_creator.create_scenario.assert_called_once()
        mock_creator.activate_scenario.assert_called_once_with(456)


class TestExampleCustomBlueprint(unittest.TestCase):
    """Test cases for example_custom_blueprint function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_custom_blueprint_success(self, mock_creator_class, mock_get_config):
        """Test successful custom blueprint example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.create_simple_blueprint.return_value = {
            "name": "HTTP Data Processor",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 789,
            "name": "HTTP Data Processor"
        }

        result = example_custom_blueprint()

        self.assertEqual(result, 789)
        mock_creator.create_simple_blueprint.assert_called_once()
        mock_creator.create_scenario.assert_called_once()


class TestExampleScenarioCloning(unittest.TestCase):
    """Test cases for example_scenario_cloning function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_scenario_cloning_success(self, mock_creator_class, mock_get_config):
        """Test successful scenario cloning example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.create_simple_blueprint.return_value = {
            "name": "Original Scenario",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 100,
            "name": "Original Scenario"
        }
        mock_creator.clone_scenario.return_value = {
            "id": 101,
            "name": "Cloned Scenario"
        }

        result = example_scenario_cloning()

        self.assertEqual(result, [100, 101])
        mock_creator.create_simple_blueprint.assert_called_once()
        mock_creator.create_scenario.assert_called_once()
        mock_creator.clone_scenario.assert_called_once()

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_scenario_cloning_with_nested_response(self, mock_creator_class, mock_get_config):
        """Test scenario cloning with nested response structure."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.create_simple_blueprint.return_value = {
            "name": "Original Scenario",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 100,
            "name": "Original Scenario"
        }
        # Test nested response structure
        mock_creator.clone_scenario.return_value = {
            "scenario": {
                "id": 101,
                "name": "Cloned Scenario"
            }
        }

        result = example_scenario_cloning()

        self.assertEqual(result, [100, 101])


class TestExampleBlueprintUpdate(unittest.TestCase):
    """Test cases for example_blueprint_update function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_blueprint_update_success(self, mock_creator_class, mock_get_config):
        """Test successful blueprint update example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock API responses
        mock_creator.create_simple_blueprint.return_value = {
            "name": "Scenario to Update",
            "flow": []
        }
        mock_creator.create_scenario.return_value = {
            "id": 200,
            "name": "Scenario to Update"
        }
        mock_creator.get_scenario_blueprint.return_value = {
            "blueprint": {
                "name": "Scenario to Update",
                "description": "This will be updated",
                "flow": [{"id": 1, "module": "test"}]
            }
        }
        mock_creator.update_scenario_blueprint.return_value = {
            "id": 200,
            "name": "Updated Scenario Name"
        }

        result = example_blueprint_update()

        self.assertEqual(result, 200)
        mock_creator.create_simple_blueprint.assert_called_once()
        mock_creator.create_scenario.assert_called_once()
        mock_creator.get_scenario_blueprint.assert_called_once_with(200)
        mock_creator.update_scenario_blueprint.assert_called_once()


class TestExampleUsingTemplates(unittest.TestCase):
    """Test cases for example_using_templates function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    @patch('make_blueprint_creator.cli.examples.create_example_blueprints')
    def test_using_templates_success(self, mock_create_examples, mock_creator_class, mock_get_config):
        """Test successful template usage example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock example blueprints
        mock_create_examples.return_value = {
            "webhook_to_email": {"name": "Webhook to Email", "flow": []},
            "http_to_database": {"name": "HTTP to Database", "flow": []}
        }
        
        # Mock scenario creation
        mock_creator.create_scenario.side_effect = [
            {"id": 300, "name": "Template: Webhook to Email"},
            {"id": 301, "name": "Template: HTTP to Database"}
        ]

        result = example_using_templates()

        self.assertEqual(result, 300)
        self.assertEqual(mock_creator.create_scenario.call_count, 1)


class TestExampleBulkOperations(unittest.TestCase):
    """Test cases for example_bulk_operations function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_bulk_operations_success(self, mock_creator_class, mock_get_config):
        """Test successful bulk operations example."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock blueprint creation
        mock_creator.create_webhook_blueprint.return_value = {"name": "Webhook", "flow": []}
        mock_creator.create_simple_blueprint.return_value = {"name": "Simple", "flow": []}
        
        # Mock scenario creation
        mock_creator.create_scenario.side_effect = [
            {"id": 400, "name": "Customer Onboarding"},
            {"id": 401, "name": "Order Processing"},
            {"id": 402, "name": "Support Ticket"},
            {"id": 403, "name": "Data Sync"},
            {"id": 404, "name": "Report Generator"}
        ]

        result = example_bulk_operations()

        self.assertEqual(result, [400, 401, 402])
        self.assertEqual(mock_creator.create_scenario.call_count, 3)
        # Note: Activation is not called in the mocked test since scenarios don't contain 'webhook' in lowercase


class TestCleanupScenarios(unittest.TestCase):
    """Test cases for cleanup_scenarios function."""

    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_cleanup_scenarios_success(self, mock_creator_class):
        """Test successful scenario cleanup."""
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock successful deletion
        mock_creator.delete_scenario.return_value = {"success": True}
        
        # Mock config
        mock_config = Mock()
        
        scenario_ids = [100, 101, 102]
        
        with patch('make_blueprint_creator.cli.examples.get_make_config', return_value=mock_config):
            cleanup_scenarios(scenario_ids)
        
        # Should call delete for each scenario
        self.assertEqual(mock_creator.delete_scenario.call_count, 3)
        mock_creator.delete_scenario.assert_any_call(100)
        mock_creator.delete_scenario.assert_any_call(101)
        mock_creator.delete_scenario.assert_any_call(102)

    @patch('make_blueprint_creator.cli.examples.MakeBlueprintCreator')
    def test_cleanup_scenarios_with_failures(self, mock_creator_class):
        """Test scenario cleanup with some failures."""
        # Mock creator instance
        mock_creator = Mock()
        mock_creator_class.return_value = mock_creator
        
        # Mock mixed success/failure
        mock_creator.delete_scenario.side_effect = [
            {"success": True},  # First succeeds
            Exception("Delete failed"),  # Second fails
            {"success": True}  # Third succeeds
        ]
        
        # Mock config
        mock_config = Mock()
        
        scenario_ids = [100, 101, 102]
        
        # Should not raise exception
        with patch('make_blueprint_creator.cli.examples.get_make_config', return_value=mock_config):
            cleanup_scenarios(scenario_ids)
        
        self.assertEqual(mock_creator.delete_scenario.call_count, 3)

    def test_cleanup_scenarios_empty_list(self):
        """Test cleanup with empty scenario list."""
        mock_config = Mock()
        
        # Should handle empty list gracefully
        with patch('make_blueprint_creator.cli.examples.get_make_config', return_value=mock_config):
            cleanup_scenarios([])
        
        # No assertions needed, just ensure no exceptions


class TestMainFunction(unittest.TestCase):
    """Test cases for main function."""

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    def test_main_config_error(self, mock_get_config):
        """Test main function with configuration error."""
        mock_get_config.side_effect = ValueError("Configuration error")
        
        # Should handle configuration error gracefully
        main()
        
        mock_get_config.assert_called_once()

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.example_basic_usage')
    @patch('make_blueprint_creator.cli.examples.example_webhook_scenario')
    @patch('make_blueprint_creator.cli.examples.example_custom_blueprint')
    @patch('make_blueprint_creator.cli.examples.example_scenario_cloning')
    @patch('make_blueprint_creator.cli.examples.example_blueprint_update')
    @patch('make_blueprint_creator.cli.examples.example_using_templates')
    @patch('make_blueprint_creator.cli.examples.example_bulk_operations')
    @patch('make_blueprint_creator.cli.examples.cleanup_scenarios')
    def test_main_successful_execution(self, mock_cleanup, mock_bulk, mock_templates, 
                                     mock_update, mock_cloning, mock_custom, 
                                     mock_webhook, mock_basic, mock_get_config):
        """Test main function successful execution."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock example function returns
        mock_basic.return_value = 100
        mock_webhook.return_value = 101
        mock_custom.return_value = 102
        mock_cloning.return_value = [103, 104]
        mock_update.return_value = 105
        mock_templates.return_value = [106, 107]
        mock_bulk.return_value = [108, 109, 110]
        
        main()
        
        # Verify all examples were called
        mock_basic.assert_called_once()
        mock_webhook.assert_called_once()
        mock_custom.assert_called_once()
        mock_cloning.assert_called_once()
        mock_update.assert_called_once()
        mock_templates.assert_called_once()
        mock_bulk.assert_called_once()
        
        # Verify cleanup was called
        mock_cleanup.assert_called_once()

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.example_basic_usage')
    @patch('make_blueprint_creator.cli.examples.cleanup_scenarios')
    def test_main_with_example_failures(self, mock_cleanup, mock_basic, mock_get_config):
        """Test main function with some example failures."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock example function that raises exception
        mock_basic.side_effect = Exception("Example failed")
        
        # Should handle exceptions gracefully
        main()
        
        mock_basic.assert_called_once()
        # Cleanup should still be called even if examples fail
        mock_cleanup.assert_called_once()

    @patch('make_blueprint_creator.cli.examples.get_make_config')
    @patch('make_blueprint_creator.cli.examples.cleanup_scenarios')
    def test_main_cleanup_failure(self, mock_cleanup, mock_get_config):
        """Test main function with cleanup failure."""
        # Mock configuration
        mock_config = Mock()
        mock_get_config.return_value = mock_config
        
        # Mock cleanup failure
        mock_cleanup.side_effect = Exception("Cleanup failed")
        
        # Should handle cleanup failure gracefully
        main()
        
        mock_cleanup.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True) 