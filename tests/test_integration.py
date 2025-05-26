#!/usr/bin/env python3
"""
Integration tests for Make.com Blueprint Creator

These tests verify the complete workflows and interactions between components.
They use mocked API responses but test the full integration flow.

Author: AI Assistant
Date: 2025-01-27
"""

import unittest
from unittest.mock import patch, Mock
import json
import os
from make_blueprint_creator.core.config import MakeConfig
from make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator
from make_blueprint_creator.core.exceptions import MakeBlueprintError
from make_blueprint_creator.cli.examples import create_example_blueprints


class TestCompleteWorkflows(unittest.TestCase):
    """Test complete workflows from start to finish."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_complete_scenario_creation_workflow(self, mock_request):
        """Test the complete workflow of creating and managing a scenario."""
        # Mock responses for the complete workflow
        mock_responses = [
            # 1. List existing scenarios
            {"scenarios": [{"id": 1, "name": "Existing Scenario", "isActive": False}]},
            # 2. Create new scenario
            {"scenario": {"id": 2, "name": "New Test Scenario", "isActive": False}},
            # 3. Activate scenario
            {"success": True},
            # 4. Run scenario
            {"executionId": "exec_123", "status": "running"},
            # 5. Get updated scenario list
            {"scenarios": [
                {"id": 1, "name": "Existing Scenario", "isActive": False},
                {"id": 2, "name": "New Test Scenario", "isActive": True}
            ]}
        ]
        
        mock_request.side_effect = mock_responses

        # 1. List existing scenarios
        initial_scenarios = self.creator.list_scenarios()
        self.assertEqual(len(initial_scenarios), 1)

        # 2. Create a new scenario
        blueprint = self.creator.create_simple_blueprint(
            name="New Test Scenario",
            description="Integration test scenario"
        )
        scenario = self.creator.create_scenario(blueprint)
        self.assertEqual(scenario["id"], 2)
        self.assertEqual(scenario["name"], "New Test Scenario")

        # 3. Activate the scenario
        activation_result = self.creator.activate_scenario(scenario["id"])
        self.assertTrue(activation_result["success"])

        # 4. Run the scenario
        execution_result = self.creator.run_scenario(scenario["id"])
        self.assertEqual(execution_result["executionId"], "exec_123")

        # 5. Verify the scenario is now active
        updated_scenarios = self.creator.list_scenarios()
        self.assertEqual(len(updated_scenarios), 2)
        active_scenario = next(s for s in updated_scenarios if s["id"] == 2)
        self.assertTrue(active_scenario["isActive"])

        # Verify all API calls were made
        self.assertEqual(mock_request.call_count, 5)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_scenario_cloning_workflow(self, mock_request):
        """Test the complete workflow of cloning and modifying a scenario."""
        mock_responses = [
            # 1. Get source scenario blueprint
            {
                "response": {
                    "name": "Source Scenario",
                    "description": "Original scenario",
                    "flow": [
                        {"id": 1, "module": "json:ParseJSON", "version": 1}
                    ],
                    "metadata": {"version": 1}
                }
            },
            # 2. Clone scenario
            {"id": 3, "name": "Cloned Scenario"},
            # 3. Update cloned scenario blueprint
            {"scenario": {"id": 3, "name": "Modified Cloned Scenario"}},
            # 4. Activate cloned scenario
            {"success": True}
        ]
        
        mock_request.side_effect = mock_responses

        # 1. Get the source scenario blueprint
        source_blueprint = self.creator.get_scenario_blueprint(1)
        self.assertEqual(source_blueprint["name"], "Source Scenario")

        # 2. Clone the scenario
        cloned_scenario = self.creator.clone_scenario(
            source_scenario_id=1,
            new_name="Cloned Scenario",
            connection_mapping={"old_conn": 1, "new_conn": 2}
        )
        self.assertEqual(cloned_scenario["id"], 3)

        # 3. Modify the cloned scenario
        modified_blueprint = source_blueprint.copy()
        modified_blueprint["name"] = "Modified Cloned Scenario"
        modified_blueprint["description"] = "Updated description"
        
        updated_scenario = self.creator.update_scenario_blueprint(
            scenario_id=3,
            blueprint=modified_blueprint
        )
        self.assertEqual(updated_scenario["name"], "Modified Cloned Scenario")

        # 4. Activate the modified scenario
        activation_result = self.creator.activate_scenario(3)
        self.assertTrue(activation_result["success"])

        # Verify all API calls were made correctly
        self.assertEqual(mock_request.call_count, 4)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_bulk_scenario_creation_workflow(self, mock_request):
        """Test creating multiple scenarios in bulk."""
        # Mock responses for bulk creation
        scenario_configs = [
            {"name": "Webhook Handler 1", "type": "webhook"},
            {"name": "Webhook Handler 2", "type": "webhook"},
            {"name": "Data Processor", "type": "simple"},
        ]
        
        mock_responses = [
            {"scenario": {"id": 10, "name": "Webhook Handler 1"}},
            {"scenario": {"id": 11, "name": "Webhook Handler 2"}},
            {"scenario": {"id": 12, "name": "Data Processor"}},
        ]
        
        mock_request.side_effect = mock_responses

        created_scenarios = []

        for i, config in enumerate(scenario_configs):
            if config["type"] == "webhook":
                blueprint = self.creator.create_webhook_blueprint(
                    name=config["name"],
                    webhook_name=f"webhook_{i+1}"
                )
            else:
                blueprint = self.creator.create_simple_blueprint(
                    name=config["name"]
                )

            scenario = self.creator.create_scenario(blueprint)
            created_scenarios.append(scenario)

        # Verify all scenarios were created
        self.assertEqual(len(created_scenarios), 3)
        self.assertEqual(created_scenarios[0]["id"], 10)
        self.assertEqual(created_scenarios[1]["id"], 11)
        self.assertEqual(created_scenarios[2]["id"], 12)

        # Verify correct number of API calls
        self.assertEqual(mock_request.call_count, 3)


class TestErrorHandlingWorkflows(unittest.TestCase):
    """Test error handling in complete workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_scenario_creation_with_api_failure(self, mock_request):
        """Test handling of API failures during scenario creation."""
        # First call succeeds (list scenarios), second fails (create scenario)
        mock_request.side_effect = [
            {"scenarios": []},  # Successful list
            MakeBlueprintError("API rate limit exceeded")  # Failed creation
        ]

        # List scenarios should work
        scenarios = self.creator.list_scenarios()
        self.assertEqual(scenarios, [])

        # Create scenario should fail gracefully
        blueprint = self.creator.create_simple_blueprint("Test Scenario")
        
        with self.assertRaises(MakeBlueprintError) as context:
            self.creator.create_scenario(blueprint)
        
        self.assertIn("API rate limit exceeded", str(context.exception))

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_partial_workflow_failure_recovery(self, mock_request):
        """Test recovery from partial workflow failures."""
        # Simulate scenario creation success but activation failure
        mock_request.side_effect = [
            {"scenario": {"id": 5, "name": "Test Scenario"}},  # Creation succeeds
            MakeBlueprintError("Scenario activation failed"),   # Activation fails
            {"success": True}  # Retry activation succeeds
        ]

        # Create scenario
        blueprint = self.creator.create_simple_blueprint("Test Scenario")
        scenario = self.creator.create_scenario(blueprint)
        self.assertEqual(scenario["id"], 5)

        # First activation attempt fails
        with self.assertRaises(MakeBlueprintError):
            self.creator.activate_scenario(scenario["id"])

        # Retry activation succeeds
        result = self.creator.activate_scenario(scenario["id"])
        self.assertTrue(result["success"])


class TestExampleBlueprintIntegration(unittest.TestCase):
    """Test integration with example blueprints."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token",
            team_id=123
        )
        self.creator = MakeBlueprintCreator(self.config)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_example_blueprint_deployment(self, mock_request):
        """Test deploying all example blueprints."""
        examples = create_example_blueprints()
        
        # Mock successful creation for each example
        mock_responses = []
        for i, (name, blueprint) in enumerate(examples.items()):
            mock_responses.append({
                "scenario": {
                    "id": 100 + i,
                    "name": blueprint["name"]
                }
            })
        
        mock_request.side_effect = mock_responses

        created_scenarios = []
        for name, blueprint in examples.items():
            scenario = self.creator.create_scenario(blueprint)
            created_scenarios.append(scenario)

        # Verify all examples were deployed
        self.assertEqual(len(created_scenarios), len(examples))
        self.assertEqual(mock_request.call_count, len(examples))

    def test_example_blueprint_structure_validation(self):
        """Test that all example blueprints have valid structure."""
        examples = create_example_blueprints()

        for name, blueprint in examples.items():
            with self.subTest(blueprint=name):
                # Validate required fields
                self.assertIn("name", blueprint)
                self.assertIn("flow", blueprint)
                self.assertIn("metadata", blueprint)
                
                # Validate flow structure
                self.assertIsInstance(blueprint["flow"], list)
                self.assertGreater(len(blueprint["flow"]), 0)
                
                # Validate each module in flow
                for module in blueprint["flow"]:
                    self.assertIn("id", module)
                    self.assertIn("module", module)
                    self.assertIn("version", module)
                    self.assertIn("metadata", module)

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_webhook_blueprint_customization(self, mock_request):
        """Test customizing webhook blueprints for different use cases."""
        mock_request.return_value = {"scenario": {"id": 200, "name": "Custom Webhook"}}

        # Test different webhook configurations
        webhook_configs = [
            {"name": "User Registration", "webhook": "user_reg", "description": "Handle user registrations"},
            {"name": "Payment Processing", "webhook": "payments", "description": "Process payments"},
            {"name": "Data Sync", "webhook": "sync", "description": "Sync external data"}
        ]

        for config in webhook_configs:
            with self.subTest(webhook=config["name"]):
                blueprint = self.creator.create_webhook_blueprint(
                    name=config["name"],
                    webhook_name=config["webhook"],
                    description=config["description"]
                )

                # Verify blueprint structure
                self.assertEqual(blueprint["name"], config["name"])
                self.assertEqual(blueprint["description"], config["description"])
                
                # Verify webhook module exists (parameters section was removed to fix API validation errors)
                webhook_module = blueprint["flow"][0]
                self.assertEqual(webhook_module["module"], "gateway:CustomWebHook")

                # Test scenario creation
                scenario = self.creator.create_scenario(blueprint)
                self.assertEqual(scenario["id"], 200)


class TestConfigurationIntegration(unittest.TestCase):
    """Test different configuration scenarios in integration context."""

    @patch.object(MakeBlueprintCreator, '_make_request')
    def test_organization_based_workflow(self, mock_request):
        """Test complete workflow using organization-based configuration."""
        # Use organization ID instead of team ID
        config = MakeConfig(
            api_token="test_token",
            organization_id=789
        )
        creator = MakeBlueprintCreator(config)

        mock_request.return_value = {"scenarios": []}

        # Test that organization ID is used in API calls
        creator.list_scenarios()

        mock_request.assert_called_once_with(
            'GET',
            '/scenarios',
            params={'organizationId': '789'}
        )

    def test_environment_variable_integration(self):
        """Test configuration from environment variables."""
        # Mock environment variables
        test_env = {
            'MAKE_API_TOKEN': 'env_test_token',
            'MAKE_TEAM_ID': '456'
        }

        with patch.dict(os.environ, test_env):
            # Simulate loading from environment (as would be done in main())
            api_token = os.getenv('MAKE_API_TOKEN')
            team_id = os.getenv('MAKE_TEAM_ID')

            self.assertEqual(api_token, 'env_test_token')
            self.assertEqual(team_id, '456')

            # Test configuration creation
            self.assertIsNotNone(api_token)
            self.assertIsNotNone(team_id)
            config = MakeConfig(
                api_token=api_token,  # type: ignore
                team_id=int(team_id)  # type: ignore
            )

            self.assertEqual(config.api_token, 'env_test_token')
            self.assertEqual(config.team_id, 456)


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True) 