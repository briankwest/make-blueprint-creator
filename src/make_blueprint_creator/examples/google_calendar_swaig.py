#!/usr/bin/env python3
"""
Google Calendar SWAIG Scenario Blueprint Creator

This script creates a Make.com scenario blueprint for integrating Google Calendar
with SignalWire AI Gateway (SWAIG). The scenario handles two main functions:
1. Creating calendar events
2. Checking free/busy status

The script prompts for the Google Calendar email address to use instead of
hardcoded values.

Usage:
    python google_calendar_swaig.py
    
Environment Variables Required:
    MAKE_API_TOKEN - Your Make.com API token
    MAKE_TEAM_ID - Your Make.com team ID (or MAKE_ORG_ID for organization)
"""

import json
import sys
from typing import Dict, Any

try:
    from make_blueprint_creator import MakeBlueprintCreator, MakeConfig
except ImportError:
    # If running as standalone script, add parent directory to path
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from make_blueprint_creator import MakeBlueprintCreator, MakeConfig


def get_user_input() -> Dict[str, str]:
    """
    Collect user input for the blueprint configuration.
    
    Returns:
        Dict containing user configuration
    """
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
                "parameters": {
                    "hook": 836593,
                    "maxResults": 1
                },
                "mapper": {},
                "metadata": {
                    "designer": {"x": -245, "y": -256},
                    "restore": {
                        "parameters": {
                            "hook": {
                                "data": {"editable": "true"},
                                "label": webhook_name
                            }
                        }
                    },
                    "parameters": [
                        {
                            "name": "hook",
                            "type": "hook:gateway-webhook",
                            "label": "Webhook",
                            "required": True
                        },
                        {
                            "name": "maxResults",
                            "type": "number",
                            "label": "Maximum number of results"
                        }
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
                        {
                            "name": "argument_desc",
                            "spec": [
                                {"name": "type", "type": "text"},
                                {
                                    "name": "properties",
                                    "spec": [
                                        {
                                            "name": "start_time",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "length",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "timezone",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "email",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "summary",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "description",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        },
                                        {
                                            "name": "location",
                                            "spec": [
                                                {"name": "type", "type": "text"},
                                                {"name": "description", "type": "text"}
                                            ],
                                            "type": "collection"
                                        }
                                    ],
                                    "type": "collection"
                                }
                            ],
                            "type": "collection"
                        },
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
                        {
                            "name": "__IMTCONN__",
                            "type": "account:google",
                            "label": "Connection",
                            "required": True
                        }
                    ],
                    "expect": [
                        {
                            "mode": "edit",
                            "name": "calendar",
                            "type": "select",
                            "label": "Calendar ID",
                            "required": True
                        }
                    ]
                },
                "onerror": [
                    {
                        "id": 27,
                        "module": "json:CreateJSON",
                        "version": 1,
                        "parameters": {"type": 111573, "space": ""},
                        "mapper": {"response": "{{22.error.message}}"},
                        "metadata": {
                            "designer": {"x": 56, "y": 89},
                            "restore": {
                                "parameters": {
                                    "type": {"label": "Error"},
                                    "space": {"label": "Empty"}
                                }
                            },
                            "parameters": [
                                {
                                    "name": "type",
                                    "type": "udt",
                                    "label": "Data structure",
                                    "required": True
                                },
                                {
                                    "name": "space",
                                    "type": "select",
                                    "label": "Indentation",
                                    "validate": {"enum": ["tab", "2", "4"]}
                                }
                            ],
                            "expect": [
                                {
                                    "name": "response",
                                    "type": "text",
                                    "label": None,
                                    "required": True
                                }
                            ]
                        }
                    },
                    {
                        "id": 28,
                        "module": "gateway:WebhookRespond",
                        "version": 1,
                        "parameters": {},
                        "mapper": {
                            "status": "200",
                            "body": "{{27.json}}",
                            "headers": []
                        },
                        "metadata": {
                            "designer": {"x": 337, "y": 209},
                            "restore": {"expect": {"headers": {"mode": "chose"}}},
                            "expect": [
                                {
                                    "name": "status",
                                    "type": "uinteger",
                                    "label": "Status",
                                    "validate": {"min": 100},
                                    "required": True
                                },
                                {"name": "body", "type": "any", "label": "Body"},
                                {
                                    "name": "headers",
                                    "type": "array",
                                    "label": "Custom headers",
                                    "validate": {"maxItems": 16},
                                    "spec": [
                                        {
                                            "name": "key",
                                            "label": "Key",
                                            "type": "text",
                                            "required": True,
                                            "validate": {"max": 256}
                                        },
                                        {
                                            "name": "value",
                                            "label": "Value",
                                            "type": "text",
                                            "required": True,
                                            "validate": {"max": 4096}
                                        }
                                    ]
                                }
                            ]
                        }
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
                                        "expect": {
                                            "end": {"collapsed": True},
                                            "select": {"label": "In Detail"},
                                            "colorId": {"mode": "chose"},
                                            "calendar": {
                                                "mode": "chose",
                                                "label": f"{email} (Primary Calendar)"
                                            },
                                            "attendees": {"mode": "chose"},
                                            "overrides": {
                                                "mode": "chose",
                                                "items": [{"method": {"mode": "chose", "label": "Pop-up"}}]
                                            },
                                            "recurrence": {"mode": "chose"},
                                            "visibility": {"mode": "chose", "label": "Default"},
                                            "allDayEvent": {"mode": "chose"},
                                            "attachments": {"mode": "chose"},
                                            "sendUpdates": {"mode": "chose", "label": "To All Guests"},
                                            "transparency": {"mode": "chose", "label": "Busy"},
                                            "conferenceDate": {"mode": "chose"}
                                        },
                                        "parameters": {
                                            "__IMTCONN__": {
                                                "data": {"scoped": "true", "connection": "google"},
                                                "label": f"My Google connection ({email})"
                                            }
                                        }
                                    },
                                    "parameters": [
                                        {
                                            "name": "__IMTCONN__",
                                            "type": "account:google",
                                            "label": "Connection",
                                            "required": True
                                        }
                                    ],
                                    "expect": [
                                        {
                                            "name": "select",
                                            "type": "select",
                                            "label": "Create an Event",
                                            "required": True,
                                            "validate": {"enum": ["quick", "detail"]}
                                        },
                                        {
                                            "name": "calendar",
                                            "type": "select",
                                            "label": "Calendar ID",
                                            "required": True
                                        }
                                        # Additional expect fields truncated for brevity
                                    ],
                                    "advanced": True
                                },
                                "onerror": [
                                    {
                                        "id": 18,
                                        "module": "json:CreateJSON",
                                        "version": 1,
                                        "parameters": {"type": 110985, "space": ""},
                                        "mapper": {"response": "Event wasn't created successfully"},
                                        "metadata": {
                                            "designer": {"x": 707, "y": -288},
                                            "restore": {
                                                "parameters": {
                                                    "type": {"label": "My data structure"},
                                                    "space": {"label": "Empty"}
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "id": 19,
                                        "module": "gateway:WebhookRespond",
                                        "version": 1,
                                        "parameters": {},
                                        "mapper": {
                                            "body": "{{18.json}}",
                                            "status": "200",
                                            "headers": []
                                        },
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
                                "mapper": {
                                    "body": "{{16.json}}",
                                    "status": "200",
                                    "headers": []
                                },
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
                                        "expect": {
                                            "item": {
                                                "mode": "chose",
                                                "items": [{"id": {"mode": "edit"}}]
                                            }
                                        },
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
                                        "mapper": {
                                            "body": "{{20.json}}",
                                            "status": "200",
                                            "headers": []
                                        },
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
                                                "mapper": {
                                                    "body": "{{23.json}}",
                                                    "status": "200",
                                                    "headers": []
                                                },
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
                                                "mapper": {
                                                    "body": "{{25.json}}",
                                                    "status": "200",
                                                    "headers": []
                                                },
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
    """Main function to create and deploy the Google Calendar SWAIG scenario."""
    try:
        # Get user input
        config = get_user_input()
        
        print(f"\n🔧 Creating blueprint for {config['email']}...")
        
        # Create the blueprint
        blueprint = create_google_calendar_swaig_blueprint(
            email=config["email"],
            scenario_name=config["scenario_name"],
            webhook_name=config["webhook_name"]
        )
        
        # Save blueprint to file
        blueprint_file = f"google_calendar_swaig_{config['email'].replace('@', '_at_').replace('.', '_')}.json"
        with open(blueprint_file, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        print(f"✅ Blueprint saved to: {blueprint_file}")
        
        # Ask if user wants to create the scenario
        create_scenario = input("\n🚀 Do you want to create this scenario in Make.com? (y/N): ").strip().lower()
        
        if create_scenario in ['y', 'yes']:
            try:
                # Initialize Make.com configuration
                make_config = MakeConfig.from_env()
                creator = MakeBlueprintCreator(make_config)
                
                print("\n📡 Creating scenario in Make.com...")
                
                # Create the scenario with new hooks (automatically replaces hardcoded hook IDs)
                scenario = creator.create_scenario_with_new_hooks(
                    blueprint=blueprint,
                    webhook_name_prefix=f"Google Calendar SWAIG - {config['email']}"
                )
                scenario_id = scenario.get('id')
                
                print(f"✅ Scenario created successfully!")
                print(f"📋 Scenario ID: {scenario_id}")
                print(f"🌐 Scenario Name: {config['scenario_name']}")
                print(f"📧 Calendar Email: {config['email']}")
                
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
                    
            except Exception as e:
                print(f"❌ Error creating scenario: {e}")
                print("💡 You can still use the saved blueprint file to import manually.")
        else:
            print("ℹ️  Blueprint created but not deployed. Use the JSON file to import manually.")
        
        print(f"\n🎉 Google Calendar SWAIG scenario blueprint ready!")
        print(f"📁 Blueprint file: {blueprint_file}")
        print(f"📧 Configured for: {config['email']}")
        
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 