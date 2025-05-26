#!/usr/bin/env python3
"""
Make.com Team and Organization ID Retriever CLI

This command-line tool helps you find your Make.com Team ID and Organization ID
by making API requests to the Make.com API.

Usage:
    make-team-info

Author: AI Assistant
Date: 2025-01-27
"""

import os
import sys
from dotenv import load_dotenv

from ..utils.team_info import (
    get_user_info,
    get_organizations,
    get_user_teams,
    get_teams_for_organization
)


def main():
    """
    Main function for the team info CLI tool.
    
    This function retrieves and displays team and organization information
    for the authenticated Make.com user.
    """
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    api_token = os.getenv('MAKE_API_TOKEN')
    base_url = os.getenv('MAKE_API_BASE_URL', 'https://us2.make.com/api/v2')
    
    if not api_token:
        print("❌ Error: MAKE_API_TOKEN environment variable is required")
        print("💡 Set your API token: export MAKE_API_TOKEN='your_token_here'")
        sys.exit(1)
    
    print("🔍 Make.com Team and Organization ID Retriever")
    print("=" * 60)
    print(f"🌍 Using API endpoint: {base_url}")
    print(f"🔑 API Token: {api_token[:12]}...")
    print()
    
    try:
        # Get user information
        print("👤 Getting user information...")
        user_info = get_user_info(api_token, base_url)
        if user_info:
            print(f"   ✅ User: {user_info.get('name', 'Unknown')} ({user_info.get('email', 'No email')})")
            print(f"   📧 Email: {user_info.get('email', 'No email')}")
            print(f"   🆔 User ID: {user_info.get('id', 'Unknown')}")
        else:
            print("   ❌ Failed to get user information")
            sys.exit(1)
        
        print()
        
        # Get organizations
        print("🏢 Getting organizations...")
        organizations = get_organizations(api_token, base_url)
        if organizations:
            print(f"   ✅ Found {len(organizations)} organization(s):")
            for i, org in enumerate(organizations, 1):
                print(f"   {i}. Organization: {org.get('name', 'Unknown')}")
                print(f"      🆔 Organization ID: {org.get('id', 'Unknown')}")
                print(f"      👑 Role: {org.get('role', 'Unknown')}")
                print(f"      📊 Status: {org.get('status', 'Unknown')}")
        else:
            print("   ❌ No organizations found")
        
        print()
        
        # Get teams
        print("👥 Getting teams...")
        teams = get_user_teams(api_token, base_url)
        if teams:
            print(f"   ✅ Found {len(teams)} team(s):")
            for i, team in enumerate(teams, 1):
                print(f"   {i}. Team: {team.get('name', 'Unknown')}")
                print(f"      🆔 Team ID: {team.get('id', 'Unknown')}")
                print(f"      👑 Your Role: {team.get('userRole', 'Unknown')}")
                print(f"      🏢 Organization ID: {team.get('organizationId', 'Unknown')}")
        else:
            print("   ❌ No teams found")
        
        print()
        
        # Get teams by organization
        if organizations:
            print("👥 Getting teams by organization...")
            for org in organizations:
                org_id = org.get('id')
                org_name = org.get('name', 'Unknown')
                if org_id:
                    print(f"   🔍 Getting teams for organization '{org_name}' (ID: {org_id})...")
                    org_teams = get_teams_for_organization(api_token, base_url, org_id)
                    if org_teams:
                        print(f"      ✅ Found {len(org_teams)} team(s) in this organization:")
                        for team in org_teams:
                            print(f"         - {team.get('name', 'Unknown')} (ID: {team.get('id', 'Unknown')})")
                    else:
                        print(f"      ❌ No teams found in organization {org_name}")
        
        print()
        
        # Provide summary and recommendations
        print("📋 Summary and Recommendations:")
        print("=" * 40)
        
        if teams:
            recommended_team = teams[0]
            print(f"✅ Recommended Team ID: {recommended_team.get('id')}")
            print(f"   Team Name: {recommended_team.get('name')}")
            print("✅ Organization ID: {recommended_team.get('organizationId')}")
            print("   💡 You can use either team_id OR organization_id in your configuration")
        
        if organizations:
            recommended_org = organizations[0]
            print(f"✅ Organization ID: {recommended_org.get('id')}")
            print(f"   Organization Name: {recommended_org.get('name')}")
            print("   💡 You can use organization_id instead of team_id for organization-wide access")
        
        print()
        print("🔧 Environment Variable Setup:")
        if teams:
            print(f"export MAKE_TEAM_ID='{teams[0].get('id')}'")
        if organizations:
            print(f"export MAKE_ORGANIZATION_ID='{organizations[0].get('id')}'")
        print(f"export MAKE_API_BASE_URL='{base_url}'")
        
        print()
        print("📝 .env File Example:")
        print("MAKE_API_TOKEN=your_api_token_here")
        if teams:
            print(f"MAKE_TEAM_ID={teams[0].get('id')}")
        if organizations:
            print(f"MAKE_ORGANIZATION_ID={organizations[0].get('id')}")
        print(f"MAKE_API_BASE_URL={base_url}")
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 