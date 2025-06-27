import os
import uuid
from typing import AsyncGenerator, Optional, Dict, Any
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models.lite_llm import LiteLlm
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.trace.propagation import set_span_in_context

class LangDBLlm(BaseLlm):
    """Custom LangDB implementation of BaseLlm."""
    
    _lite_llm: LiteLlm
    def __init__(self, model: str, api_key: Optional[str] = None, api_base: Optional[str] = None, project_id: Optional[str] = None, mcp_servers: Optional[list[Dict[str, Any]]] = None, run_id: Optional[str] = None, thread_id: Optional[str] = None, extra_headers: Optional[Dict[str, str]] = None, is_project_in_url: Optional[bool] = False, **kwargs):
        """Initialize the LangDB LLM.
        
        Args:
            model: The name of the LLM model to use
            api_key: The API key for the LangDB API, optional, by default read from env variable LANGDB_API_KEY
            api_base: The base URL for the LangDB API, optional, by default read from env variable LANGDB_API_BASE_URL
            project_id: The ID of the LangDB project to use, optional, by default read from env variable LANGDB_PROJECT_ID
            run_id: The ID of the run to use, optional, by default read from env variable LANGDB_RUN_ID
            thread_id: The ID of the thread to use, optional, by default read from env variable LANGDB_THREAD_ID
            extra_headers: The extra headers to use for the LangDB LLM, optional
            is_project_in_url: Whether the project ID is in the URL, if not, project id is in header x-project-id, optional, by default False
            mcp_servers: The MCP servers to use for the LangDB LLM, optional
        """
        # check if model is start with openai/
        custom_model_name = model
        if not model.startswith("openai/"):
            custom_model_name = "openai/" + model
        super().__init__(model=custom_model_name)
        if api_key is None:
            api_key = os.getenv("LANGDB_API_KEY")
        if api_key is None:
            raise ValueError("LANGDB_API_KEY is not set")
        
        if api_base is None:
            api_base = os.getenv("LANGDB_API_BASE_URL")
        if api_base is None:
            api_base = 'https://api.us-east-1.langdb.ai'
 
        if project_id is None:
            project_id = os.getenv("LANGDB_PROJECT_ID")
        if project_id is None:
            raise ValueError("LANGDB_PROJECT_ID is not set")
        
        if extra_headers is None:
            extra_headers = {"Content-Type": "application/json"}

        if run_id:
            extra_headers["x-run-id"] = run_id
        
        if thread_id:
            extra_headers["x-thread-id"] = thread_id
        
        if is_project_in_url:
            api_base += "/" + project_id + "/v1"
        else:
            extra_headers["x-project-id"] = project_id
        self._lite_llm = LiteLlm(
            model=custom_model_name,
            api_key=api_key,
            api_base=api_base,
            extra_headers=extra_headers,
            mcp_servers=mcp_servers,
            **kwargs
        )
    @classmethod
    def supported_models(cls) -> list[str]:
        """Returns a list of supported models in regex for LlmRegistry."""
        return ["*"]
    
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        """Generates content from the given request.
        
        Args:
            llm_request: The request to send to the LLM
            stream: Whether to stream the response
            
        Yields:
            LlmResponse objects containing the generated content
        """
        # Access session_id from _additional_args if available
        session_id = None
        agent_name = None
        
        span = trace.get_current_span()
        span_context = span.get_span_context()
        # Convert trace_id from int to UUID
        trace_id = uuid.UUID(int=span_context.trace_id)
        
        # Check if _additional_args exists and contains session_id
        if hasattr(llm_request, '_additional_args'):
            session_id = llm_request._additional_args.get('session_id')
            invocation_id = llm_request._additional_args.get('invocation_id')
            agent_name = llm_request._additional_args.get('agent_name')
            # Create a new config dict if needed
            if not hasattr(self._lite_llm, '_additional_args'):
                self._lite_llm._additional_args = {}
            prev_extra_headers = self._lite_llm._additional_args.get('extra_headers', {})
            prev_extra_headers['x-run-id'] = str(trace_id)
            prev_extra_headers['x-thread-id']= session_id
            prev_extra_headers['x-agent-name'] = agent_name
            self._lite_llm._additional_args['extra_headers'] = prev_extra_headers
        
        span.set_attribute("langdb.thread_id", session_id)
        ctx = set_span_in_context(span)
        prev_extra_headers = self._lite_llm._additional_args.get('extra_headers', {})
        TraceContextTextMapPropagator().inject(prev_extra_headers, ctx)
        
        self._lite_llm._additional_args['extra_headers'] = prev_extra_headers

        # Process the request and create a response
        async for response in self._lite_llm.generate_content_async(llm_request, stream):
            yield response