"""Asset attribute manager for Tenable.io."""

import logging
from typing import List, Dict, Any
from tenable.io import TenableIO
from datetime import datetime

logger = logging.getLogger(__name__)


class TenableAssetAttributeManager:
    """Manages Tenable asset custom attributes based on plugin filters."""

    def __init__(self, access_key: str, secret_key: str):
        """Initialize the Tenable.io client.

        Args:
            access_key: Tenable.io API access key
            secret_key: Tenable.io API secret key
        """
        self.tio = TenableIO(access_key=access_key, secret_key=secret_key)
        logger.info("Initialized Tenable.io client")

    def get_or_create_custom_attribute(self, attribute_name: str, description: str = "") -> str:
        """Get existing custom attribute or create if it doesn't exist.

        Args:
            attribute_name: Name of the custom attribute
            description: Description for the attribute (used if creating new)

        Returns:
            The attribute UUID
        """
        try:
            # List existing custom attributes
            attributes = self.tio.assets.list_attributes()

            # Check if attribute already exists
            for attr in attributes:
                if attr['name'] == attribute_name:
                    logger.info(f"Custom attribute '{attribute_name}' already exists (UUID: {attr['uuid']})")
                    return attr['uuid']

            # Create new attribute if it doesn't exist
            logger.info(f"Creating new custom attribute '{attribute_name}'")
            new_attr = self.tio.assets.create_attribute(
                name=attribute_name,
                description=description or f"Auto-created attribute: {attribute_name}"
            )
            logger.info(f"Created custom attribute '{attribute_name}' (UUID: {new_attr['uuid']})")
            return new_attr['uuid']

        except Exception as e:
            logger.error(f"Error managing custom attribute: {e}")
            raise

    def _build_filters_from_dict(self, plugin_filter: Dict[str, Any]) -> list:
        """Build Tenable API filters from a plugin filter dictionary.

        Args:
            plugin_filter: Dictionary containing filter criteria

        Returns:
            List of filter tuples for Tenable API
        """
        filters = []

        if 'plugin_id' in plugin_filter:
            plugin_ids = plugin_filter['plugin_id']
            if not isinstance(plugin_ids, list):
                plugin_ids = [plugin_ids]
            filters.append(('plugin.id', 'eq', plugin_ids))

        if 'severity' in plugin_filter:
            severity_map = {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low',
                'info': 'Info'
            }
            severity = severity_map.get(plugin_filter['severity'].lower(), plugin_filter['severity'])
            filters.append(('severity', 'eq', [severity]))

        if 'plugin_family' in plugin_filter:
            filters.append(('plugin.family', 'eq', [plugin_filter['plugin_family']]))

        if 'state' in plugin_filter:
            filters.append(('state', 'eq', [plugin_filter['state']]))
        
        if 'output_contains' in plugin_filter:
            # 'output_contains' will be handled separately in the main method
            pass    
        
        else:
            # By default, only look at open vulnerabilities
            filters.append(('state', 'eq', ['OPEN']))

        return filters

    def get_assets_by_plugin_filter(self, plugin_filters) -> List[str]:
        """Get asset UUIDs that match the plugin filter criteria.

        Supports both single filter (AND logic) and multiple filters (OR logic).

        Args:
            plugin_filters: Either a single filter dictionary or list of filter dictionaries.
                Single filter (AND logic - all conditions must match):
                {
                    'plugin_id': [19506, 20811],
                    'severity': 'critical',
                    'plugin_family': 'Windows',
                    'output_contains': 'specific text in output'
                }

                Multiple filters (OR logic - assets matching ANY filter group):
                [
                    {'plugin_id': 44871, 'output_contains': 'Active Directory Federation Services'},
                    {'severity': 'critical', 'plugin_family': 'Databases'}
                ]

                Supported filter keys:
                - plugin_id: Plugin ID or list of plugin IDs
                - severity: Severity level (critical, high, medium, low, info)
                - plugin_family: Plugin family name
                - state: Vulnerability state (OPEN, REOPENED, FIXED, etc.)
                - output_contains: Text to search for in plugin output (case-insensitive)

        Returns:
            List of asset UUIDs matching the criteria
        """
        try:
            # Handle both single dict and list of dicts
            if isinstance(plugin_filters, dict):
                filter_groups = [plugin_filters]
                logger.info(f"Searching for assets with plugin filters: {plugin_filters}")
            elif isinstance(plugin_filters, list):
                filter_groups = plugin_filters
                logger.info(f"Searching for assets with {len(filter_groups)} filter groups (OR logic)")
            else:
                raise ValueError("plugin_filters must be a dictionary or list of dictionaries")

            # Collect assets from all filter groups (OR logic)
            all_asset_uuids = set()

            for idx, filter_group in enumerate(filter_groups, 1):
                if len(filter_groups) > 1:
                    logger.info(f"Processing filter group {idx}/{len(filter_groups)}: {filter_group}")

                # Build the filters for this group
                filters = self._build_filters_from_dict(filter_group)

                # Export vulnerabilities matching this filter group
                logger.info("Exporting vulnerabilities to find matching assets...")
                vulns = self.tio.exports.vulns(filters=filters)

                group_assets = set()
                for vuln in vulns:
                    if 'asset' in vuln and 'uuid' in vuln['asset']:
                        # Check if output_contains filter is specified
                        if 'output_contains' in filter_group:
                            search_text = filter_group['output_contains'].lower()
                            # Check if the vulnerability has output that contains the search text
                            output_text = vuln.get('output', '').lower()
                            if search_text not in output_text:
                                continue  # Skip this vulnerability if output doesn't match

                        group_assets.add(vuln['asset']['uuid'])

                logger.info(f"Filter group {idx} matched {len(group_assets)} unique assets")
                all_asset_uuids.update(group_assets)

            logger.info(f"Total: Found {len(all_asset_uuids)} unique assets across all filter groups")
            return list(all_asset_uuids)

        except Exception as e:
            logger.error(f"Error querying assets: {e}")
            raise

    def update_asset_attributes(self, asset_uuids: List[str], attribute_name: str,
                               attribute_value: str, batch_size: int = 100) -> Dict[str, int]:
        """Update custom attribute for specified assets.

        Args:
            asset_uuids: List of asset UUIDs to update
            attribute_name: Name of the custom attribute
            attribute_value: Value to set for the attribute
            batch_size: Number of assets to update per batch

        Returns:
            Dictionary with success and failure counts
        """
        try:
            results = {'success': 0, 'failed': 0}
            total = len(asset_uuids)

            logger.info(f"Updating {total} assets with {attribute_name}={attribute_value}")

            # Process in batches
            for i in range(0, total, batch_size):
                batch = asset_uuids[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} assets)")

                for asset_uuid in batch:
                    try:
                        # Update the custom attribute
                        self.tio.assets.assign_attributes(
                            asset_uuid,
                            attributes=[{attribute_name: attribute_value}]
                        )
                        results['success'] += 1

                    except Exception as e:
                        logger.error(f"Failed to update asset {asset_uuid}: {e}")
                        results['failed'] += 1

                logger.info(f"Progress: {min(i + batch_size, total)}/{total} assets processed")

            logger.info(f"Update complete. Success: {results['success']}, Failed: {results['failed']}")
            return results

        except Exception as e:
            logger.error(f"Error updating asset attributes: {e}")
            raise

    def run_update(self, attribute_name: str, attribute_value: str,
                   plugin_filters: Dict[str, Any], attribute_description: str = ""):
        """Main workflow to update assets based on plugin filters.

        Args:
            attribute_name: Name of the custom attribute to update
            attribute_value: Value to set for the attribute
            plugin_filters: Dictionary of plugin filter criteria
            attribute_description: Description for the custom attribute
        """
        try:
            start_time = datetime.now()
            logger.info("=" * 60)
            logger.info(f"Starting asset attribute update job at {start_time}")
            logger.info("=" * 60)

            # Step 1: Ensure custom attribute exists
            self.get_or_create_custom_attribute(attribute_name, attribute_description)

            # Step 2: Get assets matching the plugin filter
            asset_uuids = self.get_assets_by_plugin_filter(plugin_filters)

            if not asset_uuids:
                logger.warning("No assets found matching the filter criteria")
                return

            # Step 3: Update the custom attribute on matching assets
            results = self.update_asset_attributes(asset_uuids, attribute_name, attribute_value)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info("=" * 60)
            logger.info(f"Job completed in {duration:.2f} seconds")
            logger.info(f"Total assets updated: {results['success']}")
            logger.info(f"Failed updates: {results['failed']}")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Job failed: {e}")
            raise