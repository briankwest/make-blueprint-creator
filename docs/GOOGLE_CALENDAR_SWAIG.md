# Google Calendar SWAIG Integration

This document provides comprehensive information about creating and using Google Calendar SWAIG (SignalWire AI Gateway) integration scenarios with the Make.com Blueprint Creator.

## Overview

The Google Calendar SWAIG integration creates a Make.com scenario that connects Google Calendar with SignalWire AI Gateway, enabling voice-controlled calendar operations through AI-powered conversations.

### Features

- **Event Creation**: Create calendar events through voice commands
- **Free/Busy Checking**: Check calendar availability for specific time slots
- **Dynamic Email Configuration**: Customize the Google Calendar email address
- **Error Handling**: Comprehensive error responses for failed operations
- **SWAIG Integration**: Full compatibility with SignalWire AI Gateway

## Quick Start

### Using the CLI Tool

```bash
# Interactive mode - prompts for email address
make-google-calendar-swaig

# Specify email address directly
make-google-calendar-swaig --email user@example.com

# Create with custom name and deploy automatically
make-google-calendar-swaig --email user@example.com --name "My Calendar Bot" --activate
```

### Using the Python API

```python
from make_blueprint_creator import MakeBlueprintCreator, MakeConfig
from make_blueprint_creator.examples.google_calendar_swaig import create_google_calendar_swaig_blueprint

# Configure Make.com connection
config = MakeConfig.from_env()
creator = MakeBlueprintCreator(config)

# Create the blueprint
blueprint = create_google_calendar_swaig_blueprint(
    email="user@example.com",
    scenario_name="My Calendar SWAIG",
    webhook_name="Calendar Webhook"
)

# Deploy to Make.com
scenario_id = creator.create_scenario(blueprint)
creator.activate_scenario(scenario_id)
```

### Using the Standalone Script

```bash
# Run the standalone script (no package installation required)
python scripts/create_google_calendar_swaig.py
```

## Scenario Architecture

The Google Calendar SWAIG scenario consists of three main components:

### 1. Webhook Trigger (SWAIG Server)
- **Module**: `gateway:CustomWebHook`
- **Purpose**: Receives SWAIG function calls from SignalWire AI Gateway
- **Input**: SWAIG function data including function name and arguments

### 2. Calendar Validation
- **Module**: `google-calendar:getACalendar`
- **Purpose**: Validates Google Calendar access and connection
- **Error Handling**: Returns error messages for invalid calendar access

### 3. Function Router
- **Module**: `builtin:BasicRouter`
- **Purpose**: Routes requests based on SWAIG function name
- **Routes**:
  - `events` → Create calendar event
  - `freebusy` → Check calendar availability

## SWAIG Functions

### Events Function

Creates calendar events based on voice input.

**Function Name**: `events`

**Expected Arguments**:
```json
{
  "parsed": [
    {
      "start_time": "2025-01-27T14:00:00Z",
      "length": 60,
      "timezone": "America/New_York",
      "email": "user@example.com",
      "summary": "Meeting with team",
      "description": "Weekly team sync",
      "location": "Conference Room A"
    }
  ]
}
```

**Response**:
- **Success**: `{"response": "Event created successfully"}`
- **Error**: `{"response": "Event wasn't created successfully"}`

### Free/Busy Function

Checks calendar availability for specified time periods.

**Function Name**: `freebusy`

**Expected Arguments**:
```json
{
  "parsed": [
    {
      "start_time": "2025-01-27T14:00:00Z",
      "length": 60,
      "timezone": "America/New_York"
    }
  ]
}
```

**Response**:
- **Available**: `{"response": "Time is available"}`
- **Busy**: `{"response": "Time is NOT available"}`
- **Error**: `{"response": "Error checking that time try a different time"}`

## Configuration

### Environment Variables

```bash
# Required for deployment
MAKE_API_TOKEN=your_make_api_token
MAKE_TEAM_ID=your_team_id  # or MAKE_ORG_ID for organization

# Optional for custom API endpoint
MAKE_API_BASE_URL=https://us2.make.com/api/v2
```

### Google Calendar Setup

1. **Create Google Connection in Make.com**:
   - Go to Make.com → Connections
   - Add new Google connection
   - Authorize access to Google Calendar
   - Note the connection ID (will be auto-configured)

2. **Calendar Permissions**:
   - Ensure the Google account has access to the target calendar
   - For shared calendars, verify appropriate permissions

## CLI Reference

### Command Options

```bash
make-google-calendar-swaig [OPTIONS]
```

**Options**:
- `--email, -e`: Google Calendar email address
- `--name, -n`: Scenario name (default: "Google Calendar SWAIG Scenario")
- `--webhook-name, -w`: Webhook name (default: "SWAIG Server")
- `--output-file, -o`: Output file for blueprint JSON
- `--output-only`: Only create blueprint file, don't offer deployment
- `--no-deploy`: Don't offer to deploy the scenario
- `--activate`: Automatically activate the scenario after creation
- `--quiet, -q`: Minimal output

### Examples

```bash
# Basic usage with prompts
make-google-calendar-swaig

# Automated deployment
make-google-calendar-swaig \
  --email calendar@company.com \
  --name "Company Calendar Bot" \
  --activate

# Generate blueprint only
make-google-calendar-swaig \
  --email user@example.com \
  --output-only \
  --output-file my_calendar_blueprint.json

# Quiet mode for scripts
make-google-calendar-swaig \
  --email user@example.com \
  --quiet \
  --no-deploy
```

## Integration with SignalWire AI Gateway

### SWAIG Configuration

Configure your SWAIG application to call the Make.com webhook:

```python
# Example SWAIG function definitions
swaig_functions = [
    {
        "function": "events",
        "purpose": "Create calendar events",
        "argument": {
            "type": "object",
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "Event start time in ISO format"
                },
                "length": {
                    "type": "number", 
                    "description": "Event duration in minutes"
                },
                "summary": {
                    "type": "string",
                    "description": "Event title/summary"
                },
                "description": {
                    "type": "string",
                    "description": "Event description"
                },
                "location": {
                    "type": "string",
                    "description": "Event location"
                }
            }
        }
    },
    {
        "function": "freebusy",
        "purpose": "Check calendar availability",
        "argument": {
            "type": "object", 
            "properties": {
                "start_time": {
                    "type": "string",
                    "description": "Check start time in ISO format"
                },
                "length": {
                    "type": "number",
                    "description": "Duration to check in minutes"
                }
            }
        }
    }
]
```

### Webhook URL

After creating the scenario in Make.com:

1. Copy the webhook URL from the first module
2. Configure your SWAIG application to send function calls to this URL
3. Test the integration with sample function calls

## Troubleshooting

### Common Issues

**1. Calendar Access Denied**
```
Error: Calendar access denied
```
**Solution**: Verify Google Calendar connection and permissions

**2. Invalid Time Format**
```
Error: Invalid start_time format
```
**Solution**: Ensure times are in ISO 8601 format (e.g., "2025-01-27T14:00:00Z")

**3. Webhook Not Responding**
```
Error: Webhook timeout
```
**Solution**: Check scenario activation status and webhook URL

**4. Event Creation Failed**
```
Response: Event wasn't created successfully
```
**Solution**: Verify calendar permissions and event data validity

### Debug Mode

Enable debug logging in your SWAIG application to see detailed request/response data:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing the Integration

Use curl to test the webhook directly:

```bash
# Test event creation
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "events",
    "argument": {
      "parsed": [{
        "start_time": "2025-01-27T14:00:00Z",
        "length": 60,
        "summary": "Test Event",
        "description": "Testing calendar integration"
      }]
    }
  }'

# Test free/busy check
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "freebusy", 
    "argument": {
      "parsed": [{
        "start_time": "2025-01-27T14:00:00Z",
        "length": 60
      }]
    }
  }'
```

## Advanced Configuration

### Custom Event Settings

Modify the blueprint to customize event creation:

```python
# Example: Add custom reminder settings
"overrides": [
    {"method": "email", "minutes": "30"},
    {"method": "popup", "minutes": "10"}
]

# Example: Add attendees
"attendees": [
    {"email": "attendee1@example.com", "displayName": "John Doe"},
    {"email": "attendee2@example.com", "displayName": "Jane Smith"}
]

# Example: Enable Google Meet
"conferenceDate": True
```

### Multiple Calendar Support

To support multiple calendars, modify the blueprint to:

1. Accept calendar email in the SWAIG function arguments
2. Use dynamic calendar selection in the Google Calendar modules
3. Add validation for calendar access permissions

### Error Response Customization

Customize error messages by modifying the JSON response modules:

```python
# Custom error messages
"mapper": {
    "response": "Sorry, I couldn't create that event. Please check your calendar permissions."
}
```

## Security Considerations

### API Token Security
- Store Make.com API tokens securely
- Use environment variables, never hardcode tokens
- Rotate tokens regularly

### Webhook Security
- Consider implementing webhook signature validation
- Use HTTPS endpoints only
- Monitor webhook access logs

### Calendar Permissions
- Use least-privilege access for Google Calendar connections
- Regularly audit calendar sharing permissions
- Consider using service accounts for production deployments

## Performance Optimization

### Scenario Optimization
- Enable scenario caching where appropriate
- Monitor execution times and optimize slow modules
- Use parallel execution for independent operations

### Rate Limiting
- Be aware of Google Calendar API rate limits
- Implement retry logic for transient failures
- Consider batching operations for high-volume use cases

## Support and Resources

### Documentation
- [Make.com API Documentation](https://www.make.com/en/api-documentation)
- [Google Calendar API Reference](https://developers.google.com/calendar/api/v3/reference)
- [SignalWire AI Gateway Documentation](https://developer.signalwire.com/)

### Community
- [Make.com Community Forum](https://community.make.com/)
- [SignalWire Community](https://signalwire.community/)

### Professional Support
- Make.com Enterprise Support
- SignalWire Professional Services
- Custom integration development services

---

**Created**: January 27, 2025  
**Version**: 1.0.0  
**Compatibility**: Make.com API v2, Google Calendar API v3, SignalWire AI Gateway 