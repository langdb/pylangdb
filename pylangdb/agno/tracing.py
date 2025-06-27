from openai import OpenAI
from ..core.tracing import LangDBTracing
from typing import Optional
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry import trace
from agno.models.langdb import LangDB
from agno.models.openai import OpenAIChat
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation import set_span_in_context

import os
import uuid

original_invoke = LangDB.invoke
original_invoke_stream = LangDB.invoke_stream
original_ainvoke = LangDB.ainvoke
original_ainvoke_stream = LangDB.ainvoke_stream

original_get_client_params = OpenAIChat._get_client_params

def _invoke(self, *args, **kwargs):
    return original_invoke(self, *args, **kwargs)

def _invoke_stream(self, *args, **kwargs):
    return original_invoke_stream(self, *args, **kwargs)

def _ainvoke(self, *args, **kwargs):
    return original_ainvoke(self, *args, **kwargs)

def _ainvoke_stream(self, *args, **kwargs):
    return original_ainvoke_stream(self, *args, **kwargs)

def _get_client_params(self):
    span = trace.get_current_span()
    ctx = set_span_in_context(span)

    host = os.getenv("LANGDB_API_BASE_URL")
    project_id = os.getenv("LANGDB_PROJECT_ID")
    self.base_url = f"{host}/{project_id}/v1"
    
    headers = self.default_headers or {}
    
    headers["x-thread-id"] = span._attributes.get("langdb.thread_id")
    headers["x-run-id"] = str(uuid.UUID(int=span.get_span_context().trace_id))

    TraceContextTextMapPropagator().inject(headers, ctx)

    self.default_headers = headers

    return original_get_client_params(self)

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    session_id = str(uuid.uuid4())
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "agno", session_id)
    
    processor = tracer.get_processor()

    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(processor)

    AgnoInstrumentor().instrument(tracer_provider=tracer_provider)

    LangDB.invoke = _invoke
    LangDB.invoke_stream = _invoke_stream
    LangDB.ainvoke = _ainvoke
    LangDB.ainvoke_stream = _ainvoke_stream
    OpenAIChat._get_client_params = _get_client_params