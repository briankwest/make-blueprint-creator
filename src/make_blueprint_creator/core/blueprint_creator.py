"""
Main Make.com Blueprint Creator class.

This module contains the core MakeBlueprintCreator class that provides
all the functionality for creating, managing, and deploying Make.com
automation scenarios (blueprints).

Author: AI Assistant
Date: 2025-01-27
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union

from .config import MakeConfig
from .exceptions import MakeBlueprintError, MakeAPIError


# Configure logging
logger = logging.getLogger(__name__)


class MakeBlueprintCreator:
    """
    A comprehensive class for creating and managing Make.com blueprints programmatically.

    This class provides methods to:
    - Create new scenarios from blueprints
    - Clone existing scenarios
    - Update scenario blueprints
    - Manage connections and webhooks
    - Handle blueprint JSON formatting and validation

    Note:
        The Make.com API requires the Authorization header to use the 'Token' scheme, e.g.:
            Authorization: Token <your_api_token>
        This is different from many APIs that use 'Bearer'. See:
        https://developers.make.com/api-documentation/authentication

    Example:
        >>> from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator
        >>> config = MakeConfig(
        ...     api_token="your_api_token",
        ...     team_id=123
        ... )
        >>> creator = MakeBlueprintCreator(config)
        >>> blueprint = creator.create_simple_blueprint("My Scenario")
        >>> scenario = creator.create_scenario(blueprint)
    """

    def __init__(self, config: MakeConfig):
        """
        Initialize the Make.com Blueprint Creator.

        Args:
            config (MakeConfig): Configuration object with API credentials
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update(
            {
                # Use 'Token' scheme for Make.com API authentication (as per official docs)
                "Authorization": f"Token {config.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        logger.info(f"Initialized MakeBlueprintCreator with base URL: {config.base_url}")

    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Make.com API.

        Args:
            method (str): HTTP method (GET, POST, PATCH, DELETE)
            endpoint (str): API endpoint (without base URL)
            data (Optional[Dict]): Request body data
            params (Optional[Dict]): Query parameters

        Returns:
            Dict[str, Any]: API response data

        Raises:
            MakeAPIError: If the API request fails
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method=method, url=url, json=data, params=params, timeout=30  # Add timeout for security
            )
            response.raise_for_status()

            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {e}"
            status_code = None
            response_data = None

            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                try:
                    response_data = e.response.json()
                    error_msg += f" - {response_data}"
                except (ValueError, json.JSONDecodeError):
                    # JSON parsing failed, try to get text response
                    try:
                        error_msg += f" - {e.response.text}"
                    except (AttributeError, UnicodeDecodeError):
                        # If text access fails, just use the original error
                        pass

            logger.error(error_msg)
            raise MakeAPIError(error_msg, status_code=status_code, response_data=response_data)

    def list_scenarios(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        List all scenarios for the configured team or organization.

        Args:
            active_only (bool): If True, only return active scenarios

        Returns:
            List[Dict[str, Any]]: List of scenario objects
        """
        params = self.config.get_default_params()

        if active_only:
            params["isActive"] = True

        response = self._make_request("GET", "/scenarios", params=params)
        scenarios = response.get("scenarios", [])

        logger.info(f"Retrieved {len(scenarios)} scenarios")
        return scenarios

    def get_scenario_blueprint(self, scenario_id: int) -> Dict[str, Any]:
        """
        Get the blueprint of an existing scenario.

        Args:
            scenario_id (int): ID of the scenario

        Returns:
            Dict[str, Any]: Scenario blueprint data
        """
        response = self._make_request("GET", f"/scenarios/{scenario_id}/blueprint")
        blueprint_data = response.get("response", {})

        logger.info(f"Retrieved blueprint for scenario {scenario_id}")
        return blueprint_data

    def create_simple_blueprint(
        self, name: str, description: str = "", modules: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Create a simple blueprint with basic structure.

        Args:
            name (str): Name of the scenario
            description (str): Description of the scenario
            modules (Optional[List[Dict]]): List of modules to include

        Returns:
            Dict[str, Any]: Blueprint data structure
        """
        if modules is None:
            # Create a simple HTTP module as default
            modules = [
                {
                    "id": 1,
                    "module": "http:ActionSendData",
                    "version": 3,
                    "metadata": {"designer": {"x": 0, "y": 0}},
                    "mapper": {
                        "url": "https://httpbin.org/post",
                        "method": "post",
                        "headers": [],
                        "qs": [],
                        "body": '{"message": "Hello from Make.com!"}',
                    },
                }
            ]

        blueprint = {
            "name": name,
            "description": description,
            "flow": modules,
            "metadata": {
                "version": 1,
                "scenario": {
                    "roundtrips": 1,
                    "maxErrors": 3,
                    "autoCommit": True,
                    "autoCommitTriggerLast": True,
                    "sequential": False,
                    "confidential": False,
                    "dataloss": False,
                    "dlq": False,
                    "freshVariables": False,
                },
                "designer": {"orphans": []},
            },
        }

        logger.info(f"Created simple blueprint: {name}")
        return blueprint

    def create_webhook_blueprint(
        self, name: str, webhook_name: str = "Webhook", description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a blueprint with a webhook trigger.

        Args:
            name (str): Name of the scenario
            webhook_name (str): Name for the webhook
            description (str): Description of the scenario

        Returns:
            Dict[str, Any]: Blueprint data structure with webhook
        """
        modules = [
            {
                "id": 1,
                "module": "webhook:CustomWebHook",
                "version": 1,
                "metadata": {"designer": {"x": 0, "y": 0}},
                "webhook": {"name": webhook_name, "type": "incoming"},
            },
            {
                "id": 2,
                "module": "http:ActionSendData",
                "version": 3,
                "metadata": {"designer": {"x": 300, "y": 0}},
                "mapper": {
                    "url": "https://httpbin.org/post",
                    "method": "post",
                    "headers": [],
                    "qs": [],
                    "body": '{"webhook_data": "{{1.body}}"}',
                },
            },
        ]

        blueprint = self.create_simple_blueprint(name, description, modules)
        logger.info(f"Created webhook blueprint: {name}")
        return blueprint

    def format_blueprint_for_api(self, blueprint: Dict[str, Any]) -> str:
        """
        Format blueprint data for API submission.

        Args:
            blueprint (Dict[str, Any]): Blueprint data

        Returns:
            str: JSON-formatted blueprint string
        """
        return json.dumps(blueprint, separators=(",", ":"))

    def create_scenario(
        self,
        blueprint: Union[Dict[str, Any], str],
        name: Optional[str] = None,
        folder_id: Optional[int] = None,
        scheduling: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new scenario from a blueprint.

        Args:
            blueprint (Union[Dict[str, Any], str]): Blueprint data or JSON string
            name (Optional[str]): Override name for the scenario
            folder_id (Optional[int]): Folder ID to place the scenario in
            scheduling (Optional[Dict[str, Any]]): Scheduling configuration

        Returns:
            Dict[str, Any]: Created scenario data
        """
        if isinstance(blueprint, dict):
            blueprint_json = self.format_blueprint_for_api(blueprint)
            scenario_name = name or blueprint.get("name", "Untitled Scenario")
        else:
            blueprint_json = blueprint
            # Try to extract name from JSON string
            try:
                bp_data = json.loads(blueprint)
                scenario_name = name or bp_data.get("name", "Untitled Scenario")
            except json.JSONDecodeError:
                scenario_name = name or "Untitled Scenario"

        data = {"blueprint": blueprint_json, "name": scenario_name}

        # Add default parameters
        default_params = self.config.get_default_params()
        for key, value in default_params.items():
            data[key] = value

        if folder_id:
            data["folderId"] = folder_id

        # Always provide scheduling - use provided value or default
        if scheduling:
            data["scheduling"] = json.dumps(scheduling)
        else:
            # Provide default scheduling configuration
            data["scheduling"] = json.dumps({"type": "indefinitely"})

        response = self._make_request("POST", "/scenarios", data=data)
        scenario_data = response.get("scenario", {})

        logger.info(f"Created scenario: {scenario_name} (ID: {scenario_data.get('id')})")
        return scenario_data

    def clone_scenario(
        self,
        source_scenario_id: int,
        new_name: str,
        target_team_id: Optional[int] = None,
        connection_mapping: Optional[Dict[str, int]] = None,
        webhook_mapping: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Clone an existing scenario with optional modifications.

        Args:
            source_scenario_id (int): ID of the scenario to clone
            new_name (str): Name for the new scenario
            target_team_id (Optional[int]): Target team ID (if different from current)
            connection_mapping (Optional[Dict[str, int]]): Mapping of old to new connection IDs
            webhook_mapping (Optional[Dict[str, int]]): Mapping of old to new webhook IDs

        Returns:
            Dict[str, Any]: Cloned scenario data
        """
        # Get the source blueprint
        source_blueprint = self.get_scenario_blueprint(source_scenario_id)

        # Apply connection and webhook mappings if provided
        if connection_mapping or webhook_mapping:
            # This would require more complex logic to traverse and update the blueprint
            logger.warning("Connection and webhook mapping not yet implemented")

        # Create new scenario from the blueprint
        cloned_scenario = self.create_scenario(blueprint=source_blueprint, name=new_name)

        logger.info(f"Cloned scenario {source_scenario_id} to {cloned_scenario.get('id')}")
        return cloned_scenario

    def update_scenario_blueprint(
        self, scenario_id: int, blueprint: Union[Dict[str, Any], str], scheduling: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing scenario's blueprint.

        Args:
            scenario_id (int): ID of the scenario to update
            blueprint (Union[Dict[str, Any], str]): New blueprint data
            scheduling (Optional[Dict[str, Any]]): Updated scheduling configuration

        Returns:
            Dict[str, Any]: Updated scenario data
        """
        if isinstance(blueprint, dict):
            blueprint_json = self.format_blueprint_for_api(blueprint)
        else:
            blueprint_json = blueprint

        data = {"blueprint": blueprint_json}

        if scheduling:
            data["scheduling"] = json.dumps(scheduling)

        response = self._make_request("PATCH", f"/scenarios/{scenario_id}", data=data)
        scenario_data = response.get("scenario", {})

        logger.info(f"Updated scenario {scenario_id}")
        return scenario_data

    def activate_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """
        Activate a scenario.

        Args:
            scenario_id (int): ID of the scenario to activate

        Returns:
            Dict[str, Any]: Updated scenario data
        """
        data = {"isActive": True}
        response = self._make_request("PATCH", f"/scenarios/{scenario_id}", data=data)
        logger.info(f"Activated scenario {scenario_id}")
        return response

    def deactivate_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """
        Deactivate a scenario.

        Args:
            scenario_id (int): ID of the scenario to deactivate

        Returns:
            Dict[str, Any]: Updated scenario data
        """
        data = {"isActive": False}
        response = self._make_request("PATCH", f"/scenarios/{scenario_id}", data=data)
        logger.info(f"Deactivated scenario {scenario_id}")
        return response

    def run_scenario(
        self, scenario_id: int, input_data: Optional[Dict[str, Any]] = None, wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """
        Run a scenario manually.

        Args:
            scenario_id (int): ID of the scenario to run
            input_data (Optional[Dict[str, Any]]): Input data for the scenario
            wait_for_completion (bool): Whether to wait for execution to complete

        Returns:
            Dict[str, Any]: Execution data
        """
        data = {}
        if input_data:
            data["data"] = input_data

        response = self._make_request("POST", f"/scenarios/{scenario_id}/run", data=data)

        if wait_for_completion:
            # This would require polling the execution status
            logger.warning("Wait for completion not yet implemented")

        logger.info(f"Started execution of scenario {scenario_id}")
        return response

    def delete_scenario(self, scenario_id: int) -> Dict[str, Any]:
        """
        Delete a scenario.

        Args:
            scenario_id (int): ID of the scenario to delete

        Returns:
            Dict[str, Any]: Deletion response
        """
        try:
            response = self._make_request("DELETE", f"/scenarios/{scenario_id}")
            logger.info(f"Deleted scenario {scenario_id}")
            return response
        except MakeAPIError as e:
            logger.error(f"Failed to delete scenario {scenario_id}: {e}")
            raise

    # Webhook Management Methods

    def list_hooks(
        self,
        type_name: Optional[str] = None,
        assigned: Optional[bool] = None,
        view_for_scenario_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all hooks/webhooks for the team.

        Args:
            type_name (Optional[str]): Filter by hook type (e.g., 'gateway-webhook')
            assigned (Optional[bool]): Filter by assignment status
            view_for_scenario_id (Optional[int]): Show hooks available for specific scenario

        Returns:
            List[Dict[str, Any]]: List of hooks
        """
        params: Dict[str, Any] = {"teamId": self.config.team_id}

        if type_name:
            params["typeName"] = type_name
        if assigned is not None:
            params["assigned"] = str(assigned).lower()
        if view_for_scenario_id:
            params["viewForScenarioId"] = view_for_scenario_id

        response = self._make_request("GET", "/hooks", params=params)
        hooks = response.get("hooks", [])

        logger.info(f"Retrieved {len(hooks)} hooks")
        return hooks

    def create_webhook(
        self,
        name: str,
        type_name: str = "gateway-webhook",
        method: bool = False,
        headers: bool = False,
        stringify: bool = False,
        connection_id: Optional[int] = None,
        form_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new webhook.

        Args:
            name (str): Name for the webhook
            type_name (str): Type of webhook (default: 'gateway-webhook')
            method (bool): Include HTTP method in request body
            headers (bool): Include headers in request body
            stringify (bool): Return JSON payloads as strings
            connection_id (Optional[int]): Connection ID for app-specific webhooks
            form_id (Optional[str]): Form ID for form-specific webhooks

        Returns:
            Dict[str, Any]: Created webhook data
        """
        data = {
            "name": name,
            "teamId": self.config.team_id,
            "typeName": type_name,
            "method": method,
            "headers": headers,
            "stringify": stringify,
        }

        if connection_id:
            data["__IMTCONN__"] = connection_id
        if form_id:
            data["formId"] = form_id

        response = self._make_request("POST", "/hooks", data=data)
        hook_data = response.get("hook", {})

        logger.info(f"Created webhook: {name} (ID: {hook_data.get('id')}, URL: {hook_data.get('url')})")
        return hook_data

    def get_hook_details(self, hook_id: int) -> Dict[str, Any]:
        """
        Get details of a specific hook.

        Args:
            hook_id (int): ID of the hook

        Returns:
            Dict[str, Any]: Hook details
        """
        response = self._make_request("GET", f"/hooks/{hook_id}")
        hook_data = response.get("hook", {})

        logger.info(f"Retrieved hook details for ID: {hook_id}")
        return hook_data

    def delete_hook(self, hook_id: int, confirmed: bool = False) -> Dict[str, Any]:
        """
        Delete a hook.

        Args:
            hook_id (int): ID of the hook to delete
            confirmed (bool): Confirm deletion if hook is assigned to scenario

        Returns:
            Dict[str, Any]: Deletion response
        """
        params = {}
        if confirmed:
            params["confirmed"] = "true"

        response = self._make_request("DELETE", f"/hooks/{hook_id}", params=params)

        logger.info(f"Deleted hook ID: {hook_id}")
        return response

    def update_hook(self, hook_id: int, name: str) -> Dict[str, Any]:
        """
        Update a hook's name.

        Args:
            hook_id (int): ID of the hook to update
            name (str): New name for the hook

        Returns:
            Dict[str, Any]: Updated hook data
        """
        data = {"name": name}
        response = self._make_request("PATCH", f"/hooks/{hook_id}", data=data)
        hook_data = response.get("hook", {})

        logger.info(f"Updated hook {hook_id} name to: {name}")
        return hook_data

    def replace_hardcoded_hooks_in_blueprint(
        self,
        blueprint: Dict[str, Any],
        hook_mapping: Optional[Dict[int, int]] = None,
        create_new_hooks: bool = True,
        webhook_name_prefix: str = "Auto-created Webhook",
    ) -> Dict[str, Any]:
        """
        Replace hardcoded hook IDs in a blueprint with new ones.

        Args:
            blueprint (Dict[str, Any]): Blueprint to process
            hook_mapping (Optional[Dict[int, int]]): Mapping of old hook ID to new hook ID
            create_new_hooks (bool): Whether to create new hooks automatically
            webhook_name_prefix (str): Prefix for auto-created webhook names

        Returns:
            Dict[str, Any]: Updated blueprint with new hook IDs
        """
        import copy

        updated_blueprint = copy.deepcopy(blueprint)

        if hook_mapping is None:
            hook_mapping = {}

        # Find all hardcoded hook IDs in the blueprint
        hardcoded_hooks = self._find_hardcoded_hooks(updated_blueprint)

        logger.info(f"Found {len(hardcoded_hooks)} hardcoded hook references")

        # Create new hooks for any unmapped hardcoded hooks
        for old_hook_id in hardcoded_hooks:
            if old_hook_id not in hook_mapping:
                if create_new_hooks:
                    # Create a new webhook
                    webhook_name = f"{webhook_name_prefix} {old_hook_id}"
                    new_hook = self.create_webhook(
                        name=webhook_name, type_name="gateway-webhook", method=False, headers=False, stringify=False
                    )
                    hook_mapping[old_hook_id] = new_hook["id"]
                    logger.info(f"Created new webhook {new_hook['id']} to replace hardcoded hook {old_hook_id}")
                else:
                    logger.warning(
                        f"No mapping provided for hardcoded hook {old_hook_id} and create_new_hooks is False"
                    )

        # Replace hook IDs in the blueprint
        self._replace_hook_ids_recursive(updated_blueprint, hook_mapping)

        logger.info(f"Replaced {len(hook_mapping)} hook IDs in blueprint")
        return updated_blueprint

    def replace_hardcoded_hooks_in_blueprint_with_mapping(
        self,
        blueprint: Dict[str, Any],
        hook_mapping: Optional[Dict[int, int]] = None,
        create_new_hooks: bool = True,
        webhook_name_prefix: str = "Auto-created Webhook",
    ) -> tuple[Dict[str, Any], Dict[int, int]]:
        """
        Replace hardcoded hook IDs in a blueprint with new ones and return the mapping.

        Args:
            blueprint (Dict[str, Any]): Blueprint to process
            hook_mapping (Optional[Dict[int, int]]): Mapping of old hook ID to new hook ID
            create_new_hooks (bool): Whether to create new hooks automatically
            webhook_name_prefix (str): Prefix for auto-created webhook names

        Returns:
            tuple: (Updated blueprint with new hook IDs, Hook mapping dictionary)
        """
        import copy

        updated_blueprint = copy.deepcopy(blueprint)

        if hook_mapping is None:
            hook_mapping = {}

        # Find all hardcoded hook IDs in the blueprint
        hardcoded_hooks = self._find_hardcoded_hooks(updated_blueprint)

        logger.info(f"Found {len(hardcoded_hooks)} hardcoded hook references")

        # Create new hooks for any unmapped hardcoded hooks
        for old_hook_id in hardcoded_hooks:
            if old_hook_id not in hook_mapping:
                if create_new_hooks:
                    # Create a new webhook
                    webhook_name = f"{webhook_name_prefix} {old_hook_id}"
                    new_hook = self.create_webhook(
                        name=webhook_name, type_name="gateway-webhook", method=False, headers=False, stringify=False
                    )
                    hook_mapping[old_hook_id] = new_hook["id"]
                    logger.info(f"Created new webhook {new_hook['id']} to replace hardcoded hook {old_hook_id}")
                else:
                    logger.warning(
                        f"No mapping provided for hardcoded hook {old_hook_id} and create_new_hooks is False"
                    )

        # Replace hook IDs in the blueprint
        self._replace_hook_ids_recursive(updated_blueprint, hook_mapping)

        logger.info(f"Replaced {len(hook_mapping)} hook IDs in blueprint")
        return updated_blueprint, hook_mapping

    def _find_hardcoded_hooks(self, data: Any, hooks: Optional[set] = None) -> set:
        """
        Recursively find all hardcoded hook IDs in blueprint data.

        Args:
            data: Data structure to search
            hooks: Set to accumulate found hook IDs

        Returns:
            set: Set of found hook IDs
        """
        if hooks is None:
            hooks = set()

        if isinstance(data, dict):
            for key, value in data.items():
                if key == "hook" and isinstance(value, int):
                    hooks.add(value)
                elif key == "parameters" and isinstance(value, dict) and "hook" in value:
                    if isinstance(value["hook"], int):
                        hooks.add(value["hook"])
                else:
                    self._find_hardcoded_hooks(value, hooks)
        elif isinstance(data, list):
            for item in data:
                self._find_hardcoded_hooks(item, hooks)

        return hooks

    def _replace_hook_ids_recursive(self, data: Any, hook_mapping: Dict[int, int]) -> None:
        """
        Recursively replace hook IDs in blueprint data.

        Args:
            data: Data structure to modify
            hook_mapping: Mapping of old hook ID to new hook ID
        """
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "hook" and isinstance(value, int) and value in hook_mapping:
                    data[key] = hook_mapping[value]
                    logger.debug(f"Replaced hook ID {value} with {hook_mapping[value]}")
                elif key == "parameters" and isinstance(value, dict) and "hook" in value:
                    if isinstance(value["hook"], int) and value["hook"] in hook_mapping:
                        old_id = value["hook"]
                        value["hook"] = hook_mapping[old_id]
                        logger.debug(f"Replaced parameter hook ID {old_id} with {hook_mapping[old_id]}")
                else:
                    self._replace_hook_ids_recursive(value, hook_mapping)
        elif isinstance(data, list):
            for item in data:
                self._replace_hook_ids_recursive(item, hook_mapping)

    def create_scenario_with_new_hooks(
        self,
        blueprint: Union[Dict[str, Any], str],
        name: Optional[str] = None,
        folder_id: Optional[int] = None,
        scheduling: Optional[Dict[str, Any]] = None,
        webhook_name_prefix: str = "Auto-created Webhook",
    ) -> Dict[str, Any]:
        """
        Create a scenario from a blueprint, automatically creating new webhooks for any hardcoded hook IDs.

        Args:
            blueprint (Union[Dict[str, Any], str]): Blueprint data or JSON string
            name (Optional[str]): Override name for the scenario
            folder_id (Optional[int]): Folder ID to place the scenario in
            scheduling (Optional[Dict[str, Any]]): Scheduling configuration
            webhook_name_prefix (str): Prefix for auto-created webhook names

        Returns:
            Dict[str, Any]: Created scenario data with webhook information included
        """
        # Parse blueprint if it's a string
        if isinstance(blueprint, str):
            try:
                blueprint_dict = json.loads(blueprint)
            except json.JSONDecodeError as e:
                raise MakeBlueprintError(f"Invalid JSON blueprint: {e}")
        else:
            blueprint_dict = blueprint

        # Find hardcoded hooks before replacement
        hardcoded_hooks = self._find_hardcoded_hooks(blueprint_dict)
        
        # Replace hardcoded hooks with new ones and track the mapping
        updated_blueprint, hook_mapping = self.replace_hardcoded_hooks_in_blueprint_with_mapping(
            blueprint_dict, create_new_hooks=True, webhook_name_prefix=webhook_name_prefix
        )

        # Create the scenario with the updated blueprint
        scenario_data = self.create_scenario(
            blueprint=updated_blueprint, name=name, folder_id=folder_id, scheduling=scheduling
        )

        # Get webhook details for the created hooks
        webhooks = []
        for old_hook_id, new_hook_id in hook_mapping.items():
            try:
                hook_details = self.get_hook_details(new_hook_id)
                webhooks.append({
                    'id': new_hook_id,
                    'name': hook_details.get('name', 'Unknown'),
                    'url': hook_details.get('url', 'Unknown'),
                    'replaced_hook_id': old_hook_id
                })
            except Exception as e:
                logger.warning(f"Could not get details for hook {new_hook_id}: {e}")

        # Add webhook information to scenario data
        scenario_data['webhooks'] = webhooks

        logger.info(f"Created scenario with new hooks: {scenario_data.get('name')} (ID: {scenario_data.get('id')})")
        return scenario_data
