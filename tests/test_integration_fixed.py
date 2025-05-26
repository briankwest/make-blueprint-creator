"""
Integration tests for make_blueprint_creator package.

These tests actually import and exercise the package code to provide
accurate coverage metrics while still using mocks for HTTP requests.
"""

import unittest
from unittest.mock import patch, Mock
import json
import os

# Set environment variables to prevent actual API calls
os.environ['MAKE_API_TOKEN'] = 'test_token_12345'
os.environ['MAKE_TEAM_ID'] = '123'

# Import the package components
from make_blueprint_creator import (
    MakeBlueprintCreator,
    MakeConfig,
    MakeAPIError,
    MakeConfigError,
    MakeBlueprintValidationError
)


class TestPackageIntegration(unittest.TestCase):
    """Integration tests for the complete package."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = MakeConfig(
            api_token="test_token_12345",
            team_id=123
        )

    def test_package_imports(self):
        """Test that all main package components can be imported."""
        # Test that we can import the main classes
        self.assertTrue(MakeConfig)
        self.assertTrue(MakeBlueprintCreator)
        self.assertTrue(MakeAPIError)
        self.assertTrue(MakeConfigError)
        self.assertTrue(MakeBlueprintValidationError)

    def test_config_creation_and_validation(self):
        """Test config creation and validation logic."""
        # Test valid config
        config = MakeConfig(api_token="test", team_id=123)
        self.assertEqual(config.api_token, "test")
        self.assertEqual(config.team_id, 123)
        self.assertTrue(config.is_team_based)
        self.assertFalse(config.is_organization_based)

        # Test organization-based config
        org_config = MakeConfig(api_token="test", organization_id=456)
        self.assertTrue(org_config.is_organization_based)
        self.assertFalse(org_config.is_team_based)

        # Test default parameters
        params = config.get_default_params()
        self.assertIn('teamId', params)
        self.assertEqual(params['teamId'], '123')

        # Test string representation
        repr_str = repr(config)
        self.assertIn('MakeConfig', repr_str)
        self.assertIn('team_id=123', repr_str)

    def test_config_validation_errors(self):
        """Test config validation error cases."""
        # Test empty token
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="", team_id=123)
        self.assertIn("API token is required", str(context.exception))

        # Test missing both IDs
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="test")
        self.assertIn("Either team_id or organization_id must be provided", str(context.exception))

        # Test both IDs provided
        with self.assertRaises(MakeConfigError) as context:
            MakeConfig(api_token="test", team_id=123, organization_id=456)
        self.assertIn("Cannot specify both team_id and organization_id", str(context.exception))

    @patch('make_blueprint_creator.core.blueprint_creator.requests.Session')
    def test_blueprint_creator_initialization(self, mock_session_class):
        """Test MakeBlueprintCreator initialization."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        creator = MakeBlueprintCreator(self.config)
        
        # Verify session was created and configured
        mock_session_class.assert_called_once()
        mock_session.headers.update.assert_called_once()
        
        # Check headers were set correctly
        headers_call = mock_session.headers.update.call_args[0][0]
        self.assertIn('Authorization', headers_call)
        self.assertTrue(headers_call['Authorization'].startswith('Token'))

    @patch('make_blueprint_creator.core.blueprint_creator.requests.Session')
    def test_blueprint_creation_methods(self, mock_session_class):
        """Test blueprint creation methods."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        creator = MakeBlueprintCreator(self.config)

        # Test simple blueprint creation
        simple_blueprint = creator.create_simple_blueprint(
            name="Test Simple",
            description="Test description"
        )
        
        self.assertEqual(simple_blueprint['name'], "Test Simple")
        self.assertEqual(simple_blueprint['description'], "Test description")
        self.assertIn('flow', simple_blueprint)
        self.assertIn('metadata', simple_blueprint)
        self.assertEqual(len(simple_blueprint['flow']), 1)

        # Test webhook blueprint creation
        webhook_blueprint = creator.create_webhook_blueprint(
            name="Test Webhook",
            webhook_name="test-hook"
        )
        
        self.assertEqual(webhook_blueprint['name'], "Test Webhook")
        self.assertIn('flow', webhook_blueprint)
        self.assertEqual(len(webhook_blueprint['flow']), 2)
        self.assertEqual(webhook_blueprint['flow'][0]['module'], 'webhook:CustomWebHook')

        # Test custom modules
        custom_modules = [
            {
                "id": 1,
                "module": "custom:Module",
                "version": 1,
                "metadata": {"designer": {"x": 0, "y": 0}},
                "mapper": {}
            }
        ]
        
        custom_blueprint = creator.create_simple_blueprint(
            name="Custom",
            modules=custom_modules
        )
        
        self.assertEqual(len(custom_blueprint['flow']), 1)
        self.assertEqual(custom_blueprint['flow'][0]['module'], 'custom:Module')

    @patch('make_blueprint_creator.core.blueprint_creator.requests.Session')
    def test_blueprint_formatting(self, mock_session_class):
        """Test blueprint formatting for API."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        creator = MakeBlueprintCreator(self.config)
        
        blueprint = {"name": "Test", "flow": []}
        formatted = creator.format_blueprint_for_api(blueprint)
        
        # Should be valid JSON
        parsed = json.loads(formatted)
        self.assertEqual(parsed['name'], "Test")
        self.assertEqual(parsed['flow'], [])

    @patch('make_blueprint_creator.core.blueprint_creator.requests.Session')
    def test_scenario_operations_with_mocked_requests(self, mock_session_class):
        """Test scenario operations with properly mocked HTTP requests."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock successful responses
        def mock_request(*args, **kwargs):
            method = kwargs.get('method', 'GET')
            url = kwargs.get('url', '')
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b'{"scenario": {"id": 123, "name": "Test"}}'
            mock_response.json.return_value = {"scenario": {"id": 123, "name": "Test"}}
            mock_response.raise_for_status = Mock()
            
            return mock_response

        mock_session.request.side_effect = mock_request

        creator = MakeBlueprintCreator(self.config)
        
        # Test scenario creation
        blueprint = {"name": "Test Scenario", "flow": []}
        result = creator.create_scenario(blueprint)
        
        # Verify the request was made
        mock_session.request.assert_called()
        call_args = mock_session.request.call_args
        self.assertEqual(call_args[1]['method'], 'POST')
        self.assertIn('/scenarios', call_args[1]['url'])

    def test_exception_classes(self):
        """Test custom exception classes."""
        # Test MakeAPIError
        api_error = MakeAPIError("API failed", status_code=400, response_data={"error": "bad request"})
        self.assertEqual(str(api_error), "API failed")
        self.assertEqual(api_error.status_code, 400)
        self.assertEqual(api_error.response_data, {"error": "bad request"})

        # Test MakeConfigError
        config_error = MakeConfigError("Config invalid")
        self.assertEqual(str(config_error), "Config invalid")

        # Test MakeBlueprintValidationError
        validation_error = MakeBlueprintValidationError("Blueprint invalid")
        self.assertEqual(str(validation_error), "Blueprint invalid")

    def test_utils_imports(self):
        """Test that utils can be imported."""
        try:
            from make_blueprint_creator.utils import team_info
            # Test that the module has expected functions
            self.assertTrue(hasattr(team_info, 'make_api_request'))
            self.assertTrue(hasattr(team_info, 'get_user_info'))
        except ImportError:
            self.fail("Utils should be importable")

    def test_cli_imports(self):
        """Test that CLI modules can be imported."""
        try:
            from make_blueprint_creator.cli import main, examples, team_info
            # Test that modules exist
            self.assertTrue(main)
            self.assertTrue(examples)
            self.assertTrue(team_info)
        except ImportError:
            self.fail("CLI modules should be importable")

    def test_package_metadata(self):
        """Test package metadata and version info."""
        import make_blueprint_creator
        
        # Test version info
        self.assertTrue(hasattr(make_blueprint_creator, '__version__'))
        self.assertTrue(hasattr(make_blueprint_creator, 'get_version'))
        self.assertTrue(hasattr(make_blueprint_creator, 'get_info'))
        
        # Test version functions
        version = make_blueprint_creator.get_version()
        self.assertIsInstance(version, str)
        
        info = make_blueprint_creator.get_info()
        self.assertIsInstance(info, dict)
        self.assertIn('name', info)
        self.assertIn('version', info)


if __name__ == '__main__':
    unittest.main() 