from ..core.tracing import LangDBTracing
from typing import Optional

from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
from openinference.instrumentation.openai_agents._processor import OpenInferenceTracingProcessor

from agents.tracing.setup import GLOBAL_TRACE_PROVIDER
from agents.tracing.processors import BackendSpanExporter
from agents.tracing import Span, Trace

from openai import AsyncOpenAI

from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry import trace
from opentelemetry.trace.propagation import set_span_in_context

import uuid

original_post = AsyncOpenAI.post

original_on_span_start = OpenInferenceTracingProcessor.on_span_start
original_on_trace_start = OpenInferenceTracingProcessor.on_trace_start


def post(self, *args, **kwargs):
    span = trace.get_current_span()

    ctx = set_span_in_context(span)

    headers = kwargs.get('options', {}).get('headers', {})
    TraceContextTextMapPropagator().inject(headers, ctx)

    run_id = span._attributes.get("langdb.run_id")
    thread_id = span._attributes.get("langdb.thread_id")

    headers["x-run-id"] = run_id
    headers["x-thread-id"] = thread_id
    
    kwargs['options']['headers'] = headers

    return original_post(self, *args, **kwargs)

def on_span_start(self, span: Span[any]):
    original_on_span_start(self, span)

    if not span.started_at:
        return
    
    trace = GLOBAL_TRACE_PROVIDER.get_current_trace()

    group_id = trace.export()['group_id']
    if not group_id:
        group_id = str(uuid.UUID(trace.trace_id.replace("trace_", "")))

    self._otel_spans[span.span_id].set_attribute("langdb.thread_id", group_id)
    self._otel_spans[span.span_id].set_attribute("langdb.run_id", group_id)
    self._otel_spans[span.span_id].set_attribute("langdb.duhas", group_id)

def on_trace_start(self, trace: Trace):
    original_on_trace_start(self, trace)

    group_id = trace.export()['group_id']
    if not group_id:
        group_id = str(uuid.UUID(trace.trace_id.replace("trace_", "")))

    self._root_spans[trace.trace_id].set_attribute("langdb.thread_id", group_id)
    self._root_spans[trace.trace_id].set_attribute("langdb.run_id", group_id)
    self._root_spans[trace.trace_id].set_attribute("langdb.duhas", group_id)

def init(collector_endpoint: Optional[str] = None, api_key: Optional[str] = None, project_id: Optional[str] = None):
    tracer = LangDBTracing(collector_endpoint, api_key, project_id, "openai")
    
    processor = tracer.get_processor()

    tracer_provider = trace_sdk.TracerProvider()
    tracer_provider.add_span_processor(processor)

    OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer_provider)

    OpenInferenceTracingProcessor.on_span_start = on_span_start
    OpenInferenceTracingProcessor.on_trace_start = on_trace_start
    
    # Inject trace headers
    AsyncOpenAI.post = post
    
    # Disable span export
    BackendSpanExporter.export = lambda self, items: None