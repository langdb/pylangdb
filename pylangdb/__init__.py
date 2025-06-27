"""LangDB package for Google ADK integration."""

# Import feature flags
from .feature_flags import (
    get_available_features, 
    is_feature_available,
    FEATURE_ADK, 
    FEATURE_AGNO, 
    FEATURE_CREWAI, 
    FEATURE_LANGCHAIN, 
    FEATURE_OPENAI,
    FEATURE_CLIENT
)

# Initialize available imports and __all__ list
__all__ = [
    "get_available_features",
    "is_feature_available",
    "FEATURE_ADK",
    "FEATURE_AGNO",
    "FEATURE_CREWAI",
    "FEATURE_LANGCHAIN",
    "FEATURE_OPENAI",
    "FEATURE_CLIENT"
]