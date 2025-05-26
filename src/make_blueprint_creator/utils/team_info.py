"""
Team and organization information utilities for Make.com Blueprint Creator.

This module provides utilities for retrieving team and organization information
from the Make.com API, helping users identify their team and organization IDs.

Author: AI Assistant
Date: 2025-01-27
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


def make_api_request(
    endpoint: str, 
    api_token: str, 
    base_url: str = "https://us2.make.com/api/v2"
) -> Dict[str, Any]:
    """
    Make a request to the Make.com API.
    
    Args:
        endpoint (str): API endpoint to call
        api_token (str): Make.com API token
        base_url (str): API base URL
        
    Returns:
        Dict[str, Any]: API response data
        
    Raises:
        requests.RequestException: If the API request fails
    """
    url = f"{base_url}/{endpoint.lstrip('/')}"
    
    headers = {
        # Use 'Token' scheme for Make.com API authentication (as per official docs)
        'Authorization': f'Token {api_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    logger.debug(f"Making request to: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                logger.error(f"Error details: {json.dumps(error_detail, indent=2)}")
            except (ValueError, json.JSONDecodeError):
                logger.error(f"Error response: {e.response.text}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        raise


def get_user_info(api_token: str, base_url: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Make.com API.
    
    Args:
        api_token (str): Make.com API token
        base_url (str): API base URL
        
    Returns:
        Optional[Dict[str, Any]]: User information or None if failed
    """
    try:
        response = make_api_request('/users/me', api_token, base_url)
        # The /users/me endpoint returns user data under 'authUser' key
        user_data = response.get('authUser', {})
        if user_data:
            logger.info(f"Retrieved user info for: {user_data.get('name', 'Unknown')}")
            return user_data
        else:
            logger.warning("No user data found in response")
            return None
    except Exception as e:
        logger.error(f"Failed to get user info: {e}")
        return None


def get_organizations(api_token: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Get list of organizations for the authenticated user.
    
    Args:
        api_token (str): Make.com API token
        base_url (str): API base URL
        
    Returns:
        List[Dict[str, Any]]: List of organizations
    """
    try:
        response = make_api_request('/organizations', api_token, base_url)
        organizations = response.get('organizations', [])
        logger.info(f"Retrieved {len(organizations)} organizations")
        return organizations
    except Exception as e:
        logger.error(f"Failed to get organizations: {e}")
        return []


def get_teams_for_organization(
    api_token: str, 
    base_url: str, 
    organization_id: int
) -> List[Dict[str, Any]]:
    """
    Get list of teams for a specific organization.
    
    Args:
        api_token (str): Make.com API token
        base_url (str): API base URL
        organization_id (int): Organization ID to get teams for
        
    Returns:
        List[Dict[str, Any]]: List of teams in the organization
    """
    try:
        # According to Make.com API docs, teams endpoint requires organizationId parameter
        endpoint = f'/teams?organizationId={organization_id}'
        response = make_api_request(endpoint, api_token, base_url)
        teams = response.get('teams', [])
        logger.info(f"Retrieved {len(teams)} teams for organization {organization_id}")
        return teams
    except Exception as e:
        logger.error(f"Failed to get teams for organization {organization_id}: {e}")
        return []


def get_user_teams(api_token: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Get teams that the user belongs to by checking organizations and team roles.
    
    Args:
        api_token (str): Make.com API token
        base_url (str): API base URL
        
    Returns:
        List[Dict[str, Any]]: List of teams the user belongs to
    """
    try:
        # First get user info to get user ID
        user_info = get_user_info(api_token, base_url)
        if not user_info or 'id' not in user_info:
            logger.error("Could not get user ID, cannot check team roles")
            return []
        
        user_id = user_info['id']
        
        # Get organizations first
        organizations = get_organizations(api_token, base_url)
        if not organizations:
            logger.error("No organizations found, cannot get teams")
            return []
        
        teams_with_roles = []
        
        # For each organization, get teams and check user roles
        for org in organizations:
            org_id = org.get('id')
            if not org_id:
                continue
                
            # Get teams for this organization
            org_teams = get_teams_for_organization(api_token, base_url, org_id)
            
            for team in org_teams:
                team_id = team.get('id')
                if not team_id:
                    continue
                
                try:
                    # Check if user has a role in this team using the correct endpoint
                    # GET /teams/{teamId}/user-team-roles/{userId}
                    role_response = make_api_request(
                        f'/teams/{team_id}/user-team-roles/{user_id}', 
                        api_token, 
                        base_url
                    )
                    
                    user_team_role = role_response.get('userTeamRole', {})
                    if user_team_role:
                        # User has a role in this team, add team with role info
                        team_with_role = team.copy()
                        team_with_role['userRole'] = user_team_role.get('usersRoleId', 'Unknown')
                        team_with_role['changeable'] = user_team_role.get('changeable', False)
                        teams_with_roles.append(team_with_role)
                        
                except Exception as e:
                    # User might not have access to this team, which is normal
                    # Only log if it's not a 404 (user not in team)
                    if "404" not in str(e):
                        logger.warning(f"Could not check role for team {team.get('name')} (ID: {team_id}): {e}")
        
        logger.info(f"Found {len(teams_with_roles)} teams with user access")
        return teams_with_roles
        
    except Exception as e:
        logger.error(f"Failed to get user teams: {e}")
        return []


def get_recommended_config(api_token: str, base_url: str) -> Dict[str, Any]:
    """
    Get recommended configuration for Make.com API usage.
    
    This function analyzes the user's teams and organizations to provide
    recommended team_id and organization_id values for configuration.
    
    Args:
        api_token (str): Make.com API token
        base_url (str): API base URL
        
    Returns:
        Dict[str, Any]: Recommended configuration with team_id and organization_id
    """
    config = {
        'api_token': api_token,
        'base_url': base_url,
        'team_id': None,
        'organization_id': None,
        'recommendations': []
    }
    
    try:
        # Get user info
        user_info = get_user_info(api_token, base_url)
        if user_info:
            config['user_name'] = user_info.get('name')
            config['user_email'] = user_info.get('email')
        
        # Get organizations
        organizations = get_organizations(api_token, base_url)
        if organizations:
            # Use the first organization as default
            org = organizations[0]
            config['organization_id'] = org.get('id')
            config['organization_name'] = org.get('name')
            config['recommendations'].append(f"Organization: {org.get('name')} (ID: {org.get('id')})")
        
        # Get teams
        teams = get_user_teams(api_token, base_url)
        if teams:
            # Use the first team as default
            team = teams[0]
            config['team_id'] = team.get('id')
            config['team_name'] = team.get('name')
            config['recommendations'].append(f"Team: {team.get('name')} (ID: {team.get('id')})")
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to get recommended config: {e}")
        config['error'] = str(e)
        return config 