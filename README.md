# Tenable Headshot 🎯

**Land critical hits on your vulnerabilities.** Automatically update Tenable.io asset custom attributes based on vulnerability plugin filters using a configuration-driven approach.

## Features

- **Configuration-driven**: Define multiple rules in a JSON config file
- **Complex plugin filters**: Query by plugin ID, severity, family, and state
- **AND/OR logic support**: Combine filters with AND logic (single object) or OR logic (array of objects)
- **Automatic attribute creation**: Creates custom attributes if they don't exist
- **Multiple rules support**: Process multiple attribute/filter combinations in one run
- **Selective execution**: Run specific rules or all enabled rules
- **Dry-run mode**: Preview changes without making updates
- **Batch processing**: Efficient API usage with batched updates
- **Comprehensive logging**: Detailed progress and error reporting
- **Secure credentials**: Environment variable-based authentication

## Installation

### Option 1: Install as Package (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/tenable-headshot.git
cd tenable-headshot

# Install the package
pip install -e .

# Now you can run it from anywhere
tenable-headshot --help
```

### Option 2: Run Directly

```bash
# Clone and install dependencies
git clone https://github.com/yourusername/tenable-headshot.git
cd tenable-headshot
pip install -r requirements.txt

# Run directly
python main.py --help
```

## Setup

1. Set up API credentials:
```bash
cp config.example.env .env
# Edit .env with your Tenable.io API credentials
source .env
```

2. Create configuration file:
```bash
cp config.example.json config.json
# Edit config.json to define your rules
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

Each rule's `plugin_filters` supports:

- **plugin_id**: Single plugin ID or array of IDs
  ```json
  "plugin_id": 19506
  // or
  "plugin_id": [19506, 20811, 33850]
  ```

- **severity**: Vulnerability severity level
  ```json
  "severity": "critical"  // Options: critical, high, medium, low, info
  ```

- **plugin_family**: Plugin family name
  ```json
  "plugin_family": "Windows"  // e.g., Windows, Databases, Web Servers
  ```

- **state**: Vulnerability state (defaults to "OPEN")
  ```json
  "state": "OPEN"  // Options: OPEN, REOPENED, FIXED
  ```

### AND vs OR Logic

**Single Filter Object (AND Logic)**

When `plugin_filters` is a single object, ALL conditions must match (AND logic):

```json
{
  "plugin_filters": {
    "severity": "critical",
    "plugin_family": "Windows",
    "state": "OPEN"
  }
}
```
This matches assets with: critical severity **AND** Windows family **AND** OPEN state

**Multiple Filter Objects (OR Logic)**

When `plugin_filters` is an array of objects, assets matching ANY filter group are included (OR logic):

```json
{
  "plugin_filters": [
    {
      "severity": "critical",
      "plugin_family": "Windows"
    },
    {
      "severity": "critical",
      "plugin_family": "Databases"
    },
    {
      "severity": "high",
      "plugin_family": "Web Servers"
    }
  ]
}
```
This matches assets with:
- (critical **AND** Windows) **OR**
- (critical **AND** Databases) **OR**
- (high **AND** Web Servers)

Each filter group internally uses AND logic, but groups are combined with OR logic.

**Common OR Logic Use Cases:**

1. **Multiple Plugin IDs across different criteria:**
   ```json
   "plugin_filters": [
     {"plugin_id": 121509, "state": "OPEN"},
     {"plugin_id": 121509, "state": "REOPENED"}
   ]
   ```

2. **Multiple platform families:**
   ```json
   "plugin_filters": [
     {"severity": "critical", "plugin_family": "Windows"},
     {"severity": "critical", "plugin_family": "Databases"}
   ]
   ```

3. **Different severity/family combinations:**
   ```json
   "plugin_filters": [
     {"plugin_id": [19506, 20811]},
     {"severity": "critical"}
   ]
   ```

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

> **Note**: Examples below use `tenable-headshot` (if installed) or `python main.py` (if running directly)

### List Available Rules

View all rules defined in your configuration:
```bash
tenable-headshot --list-rules
# or
python main.py --list-rules
```

Output:
```
Available rules in configuration:
================================================================================

1. Critical Windows Vulnerabilities [ENABLED]
   Description: Mark Windows assets with critical vulnerabilities as high criticality
   Attribute: Criticality = High
   Filters: {'severity': 'critical', 'plugin_family': 'Windows', 'state': 'OPEN'}
...
```

### Run All Enabled Rules

Process all rules where `"enabled": true`:
```bash
tenable-headshot
# or
python main.py
```

### Run Specific Rules

Execute only specific rules by name:
```bash
# Single rule
tenable-headshot --rules "Critical Windows Vulnerabilities"

# Multiple rules
tenable-headshot --rules "Critical Windows Vulnerabilities" "Database Critical Vulnerabilities"
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

## Scheduling (Weekly Runs)

### Linux/Mac (cron)

1. Edit crontab:
```bash
crontab -e
```

2. Add a weekly job (runs every Sunday at 2 AM):
```bash
0 2 * * 0 cd /home/hyperlisk/Projects/tenable-asset-criticality && source .env && /usr/bin/python3 main.py >> /var/log/tenable-updates.log 2>&1
```

Other schedule examples:
```bash
# Every Monday at 3 AM
0 3 * * 1 cd /path/to/script && source .env && python3 main.py

# Every Friday at 6 PM
0 18 * * 5 cd /path/to/script && source .env && python3 main.py

# Every 7 days at midnight
0 0 */7 * * cd /path/to/script && source .env && python3 main.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to "Weekly"
4. Set action to run a batch file:
   ```batch
   @echo off
   cd C:\path\to\tenable-asset-criticality
   set TENABLE_ACCESS_KEY=your_key_here
   set TENABLE_SECRET_KEY=your_secret_here
   python main.py
   ```
5. Save and enable the task

## Logging

The script provides detailed logging:

```
2025-12-01 10:30:15 - INFO - Loaded configuration from config.json
2025-12-01 10:30:15 - INFO - Initialized Tenable.io client
2025-12-01 10:30:15 - INFO - Processing 2 rule(s)
================================================================================

================================================================================
RULE 1/2: Critical Windows Vulnerabilities
Description: Mark Windows assets with critical vulnerabilities as high criticality
================================================================================
2025-12-01 10:30:16 - INFO - Starting asset attribute update job at 2025-12-01 10:30:16
2025-12-01 10:30:16 - INFO - Custom attribute 'Criticality' already exists (UUID: abc-123)
2025-12-01 10:30:20 - INFO - Found 42 unique assets matching the filter
2025-12-01 10:30:25 - INFO - Update complete. Success: 42, Failed: 0
2025-12-01 10:30:25 - INFO - Rule 'Critical Windows Vulnerabilities' completed successfully
...
================================================================================
FINAL SUMMARY
================================================================================
Total rules processed: 2
Successful: 2
Failed: 0
```

## Troubleshooting

### Configuration File Not Found
```
ERROR - Configuration file not found: config.json
INFO - Create a config.json file based on config.example.json
```

**Solution**: Copy `config.example.json` to `config.json` and customize it.

### API Credentials Not Set
```
ERROR - API credentials not found. Please set TENABLE_ACCESS_KEY and TENABLE_SECRET_KEY environment variables
```

**Solution**: Set environment variables or create `.env` file with your credentials.

### No Assets Found
```
WARNING - No assets found matching the filter criteria
```

**Causes**:
- Plugin filters don't match any vulnerabilities
- All matching vulnerabilities are in 'FIXED' state
- Plugin IDs don't exist in your environment

**Solution**:
- Verify filters in config.json
- Check vulnerability state
- Test with broader filters (e.g., only severity)

### API Rate Limits

If you encounter rate limits, the script processes in batches of 100 assets. Adjust in main.py:127:
```python
def update_asset_attributes(self, asset_uuids: List[str], attribute_name: str,
                           attribute_value: str, batch_size: int = 50):  # Reduce batch size
```

### Invalid Configuration
```
ERROR - Configuration error: Rule 'My Rule' missing 'custom_attribute' field
```

**Solution**: Validate your `config.json` structure against `config.example.json`.

## Security Notes

- **Never commit credentials**: `.env` and `config.json` may contain sensitive data
- **Use environment variables**: Don't hardcode API keys
- **Restrict API permissions**: Use keys with minimum required permissions
- **Rotate keys regularly**: Update API keys periodically
- **Review config files**: Ensure no sensitive data in config before committing

## API Permissions Required

Tenable.io API keys need:
- **Assets**: Read, Edit (for assigning custom attributes)
- **Vulnerabilities**: Read (for querying by plugin filters)

Create API keys at: https://cloud.tenable.com/app.html#/settings/my-account/api-keys

## Example Use Cases

### 1. Tiered Asset Criticality Based on Vulnerability Severity

Define rules to tag assets by their highest vulnerability severity:

```json
{
  "rules": [
    {
      "name": "Critical Asset Tag",
      "enabled": true,
      "custom_attribute": {"name": "Criticality", "value": "Critical"},
      "plugin_filters": {"severity": "critical"}
    },
    {
      "name": "High Asset Tag",
      "enabled": true,
      "custom_attribute": {"name": "Criticality", "value": "High"},
      "plugin_filters": {"severity": "high"}
    }
  ]
}
```

### 2. Compliance-Driven Tagging

Tag assets that need specific compliance remediation:

```json
{
  "rules": [
    {
      "name": "PCI-DSS Priority",
      "enabled": true,
      "custom_attribute": {"name": "CompliancePriority", "value": "PCI-DSS"},
      "plugin_filters": {"plugin_id": [45590, 57582, 10863]}
    }
  ]
}
```

### 3. Platform-Specific Risk Assessment

Different risk tags for different platforms:

```json
{
  "rules": [
    {
      "name": "Windows High Risk",
      "enabled": true,
      "custom_attribute": {"name": "PlatformRisk", "value": "WindowsHigh"},
      "plugin_filters": {"plugin_family": "Windows", "severity": "critical"}
    },
    {
      "name": "Database High Risk",
      "enabled": true,
      "custom_attribute": {"name": "PlatformRisk", "value": "DatabaseHigh"},
      "plugin_filters": {"plugin_family": "Databases", "severity": "critical"}
    }
  ]
}
```

## License

This project is provided as-is for use with Tenable.io environments.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review [Tenable.io API documentation](https://developer.tenable.com/reference/navigate)
3. Verify your configuration against examples