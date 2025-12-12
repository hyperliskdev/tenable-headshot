# Tenable Headshot 🎯

**Land critical hits on your vulnerabilities.** Automatically update Tenable.io asset custom attributes based on vulnerability plugin filters using a configuration-driven approach.

## Features

- **Configuration-driven**: Define multiple rules in a JSON config file
- **Complex plugin filters**: Query by plugin ID, severity, family, state, and output content
- **AND/OR logic support**: Combine filters with AND logic (single object) or OR logic (array of objects)
- **Automatic attribute creation**: Creates custom attributes if they don't exist
- **Dry-run mode**: Preview changes without making updates
- **CLI tool**: Simple command-line interface with rule selection

## Installation

Install the package directly:
```bash
pip install .
```

For development (editable install):
```bash
pip install -e .
```

Create your configuration file:
```bash
cp config.example.json config.json
# Edit config.json to define your rules
```

Set environment variables for Tenable API credentials:
```bash
export TENABLE_ACCESS_KEY="your_access_key"
export TENABLE_SECRET_KEY="your_secret_key"
```

## Configuration

### Configuration File Structure

The `config.json` file defines rules for updating asset attributes:

```json
{
  "tenable": {
    "access_key_env": "TENABLE_ACCESS_KEY",
    "secret_key_env": "TENABLE_SECRET_KEY"
  },
  "rules": [
    {
      "name": "Rule Name",
      "description": "What this rule does",
      "enabled": true,
      "custom_attribute": {
        "name": "AttributeName",
        "value": "AttributeValue",
        "description": "Attribute description"
      },
      "plugin_filters": {
        "severity": "critical",
        "plugin_family": "Windows"
      }
    }
  ]
}
```

### Plugin Filter Options

- **plugin_id**: Single ID or array of IDs (e.g., `19506` or `[19506, 20811]`)
- **severity**: `critical`, `high`, `medium`, `low`, or `info`
- **plugin_family**: Plugin family name (e.g., `Windows`, `Databases`)
- **state**: `OPEN` (default), `REOPENED`, or `FIXED`
- **output_contains**: Match specific text in plugin output

### Filter Logic

- **Single object** = AND logic (all conditions must match)
- **Array of objects** = OR logic (any filter group matches)

Example with OR logic:
```json
"plugin_filters": [
  {"severity": "critical", "plugin_family": "Windows"},
  {"severity": "critical", "plugin_family": "Databases"}
]
```
Matches assets with critical Windows **OR** critical Database vulnerabilities.

### Example Configuration

```json
{
  "tenable": {
    "access_key_env": "TENABLE_ACCESS_KEY",
    "secret_key_env": "TENABLE_SECRET_KEY"
  },
  "rules": [
    {
      "name": "Critical Windows Vulnerabilities",
      "description": "Mark Windows assets with critical vulnerabilities as high criticality",
      "enabled": true,
      "custom_attribute": {
        "name": "Criticality",
        "value": "High",
        "description": "Asset criticality level based on vulnerability presence"
      },
      "plugin_filters": {
        "severity": "critical",
        "plugin_family": "Windows",
        "state": "OPEN"
      }
    },
    {
      "name": "Database Critical Vulnerabilities",
      "description": "Tag database servers with critical vulnerabilities",
      "enabled": true,
      "custom_attribute": {
        "name": "DatabaseRisk",
        "value": "High",
        "description": "Database vulnerability risk level"
      },
      "plugin_filters": {
        "severity": "critical",
        "plugin_family": "Databases"
      }
    },
    {
      "name": "Specific High-Risk Plugins",
      "description": "Assets with specific high-risk plugin IDs",
      "enabled": false,
      "custom_attribute": {
        "name": "PatchPriority",
        "value": "Urgent",
        "description": "Patch priority level"
      },
      "plugin_filters": {
        "plugin_id": [19506, 20811, 10394],
        "severity": "high"
      }
    }
  ]
}
```

## Usage

After installation, use the `tenable-headshot` command:

### List Available Rules

View all rules defined in your configuration:
```bash
tenable-headshot --list-rules
```

### Run All Enabled Rules

Process all rules where `"enabled": true`:
```bash
tenable-headshot
```

### Run Specific Rules

Execute only specific rules by name:
```bash
# Single rule
tenable-headshot --rules "DHCP Servers"

# Multiple rules
tenable-headshot --rules "DHCP Servers" "DNS Servers"
```

### Dry Run

Preview what would happen without making changes:
```bash
tenable-headshot --dry-run
```

### Use Custom Config File

Specify a different configuration file:
```bash
tenable-headshot --config production-config.json
```

### Command Line Options

```
usage: tenable-headshot [-h] [--config CONFIG] [--rules RULES [RULES ...]] [--dry-run] [--list-rules]

Options:
  -h, --help                        Show help message
  --config, -c CONFIG               Path to config file (default: config.json)
  --rules, -r RULES [RULES ...]     Specific rule names to run
  --dry-run                         Preview changes without making updates
  --list-rules                      List all available rules and exit
```

## Scheduling (Automated Runs)

### Linux/Mac (cron)

Add a scheduled job to run automatically:
```bash
# Every Sunday at 2 AM
0 2 * * 0 /usr/bin/tenable-headshot >> /var/log/tenable-updates.log 2>&1
```

### Windows (Task Scheduler)

Create a scheduled task that runs `tenable-headshot` at your desired frequency. Ensure environment variables are set in the task configuration.

## Troubleshooting

Common issues and solutions:

- **Configuration file not found**: Copy `config.example.json` to `config.json`
- **API credentials not set**: Export `TENABLE_ACCESS_KEY` and `TENABLE_SECRET_KEY` environment variables
- **No assets found**: Verify plugin filters match your environment; check vulnerability states
- **Invalid configuration**: Validate `config.json` structure against `config.example.json`

## API Permissions

Tenable.io API keys require:
- **Assets**: Read, Edit
- **Vulnerabilities**: Read

Create API keys at: https://cloud.tenable.com/app.html#/settings/my-account/api-keys

## Security

- Never commit credentials or sensitive config files
- Use environment variables for API keys
- Use minimum required API permissions
- Rotate keys regularly

## License

MIT License - See project repository for details.