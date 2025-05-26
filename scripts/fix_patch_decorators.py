#!/usr/bin/env python3
"""
Script to fix all patch decorators in test files to use the new package structure.
"""

import os
import re
from pathlib import Path

def fix_patch_decorators():
    """Fix all patch decorators to use new package imports."""
    
    # Define the patch mappings
    patch_mappings = {
        # get_team_info patches
        r"@patch\('get_team_info\.": "@patch('make_blueprint_creator.utils.team_info.",
        r"@patch\('get_team_info\.load_dotenv'\)": "@patch('make_blueprint_creator.cli.team_info.load_dotenv')",
        
        # example patches
        r"@patch\('example\.": "@patch('make_blueprint_creator.cli.examples.",
        
        # app patches (already fixed in previous script, but just in case)
        r"@patch\('app\.": "@patch('make_blueprint_creator.cli.main.",
    }
    
    # Get all test files
    test_dir = Path('tests')
    test_files = list(test_dir.glob('test_*.py'))
    
    print(f"🔄 Fixing patch decorators in {len(test_files)} test files...")
    
    for test_file in test_files:
        print(f"   📝 Fixing {test_file.name}")
        
        # Read the file
        with open(test_file, 'r') as f:
            content = f.read()
        
        # Apply all mappings
        for old_pattern, new_pattern in patch_mappings.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back the file
        with open(test_file, 'w') as f:
            f.write(content)
    
    print("✅ All patch decorators fixed successfully!")

if __name__ == '__main__':
    fix_patch_decorators() 