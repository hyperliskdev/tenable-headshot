"""Command-line interface for Tenable Headshot."""

import sys
import logging
import argparse

from tenable_headshot.core.config import load_config, get_credentials
from tenable_headshot.core.manager import TenableAssetAttributeManager
from tenable_headshot.core.runner import process_rules

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Tenable Headshot - Land critical hits on your vulnerabilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all enabled rules from config.json
  tenable-headshot

  # Run specific rules by name
  tenable-headshot --rules "Critical Windows Vulnerabilities" "Database Critical Vulnerabilities"

  # Use a different config file
  tenable-headshot --config custom-config.json

  # Dry run to see what would happen
  tenable-headshot --dry-run

  # List available rules
  tenable-headshot --list-rules
        """
    )

    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )

    parser.add_argument(
        '--rules', '-r',
        nargs='+',
        help='Specific rule names to run (default: all enabled rules)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--list-rules',
        action='store_true',
        help='List all available rules and exit'
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config(args.config)

        # List rules if requested
        if args.list_rules:
            print("\nAvailable rules in configuration:")
            print("=" * 80)
            for idx, rule in enumerate(config['rules'], 1):
                enabled = rule.get('enabled', True)
                status = "ENABLED" if enabled else "DISABLED"
                print(f"\n{idx}. {rule['name']} [{status}]")
                print(f"   Description: {rule.get('description', 'N/A')}")
                print(f"   Attribute: {rule['custom_attribute']['name']} = {rule['custom_attribute']['value']}")
                print(f"   Filters: {rule['plugin_filters']}")
            print("\n" + "=" * 80)
            return

        # Get credentials
        access_key, secret_key = get_credentials(config)

        # Initialize manager
        manager = TenableAssetAttributeManager(access_key, secret_key)

        # Process rules
        process_rules(manager, config, rule_names=args.rules, dry_run=args.dry_run)

    except FileNotFoundError as e:
        logger.error(str(e))
        logger.info("Create a config.json file based on config.example.json")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
