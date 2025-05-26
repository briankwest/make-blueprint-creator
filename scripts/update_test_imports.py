#!/usr/bin/env python3
"""
Script to update test file imports to use the new package structure.
"""

import os
import re
from pathlib import Path

def update_test_imports():
    """Update all test files to use new package imports."""
    
    # Define the import mappings
    import_mappings = {
        # Old app.py imports
        r'from app import \(\s*MakeConfig,\s*MakeBlueprintCreator,\s*MakeBlueprintError,\s*create_example_blueprints\s*\)': 
        'from make_blueprint_creator.core.config import MakeConfig\nfrom make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator\nfrom make_blueprint_creator.core.exceptions import MakeBlueprintError\nfrom make_blueprint_creator.cli.examples import create_example_blueprints',
        
        r'from app import \(\s*MakeConfig,\s*MakeBlueprintCreator,\s*MakeBlueprintError,\s*MakeAPIError\s*\)':
        'from make_blueprint_creator.core.config import MakeConfig\nfrom make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator\nfrom make_blueprint_creator.core.exceptions import MakeBlueprintError, MakeAPIError',
        
        r'from app import MakeBlueprintCreator, MakeConfig, MakeBlueprintError':
        'from make_blueprint_creator.core.config import MakeConfig\nfrom make_blueprint_creator.core.blueprint_creator import MakeBlueprintCreator\nfrom make_blueprint_creator.core.exceptions import MakeBlueprintError',
        
        # Old example.py imports
        r'from example import \(\s*create_example_blueprints,\s*create_webhook_to_email_blueprint,\s*create_http_to_database_blueprint,\s*create_timer_to_slack_blueprint,\s*create_google_sheets_to_email_blueprint,\s*create_file_processor_blueprint,\s*create_data_aggregator_blueprint,\s*create_notification_system_blueprint,\s*create_backup_system_blueprint,\s*create_monitoring_blueprint,\s*main\s*\)':
        'from make_blueprint_creator.cli.examples import (\n    create_example_blueprints,\n    create_webhook_to_email_blueprint,\n    create_http_to_database_blueprint,\n    create_timer_to_slack_blueprint,\n    create_google_sheets_to_email_blueprint,\n    create_file_processor_blueprint,\n    create_data_aggregator_blueprint,\n    create_notification_system_blueprint,\n    create_backup_system_blueprint,\n    create_monitoring_blueprint,\n    main\n)',
        
        # Old get_team_info.py imports
        r'from get_team_info import \(\s*get_user_info,\s*get_team_info,\s*get_organization_info,\s*list_user_teams,\s*list_team_members,\s*list_organization_teams,\s*main\s*\)':
        'from make_blueprint_creator.utils.team_info import (\n    get_user_info,\n    get_team_info,\n    get_organization_info,\n    list_user_teams,\n    list_team_members,\n    list_organization_teams\n)\nfrom make_blueprint_creator.cli.team_info import main',
        
        # Simple imports
        r"@patch\('app\.load_dotenv'\)": "@patch('make_blueprint_creator.cli.main.load_dotenv')",
        r"@patch\('app\.MakeBlueprintCreator'\)": "@patch('make_blueprint_creator.core.blueprint_creator.MakeBlueprintCreator')",
        r"@patch\('app\.MakeConfig'\)": "@patch('make_blueprint_creator.core.config.MakeConfig')",
        r"'app\.": "'make_blueprint_creator.cli.main.",
    }
    
    # Get all test files
    test_dir = Path('tests')
    test_files = list(test_dir.glob('test_*.py'))
    
    print(f"🔄 Updating imports in {len(test_files)} test files...")
    
    for test_file in test_files:
        print(f"   📝 Updating {test_file.name}")
        
        # Read the file
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Apply all mappings
        for old_pattern, new_import in import_mappings.items():
            content = re.sub(old_pattern, new_import, content, flags=re.MULTILINE | re.DOTALL)
        
        # Write back the file
        with open(test_file, 'w') as f:
            f.write(content)
    
    print("✅ All test imports updated successfully!")

if __name__ == '__main__':
    update_test_imports() 