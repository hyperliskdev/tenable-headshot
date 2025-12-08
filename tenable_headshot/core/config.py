"""Configuration loading and validation."""

import os
import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and validate configuration from JSON file.

    Args:
        config_path: Path to the configuration JSON file

    Returns:
        Parsed configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        # Validate required fields
        if 'rules' not in config:
            raise ValueError("Configuration must contain 'rules' array")

        if not isinstance(config['rules'], list):
            raise ValueError("'rules' must be an array")

        # Validate each rule
        for idx, rule in enumerate(config['rules']):
            if 'name' not in rule:
                raise ValueError(f"Rule {idx} missing 'name' field")
            if 'custom_attribute' not in rule:
                raise ValueError(f"Rule '{rule['name']}' missing 'custom_attribute' field")
            if 'plugin_filters' not in rule:
                raise ValueError(f"Rule '{rule['name']}' missing 'plugin_filters' field")

            # Validate custom_attribute structure
            attr = rule['custom_attribute']
            if 'name' not in attr or 'value' not in attr:
                raise ValueError(f"Rule '{rule['name']}' custom_attribute missing 'name' or 'value'")

        logger.info(f"Loaded configuration from {config_path}")
        return config

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")


def get_credentials(config: Dict[str, Any]) -> tuple:
    """Get API credentials from environment variables.

    Args:
        config: Configuration dictionary

    Returns:
        Tuple of (access_key, secret_key)

    Raises:
        ValueError: If credentials are not set
    """
    tenable_config = config.get('tenable', {})
    access_key_env = tenable_config.get('access_key_env', 'TENABLE_ACCESS_KEY')
    secret_key_env = tenable_config.get('secret_key_env', 'TENABLE_SECRET_KEY')

    access_key = os.environ.get(access_key_env)
    secret_key = os.environ.get(secret_key_env)

    if not access_key or not secret_key:
        raise ValueError(
            f"API credentials not found. Please set {access_key_env} and {secret_key_env} "
            "environment variables"
        )

    return access_key, secret_key