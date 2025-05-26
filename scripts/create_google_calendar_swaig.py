#!/usr/bin/env python3
"""
Standalone Google Calendar SWAIG Blueprint Creator

This standalone script creates a Make.com scenario blueprint for integrating 
Google Calendar with SignalWire AI Gateway (SWAIG) without requiring the 
make_blueprint_creator package to be installed.

Usage:
    python create_google_calendar_swaig.py
    
Features:
- Prompts for Google Calendar email address
- Creates complete SWAIG scenario blueprint
- Saves blueprint as JSON file
- Can optionally deploy to Make.com if package is available

Environment Variables (optional for deployment):
    MAKE_API_TOKEN - Your Make.com API token
    MAKE_TEAM_ID - Your Make.com team ID (or MAKE_ORG_ID for organization)
"""

import json
import sys
import os
from typing import Dict, Any


def get_user_input() -> Dict[str, str]:
    """Collect user input for the blueprint configuration."""
    print("🎯 Google Calendar SWAIG Scenario Blueprint Creator")
    print("=" * 55)
    print()
    
    # Get email address
    while True:
        email = input("📧 Enter the Google Calendar email address: ").strip()
        if email and "@" in email:
            break
        print("❌ Please enter a valid email address.")
    
    # Get scenario name (optional)
    scenario_name = input("📝 Enter scenario name (press Enter for default): ").strip()
    if not scenario_name:
        scenario_name = "Google Calendar SWAIG Scenario"
    
    # Get webhook name (optional)
    webhook_name = input("🔗 Enter webhook name (press Enter for default): ").strip()
    if not webhook_name:
        webhook_name = "SWAIG Server"
    
    return {
        "email": email,
        "scenario_name": scenario_name,
        "webhook_name": webhook_name
    }


def create_blueprint_template(email: str, scenario_name: str, webhook_name: str) -> Dict[str, Any]:
    """Create the Google Calendar SWAIG blueprint with user's email."""
    
    # Base blueprint structure with email substitution
    blueprint = {
        "name": scenario_name,
        "flow": [
            # Webhook module
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
                    "advanced": True
                }
            },
            
            # Calendar validation module
            {
                "id": 22,
                "module": "google-calendar:getACalendar",
                "version": 5,
                "parameters": {"__IMTCONN__": 3499150},
                "mapper": {"calendar": email},
                "metadata": {
                    "designer": {"x": 72, "y": -256},
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
            
            # Function router
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


def try_deploy_scenario(blueprint: Dict[str, Any], scenario_name: str, email: str) -> bool:
    """Try to deploy the scenario using the make_blueprint_creator package if available."""
    try:
        # Try to import the package
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from make_blueprint_creator import MakeBlueprintCreator, MakeConfig
        
        # Initialize configuration from environment variables
        config = MakeConfig.from_env()
        creator = MakeBlueprintCreator(config)
        
        print("\n📡 Creating scenario in Make.com...")
        
        # Create the scenario with new hooks (automatically replaces hardcoded hook IDs)
        scenario = creator.create_scenario_with_new_hooks(
            blueprint=blueprint,
            webhook_name_prefix=f"Google Calendar SWAIG - {email}"
        )
        scenario_id = scenario.get('id') if isinstance(scenario, dict) else None
        
        print(f"✅ Scenario created successfully!")
        print(f"📋 Scenario ID: {scenario_id}")
        print(f"🌐 Scenario Name: {scenario_name}")
        print(f"📧 Calendar Email: {email}")
        
        # Ask if user wants to activate the scenario
        if scenario_id:
            activate = input("\n⚡ Do you want to activate this scenario? (y/N): ").strip().lower()
            
            if activate in ['y', 'yes']:
                creator.activate_scenario(scenario_id)
                print("✅ Scenario activated successfully!")
            else:
                print("ℹ️  Scenario created but not activated. You can activate it later in Make.com.")
        else:
            print("⚠️  Warning: Could not extract scenario ID from response.")
        
        return True
        
    except ImportError:
        print("ℹ️  make_blueprint_creator package not found. Blueprint saved as JSON file only.")
        return False
    except Exception as e:
        print(f"❌ Error deploying scenario: {e}")
        print("💡 You can still use the saved blueprint file to import manually.")
        return False


def main():
    """Main function to create the Google Calendar SWAIG scenario."""
    import argparse
    
    # Simple argument parsing for help
    parser = argparse.ArgumentParser(
        description="Standalone Google Calendar SWAIG Blueprint Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This standalone script creates Make.com scenario blueprints for Google Calendar
SWAIG integration without requiring the make_blueprint_creator package.

Examples:
  python create_google_calendar_swaig.py
  
Environment Variables (optional for deployment):
  MAKE_API_TOKEN    Your Make.com API token
  MAKE_TEAM_ID      Your Make.com team ID (or MAKE_ORG_ID for organization)
        """
    )
    
    parser.add_argument(
        "--help-only", 
        action="store_true", 
        help="Show this help message and exit"
    )
    
    # Parse args but don't exit on help
    args, unknown = parser.parse_known_args()
    
    if args.help_only or '--help' in sys.argv or '-h' in sys.argv:
        parser.print_help()
        return
    
    try:
        # Get user input
        config = get_user_input()
        
        print(f"\n🔧 Creating blueprint for {config['email']}...")
        
        # Create the blueprint
        blueprint = create_blueprint_template(
            email=config["email"],
            scenario_name=config["scenario_name"],
            webhook_name=config["webhook_name"]
        )
        
        # Save blueprint to file
        safe_email = config['email'].replace('@', '_at_').replace('.', '_')
        blueprint_file = f"google_calendar_swaig_{safe_email}.json"
        
        with open(blueprint_file, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        print(f"✅ Blueprint saved to: {blueprint_file}")
        
        # Ask if user wants to deploy the scenario
        deploy_scenario = input("\n🚀 Do you want to deploy this scenario to Make.com? (y/N): ").strip().lower()
        
        if deploy_scenario in ['y', 'yes']:
            success = try_deploy_scenario(blueprint, config["scenario_name"], config["email"])
            if not success:
                print("💡 To deploy later, install the make_blueprint_creator package and run:")
                print(f"   python -c \"from make_blueprint_creator import *; creator = MakeBlueprintCreator(MakeConfig.from_env()); creator.create_scenario(json.load(open('{blueprint_file}')))\"")
        else:
            print("ℹ️  Blueprint created but not deployed. Use the JSON file to import manually.")
        
        print(f"\n🎉 Google Calendar SWAIG scenario blueprint ready!")
        print(f"📁 Blueprint file: {blueprint_file}")
        print(f"📧 Configured for: {config['email']}")
        
        # Show usage instructions
        print(f"\n📋 Usage Instructions:")
        print(f"1. Import {blueprint_file} into Make.com")
        print(f"2. Configure your Google Calendar connection")
        print(f"3. Set up the webhook URL in your SWAIG application")
        print(f"4. Test with SWAIG functions: 'events' and 'freebusy'")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 