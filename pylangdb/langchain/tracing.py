from ..core.tracing import LangDBTracing
from typing import Optional
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.langchain import get_current_span
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation import set_span_in_context

import httpx
import uuid

processor = None

original_send = httpx.Client.send

def _send(session_id: str):
    def fn(*args, **kwargs):
        span = get_current_span()

        ctx = set_span_in_context(span)

        headers = {}
        TraceContextTextMapPropagator().inject(headers, ctx)
        headers.update({"x-run-id": str(uuid.UUID(int=span.get_span_context().trace_id))})

        if headers.get("x-thread-id"):
            span.set_attribute("langdb.thread_id", headers['x-thread-id'])
        else:
            if processor:
                print("processor", processor.span_attributes)
                print("span", span._attributes)
                thread_id = processor.span_attributes.get(uuid.UUID(int=span.get_span_context().trace_id), {}).get("langdb.thread_id")
                if thread_id:
                    headers.update({"x-thread-id": thread_id})
            else:
                span.set_attribute("langdb.thread_id", session_id)
                headers.update({"x-thread-id": session_id})

        args[1].headers.update(headers)

        return original_send(*args, **kwargs)
    
    return fn

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    session_id = str(uuid.uuid4())
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "langchain", session_id)
    
    processor = tracer.get_processor()

    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(processor)

    instrumentor = LangChainInstrumentor()
    instrumentor.instrument(tracer_provider=tracer_provider, separate_trace_from_runtime_context=False)

    httpx.Client.send = _send(session_id)