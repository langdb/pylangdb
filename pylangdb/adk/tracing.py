from ..core.tracing import LangDBTracing
from typing import Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "adk")
    processor = tracer.get_processor()
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, 'add_span_processor'):
        tracer_provider.add_span_processor(processor)
    else:
        custom_provider = TracerProvider()
        custom_provider.add_span_processor(processor)
        trace.set_tracer_provider(custom_provider)