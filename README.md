# Intervals.icu MCP Server

![Intervals.icu MCP Server](docs/heading.png)

A Model Context Protocol (MCP) server for Intervals.icu integration. Access your training data, wellness metrics, and performance analysis through Claude and other LLMs.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Overview

This MCP server provides 51 tools to interact with your Intervals.icu account, organized into 9 categories:

- Activities (10 tools) - Query, search, update, delete, and download activities
- Activity Analysis (8 tools) - Deep dive into streams, intervals, best efforts, and histograms
- Athlete (2 tools) - Access profile, fitness metrics, and training load
- Wellness (3 tools) - Track and update recovery, HRV, sleep, and health metrics
- Events/Calendar (9 tools) - Manage planned workouts, races, notes with bulk operations
- Performance/Curves (3 tools) - Analyze power, heart rate, and pace curves
- Workout Library (5 tools) - Browse, create, and manage workout templates and training plans
- Gear Management (6 tools) - Track equipment and maintenance reminders
- Sport Settings (5 tools) - Configure FTP, FTHR, pace thresholds, and zones

Additionally, the server provides:

- 1 MCP Resource - Athlete profile with fitness metrics for ongoing context
- 6 MCP Prompts - Templates for common queries (training analysis, performance analysis, activity deep dive, recovery check, training plan review, weekly planning)

## Prerequisites

- Python 3.11+ and [uv](https://github.com/astral-sh/uv), OR
- Docker

## Intervals.icu API Key Setup

Before installation, you need to obtain your Intervals.icu API key:

1. Go to https://intervals.icu/settings
2. Scroll to the **Developer** section
3. Click **Create API Key**
4. Copy the API key (you'll use it during setup)
5. Note your **Athlete ID** from your profile URL (format: `i123456`)

## Installation & Setup

### How Authentication Works

1. API Key - Simple API key authentication (no OAuth required)
2. Configuration - API key and athlete ID saved to `.env` file
3. Basic Auth - HTTP Basic Auth with username "API_KEY" and your key as password
4. Persistence - Subsequent runs reuse stored credentials

### Option 1: Using UV

```bash
# Install dependencies
cd intervals-icu-mcp
uv sync
```

Then configure credentials using one of these methods:

#### Interactive Setup

```bash
uv run intervals-icu-mcp-auth
```

This will prompt for your API key and athlete ID and save credentials to `.env`.

#### Manual Setup

Create a `.env` file manually:

```bash
INTERVALS_ICU_API_KEY=your_api_key_here
INTERVALS_ICU_ATHLETE_ID=i123456
```

### Option 2: Using Docker

```bash
# Build the image
docker build -t intervals-icu-mcp .
```

Then configure credentials using one of these methods:

#### Interactive Setup

```bash
# Create the env file first (Docker will create it as a directory if it doesn't exist)
touch intervals-icu-mcp.env

# Run the setup script
docker run -it --rm \
  -v "/ABSOLUTE/PATH/TO/intervals-icu-mcp.env:/app/.env" \
  --entrypoint= \
  intervals-icu-mcp:latest \
  python -m intervals_icu_mcp.scripts.setup_auth
```

This will prompt for credentials and save them to `intervals-icu-mcp.env`.

#### Manual Setup

Create an `intervals-icu-mcp.env` file manually in your current directory (see UV manual setup above for format).

## Claude Desktop Configuration

Add to your configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Using UV

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/intervals-icu-mcp",
        "intervals-icu-mcp"
      ]
    }
  }
}
```

### Using Docker

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/ABSOLUTE/PATH/TO/intervals-icu-mcp.env:/app/.env",
        "intervals-icu-mcp:latest"
      ]
    }
  }
}
```

## Usage

Ask Claude to interact with your Intervals.icu data using natural language. The server provides tools, a resource, and prompt templates to help you get started.

### Quick Start with MCP Prompts

Use built-in prompt templates for common queries (available via prompt suggestions in Claude):

- `analyze-recent-training` - Comprehensive training analysis over a specified period
- `performance-analysis` - Analyze power/HR/pace curves and zones
- `activity-deep-dive` - Deep dive into a specific activity with streams, intervals, and best efforts
- `recovery-check` - Recovery assessment with wellness trends and training load
- `training-plan-review` - Weekly training plan evaluation with workout library
- `plan-training-week` - AI-assisted weekly training plan creation based on current fitness

### Activities

```
"Show me my activities from the last 30 days"
"Get details for my last long run"
"Find all my threshold workouts"
"Update the name of my last activity"
"Delete that duplicate activity"
"Download the FIT file for my race"
```

### Activity Analysis

```
"Show me the power data from yesterday's ride"
"What were my best efforts in my last race?"
"Find similar interval workouts to my last session"
"Show me the intervals from my workout on Tuesday"
"Get the power histogram for my last ride"
"Show me the heart rate distribution for that workout"
```

### Athlete Profile & Fitness

```
"Show my current fitness metrics and training load"
"Am I overtraining? Check my CTL, ATL, and TSB"
```

_Note: The athlete profile resource (`intervals-icu://athlete/profile`) automatically provides ongoing context._

### Wellness & Recovery

```
"How's my recovery this week? Show HRV and sleep trends"
"What was my wellness data for yesterday?"
"Update my wellness data for today - I slept 8 hours and feel great"
```

### Calendar & Planning

```
"What workouts do I have planned this week?"
"Create a threshold workout for tomorrow"
"Update my workout on Friday"
"Delete the workout on Saturday"
"Duplicate this week's plan for next week"
"Create 5 workouts for my build phase"
```

### Performance Analysis

```
"What's my 20-minute power and FTP?"
"Show me my heart rate zones"
"Analyze my running pace curve"
```

### Workout Library & Training Plans

```
"Show me my workout library"
"What workouts are in my threshold folder?"
"Create a 12-week marathon training plan"
"Add interval workouts to my cycling plan"
"Delete my old training plan"
```

### Gear Management

```
"Show me my gear list"
"Add my new running shoes to gear tracking"
"Create a reminder to replace my bike chain at 3000km"
"Update the mileage on my road bike"
```

### Sport Settings

```
"Update my FTP to 275 watts"
"Show my current zone settings for cycling"
"Set my running threshold pace to 4:30 per kilometer"
"Apply my new threshold settings to historical activities"
```

## Available Tools

### Activities (10 tools)

| Tool                     | Description                                       |
| ------------------------ | ------------------------------------------------- |
| `get-recent-activities`  | List recent activities with summary metrics       |
| `get-activity-details`   | Get comprehensive details for a specific activity |
| `search-activities`      | Search activities by name or tag                  |
| `search-activities-full` | Search activities with full details               |
| `get-activities-around`  | Get activities before and after a specific one    |
| `update-activity`        | Update activity name, description, or metadata    |
| `delete-activity`        | Delete an activity                                |
| `download-activity-file` | Download original activity file                   |
| `download-fit-file`      | Download activity as FIT file                     |
| `download-gpx-file`      | Download activity as GPX file                     |

### Activity Analysis (8 tools)

| Tool                     | Description                                                   |
| ------------------------ | ------------------------------------------------------------- |
| `get-activity-streams`   | Get time-series data (power, HR, cadence, altitude, GPS)      |
| `get-activity-intervals` | Get structured workout intervals with targets and performance |
| `get-best-efforts`       | Find peak performances across all durations in an activity    |
| `search-intervals`       | Find similar intervals across activity history                |
| `get-power-histogram`    | Get power distribution histogram for an activity              |
| `get-hr-histogram`       | Get heart rate distribution histogram for an activity         |
| `get-pace-histogram`     | Get pace distribution histogram for an activity               |
| `get-gap-histogram`      | Get grade-adjusted pace histogram for an activity             |

### Athlete (2 tools)

| Tool                  | Description                                                     |
| --------------------- | --------------------------------------------------------------- |
| `get-athlete-profile` | Get athlete profile with fitness metrics and sport settings     |
| `get-fitness-summary` | Get detailed CTL/ATL/TSB analysis with training recommendations |

### Wellness (3 tools)

| Tool                    | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| `get-wellness-data`     | Get recent wellness metrics with trends (HRV, sleep, mood, fatigue) |
| `get-wellness-for-date` | Get complete wellness data for a specific date                      |
| `update-wellness`       | Update or create wellness data for a date                           |

### Events/Calendar (9 tools)

| Tool                    | Description                                                |
| ----------------------- | ---------------------------------------------------------- |
| `get-calendar-events`   | Get planned events and workouts from calendar              |
| `get-upcoming-workouts` | Get upcoming planned workouts only                         |
| `get-event`             | Get details for a specific event                           |
| `create-event`          | Create new calendar events (workouts, races, notes, goals) |
| `update-event`          | Modify existing calendar events                            |
| `delete-event`          | Remove events from calendar                                |
| `bulk-create-events`    | Create multiple events in a single operation               |
| `bulk-delete-events`    | Delete multiple events in a single operation               |
| `duplicate-event`       | Duplicate an event to a new date                           |

### Performance/Curves (3 tools)

| Tool               | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `get-power-curves` | Analyze power curves with FTP estimation and power zones |
| `get-hr-curves`    | Analyze heart rate curves with HR zones                  |
| `get-pace-curves`  | Analyze running/swimming pace curves with optional GAP   |

### Workout Library (5 tools)

| Tool                     | Description                                         |
| ------------------------ | --------------------------------------------------- |
| `get-workout-library`    | Browse workout folders and training plans           |
| `get-workouts-in-folder` | View all workouts in a specific folder              |
| `create-training-plan`   | Create training plans with optional workouts        |
| `add-workouts-to-plan`   | Add multiple workouts to an existing plan           |
| `delete-training-plan`   | Delete a training plan and all its workouts         |

### Gear Management (6 tools)

| Tool                   | Description                                |
| ---------------------- | ------------------------------------------ |
| `get-gear-list`        | Get all gear items with usage and status   |
| `create-gear`          | Add new gear to tracking                   |
| `update-gear`          | Update gear details, mileage, or status    |
| `delete-gear`          | Remove gear from tracking                  |
| `create-gear-reminder` | Create maintenance reminders for gear      |
| `update-gear-reminder` | Update existing gear maintenance reminders |

### Sport Settings (5 tools)

| Tool                    | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `get-sport-settings`    | Get sport-specific settings and thresholds              |
| `update-sport-settings` | Update FTP, FTHR, pace threshold, or zone configuration |
| `apply-sport-settings`  | Apply updated settings to historical activities         |
| `create-sport-settings` | Create new sport-specific settings                      |
| `delete-sport-settings` | Delete sport-specific settings                          |

## MCP Resources

Resources provide ongoing context to the LLM without requiring explicit tool calls:

| Resource                          | Description                                                              |
| --------------------------------- | ------------------------------------------------------------------------ |
| `intervals-icu://athlete/profile` | Complete athlete profile with current fitness metrics and sport settings |

## MCP Prompts

Prompt templates for common queries (accessible via prompt suggestions in Claude):

| Prompt                    | Description                                                              |
| ------------------------- | ------------------------------------------------------------------------ |
| `analyze-recent-training` | Comprehensive training analysis over a specified period                  |
| `performance-analysis`    | Detailed power/HR/pace curve analysis with zones                         |
| `activity-deep-dive`      | Deep dive into a specific activity with streams, intervals, best efforts |
| `recovery-check`          | Recovery assessment with wellness trends and training load               |
| `training-plan-review`    | Weekly training plan evaluation with workout library                     |
| `plan-training-week`      | AI-assisted weekly training plan creation based on current fitness       |

## Training Plans - Complete Guide

### Creating Training Plans

You can create training plans with or without workouts in a single operation.

#### Basic Training Plan

```python
create_training_plan(
    name="Marathon Training Plan",
    plan_type="PLAN",
    description="12-week marathon training plan",
    start_date="2024-01-01",
    visibility="PRIVATE"
)
```

**Important**: If you don't specify a `start_date` for a plan (`plan_type="PLAN"`), it will automatically be set to the next Monday to ensure plans start at the beginning of a week.

#### Workout Folder

For organizing workouts without a schedule:

```python
create_training_plan(
    name="My Workouts",
    plan_type="FOLDER",
    visibility="PRIVATE"
)
```

### Workout Description Format

⚠️ **CRITICAL**: Workout descriptions must follow the Intervals.icu Markdown format for proper interpretation on your device.

#### Format Rules

1. **Section headers** (Warmup/Main Set/Cooldown) on separate lines
2. **Steps** begin with `- `, followed by:
   - Duration (e.g., `5m`, `30s`, `1m30`)
   - Intensity:
     - **Cycling**: % of FTP (e.g., `85%`, `95-105%`)
     - **Running/Trail**:
       - ⚠️ **IMPORTANT**: Cannot mix pace and HR in the same workout. Choose one mode for the entire session.
       - **For intensive flat intervals/VMA**: Use PACE for entire workout (warmup, main set, cooldown)
         - Warmup: `Press lap 15m 60-75% pace`
         - Main Set: pace (e.g., `100-105% pace`)
         - Cooldown: pace (e.g., `10m 60-70% pace`)
       - **For all other workouts** (easy runs, tempo, long runs, uphill/trail): Use HR for entire workout
         - Warmup: `Press lap 15m Z1-Z2 HR`
         - Main Set: HR zones (e.g., `Z2 HR`, `Z3 HR`, `Z4 HR`)
         - Cooldown: HR zones (e.g., `10m Z1-Z2 HR`)
       - **NEVER use ramp for warmup or cooldown in running/trail**
   - Optional: cadence (e.g., `90rpm`)
   - Optional: ramp (e.g., `ramp 60-80%`)
3. **Repeats**: use `Nx` on its own line before the block
4. **Leave blank lines** between sections

#### Example Workouts

**Cycling:**
```
Warmup
- 10m ramp 55-75% FTP 90rpm

Main Set 3x
- 5m 90% FTP 95rpm
- 3m 65% FTP 85rpm

Cooldown
- 10m ramp 75-55% FTP 85rpm
```

**Running - Easy Run (HR-based):**
```
Warmup
- Press lap 15m Z1-Z2 HR

Main Set
- 30m Z2 HR

Cooldown
- 10m Z1-Z2 HR
```

**Running - VMA Intervals on Flat (pace for entire workout):**
```
Warmup
- Press lap 15m 60-75% pace

Main Set 6x
- 3m 100-105% pace
- 2m 70% pace

Cooldown
- 10m 60-70% pace
```

**Running - Trail/Uphill (HR-based):**
```
Warmup
- Press lap 15m Z1-Z2 HR

Main Set 5x
- 5m Z4 HR
- 3m Z2 HR

Cooldown
- 10m Z1-Z2 HR
```

### Creating Plans with Workouts

You can create a plan and add workouts in one operation:

```python
create_training_plan(
    name="Weekly Running Plan",
    plan_type="PLAN",
    description="Complete weekly running plan",
    start_date="2024-01-01",
    visibility="PRIVATE",
    workouts='''[
        {
            "name": "Recovery Run",
            "description": "Main Set\\n- 30m Z1-Z2 HR",
            "type": "Run",
            "moving_time": 1800,
            "day": 1,
            "icu_training_load": 25,
            "targets": ["HR"]
        },
        {
            "name": "VMA Intervals",
            "description": "Warmup\\n- Press lap 15m 60-75% pace\\n\\nMain Set 6x\\n- 3m 100-105% pace\\n- 2m 70% pace\\n\\nCooldown\\n- 10m 60-70% pace",
            "type": "Run",
            "moving_time": 3900,
            "day": 2,
            "icu_training_load": 65,
            "targets": ["PACE"]
        },
        {
            "name": "Long Run",
            "description": "Warmup\\n- Press lap 15m Z1-Z2 HR\\n\\nMain Set\\n- 90m Z2 HR\\n\\nCooldown\\n- 10m Z1-Z2 HR",
            "type": "Run",
            "moving_time": 7500,
            "day": 7,
            "icu_training_load": 95,
            "targets": ["HR"]
        }
    ]'''
)
```

### Adding Workouts to Existing Plans

Use `add_workouts_to_plan` to add workouts to an already created plan:

```python
add_workouts_to_plan(
    folder_id=12345,
    workouts='''[
        {
            "name": "Threshold Intervals",
            "description": "Warmup\\n- 10m ramp 55-75% FTP 90rpm\\n\\nMain Set 4x\\n- 8m 95-105% FTP 95rpm\\n- 2m 55% FTP 85rpm\\n\\nCooldown\\n- 10m ramp 75-55% FTP 85rpm",
            "type": "Ride",
            "moving_time": 3600,
            "day": 3,
            "indoor": true,
            "color": "red",
            "icu_training_load": 85,
            "targets": ["POWER"]
        }
    ]'''
)
```

### Workout Fields

**Required Fields:**
- `name`: Workout name
- `type`: Activity type ("Run", "Ride", "Swim", etc.)
- `moving_time`: Duration in seconds
- `day`: Day number in the plan (starts at 1)

**Optional Fields:**
- `description`: Workout description in Intervals.icu Markdown format
- `indoor`: true/false (default: false)
- `color`: Display color ("blue", "green", "red", etc.)
- `icu_training_load`: Estimated training load
- `targets`: Array of targets - `["HR"]`, `["POWER"]`, `["PACE"]`, or `["AUTO"]`
- `sub_type`: "NONE", "WARMUP", "COOLDOWN", "RACE", "COMMUTE"

### Using AI to Generate Workouts

You can use an AI assistant (like Claude) to generate workout descriptions in the correct Intervals.icu Markdown format.

**System Prompt for AI:**

```
You are a workout generator that outputs correctly formatted Intervals.icu Markdown.

Format rules:
1. Section headers like Warmup/Main Set/Cooldown on a separate line
2. Steps begin with `- `, followed by:
   • Duration (e.g., `5m`, `30s`, `1m30`)
   • Target intensity:
     – For cycling: % of FTP (e.g., `85%`, `95-105%`)
     – For running/trail: HR zones by default (e.g., `Z2 HR`, `Z3 HR`)
       ONLY use pace for intensive flat intervals/VMA (e.g., `100-105% pace`)
   • Optional cadence (e.g., `90rpm`)
   • Optional ramp (e.g., `ramp 60-80%`)
3. Repeats: use `Nx` on its own line, preceding the block
4. Leave blank lines between sections and repeats
5. Running/Trail specificity:
   - IMPORTANT: Cannot mix pace and HR in the same workout
   - For intensive flat intervals/VMA: Use PACE for entire workout
   - For all other workouts: Use HR for entire workout
   - NEVER use ramp for warmup or cooldown

When I give you a workout description in plain English, respond ONLY with the correctly formatted Intervals.icu Markdown.
```

**Example Usage:**

User: "Create a 60-minute cycling threshold intervals workout with 10 min warmup ramping from 55% to 75% FTP, 4 intervals of 8 minutes at 95-105% FTP with 2 minutes recovery at 55% FTP, and 10 min cooldown ramping from 75% to 55% FTP"

AI Response:
```
Warmup
- 10m ramp 55-75% FTP 90rpm

Main Set 4x
- 8m 95-105% FTP 95rpm
- 2m 55% FTP 85rpm

Cooldown
- 10m ramp 75-55% FTP 85rpm
```

Then use this description in your workout JSON with proper escaping (`\\n` for newlines).

### Complete Workflow

1. Describe your desired workout in natural language to an AI
2. AI generates the correctly formatted Intervals.icu Markdown
3. Copy the Markdown into the `description` field (with `\\n` for line breaks)
4. Complete the other required fields (name, type, moving_time, day)
5. Call `create_training_plan` or `add_workouts_to_plan` with the complete workout JSON

This allows you to rapidly generate complex, properly formatted training plans!

## License

MIT License - see [LICENSE](LICENSE) file for details

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Intervals.icu. All product names, logos, and brands are property of their respective owners.
