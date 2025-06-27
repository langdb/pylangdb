"""Feature flag management for langdb-adk client libraries."""

import importlib.util
import os
from typing import Dict, Set

# Feature flag environment variable prefix
ENV_LANGDB_FEATURE_PREFIX = "LANGDB_FEATURE_"

# Client library feature flags
FEATURE_ADK = "adk"
FEATURE_AGNO = "agno"
FEATURE_CREWAI = "crewai"
FEATURE_LANGCHAIN = "langchain"
FEATURE_OPENAI = "openai"
FEATURE_CLIENT = "client"

# Map of feature flags to required packages
FEATURE_PACKAGE_MAP = {
    FEATURE_ADK: ["google_adk"],
    FEATURE_AGNO: ["agno"],
    FEATURE_CREWAI: ["crewai"],
    FEATURE_LANGCHAIN: ["langchain", "langchain_core"],
    FEATURE_OPENAI: ["openai"],
    FEATURE_CLIENT: ["pandas", "requests", "openai", "python-dotenv"],
}

# Cache for available features
_available_features: Set[str] = set()
_features_checked = False


def _is_package_available(package_name: str) -> bool:
    """Check if a package is available in the current environment."""
    return importlib.util.find_spec(package_name) is not None


def _check_feature_available(feature: str) -> bool:
    """Check if a feature is available based on installed packages."""
    # First check if it's explicitly enabled/disabled via environment variable
    env_var = f"{ENV_LANGDB_FEATURE_PREFIX}{feature.upper()}"
    if env_var in os.environ:
        return os.environ[env_var].lower() in ("1", "true", "yes", "on")
    
    # Then check if required packages are available
    required_packages = FEATURE_PACKAGE_MAP.get(feature, [])
    if not required_packages:
        return False
    
    return all(_is_package_available(pkg) for pkg in required_packages)


def get_available_features() -> Set[str]:
    """Get all available features based on installed packages."""
    global _available_features, _features_checked
    
    if _features_checked:
        return _available_features
    
    _features_checked = True
    
    for feature in FEATURE_PACKAGE_MAP.keys():
        if _check_feature_available(feature):
            _available_features.add(feature)
    
    return _available_features


def is_feature_available(feature: str) -> bool:
    """Check if a specific feature is available."""
    if not _features_checked:
        get_available_features()
    
    return feature in _available_features
