#!/usr/bin/env python3
"""
Make.com Blueprint Creator - Example Usage CLI

This command-line tool demonstrates various ways to use the Make.com Blueprint Creator
to programmatically create and manage Make.com scenarios.

Usage:
    make-examples

Author: AI Assistant
Date: 2025-01-27
"""

import os
import sys
import logging
from dotenv import load_dotenv
from typing import List, Optional

from ..core import MakeConfig, MakeBlueprintCreator, MakeConfigError, MakeBlueprintError

# Global list to track created scenarios for cleanup
created_scenarios = []


def get_make_config():
    """Get Make.com configuration from environment variables."""
    api_token = os.getenv('MAKE_API_TOKEN')
    team_id = os.getenv('MAKE_TEAM_ID')
    organization_id = os.getenv('MAKE_ORGANIZATION_ID')
    base_url = os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
    
    if not api_token:
        raise ValueError("MAKE_API_TOKEN environment variable is required")
    
    if not team_id and not organization_id:
        raise ValueError("Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required")
    
    # Prioritize team_id over organization_id if both are set
    # This follows the principle that team-level access is more specific than org-level
    if team_id:
        return MakeConfig(
            api_token=api_token,
            base_url=base_url,
            team_id=int(team_id)
        )
    elif organization_id:
        return MakeConfig(
            api_token=api_token,
            base_url=base_url,
            organization_id=int(organization_id)
        )
    else:
        # This should never happen due to the check above, but for type safety
        raise ValueError("Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required")


def create_example_blueprints():
    """Create example blueprint templates."""
    return {
        "webhook_to_email": {
            "name": "Webhook to Email",
            "description": "Process webhook data and send email",
            "flow": []
        },
        "http_to_database": {
            "name": "HTTP to Database", 
            "description": "Fetch data via HTTP and store in database",
            "flow": []
        }
    }


def example_basic_usage():
    """Demonstrate basic blueprint creation and scenario management."""
    print("=== Basic Usage Example ===")

    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)

        print("📋 Listing existing scenarios...")
        scenarios = creator.list_scenarios()
        print(f"✅ Found {len(scenarios)} scenarios")

        print("🔨 Creating a simple blueprint...")
        simple_blueprint = creator.create_simple_blueprint(
            name="API Test Scenario",
            description="A test scenario created via API"
        )

        print("🚀 Creating scenario from blueprint...")
        scenario = creator.create_scenario(simple_blueprint)
        print(f"✅ Created scenario: {scenario['name']} (ID: {scenario['id']})")
        
        # Track for cleanup
        created_scenarios.append(scenario['id'])
        return scenario['id']

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_webhook_scenario():
    """Demonstrate webhook scenario creation."""
    print("=== Webhook Scenario Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        print("🔨 Creating webhook blueprint...")
        webhook_blueprint = creator.create_webhook_blueprint(
            name="Data Processing Webhook",
            description="Process incoming webhook data"
        )
        
        print("🚀 Creating scenario from webhook blueprint...")
        scenario = creator.create_scenario(webhook_blueprint)
        print(f"✅ Created webhook scenario: {scenario['name']} (ID: {scenario['id']})")
        
        print("⚡ Activating scenario...")
        creator.activate_scenario(scenario['id'])
        print("✅ Scenario activated")
        
        # Track for cleanup
        created_scenarios.append(scenario['id'])
        return scenario['id']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_custom_blueprint():
    """Demonstrate custom blueprint creation."""
    print("=== Custom Blueprint Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        print("🔨 Creating custom blueprint...")
        custom_blueprint = creator.create_simple_blueprint(
            name="HTTP Data Processor",
            description="Custom HTTP data processing workflow"
        )
        
        print("🚀 Creating scenario from custom blueprint...")
        scenario = creator.create_scenario(custom_blueprint)
        print(f"✅ Created custom scenario: {scenario['name']} (ID: {scenario['id']})")
        
        # Track for cleanup
        created_scenarios.append(scenario['id'])
        return scenario['id']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_scenario_cloning():
    """Demonstrate scenario cloning."""
    print("=== Scenario Cloning Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        # First create a scenario to clone
        print("🔨 Creating original scenario...")
        original_blueprint = creator.create_simple_blueprint(
            name="Original Scenario",
            description="Scenario to be cloned"
        )
        original_scenario = creator.create_scenario(original_blueprint)
        original_id = original_scenario['id']
        print(f"✅ Created original scenario: {original_scenario['name']} (ID: {original_id})")
        
        print("🔄 Cloning scenario...")
        cloned_scenario = creator.clone_scenario(
            original_id,
            new_name="Cloned Scenario"
        )
        cloned_id = cloned_scenario['id']
        print(f"✅ Cloned scenario: {cloned_scenario['name']} (ID: {cloned_id})")
        
        # Track both for cleanup
        created_scenarios.extend([original_id, cloned_id])
        return [original_id, cloned_id]
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_blueprint_update():
    """Demonstrate blueprint updating."""
    print("=== Blueprint Update Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        # Create a scenario to update
        print("🔨 Creating scenario to update...")
        original_blueprint = creator.create_simple_blueprint(
            name="Scenario to Update",
            description="Original description"
        )
        scenario = creator.create_scenario(original_blueprint)
        scenario_id = scenario['id']
        print(f"✅ Created scenario: {scenario['name']} (ID: {scenario_id})")
        
        print("🔄 Updating scenario blueprint...")
        updated_blueprint = creator.create_simple_blueprint(
            name="Updated Scenario",
            description="Updated description"
        )
        creator.update_scenario_blueprint(scenario_id, updated_blueprint)
        print("✅ Blueprint updated successfully")
        
        # Track for cleanup
        created_scenarios.append(scenario_id)
        return scenario_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_using_templates():
    """Demonstrate using blueprint templates."""
    print("=== Using Templates Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        print("📋 Getting example templates...")
        templates = create_example_blueprints()
        
        print("🔨 Creating scenario from template...")
        template = templates["webhook_to_email"]
        scenario = creator.create_scenario(template)
        print(f"✅ Created scenario from template: {scenario['name']} (ID: {scenario['id']})")
        
        # Track for cleanup
        created_scenarios.append(scenario['id'])
        return scenario['id']
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_bulk_operations():
    """Demonstrate bulk scenario operations."""
    print("=== Bulk Operations Example ===")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        print("🔨 Creating multiple scenarios...")
        scenario_ids = []
        
        for i in range(3):
            blueprint = creator.create_simple_blueprint(
                name=f"Bulk Scenario {i+1}",
                description=f"Bulk created scenario {i+1}"
            )
            scenario = creator.create_scenario(blueprint)
            scenario_ids.append(scenario['id'])
            print(f"✅ Created scenario {i+1}: {scenario['name']} (ID: {scenario['id']})")
        
        # Track for cleanup
        created_scenarios.extend(scenario_ids)
        return scenario_ids
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def cleanup_scenarios(scenario_ids: Optional[List[int]] = None):
    """Clean up created scenarios."""
    if scenario_ids is None:
        scenario_ids = created_scenarios.copy()
    
    if not scenario_ids:
        print("🧹 No scenarios to clean up")
        return
    
    print(f"🧹 Cleaning up {len(scenario_ids)} scenarios...")
    
    try:
        config = get_make_config()
        creator = MakeBlueprintCreator(config)
        
        for scenario_id in scenario_ids:
            try:
                creator.delete_scenario(scenario_id)
                print(f"✅ Deleted scenario {scenario_id}")
            except Exception as e:
                print(f"⚠️ Failed to delete scenario {scenario_id}: {e}")
        
        # Clear the global list
        created_scenarios.clear()
        print("🎉 Cleanup completed")
        
    except Exception as e:
        print(f"❌ Cleanup error: {e}")


def main():
    """Main function that runs examples."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 Make.com Blueprint Creator - Examples")
    print("=" * 60)
    
    try:
        config = get_make_config()
        print(f"🔧 Using configuration: {config}")
        
        # Run all examples
        example_basic_usage()
        example_webhook_scenario()
        example_custom_blueprint()
        example_scenario_cloning()
        example_blueprint_update()
        example_using_templates()
        example_bulk_operations()
        
        print("\n🎉 Examples completed!")
        
        # Clean up all created scenarios
        cleanup_scenarios()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 