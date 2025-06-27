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

# Conditionally import client libraries based on available features

# Core imports are always available

# ADK client
if is_feature_available(FEATURE_ADK):
    try:
        from .adk.agent import init_agent
        from .adk.tracing import init
        __all__.extend(["init_agent", "init"])
    except ImportError:
        pass

# Agno client
if is_feature_available(FEATURE_AGNO):
    try:
        from .agno.tracing import init
        __all__.append("init")
    except ImportError:
        pass

# CrewAI client
if is_feature_available(FEATURE_CREWAI):
    try:
        from .crewai.tracing import init
        __all__.append("init")
    except ImportError:
        pass

# Langchain client
if is_feature_available(FEATURE_LANGCHAIN):
    try:
        from .langchain.tracing import init
        __all__.append("init")
    except ImportError:
        pass

# OpenAI client
if is_feature_available(FEATURE_OPENAI):
    try:
        from .openai.tracing import init
        __all__.append("init")
    except ImportError:
        pass

if is_feature_available(FEATURE_CLIENT):
    try:
        from .client.client import LangDb
        __all__.append("LangDb")
    except ImportError:
        pass