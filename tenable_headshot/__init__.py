"""
Tenable Headshot - Land critical hits on your vulnerabilities.

Automatically update Tenable.io asset custom attributes based on
vulnerability plugin filters.
"""

__version__ = "1.0.0"
__author__ = "David Tomelnovich"

from tenable_headshot.core.manager import TenableAssetAttributeManager

__all__ = ["TenableAssetAttributeManager", "__version__"]
