"""
Configuration management for Make.com Blueprint Creator.

This module provides configuration classes and utilities for managing
Make.com API connections and settings.

Author: AI Assistant
Date: 2025-01-27
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .exceptions import MakeConfigError


@dataclass
class MakeConfig:
    """
    Configuration for Make.com API connection.
    
    This class holds all the necessary configuration for connecting to
    the Make.com API, including authentication and endpoint information.
    
    Attributes:
        api_token (str): Make.com API token for authentication
        base_url (str): Base URL for Make.com API (defaults to US region)
        team_id (Optional[int]): Team ID for team-based operations
        organization_id (Optional[int]): Organization ID for org-based operations
        
    Example:
        >>> config = MakeConfig(
        ...     api_token="your_token",
        ...     team_id=123456
        ... )
        >>> # Or for organization-based access:
        >>> config = MakeConfig(
        ...     api_token="your_token",
        ...     organization_id=789012
        ... )
    """
    api_token: str
    base_url: str = "https://us2.make.com/api/v2"
    team_id: Optional[int] = None
    organization_id: Optional[int] = None

    def __post_init__(self):
        """
        Validate configuration after initialization.
        
        Raises:
            MakeConfigError: If configuration is invalid
        """
        if not self.api_token:
            raise MakeConfigError("API token is required")
        if not self.api_token.strip():
            raise MakeConfigError("API token cannot be empty")
        if not self.team_id and not self.organization_id:
            raise MakeConfigError("Either team_id or organization_id must be provided")
        if self.team_id and self.organization_id:
            raise MakeConfigError("Cannot specify both team_id and organization_id")
        
        # Validate base URL format
        if not self.base_url.startswith(('http://', 'https://')):
            raise MakeConfigError("Base URL must start with http:// or https://")
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
    
    @property
    def is_organization_based(self) -> bool:
        """Check if this configuration is for organization-based access."""
        return self.organization_id is not None
    
    @property
    def is_team_based(self) -> bool:
        """Check if this configuration is for team-based access."""
        return self.team_id is not None
    
    def get_default_params(self) -> Dict[str, Any]:
        """
        Get default query parameters for API requests.
        
        Returns:
            dict: Default parameters based on configuration
        """
        if self.organization_id:
            return {'organizationId': str(self.organization_id)}
        elif self.team_id:
            return {'teamId': str(self.team_id)}
        return {}
    
    def __repr__(self) -> str:
        """String representation of the configuration (without exposing token)."""
        token_preview = f"{self.api_token[:8]}..." if len(self.api_token) > 8 else "***"
        if self.organization_id:
            return f"MakeConfig(organization_id={self.organization_id}, token={token_preview})"
        else:
            return f"MakeConfig(team_id={self.team_id}, token={token_preview})" 