from ..core.tracing import LangDBTracing
from typing import Optional
from openinference.instrumentation.crewai import CrewAIInstrumentor
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import trace
from opentelemetry.trace.propagation import set_span_in_context
import uuid
from litellm import litellm

original_completion = litellm.completion

def completion(*args, **kwargs):
    span = trace.get_current_span()

    ctx = set_span_in_context(span)
    
    headers = kwargs.get('extra_headers', {})
    TraceContextTextMapPropagator().inject(headers, ctx)
    headers["x-run-id"] = str(uuid.UUID(int=span.get_span_context().trace_id))
    
    headers["x-thread-id"] = headers["x-run-id"]
    span.set_attribute("langdb.thread_id", headers['x-thread-id'])
    
    kwargs['extra_headers'] = headers
    return original_completion(*args, **kwargs)

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "crewai")

    processor = tracer.get_processor()
    tracer_provider = trace_sdk.TracerProvider()

    tracer_provider.add_span_processor(processor)
    CrewAIInstrumentor().instrument(tracer_provider=tracer_provider)
    
    litellm.completion = completion