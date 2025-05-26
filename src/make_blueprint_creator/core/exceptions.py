"""
Custom exceptions for Make.com Blueprint Creator.

This module defines custom exception classes used throughout the package
for better error handling and debugging.

Author: AI Assistant
Date: 2025-01-27
"""

from typing import Optional


class MakeBlueprintError(Exception):
    """
    Base exception for Make.com blueprint operations.
    
    This exception is raised when there are errors in blueprint creation,
    API communication, or other Make.com related operations.
    
    Example:
        >>> raise MakeBlueprintError("Failed to create scenario")
    """
    pass


class MakeAPIError(MakeBlueprintError):
    """
    Exception raised for Make.com API communication errors.
    
    This exception is raised when API requests fail due to network issues,
    authentication problems, or server errors.
    
    Attributes:
        status_code (int): HTTP status code if available
        response_data (dict): API response data if available
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class MakeConfigError(MakeBlueprintError):
    """
    Exception raised for configuration errors.
    
    This exception is raised when there are issues with the Make.com
    configuration such as missing API tokens or invalid team IDs.
    """
    pass


class MakeBlueprintValidationError(MakeBlueprintError):
    """
    Exception raised for blueprint validation errors.
    
    This exception is raised when blueprint data is invalid or
    doesn't meet Make.com API requirements.
    """
    pass 