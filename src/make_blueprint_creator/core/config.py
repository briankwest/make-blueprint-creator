"""
Configuration management for Make.com Blueprint Creator.

This module provides configuration classes and utilities for managing
Make.com API connections and settings.

Author: AI Assistant
Date: 2025-01-27
"""

import os
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
    
    @classmethod
    def from_env(cls) -> 'MakeConfig':
        """
        Create MakeConfig from environment variables.
        
        Environment variables used:
        - MAKE_API_TOKEN (required): Make.com API token
        - MAKE_TEAM_ID (conditional): Team ID for team-based access
        - MAKE_ORGANIZATION_ID (conditional): Organization ID for org-based access
        - MAKE_API_BASE_URL (optional): API base URL (defaults to US region)
        
        Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID must be provided.
        If both are provided, MAKE_TEAM_ID takes precedence.
        
        Returns:
            MakeConfig: Configuration instance
            
        Raises:
            MakeConfigError: If required environment variables are missing
            
        Example:
            >>> # Set environment variables first
            >>> os.environ['MAKE_API_TOKEN'] = 'your_token'
            >>> os.environ['MAKE_TEAM_ID'] = '123'
            >>> config = MakeConfig.from_env()
        """
        api_token = os.getenv('MAKE_API_TOKEN')
        team_id = os.getenv('MAKE_TEAM_ID')
        organization_id = os.getenv('MAKE_ORGANIZATION_ID')
        base_url = os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
        
        if not api_token:
            raise MakeConfigError(
                "MAKE_API_TOKEN environment variable is required. "
                "Set it with: export MAKE_API_TOKEN='your_token_here'"
            )
        
        if not team_id and not organization_id:
            raise MakeConfigError(
                "Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required. "
                "Set one with: export MAKE_TEAM_ID='your_team_id' or export MAKE_ORGANIZATION_ID='your_org_id'"
            )
        
        # Prioritize team_id over organization_id if both are set
        if team_id:
            try:
                team_id_int = int(team_id)
            except ValueError:
                raise MakeConfigError(f"MAKE_TEAM_ID must be a valid integer, got: {team_id}")
            
            return cls(
                api_token=api_token,
                base_url=base_url,
                team_id=team_id_int
            )
        elif organization_id:
            try:
                organization_id_int = int(organization_id)
            except ValueError:
                raise MakeConfigError(f"MAKE_ORGANIZATION_ID must be a valid integer, got: {organization_id}")
            
            return cls(
                api_token=api_token,
                base_url=base_url,
                organization_id=organization_id_int
            )
        else:
            # This should never happen due to the check above, but for type safety
            raise MakeConfigError(
                "Either MAKE_TEAM_ID or MAKE_ORGANIZATION_ID environment variable is required"
            )
    
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