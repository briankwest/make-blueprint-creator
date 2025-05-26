# Make.com Blueprint Creator - Class Reference Guide

## 📚 Comprehensive Class Documentation

**Date**: 2025-01-27  
**Version**: 1.0.0  
**Package**: `make-blueprint-creator`

This document provides comprehensive documentation for all classes, methods, and options available in the Make.com Blueprint Creator package.

---

## 🏗️ **Core Classes**

### **1. MakeConfig**

**Location**: `make_blueprint_creator.core.config`

Configuration class for Make.com API connection and authentication.

#### **Class Definition**
```python
@dataclass
class MakeConfig:
    """Configuration for Make.com API connection."""
    api_token: str
    base_url: str = "https://us2.make.com/api/v2"
    team_id: Optional[int] = None
    organization_id: Optional[int] = None
```

#### **Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `api_token` | `str` | ✅ Yes | - | Your Make.com API token |
| `base_url` | `str` | ❌ No | `"https://us2.make.com/api/v2"` | API base URL (region-specific) |
| `team_id` | `Optional[int]` | ⚠️ Conditional | `None` | Team ID (required if no organization_id) |
| `organization_id` | `Optional[int]` | ⚠️ Conditional | `None` | Organization ID (required if no team_id) |

#### **Properties**

| Property | Type | Description |
|----------|------|-------------|
| `is_organization_based` | `bool` | Returns `True` if using organization-based access |
| `is_team_based` | `bool` | Returns `True` if using team-based access |

#### **Methods**

##### **`from_env() -> MakeConfig`** (Class Method)
Create MakeConfig instance from environment variables.

**Environment Variables**:
- `MAKE_API_TOKEN` (required): Your Make.com API token
- `MAKE_TEAM_ID` (conditional): Team ID for team-based access
- `MAKE_ORGANIZATION_ID` (conditional): Organization ID for org-based access  
- `MAKE_API_BASE_URL` (optional): API base URL (defaults to US region)

**Returns**: MakeConfig instance

**Raises**: `MakeConfigError` if required environment variables are missing

**Example**:
```python
# Set environment variables first
import os
os.environ['MAKE_API_TOKEN'] = 'your_token'
os.environ['MAKE_TEAM_ID'] = '123'

# Create config from environment
config = MakeConfig.from_env()
```

##### **`get_default_params() -> Dict[str, Any]`**
Returns default query parameters for API requests based on configuration.

**Returns**: Dictionary with `organizationId` or `teamId` parameter

##### **`__post_init__()`**
Validates configuration after initialization. Raises `MakeConfigError` for invalid configurations.

#### **Usage Examples**

##### **Team-Based Configuration**
```python
from make_blueprint_creator.core import MakeConfig

# Team-based access
config = MakeConfig(
    api_token="your_api_token_here",
    team_id=123456
)

print(f"Team-based: {config.is_team_based}")  # True
print(f"Default params: {config.get_default_params()}")  # {'teamId': '123456'}
```

##### **Organization-Based Configuration**
```python
# Organization-based access
config = MakeConfig(
    api_token="your_api_token_here",
    organization_id=789012
)

print(f"Org-based: {config.is_organization_based}")  # True
print(f"Default params: {config.get_default_params()}")  # {'organizationId': '789012'}
```

##### **Custom Region Configuration**
```python
# EU region configuration
config = MakeConfig(
    api_token="your_api_token_here",
    team_id=123456,
    base_url="https://eu1.make.com/api/v2"
)
```

##### **Environment Variable Configuration**
```python
from make_blueprint_creator.core import MakeConfig

# Recommended: Use the from_env() class method
config = MakeConfig.from_env()

# Alternative: Manual environment variable handling
import os
config = MakeConfig(
    api_token=os.getenv('MAKE_API_TOKEN'),
    team_id=int(os.getenv('MAKE_TEAM_ID')),
    base_url=os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
)
```

#### **Validation Rules**

- ✅ `api_token` must be non-empty string
- ✅ Either `team_id` OR `organization_id` must be provided (not both)
- ✅ `base_url` must start with `http://` or `https://`
- ✅ Trailing slashes are automatically removed from `base_url`

#### **Error Handling**

```python
from make_blueprint_creator.core.exceptions import MakeConfigError

try:
    config = MakeConfig(api_token="", team_id=123)
except MakeConfigError as e:
    print(f"Configuration error: {e}")
    # Output: Configuration error: API token is required
```

---

### **2. MakeBlueprintCreator**

**Location**: `make_blueprint_creator.core.blueprint_creator`

Main class for creating and managing Make.com automation scenarios (blueprints).

#### **Class Definition**
```python
class MakeBlueprintCreator:
    """A comprehensive class for creating and managing Make.com blueprints programmatically."""
    
    def __init__(self, config: MakeConfig):
        """Initialize with MakeConfig object."""
```

#### **Initialization**

```python
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator

config = MakeConfig(api_token="your_token", team_id=123)
creator = MakeBlueprintCreator(config)
```

#### **Core Methods**

##### **Scenario Management**

###### **`list_scenarios(active_only: bool = False) -> List[Dict[str, Any]]`**

List all scenarios for the configured team or organization.

**Parameters:**
- `active_only` (bool): If `True`, only return active scenarios

**Returns:** List of scenario objects

**Example:**
```python
# List all scenarios
all_scenarios = creator.list_scenarios()
print(f"Total scenarios: {len(all_scenarios)}")

# List only active scenarios
active_scenarios = creator.list_scenarios(active_only=True)
print(f"Active scenarios: {len(active_scenarios)}")

# Process scenarios
for scenario in all_scenarios:
    print(f"- {scenario['name']} (ID: {scenario['id']}, Active: {scenario['isActive']})")
```

###### **`get_scenario_blueprint(scenario_id: int) -> Dict[str, Any]`**

Get the blueprint of an existing scenario.

**Parameters:**
- `scenario_id` (int): ID of the scenario

**Returns:** Scenario blueprint data

**Example:**
```python
# Get blueprint from existing scenario
blueprint = creator.get_scenario_blueprint(scenario_id=123)
print(f"Blueprint name: {blueprint['name']}")
print(f"Number of modules: {len(blueprint['flow'])}")
```

##### **Blueprint Creation**

###### **`create_simple_blueprint(name: str, description: str = "", modules: Optional[List[Dict]] = None) -> Dict[str, Any]`**

Create a simple blueprint with basic structure.

**Parameters:**
- `name` (str): Name of the scenario
- `description` (str): Description of the scenario
- `modules` (Optional[List[Dict]]): List of modules to include

**Returns:** Blueprint data structure

**Example:**
```python
# Create simple blueprint with default HTTP module
blueprint = creator.create_simple_blueprint(
    name="My API Scenario",
    description="Sends data to external API"
)

# Create blueprint with custom modules
custom_modules = [
    {
        "id": 1,
        "module": "http:ActionSendData",
        "version": 3,
        "metadata": {"designer": {"x": 0, "y": 0}},
        "mapper": {
            "url": "https://api.example.com/webhook",
            "method": "post",
            "headers": [{"name": "Content-Type", "value": "application/json"}],
            "body": '{"message": "Hello World"}'
        }
    }
]

custom_blueprint = creator.create_simple_blueprint(
    name="Custom HTTP Scenario",
    description="Custom API integration",
    modules=custom_modules
)
```

###### **`create_webhook_blueprint(name: str, webhook_name: str = "Webhook", description: str = "") -> Dict[str, Any]`**

Create a blueprint with a webhook trigger.

**Parameters:**
- `name` (str): Name of the scenario
- `webhook_name` (str): Name for the webhook
- `description` (str): Description of the scenario

**Returns:** Blueprint data structure with webhook

**Example:**
```python
# Create webhook blueprint
webhook_blueprint = creator.create_webhook_blueprint(
    name="Data Processing Webhook",
    webhook_name="process_data",
    description="Processes incoming webhook data"
)

# Create webhook for user registration
user_webhook = creator.create_webhook_blueprint(
    name="User Registration Handler",
    webhook_name="user_registration",
    description="Handles new user registrations"
)
```

##### **Scenario Operations**

###### **`create_scenario(blueprint: Union[Dict[str, Any], str], name: Optional[str] = None, folder_id: Optional[int] = None, scheduling: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`**

Create a new scenario from a blueprint.

**Parameters:**
- `blueprint` (Union[Dict, str]): Blueprint data or JSON string
- `name` (Optional[str]): Override name for the scenario
- `folder_id` (Optional[int]): Folder ID to place the scenario in
- `scheduling` (Optional[Dict]): Scheduling configuration

**Returns:** Created scenario data

**Example:**
```python
# Create scenario from blueprint
blueprint = creator.create_simple_blueprint("Test Scenario")
scenario = creator.create_scenario(blueprint)
print(f"Created scenario: {scenario['name']} (ID: {scenario['id']})")

# Create scenario with custom name and folder
scenario = creator.create_scenario(
    blueprint=blueprint,
    name="Production API Handler",
    folder_id=456
)

# Create scenario with scheduling
scheduling = {
    "type": "cron",
    "cron": "0 9 * * 1-5"  # Weekdays at 9 AM
}

scheduled_scenario = creator.create_scenario(
    blueprint=blueprint,
    name="Daily Report Generator",
    scheduling=scheduling
)
```

###### **`clone_scenario(source_scenario_id: int, new_name: str, target_team_id: Optional[int] = None, connection_mapping: Optional[Dict[str, int]] = None, webhook_mapping: Optional[Dict[str, int]] = None) -> Dict[str, Any]`**

Clone an existing scenario with optional modifications.

**Parameters:**
- `source_scenario_id` (int): ID of the scenario to clone
- `new_name` (str): Name for the new scenario
- `target_team_id` (Optional[int]): Target team ID (if different)
- `connection_mapping` (Optional[Dict]): Mapping of old to new connection IDs
- `webhook_mapping` (Optional[Dict]): Mapping of old to new webhook IDs

**Returns:** Cloned scenario data

**Example:**
```python
# Simple scenario cloning
cloned_scenario = creator.clone_scenario(
    source_scenario_id=123,
    new_name="Cloned Production Scenario"
)

# Clone with connection mapping (future feature)
cloned_scenario = creator.clone_scenario(
    source_scenario_id=123,
    new_name="Staging Environment",
    connection_mapping={
        "old_connection_id": "new_connection_id"
    },
    webhook_mapping={
        "old_webhook_id": "new_webhook_id"
    }
)
```

###### **`update_scenario_blueprint(scenario_id: int, blueprint: Union[Dict[str, Any], str], scheduling: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`**

Update an existing scenario's blueprint.

**Parameters:**
- `scenario_id` (int): ID of the scenario to update
- `blueprint` (Union[Dict, str]): New blueprint data
- `scheduling` (Optional[Dict]): Updated scheduling configuration

**Returns:** Updated scenario data

**Example:**
```python
# Update scenario blueprint
new_blueprint = creator.create_simple_blueprint(
    name="Updated Scenario",
    description="Updated functionality"
)

updated_scenario = creator.update_scenario_blueprint(
    scenario_id=123,
    blueprint=new_blueprint
)

# Update with new scheduling
new_scheduling = {
    "type": "cron",
    "cron": "0 */6 * * *"  # Every 6 hours
}

updated_scenario = creator.update_scenario_blueprint(
    scenario_id=123,
    blueprint=new_blueprint,
    scheduling=new_scheduling
)
```

##### **Scenario Control**

###### **`activate_scenario(scenario_id: int) -> Dict[str, Any]`**

Activate a scenario.

**Parameters:**
- `scenario_id` (int): ID of the scenario to activate

**Returns:** Updated scenario data

**Example:**
```python
# Activate scenario
result = creator.activate_scenario(scenario_id=123)
print(f"Scenario {scenario_id} activated successfully")
```

###### **`deactivate_scenario(scenario_id: int) -> Dict[str, Any]`**

Deactivate a scenario.

**Parameters:**
- `scenario_id` (int): ID of the scenario to deactivate

**Returns:** Updated scenario data

**Example:**
```python
# Deactivate scenario
result = creator.deactivate_scenario(scenario_id=123)
print(f"Scenario {scenario_id} deactivated successfully")
```

###### **`run_scenario(scenario_id: int, input_data: Optional[Dict[str, Any]] = None, wait_for_completion: bool = False) -> Dict[str, Any]`**

Run a scenario manually.

**Parameters:**
- `scenario_id` (int): ID of the scenario to run
- `input_data` (Optional[Dict]): Input data for the scenario
- `wait_for_completion` (bool): Whether to wait for execution to complete

**Returns:** Execution data

**Example:**
```python
# Run scenario without input data
execution = creator.run_scenario(scenario_id=123)
print(f"Execution started: {execution}")

# Run scenario with input data
input_data = {
    "user_id": 12345,
    "action": "process_order",
    "data": {"order_id": 67890}
}

execution = creator.run_scenario(
    scenario_id=123,
    input_data=input_data,
    wait_for_completion=True
)
```

###### **`delete_scenario(scenario_id: int) -> Dict[str, Any]`**

Delete a scenario.

**Parameters:**
- `scenario_id` (int): ID of the scenario to delete

**Returns:** Deletion response

**Example:**
```python
# Delete scenario
try:
    result = creator.delete_scenario(scenario_id=123)
    print("Scenario deleted successfully")
except MakeAPIError as e:
    print(f"Failed to delete scenario: {e}")
```

##### **Utility Methods**

###### **`format_blueprint_for_api(blueprint: Dict[str, Any]) -> str`**

Format blueprint data for API submission.

**Parameters:**
- `blueprint` (Dict): Blueprint data

**Returns:** JSON-formatted blueprint string

**Example:**
```python
blueprint = creator.create_simple_blueprint("Test")
json_blueprint = creator.format_blueprint_for_api(blueprint)
print(f"Formatted blueprint: {json_blueprint}")
```

#### **Complete Workflow Examples**

##### **Basic Scenario Creation Workflow**
```python
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator

# 1. Setup configuration
config = MakeConfig(
    api_token="your_api_token",
    team_id=123456
)

# 2. Create blueprint creator
creator = MakeBlueprintCreator(config)

# 3. List existing scenarios
scenarios = creator.list_scenarios()
print(f"Existing scenarios: {len(scenarios)}")

# 4. Create a new blueprint
blueprint = creator.create_simple_blueprint(
    name="API Data Processor",
    description="Processes incoming API data"
)

# 5. Create scenario from blueprint
scenario = creator.create_scenario(blueprint)
print(f"Created scenario: {scenario['name']} (ID: {scenario['id']})")

# 6. Activate the scenario
creator.activate_scenario(scenario['id'])
print("Scenario activated and ready to run")
```

##### **Webhook Scenario Workflow**
```python
# 1. Create webhook blueprint
webhook_blueprint = creator.create_webhook_blueprint(
    name="User Registration Webhook",
    webhook_name="user_registration",
    description="Handles new user registrations"
)

# 2. Create scenario with folder organization
scenario = creator.create_scenario(
    blueprint=webhook_blueprint,
    name="Production User Registration",
    folder_id=789  # Production folder
)

# 3. Activate for immediate use
creator.activate_scenario(scenario['id'])

# 4. Test with manual execution
test_data = {
    "user": {
        "email": "test@example.com",
        "name": "Test User"
    }
}

execution = creator.run_scenario(
    scenario_id=scenario['id'],
    input_data=test_data
)
print(f"Test execution: {execution}")
```

##### **Scenario Cloning and Environment Migration**
```python
# 1. Get production scenario
prod_scenarios = creator.list_scenarios()
prod_scenario = next(s for s in prod_scenarios if s['name'] == 'Production API Handler')

# 2. Clone for staging environment
staging_scenario = creator.clone_scenario(
    source_scenario_id=prod_scenario['id'],
    new_name="Staging API Handler"
)

# 3. Update staging scenario with different configuration
staging_blueprint = creator.get_scenario_blueprint(staging_scenario['id'])

# Modify blueprint for staging (example: change API endpoint)
for module in staging_blueprint['flow']:
    if module.get('module') == 'http:ActionSendData':
        if 'mapper' in module and 'url' in module['mapper']:
            module['mapper']['url'] = module['mapper']['url'].replace(
                'api.production.com', 
                'api.staging.com'
            )

# 4. Update the staging scenario
creator.update_scenario_blueprint(
    scenario_id=staging_scenario['id'],
    blueprint=staging_blueprint
)

# 5. Activate staging scenario
creator.activate_scenario(staging_scenario['id'])
```

##### **Bulk Operations Workflow**
```python
# Create multiple scenarios from templates
webhook_configs = [
    {"name": "User Registration", "webhook": "user_reg", "folder": 100},
    {"name": "Order Processing", "webhook": "order_proc", "folder": 101},
    {"name": "Payment Notifications", "webhook": "payment_notif", "folder": 102}
]

created_scenarios = []

for config in webhook_configs:
    # Create webhook blueprint
    blueprint = creator.create_webhook_blueprint(
        name=config["name"],
        webhook_name=config["webhook"],
        description=f"Handles {config['name'].lower()} events"
    )
    
    # Create scenario
    scenario = creator.create_scenario(
        blueprint=blueprint,
        folder_id=config["folder"]
    )
    
    # Activate scenario
    creator.activate_scenario(scenario['id'])
    
    created_scenarios.append(scenario)
    print(f"✅ Created and activated: {scenario['name']}")

print(f"🎉 Successfully created {len(created_scenarios)} scenarios")
```

---

## 🚨 **Exception Classes**

### **Exception Hierarchy**

```
MakeBlueprintError (Base)
├── MakeAPIError
├── MakeConfigError
└── MakeBlueprintValidationError
```

### **1. MakeBlueprintError**

**Location**: `make_blueprint_creator.core.exceptions`

Base exception for all Make.com blueprint operations.

```python
class MakeBlueprintError(Exception):
    """Base exception for Make.com blueprint operations."""
    pass
```

**Usage:**
```python
from make_blueprint_creator.core.exceptions import MakeBlueprintError

try:
    # Some blueprint operation
    pass
except MakeBlueprintError as e:
    print(f"Blueprint operation failed: {e}")
```

### **2. MakeAPIError**

**Location**: `make_blueprint_creator.core.exceptions`

Exception for Make.com API communication errors.

```python
class MakeAPIError(MakeBlueprintError):
    """Exception raised for Make.com API communication errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data
```

**Attributes:**
- `status_code` (int): HTTP status code if available
- `response_data` (dict): API response data if available

**Usage:**
```python
from make_blueprint_creator.core.exceptions import MakeAPIError

try:
    scenarios = creator.list_scenarios()
except MakeAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response Data: {e.response_data}")
```

### **3. MakeConfigError**

**Location**: `make_blueprint_creator.core.exceptions`

Exception for configuration errors.

```python
class MakeConfigError(MakeBlueprintError):
    """Exception raised for configuration errors."""
    pass
```

**Usage:**
```python
from make_blueprint_creator.core.exceptions import MakeConfigError

try:
    config = MakeConfig(api_token="", team_id=123)
except MakeConfigError as e:
    print(f"Configuration error: {e}")
```

### **4. MakeBlueprintValidationError**

**Location**: `make_blueprint_creator.core.exceptions`

Exception for blueprint validation errors.

```python
class MakeBlueprintValidationError(MakeBlueprintError):
    """Exception raised for blueprint validation errors."""
    pass
```

**Usage:**
```python
from make_blueprint_creator.core.exceptions import MakeBlueprintValidationError

try:
    # Blueprint validation
    pass
except MakeBlueprintValidationError as e:
    print(f"Blueprint validation failed: {e}")
```

---

## 🛠️ **Utility Functions**

### **Team and Organization Management**

**Location**: `make_blueprint_creator.utils.team_info`

#### **`make_api_request(endpoint: str, api_token: str, base_url: str = "https://us2.make.com/api/v2") -> Dict[str, Any]`**

Make a request to the Make.com API.

**Parameters:**
- `endpoint` (str): API endpoint to call
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL

**Returns:** API response data

**Example:**
```python
from make_blueprint_creator.utils import make_api_request

response = make_api_request(
    endpoint="/users/me",
    api_token="your_token",
    base_url="https://us2.make.com/api/v2"
)
print(f"User info: {response}")
```

#### **`get_user_info(api_token: str, base_url: str) -> Optional[Dict[str, Any]]`**

Get user information from Make.com API.

**Parameters:**
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL

**Returns:** User information or None if failed

**Example:**
```python
from make_blueprint_creator.utils import get_user_info

user_info = get_user_info("your_token", "https://us2.make.com/api/v2")
if user_info:
    print(f"User: {user_info['name']} (ID: {user_info['id']})")
```

#### **`get_organizations(api_token: str, base_url: str) -> List[Dict[str, Any]]`**

Get list of organizations for the authenticated user.

**Parameters:**
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL

**Returns:** List of organizations

**Example:**
```python
from make_blueprint_creator.utils import get_organizations

organizations = get_organizations("your_token", "https://us2.make.com/api/v2")
for org in organizations:
    print(f"Organization: {org['name']} (ID: {org['id']})")
```

#### **`get_teams_for_organization(api_token: str, base_url: str, organization_id: int) -> List[Dict[str, Any]]`**

Get list of teams for a specific organization.

**Parameters:**
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL
- `organization_id` (int): Organization ID

**Returns:** List of teams in the organization

**Example:**
```python
from make_blueprint_creator.utils import get_teams_for_organization

teams = get_teams_for_organization(
    api_token="your_token",
    base_url="https://us2.make.com/api/v2",
    organization_id=123456
)

for team in teams:
    print(f"Team: {team['name']} (ID: {team['id']})")
```

#### **`get_user_teams(api_token: str, base_url: str) -> List[Dict[str, Any]]`**

Get teams that the user belongs to.

**Parameters:**
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL

**Returns:** List of teams the user belongs to

**Example:**
```python
from make_blueprint_creator.utils import get_user_teams

user_teams = get_user_teams("your_token", "https://us2.make.com/api/v2")
for team in user_teams:
    print(f"Team: {team['name']} (Role: {team.get('userRole', 'Unknown')})")
```

#### **`get_recommended_config(api_token: str, base_url: str) -> Dict[str, Any]`**

Get recommended configuration based on user's teams and organizations.

**Parameters:**
- `api_token` (str): Make.com API token
- `base_url` (str): API base URL

**Returns:** Recommended configuration data

**Example:**
```python
from make_blueprint_creator.utils import get_recommended_config

config_data = get_recommended_config("your_token", "https://us2.make.com/api/v2")
print(f"Recommended team ID: {config_data.get('team_id')}")
print(f"Recommended org ID: {config_data.get('organization_id')}")
```

---

## 🖥️ **Command Line Interface (CLI)**

### **Available Commands**

#### **1. `make-blueprint`**

**Location**: `make_blueprint_creator.cli.main`

Main CLI for basic blueprint operations.

**Usage:**
```bash
make-blueprint
```

**Environment Variables Required:**
- `MAKE_API_TOKEN`: Your Make.com API token
- `MAKE_TEAM_ID` or `MAKE_ORGANIZATION_ID`: Team or organization ID
- `MAKE_API_BASE_URL` (optional): Custom API base URL

**Example:**
```bash
export MAKE_API_TOKEN="your_token_here"
export MAKE_TEAM_ID="123456"
make-blueprint
```

#### **2. `make-examples`**

**Location**: `make_blueprint_creator.cli.examples`

Comprehensive examples and demonstrations.

**Usage:**
```bash
make-examples
```

**Features:**
- Basic usage examples
- Webhook scenario creation
- Custom blueprint examples
- Scenario cloning demonstrations
- Blueprint update examples
- Template usage examples
- Bulk operations examples

#### **3. `make-team-info`**

**Location**: `make_blueprint_creator.cli.team_info`

Team and organization ID discovery tool.

**Usage:**
```bash
make-team-info
```

**Features:**
- Lists user information
- Shows available organizations
- Displays teams for each organization
- Provides recommended configuration
- Helps identify correct IDs for configuration

---

## 📋 **Blueprint Structure Reference**

### **Blueprint JSON Format**

```json
{
  "name": "Scenario Name",
  "description": "Scenario Description",
  "flow": [
    {
      "id": 1,
      "module": "module:type",
      "version": 1,
      "metadata": {
        "designer": {"x": 0, "y": 0}
      },
      "parameters": {},
      "mapper": {}
    }
  ],
  "metadata": {
    "version": 1,
    "scenario": {
      "roundtrips": 1,
      "maxErrors": 3,
      "autoCommit": true,
      "autoCommitTriggerLast": true,
      "sequential": false,
      "confidential": false,
      "dataloss": false,
      "dlq": false,
      "freshVariables": false
    },
    "designer": {"orphans": []}
  }
}
```

### **Common Module Types**

| Module | Description | Example Usage |
|--------|-------------|---------------|
| `http:ActionSendData` | HTTP request module | API calls, webhooks |
| `webhook:CustomWebHook` | Webhook trigger | Incoming data processing |
| `json:ParseJSON` | JSON parser | Data transformation |
| `tools:SetVariable` | Variable setter | Data storage |
| `gateway:CustomWebHook` | Gateway webhook | Legacy webhook format |

### **Module Structure**

```json
{
  "id": 1,
  "module": "http:ActionSendData",
  "version": 3,
  "metadata": {
    "designer": {"x": 0, "y": 0}
  },
  "mapper": {
    "url": "https://api.example.com/endpoint",
    "method": "post",
    "headers": [
      {"name": "Content-Type", "value": "application/json"},
      {"name": "Authorization", "value": "Bearer {{token}}"}
    ],
    "body": "{\"data\": \"{{input.data}}\"}"
  }
}
```

---

## 🔧 **Configuration Examples**

### **Environment Variables Setup**

#### **`.env` File Example**
```env
# Required: Your Make.com API token
MAKE_API_TOKEN=your_actual_api_token_here

# Required: Either team_id OR organization_id
MAKE_TEAM_ID=123456
# OR
MAKE_ORGANIZATION_ID=789012

# Optional: API base URL (defaults to US region)
MAKE_API_BASE_URL=https://us2.make.com/api/v2

# For EU region, use:
# MAKE_API_BASE_URL=https://eu1.make.com/api/v2
```

#### **Shell Environment Setup**
```bash
# Export environment variables
export MAKE_API_TOKEN="your_token_here"
export MAKE_TEAM_ID="123456"
export MAKE_API_BASE_URL="https://us2.make.com/api/v2"

# Verify setup
echo "Token: $MAKE_API_TOKEN"
echo "Team ID: $MAKE_TEAM_ID"
echo "Base URL: $MAKE_API_BASE_URL"
```

### **Programmatic Configuration**

#### **Direct Configuration**
```python
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator

# Direct configuration
config = MakeConfig(
    api_token="your_token_here",
    team_id=123456,
    base_url="https://us2.make.com/api/v2"
)

creator = MakeBlueprintCreator(config)
```

#### **Environment-Based Configuration**
```python
import os
from dotenv import load_dotenv
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator

# Load environment variables
load_dotenv()

# Create configuration from environment
config = MakeConfig(
    api_token=os.getenv('MAKE_API_TOKEN'),
    team_id=int(os.getenv('MAKE_TEAM_ID')) if os.getenv('MAKE_TEAM_ID') else None,
    organization_id=int(os.getenv('MAKE_ORGANIZATION_ID')) if os.getenv('MAKE_ORGANIZATION_ID') else None,
    base_url=os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
)

creator = MakeBlueprintCreator(config)
```

#### **Dynamic Configuration Discovery**
```python
from make_blueprint_creator.utils import get_recommended_config
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator

# Discover configuration automatically
api_token = "your_token_here"
base_url = "https://us2.make.com/api/v2"

config_data = get_recommended_config(api_token, base_url)

# Create configuration with discovered values
config = MakeConfig(
    api_token=api_token,
    base_url=base_url,
    team_id=config_data.get('team_id'),
    organization_id=config_data.get('organization_id')
)

creator = MakeBlueprintCreator(config)
```

---

## 🚀 **Advanced Usage Patterns**

### **Error Handling Patterns**

#### **Comprehensive Error Handling**
```python
from make_blueprint_creator.core import MakeConfig, MakeBlueprintCreator
from make_blueprint_creator.core.exceptions import (
    MakeBlueprintError, 
    MakeAPIError, 
    MakeConfigError
)

try:
    # Configuration
    config = MakeConfig(
        api_token=os.getenv('MAKE_API_TOKEN'),
        team_id=int(os.getenv('MAKE_TEAM_ID'))
    )
    
    # Blueprint creator
    creator = MakeBlueprintCreator(config)
    
    # Operations
    scenarios = creator.list_scenarios()
    blueprint = creator.create_simple_blueprint("Test Scenario")
    scenario = creator.create_scenario(blueprint)
    
except MakeConfigError as e:
    print(f"❌ Configuration Error: {e}")
    print("💡 Check your API token and team/organization ID")
    
except MakeAPIError as e:
    print(f"❌ API Error: {e}")
    print(f"📊 Status Code: {e.status_code}")
    print(f"📋 Response: {e.response_data}")
    
except MakeBlueprintError as e:
    print(f"❌ Blueprint Error: {e}")
    
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
```

#### **Retry Logic Pattern**
```python
import time
from make_blueprint_creator.core.exceptions import MakeAPIError

def create_scenario_with_retry(creator, blueprint, max_retries=3, delay=1):
    """Create scenario with retry logic for transient failures."""
    
    for attempt in range(max_retries):
        try:
            return creator.create_scenario(blueprint)
            
        except MakeAPIError as e:
            if e.status_code in [429, 500, 502, 503, 504]:  # Retryable errors
                if attempt < max_retries - 1:
                    print(f"⏳ Attempt {attempt + 1} failed, retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                    continue
            raise  # Re-raise if not retryable or max retries exceeded
            
    raise MakeAPIError(f"Failed to create scenario after {max_retries} attempts")

# Usage
blueprint = creator.create_simple_blueprint("Resilient Scenario")
scenario = create_scenario_with_retry(creator, blueprint)
```

### **Batch Operations Pattern**

#### **Bulk Scenario Management**
```python
def bulk_scenario_operations(creator, operations):
    """Perform bulk operations on scenarios with progress tracking."""
    
    results = []
    total = len(operations)
    
    for i, operation in enumerate(operations, 1):
        try:
            print(f"📋 Processing {i}/{total}: {operation['name']}")
            
            if operation['type'] == 'create':
                blueprint = creator.create_simple_blueprint(
                    name=operation['name'],
                    description=operation.get('description', '')
                )
                result = creator.create_scenario(blueprint)
                
            elif operation['type'] == 'activate':
                result = creator.activate_scenario(operation['scenario_id'])
                
            elif operation['type'] == 'deactivate':
                result = creator.deactivate_scenario(operation['scenario_id'])
                
            elif operation['type'] == 'delete':
                result = creator.delete_scenario(operation['scenario_id'])
                
            results.append({
                'operation': operation,
                'success': True,
                'result': result
            })
            print(f"✅ Completed: {operation['name']}")
            
        except Exception as e:
            results.append({
                'operation': operation,
                'success': False,
                'error': str(e)
            })
            print(f"❌ Failed: {operation['name']} - {e}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    print(f"\n📊 Summary: {successful}/{total} operations successful")
    
    return results

# Usage
operations = [
    {'type': 'create', 'name': 'User Registration Handler'},
    {'type': 'create', 'name': 'Order Processing System'},
    {'type': 'activate', 'scenario_id': 123},
    {'type': 'activate', 'scenario_id': 124}
]

results = bulk_scenario_operations(creator, operations)
```

### **Template System Pattern**

#### **Blueprint Template Manager**
```python
class BlueprintTemplateManager:
    """Manages blueprint templates for reusable scenario creation."""
    
    def __init__(self, creator: MakeBlueprintCreator):
        self.creator = creator
        self.templates = {}
    
    def register_template(self, name: str, template_func):
        """Register a blueprint template function."""
        self.templates[name] = template_func
    
    def create_from_template(self, template_name: str, **kwargs):
        """Create a scenario from a registered template."""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template_func = self.templates[template_name]
        blueprint = template_func(self.creator, **kwargs)
        return self.creator.create_scenario(blueprint)
    
    def list_templates(self):
        """List available templates."""
        return list(self.templates.keys())

# Template functions
def webhook_to_email_template(creator, webhook_name, email_address):
    """Template for webhook-to-email scenarios."""
    modules = [
        {
            "id": 1,
            "module": "webhook:CustomWebHook",
            "version": 1,
            "metadata": {"designer": {"x": 0, "y": 0}},
            "webhook": {"name": webhook_name, "type": "incoming"}
        },
        {
            "id": 2,
            "module": "email:ActionSendEmail",
            "version": 1,
            "metadata": {"designer": {"x": 300, "y": 0}},
            "mapper": {
                "to": email_address,
                "subject": "Webhook Notification",
                "body": "Received data: {{1.body}}"
            }
        }
    ]
    
    return creator.create_simple_blueprint(
        name=f"Webhook to Email: {webhook_name}",
        description=f"Forwards webhook data to {email_address}",
        modules=modules
    )

def api_to_database_template(creator, api_url, database_config):
    """Template for API-to-database scenarios."""
    modules = [
        {
            "id": 1,
            "module": "http:ActionSendData",
            "version": 3,
            "metadata": {"designer": {"x": 0, "y": 0}},
            "mapper": {
                "url": api_url,
                "method": "get"
            }
        },
        {
            "id": 2,
            "module": "database:Insert",
            "version": 1,
            "metadata": {"designer": {"x": 300, "y": 0}},
            "mapper": database_config
        }
    ]
    
    return creator.create_simple_blueprint(
        name=f"API to Database: {api_url}",
        description=f"Fetches data from {api_url} and stores in database",
        modules=modules
    )

# Usage
template_manager = BlueprintTemplateManager(creator)
template_manager.register_template('webhook_to_email', webhook_to_email_template)
template_manager.register_template('api_to_database', api_to_database_template)

# Create scenarios from templates
email_scenario = template_manager.create_from_template(
    'webhook_to_email',
    webhook_name='user_registration',
    email_address='admin@example.com'
)

database_scenario = template_manager.create_from_template(
    'api_to_database',
    api_url='https://api.example.com/data',
    database_config={'table': 'api_data', 'fields': ['id', 'data']}
)
```

### **Environment Management Pattern**

#### **Multi-Environment Deployment**
```python
class EnvironmentManager:
    """Manages scenarios across different environments."""
    
    def __init__(self, environments):
        self.environments = environments
        self.creators = {}
        
        # Initialize creators for each environment
        for env_name, env_config in environments.items():
            config = MakeConfig(**env_config)
            self.creators[env_name] = MakeBlueprintCreator(config)
    
    def deploy_to_environment(self, env_name, blueprint, scenario_name):
        """Deploy a blueprint to a specific environment."""
        if env_name not in self.creators:
            raise ValueError(f"Environment '{env_name}' not configured")
        
        creator = self.creators[env_name]
        
        # Modify blueprint for environment-specific settings
        env_blueprint = self._adapt_blueprint_for_environment(blueprint, env_name)
        
        scenario = creator.create_scenario(env_blueprint, name=scenario_name)
        creator.activate_scenario(scenario['id'])
        
        return scenario
    
    def deploy_to_all_environments(self, blueprint, base_name):
        """Deploy a blueprint to all configured environments."""
        results = {}
        
        for env_name in self.environments:
            try:
                scenario_name = f"{base_name} ({env_name.title()})"
                scenario = self.deploy_to_environment(env_name, blueprint, scenario_name)
                results[env_name] = {'success': True, 'scenario': scenario}
                print(f"✅ Deployed to {env_name}: {scenario['name']}")
                
            except Exception as e:
                results[env_name] = {'success': False, 'error': str(e)}
                print(f"❌ Failed to deploy to {env_name}: {e}")
        
        return results
    
    def _adapt_blueprint_for_environment(self, blueprint, env_name):
        """Adapt blueprint for specific environment."""
        import copy
        env_blueprint = copy.deepcopy(blueprint)
        
        # Environment-specific adaptations
        env_settings = {
            'development': {
                'api_base': 'https://api.dev.example.com',
                'debug': True
            },
            'staging': {
                'api_base': 'https://api.staging.example.com',
                'debug': False
            },
            'production': {
                'api_base': 'https://api.example.com',
                'debug': False
            }
        }
        
        settings = env_settings.get(env_name, {})
        
        # Update API URLs in modules
        for module in env_blueprint.get('flow', []):
            if module.get('module') == 'http:ActionSendData':
                if 'mapper' in module and 'url' in module['mapper']:
                    # Replace base URL for environment
                    original_url = module['mapper']['url']
                    if 'api.example.com' in original_url:
                        module['mapper']['url'] = original_url.replace(
                            'api.example.com',
                            settings.get('api_base', 'api.example.com').replace('https://', '')
                        )
        
        return env_blueprint

# Usage
environments = {
    'development': {
        'api_token': os.getenv('MAKE_DEV_TOKEN'),
        'team_id': int(os.getenv('MAKE_DEV_TEAM_ID')),
        'base_url': 'https://us2.make.com/api/v2'
    },
    'staging': {
        'api_token': os.getenv('MAKE_STAGING_TOKEN'),
        'team_id': int(os.getenv('MAKE_STAGING_TEAM_ID')),
        'base_url': 'https://us2.make.com/api/v2'
    },
    'production': {
        'api_token': os.getenv('MAKE_PROD_TOKEN'),
        'team_id': int(os.getenv('MAKE_PROD_TEAM_ID')),
        'base_url': 'https://us2.make.com/api/v2'
    }
}

env_manager = EnvironmentManager(environments)

# Create blueprint
blueprint = creator.create_simple_blueprint(
    name="API Integration",
    description="Processes API data"
)

# Deploy to all environments
results = env_manager.deploy_to_all_environments(blueprint, "API Integration")
```

---

## 🔗 **Webhook Management Methods**

The MakeBlueprintCreator class includes comprehensive webhook management functionality to handle webhook creation, assignment conflicts, and automatic hook replacement in blueprints.

### **Hook Listing and Management**

#### **`list_hooks(type_name: Optional[str] = None, assigned: Optional[bool] = None, view_for_scenario_id: Optional[int] = None) -> List[Dict[str, Any]]`**

List all hooks/webhooks for the team.

**Parameters:**
- `type_name` (Optional[str]): Filter by hook type (e.g., 'gateway-webhook')
- `assigned` (Optional[bool]): Filter by assignment status
- `view_for_scenario_id` (Optional[int]): Show hooks available for specific scenario

**Returns:** List of hooks with details

**Example:**
```python
# List all hooks
hooks = creator.list_hooks()
print(f"Total hooks: {len(hooks)}")

# List only unassigned gateway webhooks
unassigned_webhooks = creator.list_hooks(
    type_name="gateway-webhook",
    assigned=False
)

# List hooks available for a specific scenario
available_hooks = creator.list_hooks(view_for_scenario_id=123)
```

#### **`create_webhook(name: str, type_name: str = "gateway-webhook", method: bool = False, headers: bool = False, stringify: bool = False, connection_id: Optional[int] = None, form_id: Optional[str] = None) -> Dict[str, Any]`**

Create a new webhook.

**Parameters:**
- `name` (str): Name for the webhook
- `type_name` (str): Type of webhook (default: 'gateway-webhook')
- `method` (bool): Include HTTP method in request body
- `headers` (bool): Include headers in request body
- `stringify` (bool): Return JSON payloads as strings
- `connection_id` (Optional[int]): Connection ID for app-specific webhooks
- `form_id` (Optional[str]): Form ID for form-specific webhooks

**Returns:** Created webhook data including ID and URL

**Note:** This method has been updated to use the correct `headers` parameter name as required by the Make.com API. Previous versions used `header` (singular) which caused API validation errors.

**Example:**
```python
# Create a basic webhook
webhook = creator.create_webhook("My API Webhook")
print(f"Webhook URL: {webhook['url']}")
print(f"Webhook ID: {webhook['id']}")

# Create webhook with custom settings
advanced_webhook = creator.create_webhook(
    name="Advanced API Webhook",
    method=True,
    headers=True,  # Correctly uses 'headers' parameter
    stringify=False
)
```

#### **`get_hook_details(hook_id: int) -> Dict[str, Any]`**

Get details of a specific hook.

**Parameters:**
- `hook_id` (int): ID of the hook

**Returns:** Hook details including configuration and status

**Example:**
```python
hook_details = creator.get_hook_details(12345)
print(f"Hook name: {hook_details['name']}")
print(f"Hook URL: {hook_details['url']}")
print(f"Hook enabled: {hook_details['enabled']}")
print(f"Assigned to scenario: {hook_details.get('scenarioId')}")
```

#### **`delete_hook(hook_id: int, confirmed: bool = False) -> Dict[str, Any]`**

Delete a hook.

**Parameters:**
- `hook_id` (int): ID of the hook to delete
- `confirmed` (bool): Confirm deletion if hook is assigned to scenario

**Returns:** Deletion response

**Example:**
```python
# Delete unassigned hook
creator.delete_hook(12345)

# Force delete assigned hook (requires confirmation)
creator.delete_hook(12345, confirmed=True)
```

#### **`update_hook(hook_id: int, name: str) -> Dict[str, Any]`**

Update a hook's name.

**Parameters:**
- `hook_id` (int): ID of the hook to update
- `name` (str): New name for the hook

**Returns:** Updated hook data

**Example:**
```python
updated_hook = creator.update_hook(12345, "Updated Webhook Name")
print(f"Hook renamed to: {updated_hook['name']}")
```

### **Blueprint Hook Management**

#### **`replace_hardcoded_hooks_in_blueprint(blueprint: Dict[str, Any], hook_mapping: Optional[Dict[int, int]] = None, create_new_hooks: bool = True, webhook_name_prefix: str = "Auto-created Webhook") -> Dict[str, Any]`**

Replace hardcoded hook IDs in a blueprint with new ones.

**Parameters:**
- `blueprint` (Dict[str, Any]): Blueprint to process
- `hook_mapping` (Optional[Dict[int, int]]): Mapping of old hook ID to new hook ID
- `create_new_hooks` (bool): Whether to create new hooks automatically
- `webhook_name_prefix` (str): Prefix for auto-created webhook names

**Returns:** Updated blueprint with new hook IDs

**Example:**
```python
# Automatically create new hooks for hardcoded ones
updated_blueprint = creator.replace_hardcoded_hooks_in_blueprint(
    blueprint=my_blueprint,
    webhook_name_prefix="My App Webhook"
)

# Use existing hook mapping
hook_mapping = {836593: 999999}  # old_id: new_id
updated_blueprint = creator.replace_hardcoded_hooks_in_blueprint(
    blueprint=my_blueprint,
    hook_mapping=hook_mapping,
    create_new_hooks=False
)

# Find what hooks were replaced
original_hooks = creator._find_hardcoded_hooks(my_blueprint)
new_hooks = creator._find_hardcoded_hooks(updated_blueprint)
print(f"Replaced hooks: {original_hooks} -> {new_hooks}")
```

#### **`create_scenario_with_new_hooks(blueprint: Union[Dict[str, Any], str], name: Optional[str] = None, folder_id: Optional[int] = None, scheduling: Optional[Dict[str, Any]] = None, webhook_name_prefix: str = "Auto-created Webhook") -> Dict[str, Any]`**

Create a scenario from a blueprint, automatically creating new webhooks for any hardcoded hook IDs.

**Parameters:**
- `blueprint` (Union[Dict[str, Any], str]): Blueprint data or JSON string
- `name` (Optional[str]): Override name for the scenario
- `folder_id` (Optional[int]): Folder ID to place the scenario in
- `scheduling` (Optional[Dict[str, Any]]): Scheduling configuration
- `webhook_name_prefix` (str): Prefix for auto-created webhook names

**Returns:** Created scenario data

**Example:**
```python
# Create scenario with automatic webhook creation
scenario = creator.create_scenario_with_new_hooks(
    blueprint=my_blueprint,
    name="My New Scenario",
    webhook_name_prefix="My App"
)

print(f"Created scenario: {scenario['id']}")
print(f"Scenario name: {scenario['name']}")

# The method automatically:
# 1. Finds hardcoded hook IDs in the blueprint
# 2. Creates new webhooks for each hardcoded hook
# 3. Replaces the hardcoded IDs with new webhook IDs
# 4. Creates the scenario with the updated blueprint
```

### **Webhook Management Workflow Examples**

#### **Resolving Hook Assignment Conflicts**
```python
# Problem: Blueprint has hardcoded hook ID that's already assigned
try:
    # This would fail with "The hook already has a scenario assigned"
    scenario = creator.create_scenario(blueprint_with_hardcoded_hooks)
except MakeAPIError as e:
    if "hook already has a scenario assigned" in str(e):
        print("Hook conflict detected, creating scenario with new hooks...")
        
        # Solution: Use automatic hook replacement
        scenario = creator.create_scenario_with_new_hooks(
            blueprint=blueprint_with_hardcoded_hooks,
            webhook_name_prefix="New Deployment"
        )
        print(f"✅ Scenario created with new hooks: {scenario['id']}")
```

#### **Managing Webhook Lifecycle**
```python
# 1. Create webhook for new integration
webhook = creator.create_webhook(
    name="Customer API Integration",
    method=True,
    headers=True
)

print(f"New webhook created: {webhook['url']}")

# 2. Use webhook in blueprint
blueprint = creator.create_webhook_blueprint(
    name="Customer Integration Scenario",
    webhook_name="Customer API Integration"
)

# 3. Replace any hardcoded hooks with our new webhook
hook_mapping = {836593: webhook['id']}  # Replace hardcoded with new
updated_blueprint = creator.replace_hardcoded_hooks_in_blueprint(
    blueprint=blueprint,
    hook_mapping=hook_mapping,
    create_new_hooks=False
)

# 4. Create scenario
scenario = creator.create_scenario(updated_blueprint)

# 5. Clean up old unused webhooks
old_hooks = creator.list_hooks(assigned=False)
for hook in old_hooks:
    if "test" in hook['name'].lower():
        creator.delete_hook(hook['id'])
        print(f"Deleted test webhook: {hook['name']}")
```

#### **Bulk Webhook Management**
```python
# Create multiple scenarios from same blueprint template
blueprint_template = creator.create_webhook_blueprint(
    name="API Integration Template",
    webhook_name="API Webhook"
)

customers = ["CustomerA", "CustomerB", "CustomerC"]
created_scenarios = []

for customer in customers:
    # Each customer gets their own scenario with unique webhooks
    scenario = creator.create_scenario_with_new_hooks(
        blueprint=blueprint_template,
        name=f"{customer} API Integration",
        webhook_name_prefix=f"{customer} Webhook"
    )
    
    created_scenarios.append({
        'customer': customer,
        'scenario_id': scenario['id'],
        'scenario_name': scenario['name']
    })
    
    print(f"✅ Created scenario for {customer}: {scenario['id']}")

# Activate all scenarios
for scenario_info in created_scenarios:
    creator.activate_scenario(scenario_info['scenario_id'])
    print(f"✅ Activated {scenario_info['customer']} scenario")
```

---

## 📚 **Best Practices**

### **1. Configuration Management**
- ✅ Use environment variables for sensitive data
- ✅ Validate configuration before use
- ✅ Use different configurations for different environments
- ✅ Store API tokens securely

### **2. Error Handling**
- ✅ Catch specific exceptions rather than generic ones
- ✅ Implement retry logic for transient failures
- ✅ Log errors with sufficient context
- ✅ Provide meaningful error messages to users

### **3. Blueprint Design**
- ✅ Use descriptive names for scenarios and modules
- ✅ Include comprehensive descriptions
- ✅ Organize scenarios in folders
- ✅ Use consistent naming conventions

### **4. API Usage**
- ✅ Respect rate limits
- ✅ Use appropriate timeouts
- ✅ Handle authentication errors gracefully
- ✅ Monitor API usage and costs

### **5. Testing**
- ✅ Test blueprints in development environment first
- ✅ Use mock data for testing
- ✅ Validate blueprint structure before deployment
- ✅ Test error scenarios

---

## 🔗 **Related Resources**

- **Make.com API Documentation**: https://developers.make.com/api-documentation
- **Make.com Community**: https://community.make.com
- **Package Repository**: https://github.com/briankwest/make-blueprint-creator
- **Issue Tracker**: https://github.com/briankwest/make-blueprint-creator/issues

---

*This documentation covers all classes, methods, and usage patterns available in the Make.com Blueprint Creator package. For additional examples and use cases, refer to the example scripts and test files in the package.* 