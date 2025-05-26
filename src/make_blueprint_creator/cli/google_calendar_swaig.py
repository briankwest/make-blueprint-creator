#!/usr/bin/env python3
"""
Google Calendar SWAIG Blueprint CLI

Command-line interface for creating Google Calendar SWAIG scenario blueprints.
This CLI tool creates Make.com scenarios that integrate Google Calendar with
SignalWire AI Gateway (SWAIG).

Usage:
    make-google-calendar-swaig [OPTIONS]
    
Features:
- Interactive email address input
- Customizable scenario and webhook names
- Blueprint generation and optional deployment
- Comprehensive error handling and validation
"""

import argparse
import json
import sys
from typing import Dict, Any

from ..core.config import MakeConfig
from ..core.blueprint_creator import MakeBlueprintCreator
from ..core.exceptions import MakeBlueprintError


def get_user_input(args: argparse.Namespace) -> Dict[str, str]:
    """
    Collect user input for the blueprint configuration.
    
    Args:
        args: Command line arguments
        
    Returns:
        Dict containing user configuration
    """
    config = {}
    
    # Get email address
    if args.email:
        config["email"] = args.email
    else:
        while True:
            email = input("📧 Enter the Google Calendar email address: ").strip()
            if email and "@" in email:
                config["email"] = email
                break
            print("❌ Please enter a valid email address.")
    
    # Get scenario name
    if args.name:
        config["scenario_name"] = args.name
    else:
        scenario_name = input("📝 Enter scenario name (press Enter for default): ").strip()
        config["scenario_name"] = scenario_name if scenario_name else "Google Calendar SWAIG Scenario"
    
    # Get webhook name
    if args.webhook_name:
        config["webhook_name"] = args.webhook_name
    else:
        webhook_name = input("🔗 Enter webhook name (press Enter for default): ").strip()
        config["webhook_name"] = webhook_name if webhook_name else "SWAIG Server"
    
    return config


def create_google_calendar_swaig_blueprint(email: str, scenario_name: str, webhook_name: str) -> Dict[str, Any]:
    """
    Create the complete Google Calendar SWAIG scenario blueprint.
    
    Args:
        email: Google Calendar email address
        scenario_name: Name for the scenario
        webhook_name: Name for the webhook
        
    Returns:
        Complete blueprint dictionary
    """
    blueprint = {
        "name": scenario_name,
        "flow": [
            # Module 1: Custom Webhook (SWAIG Server)
            {
                "id": 1,
                "module": "gateway:CustomWebHook",
                "version": 1,
                "parameters": {"hook": 836593, "maxResults": 1},
                "mapper": {},
                "metadata": {
                    "designer": {"x": -245, "y": -256},
                    "restore": {
                        "parameters": {
                            "hook": {"data": {"editable": "true"}, "label": webhook_name}
                        }
                    },
                    "parameters": [
                        {"name": "hook", "type": "hook:gateway-webhook", "label": "Webhook", "required": True},
                        {"name": "maxResults", "type": "number", "label": "Maximum number of results"}
                    ],
                    "interface": [
                        {"name": "app_name", "type": "text"},
                        {
                            "name": "global_data",
                            "spec": [
                                {"name": "caller_id_name", "type": "text"},
                                {"name": "caller_id_number", "type": "text"}
                            ],
                            "type": "collection"
                        },
                        {"name": "project_id", "type": "text"},
                        {"name": "space_id", "type": "text"},
                        {"name": "caller_id_name", "type": "text"},
                        {"name": "caller_id_num", "type": "text"},
                        {"name": "channel_active", "type": "boolean"},
                        {"name": "channel_offhook", "type": "boolean"},
                        {"name": "channel_ready", "type": "boolean"},
                        {"name": "content_type", "type": "text"},
                        {"name": "version", "type": "text"},
                        {"name": "content_disposition", "type": "text"},
                        {"name": "function", "type": "text"},
                        {
                            "name": "argument",
                            "spec": [
                                {
                                    "name": "parsed",
                                    "spec": {
                                        "spec": [
                                            {"name": "start_time", "type": "text"},
                                            {"name": "length", "type": "number"},
                                            {"name": "timezone", "type": "text"},
                                            {"name": "email", "type": "text"},
                                            {"name": "summary", "type": "text"},
                                            {"name": "description", "type": "text"},
                                            {"name": "location", "type": "text"}
                                        ],
                                        "type": "collection"
                                    },
                                    "type": "array"
                                },
                                {"name": "raw", "type": "text"}
                            ],
                            "type": "collection"
                        },
                        {"name": "call_id", "type": "text"},
                        {"name": "ai_session_id", "type": "text"},
                        {"name": "purpose", "type": "text"},
                        {
                            "name": "__IMTHEADERS__",
                            "spec": [
                                {"name": "name", "type": "text", "label": "Name"},
                                {"name": "value", "type": "text", "label": "Value"}
                            ],
                            "type": "array",
                            "label": "Headers"
                        },
                        {"name": "__IMTMETHOD__", "type": "text", "label": "Method"}
                    ],
                    "advanced": True
                }
            },
            
            # Module 22: Get Calendar (for validation)
            {
                "id": 22,
                "module": "google-calendar:getACalendar",
                "version": 5,
                "parameters": {"__IMTCONN__": 3499150},
                "mapper": {"calendar": email},
                "metadata": {
                    "designer": {"x": 72, "y": -256},
                    "restore": {
                        "expect": {"calendar": {"mode": "edit"}},
                        "parameters": {
                            "__IMTCONN__": {
                                "data": {"scoped": "true", "connection": "google"},
                                "label": f"My Google connection ({email})"
                            }
                        }
                    },
                    "parameters": [
                        {"name": "__IMTCONN__", "type": "account:google", "label": "Connection", "required": True}
                    ],
                    "expect": [
                        {"mode": "edit", "name": "calendar", "type": "select", "label": "Calendar ID", "required": True}
                    ]
                },
                "onerror": [
                    {
                        "id": 27,
                        "module": "json:CreateJSON",
                        "version": 1,
                        "parameters": {"type": 111573, "space": ""},
                        "mapper": {"response": "{{22.error.message}}"},
                        "metadata": {"designer": {"x": 56, "y": 89}}
                    },
                    {
                        "id": 28,
                        "module": "gateway:WebhookRespond",
                        "version": 1,
                        "parameters": {},
                        "mapper": {"status": "200", "body": "{{27.json}}", "headers": []},
                        "metadata": {"designer": {"x": 337, "y": 209}}
                    }
                ]
            },
            
            # Module 2: Function Router
            {
                "id": 2,
                "module": "builtin:BasicRouter",
                "version": 1,
                "mapper": None,
                "metadata": {"designer": {"x": 372, "y": -406}},
                "routes": [
                    # Route 1: Create Event
                    {
                        "flow": [
                            {
                                "id": 11,
                                "module": "google-calendar:createAnEvent",
                                "version": 5,
                                "parameters": {"__IMTCONN__": 3499150},
                                "filter": {
                                    "name": "",
                                    "conditions": [
                                        [{"a": "{{1.function}}", "b": "events", "o": "text:equal"}]
                                    ]
                                },
                                "mapper": {
                                    "start": "{{1.argument.parsed[].start_time}}",
                                    "select": "detail",
                                    "summary": "{{1.argument.parsed[].summary}}",
                                    "calendar": email,
                                    "duration": "{{1.argument.parsed[].length}}",
                                    "location": "{{1.argument.parsed[].location}}",
                                    "overrides": [{"method": "popup", "minutes": "10"}],
                                    "visibility": "default",
                                    "allDayEvent": False,
                                    "description": "{{1.argument.parsed[].description}}",
                                    "sendUpdates": "all",
                                    "transparency": "opaque",
                                    "conferenceDate": False,
                                    "guestPermissions": {
                                        "guestsCanModify": False,
                                        "guestsCanInviteOthers": True,
                                        "guestsCanSeeOtherGuests": True
                                    }
                                },
                                "metadata": {
                                    "designer": {"x": 700, "y": -593},
                                    "restore": {
                                        "parameters": {
                                            "__IMTCONN__": {
                                                "data": {"scoped": "true", "connection": "google"},
                                                "label": f"My Google connection ({email})"
                                            }
                                        }
                                    },
                                    "advanced": True
                                },
                                "onerror": [
                                    {
                                        "id": 18,
                                        "module": "json:CreateJSON",
                                        "version": 1,
                                        "parameters": {"type": 110985, "space": ""},
                                        "mapper": {"response": "Event wasn't created successfully"},
                                        "metadata": {"designer": {"x": 707, "y": -288}}
                                    },
                                    {
                                        "id": 19,
                                        "module": "gateway:WebhookRespond",
                                        "version": 1,
                                        "parameters": {},
                                        "mapper": {"body": "{{18.json}}", "status": "200", "headers": []},
                                        "metadata": {"designer": {"x": 996, "y": -288}}
                                    }
                                ]
                            },
                            {
                                "id": 16,
                                "module": "json:CreateJSON",
                                "version": 1,
                                "parameters": {"type": 110984, "space": ""},
                                "mapper": {"response": "Event created successfully"},
                                "metadata": {"designer": {"x": 1008, "y": -589}}
                            },
                            {
                                "id": 17,
                                "module": "gateway:WebhookRespond",
                                "version": 1,
                                "parameters": {},
                                "mapper": {"body": "{{16.json}}", "status": "200", "headers": []},
                                "metadata": {"designer": {"x": 1312, "y": -590}}
                            }
                        ]
                    },
                    # Route 2: Check Free/Busy
                    {
                        "flow": [
                            {
                                "id": 7,
                                "module": "google-calendar:getFreeBusyInformation",
                                "version": 5,
                                "parameters": {"__IMTCONN__": 3499150},
                                "filter": {
                                    "name": "",
                                    "conditions": [
                                        [{"a": "{{1.function}}", "b": "freebusy", "o": "text:equal"}]
                                    ]
                                },
                                "mapper": {
                                    "item": [{"id": email}],
                                    "timeMax": "{{addMinutes(1.argument.parsed[].start_time; 1.argument.parsed[].length)}}",
                                    "timeMin": "{{1.argument.parsed[].start_time}}"
                                },
                                "metadata": {
                                    "designer": {"x": 695, "y": -22},
                                    "restore": {
                                        "parameters": {
                                            "__IMTCONN__": {
                                                "data": {"scoped": "true", "connection": "google"},
                                                "label": f"My Google connection ({email})"
                                            }
                                        }
                                    }
                                },
                                "onerror": [
                                    {
                                        "id": 20,
                                        "module": "json:CreateJSON",
                                        "version": 1,
                                        "parameters": {"type": 110986, "space": ""},
                                        "mapper": {"response": "Error checking that time try a different time"},
                                        "metadata": {"designer": {"x": 708, "y": 291}}
                                    },
                                    {
                                        "id": 21,
                                        "module": "gateway:WebhookRespond",
                                        "version": 1,
                                        "parameters": {},
                                        "mapper": {"body": "{{20.json}}", "status": "200", "headers": []},
                                        "metadata": {"designer": {"x": 1018, "y": 287}}
                                    }
                                ]
                            },
                            {
                                "id": 8,
                                "module": "builtin:BasicRouter",
                                "version": 1,
                                "mapper": None,
                                "metadata": {"designer": {"x": 998, "y": -20}},
                                "routes": [
                                    # Free time response
                                    {
                                        "flow": [
                                            {
                                                "id": 23,
                                                "module": "json:CreateJSON",
                                                "version": 1,
                                                "parameters": {"type": 110987, "space": ""},
                                                "filter": {
                                                    "name": "free",
                                                    "conditions": [
                                                        [{"a": f"{{{{length(7.calendars.`{email}`.busy)}}}}", "b": "0", "o": "text:equal"}]
                                                    ]
                                                },
                                                "mapper": {"response": "Time is available"},
                                                "metadata": {"designer": {"x": 1257, "y": -140}}
                                            },
                                            {
                                                "id": 24,
                                                "module": "gateway:WebhookRespond",
                                                "version": 1,
                                                "parameters": {},
                                                "mapper": {"body": "{{23.json}}", "status": "200", "headers": []},
                                                "metadata": {"designer": {"x": 1559, "y": -139}}
                                            }
                                        ]
                                    },
                                    # Busy time response
                                    {
                                        "flow": [
                                            {
                                                "id": 25,
                                                "module": "json:CreateJSON",
                                                "version": 1,
                                                "parameters": {"type": 110989, "space": ""},
                                                "filter": {
                                                    "name": "busy",
                                                    "conditions": [
                                                        [{"a": f"{{{{length(7.calendars.`{email}`.busy)}}}}", "b": "0", "o": "number:greater"}]
                                                    ]
                                                },
                                                "mapper": {"response": "Time is NOT available"},
                                                "metadata": {"designer": {"x": 1259, "y": 111}}
                                            },
                                            {
                                                "id": 26,
                                                "module": "gateway:WebhookRespond",
                                                "version": 1,
                                                "parameters": {},
                                                "mapper": {"body": "{{25.json}}", "status": "200", "headers": []},
                                                "metadata": {"designer": {"x": 1569, "y": 107}}
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        "metadata": {
            "instant": True,
            "version": 1,
            "scenario": {
                "roundtrips": 1,
                "maxErrors": 3,
                "autoCommit": True,
                "autoCommitTriggerLast": True,
                "sequential": False,
                "slots": None,
                "confidential": False,
                "dataloss": False,
                "dlq": False,
                "freshVariables": False
            },
            "designer": {"orphans": []},
            "zone": "us2.make.com",
            "notes": [
                {
                    "moduleIds": [2],
                    "content": "<p>Function Router</p>",
                    "isFilterNote": False,
                    "metadata": {"color": "#9138FE"}
                }
            ]
        }
    }
    
    return blueprint


def main():
    """Main CLI function for Google Calendar SWAIG blueprint creation."""
    parser = argparse.ArgumentParser(
        description="Create Google Calendar SWAIG scenario blueprints for Make.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  make-google-calendar-swaig
  make-google-calendar-swaig --email user@example.com
  make-google-calendar-swaig --email user@example.com --name "My Calendar Bot" --no-deploy
  make-google-calendar-swaig --output-only --email user@example.com

Environment Variables:
  MAKE_API_TOKEN    Your Make.com API token (required for deployment)
  MAKE_TEAM_ID      Your Make.com team ID (or MAKE_ORG_ID for organization)
        """
    )
    
    parser.add_argument(
        "--email", "-e",
        help="Google Calendar email address"
    )
    
    parser.add_argument(
        "--name", "-n",
        help="Scenario name (default: 'Google Calendar SWAIG Scenario')"
    )
    
    parser.add_argument(
        "--webhook-name", "-w",
        help="Webhook name (default: 'SWAIG Server')"
    )
    
    parser.add_argument(
        "--output-file", "-o",
        help="Output file for blueprint JSON (default: auto-generated)"
    )
    
    parser.add_argument(
        "--output-only",
        action="store_true",
        help="Only create blueprint file, don't offer deployment"
    )
    
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Don't offer to deploy the scenario"
    )
    
    parser.add_argument(
        "--activate",
        action="store_true",
        help="Automatically activate the scenario after creation"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    try:
        if not args.quiet:
            print("🎯 Google Calendar SWAIG Scenario Blueprint Creator")
            print("=" * 55)
            print()
        
        # Get user input
        config = get_user_input(args)
        
        if not args.quiet:
            print(f"\n🔧 Creating blueprint for {config['email']}...")
        
        # Create the blueprint
        blueprint = create_google_calendar_swaig_blueprint(
            email=config["email"],
            scenario_name=config["scenario_name"],
            webhook_name=config["webhook_name"]
        )
        
        # Determine output file
        if args.output_file:
            blueprint_file = args.output_file
        else:
            safe_email = config['email'].replace('@', '_at_').replace('.', '_')
            blueprint_file = f"google_calendar_swaig_{safe_email}.json"
        
        # Save blueprint to file
        with open(blueprint_file, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        if not args.quiet:
            print(f"✅ Blueprint saved to: {blueprint_file}")
        
        # Handle deployment
        if not args.output_only and not args.no_deploy:
            deploy_scenario = True
            if not args.activate:
                deploy_input = input("\n🚀 Do you want to deploy this scenario to Make.com? (y/N): ").strip().lower()
                deploy_scenario = deploy_input in ['y', 'yes']
            
            if deploy_scenario:
                try:
                    # Initialize Make.com configuration
                    make_config = MakeConfig.from_env()
                    creator = MakeBlueprintCreator(make_config)
                    
                    if not args.quiet:
                        print("\n📡 Creating scenario in Make.com...")
                    
                    # Create the scenario with new hooks (automatically replaces hardcoded hook IDs)
                    scenario = creator.create_scenario_with_new_hooks(
                        blueprint=blueprint,
                        webhook_name_prefix=f"Google Calendar SWAIG - {config['email']}"
                    )
                    scenario_id = scenario.get('id')
                    webhooks = scenario.get('webhooks', [])
                    
                    print(f"✅ Scenario created successfully!")
                    print(f"📋 Scenario ID: {scenario_id}")
                    print(f"🌐 Scenario Name: {config['scenario_name']}")
                    print(f"📧 Calendar Email: {config['email']}")
                    
                    # Display webhook URLs
                    if webhooks:
                        print(f"\n🔗 Webhook URLs:")
                        for webhook in webhooks:
                            print(f"   📡 {webhook['name']}: {webhook['url']}")
                        
                        # Show the primary webhook URL prominently
                        primary_webhook = webhooks[0] if webhooks else None
                        if primary_webhook:
                            print(f"\n🎯 Primary SWAIG Webhook URL:")
                            print(f"   {primary_webhook['url']}")
                            print(f"\n💡 Use this URL in your SWAIG application configuration.")
                    
                    # Handle activation
                    if args.activate and scenario_id:
                        creator.activate_scenario(scenario_id)
                        print("✅ Scenario activated successfully!")
                    elif scenario_id:
                        activate_input = input("\n⚡ Do you want to activate this scenario? (y/N): ").strip().lower()
                        if activate_input in ['y', 'yes']:
                            creator.activate_scenario(scenario_id)
                            print("✅ Scenario activated successfully!")
                        else:
                            print("ℹ️  Scenario created but not activated. You can activate it later in Make.com.")
                    else:
                        print("⚠️  Warning: Could not extract scenario ID from response.")
                            
                except MakeBlueprintError as e:
                    print(f"❌ Error creating scenario: {e}")
                    print("💡 You can still use the saved blueprint file to import manually.")
                    sys.exit(1)
            else:
                if not args.quiet:
                    print("ℹ️  Blueprint created but not deployed. Use the JSON file to import manually.")
        
        if not args.quiet:
            print(f"\n🎉 Google Calendar SWAIG scenario blueprint ready!")
            print(f"📁 Blueprint file: {blueprint_file}")
            print(f"📧 Configured for: {config['email']}")
            
            # Show usage instructions
            print(f"\n📋 Usage Instructions:")
            if not args.output_only and not args.no_deploy:
                print(f"1. Configure your Google Calendar connection in Make.com")
                print(f"2. Use the webhook URL shown above in your SWAIG application")
                print(f"3. Test with SWAIG functions: 'events' and 'freebusy'")
            else:
                print(f"1. Import {blueprint_file} into Make.com")
                print(f"2. Configure your Google Calendar connection")
                print(f"3. Set up the webhook URL in your SWAIG application")
                print(f"4. Test with SWAIG functions: 'events' and 'freebusy'")
        
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 