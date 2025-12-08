"""Rule processing and execution."""

import logging
from typing import List, Dict, Any, Optional

from tenable_headshot.core.manager import TenableAssetAttributeManager

logger = logging.getLogger(__name__)


def process_rules(manager: TenableAssetAttributeManager, config: Dict[str, Any],
                  rule_names: Optional[List[str]] = None, dry_run: bool = False):
    """Process rules from configuration.

    Args:
        manager: TenableAssetAttributeManager instance
        config: Configuration dictionary
        rule_names: Optional list of specific rule names to run. If None, runs all enabled rules.
        dry_run: If True, only show what would be done without making changes
    """
    rules = config['rules']
    total_rules = 0
    successful_rules = 0
    failed_rules = 0

    # Filter rules based on rule_names if provided
    if rule_names:
        rules_to_process = [r for r in rules if r['name'] in rule_names]
        if len(rules_to_process) != len(rule_names):
            found_names = {r['name'] for r in rules_to_process}
            missing = set(rule_names) - found_names
            logger.warning(f"Rules not found in config: {missing}")
    else:
        # Only process enabled rules if no specific names provided
        rules_to_process = [r for r in rules if r.get('enabled', True)]

    if not rules_to_process:
        logger.warning("No rules to process")
        return

    logger.info(f"Processing {len(rules_to_process)} rule(s)")
    logger.info("=" * 80)

    for rule in rules_to_process:
        total_rules += 1
        rule_name = rule['name']

        try:
            logger.info(f"\n{'=' * 80}")
            logger.info(f"RULE {total_rules}/{len(rules_to_process)}: {rule_name}")
            logger.info(f"Description: {rule.get('description', 'N/A')}")
            logger.info(f"{'=' * 80}")

            if dry_run:
                logger.info("[DRY RUN] Would process this rule with:")
                logger.info(f"  Attribute: {rule['custom_attribute']['name']} = {rule['custom_attribute']['value']}")
                logger.info(f"  Filters: {rule['plugin_filters']}")
                successful_rules += 1
                continue

            # Extract rule details
            attr = rule['custom_attribute']
            attribute_name = attr['name']
            attribute_value = attr['value']
            attribute_description = attr.get('description', '')
            plugin_filters = rule['plugin_filters']

            # Run the update
            manager.run_update(
                attribute_name=attribute_name,
                attribute_value=attribute_value,
                plugin_filters=plugin_filters,
                attribute_description=attribute_description
            )

            successful_rules += 1
            logger.info(f"Rule '{rule_name}' completed successfully")

        except Exception as e:
            failed_rules += 1
            logger.error(f"Rule '{rule_name}' failed: {e}")
            # Continue with next rule instead of stopping

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total rules processed: {total_rules}")
    logger.info(f"Successful: {successful_rules}")
    logger.info(f"Failed: {failed_rules}")
    logger.info("=" * 80)