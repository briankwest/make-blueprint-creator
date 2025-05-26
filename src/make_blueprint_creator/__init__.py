"""
Make.com Blueprint Creator

A Python package for programmatically creating, managing, and deploying
Make.com automation scenarios (blueprints) via the Make.com API.

This package provides:
- MakeBlueprintCreator: Core class for scenario management
- MakeConfig: Configuration management
- Example blueprints and usage patterns
- Team and organization management utilities

Author: AI Assistant
Date: 2025-01-27
License: MIT
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@cursor.com"
__license__ = "MIT"

# Import main classes and functions for easy access
from .core import (
    MakeBlueprintCreator,
    MakeConfig,
    MakeBlueprintError,
    MakeAPIError,
    MakeConfigError,
    MakeBlueprintValidationError
)

from .utils import (
    make_api_request,
    get_user_info,
    get_organizations,
    get_user_teams,
    get_recommended_config
)

# Define what gets imported with "from make_blueprint_creator import *"
__all__ = [
    # Core classes
    'MakeBlueprintCreator',
    'MakeConfig', 
    'MakeBlueprintError',
    'MakeAPIError',
    'MakeConfigError',
    'MakeBlueprintValidationError',
    
    # Utility functions
    'make_api_request',
    'get_user_info',
    'get_organizations',
    'get_user_teams',
    'get_recommended_config',
    
    # Package metadata
    '__version__',
    '__author__',
    '__email__',
    '__license__',
]

# Package information
def get_version():
    """Get the package version."""
    return __version__

def get_info():
    """Get package information."""
    return {
        'name': 'make-blueprint-creator',
        'version': __version__,
        'author': __author__,
        'email': __email__,
        'license': __license__,
        'description': 'Programmatic Make.com automation scenario creator and manager',
    }
