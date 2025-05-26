#!/usr/bin/env python3
"""
Make.com Blueprint Creator CLI

Main command-line interface for the Make.com Blueprint Creator.

Usage:
    make-blueprint

Author: AI Assistant
Date: 2025-01-27
"""

import os
import sys
import logging
from dotenv import load_dotenv

from ..core import MakeConfig, MakeBlueprintCreator, MakeConfigError


def main():
    """
    Main function for the blueprint creator CLI.
    
    This function demonstrates basic usage of the Make.com Blueprint Creator
    by creating a simple scenario and listing existing scenarios.
    """
    # Load environment variables
    load_dotenv()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Make.com Blueprint Creator")
    print("=" * 50)
    
    try:
        # Get configuration from environment
        api_token = os.getenv('MAKE_API_TOKEN')
        team_id = os.getenv('MAKE_TEAM_ID')
        organization_id = os.getenv('MAKE_ORGANIZATION_ID')
        base_url = os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
        
        if not api_token:
            print("❌ Error: MAKE_API_TOKEN environment variable is required")
            print("💡 Set your API token: export MAKE_API_TOKEN='your_token_here'")
            print("💡 Use 'make-team-info' to find your team/organization IDs")
            sys.exit(1)
        
        # Convert team_id and organization_id to integers if provided
        team_id_int = int(team_id) if team_id else None
        organization_id_int = int(organization_id) if organization_id else None
        
        if not team_id_int and not organization_id_int:
            print("❌ Error: Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID is required")
            print("💡 Use 'make-team-info' to find your team/organization IDs")
            sys.exit(1)
        
        # Create configuration - prioritize team_id over organization_id if both are set
        if team_id_int:
            config = MakeConfig(
                api_token=api_token,
                team_id=team_id_int,
                base_url=base_url
            )
        elif organization_id_int:
            config = MakeConfig(
                api_token=api_token,
                organization_id=organization_id_int,
                base_url=base_url
            )
        else:
            # This should never happen due to the check above, but for safety
            print("❌ Error: Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID is required")
            sys.exit(1)
        
        print(f"🔧 Configuration: {config}")
        print()
        
        # Create blueprint creator
        creator = MakeBlueprintCreator(config)
        
        # List existing scenarios
        print("📋 Listing existing scenarios...")
        scenarios = creator.list_scenarios()
        
        if scenarios:
            print(f"✅ Found {len(scenarios)} scenarios:")
            for i, scenario in enumerate(scenarios[:5], 1):  # Show first 5
                status = "🟢 Active" if scenario.get('isActive') else "🔴 Inactive"
                print(f"   {i}. {scenario.get('name', 'Untitled')} (ID: {scenario.get('id')}) - {status}")
            
            if len(scenarios) > 5:
                print(f"   ... and {len(scenarios) - 5} more scenarios")
        else:
            print("📝 No scenarios found")
        
        print()
        
        # Create a simple blueprint
        print("🔨 Creating a simple blueprint...")
        blueprint = creator.create_simple_blueprint(
            name="CLI Test Scenario",
            description="Created via CLI tool"
        )
        
        print("✅ Blueprint created successfully!")
        print(f"   Name: {blueprint.get('name')}")
        print(f"   Description: {blueprint.get('description')}")
        print(f"   Modules: {len(blueprint.get('flow', []))}")
        
        print()
        print("🎉 Make.com Blueprint Creator CLI completed successfully!")
        print("💡 Use 'make-examples' to see more comprehensive examples")
        
    except MakeConfigError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logging.exception("Detailed error information:")
        sys.exit(1)


if __name__ == '__main__':
    main() 