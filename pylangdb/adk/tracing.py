from ..core.tracing import LangDBTracing
from typing import Optional
from opentelemetry import trace

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "adk")
    processor = tracer.get_processor()
    trace.get_tracer_provider().add_span_processor(processor)