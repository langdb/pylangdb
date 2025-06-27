from typing import Optional, Dict, Any
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from typing import Dict, Any
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from .langdb_llm import LangDBLlm
from opentelemetry import trace
from google.genai import types

# Model callbacks
def langdb_after_model_cb(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    current_state = callback_context.state
    current_state_dict = current_state.to_dict()
    session_id = callback_context._invocation_context.session.id
    span = trace.get_current_span()
    if 'init_session_id' not in current_state_dict:
        callback_context.state['init_session_id'] = session_id
        span.set_attribute("langdb.thread_id", session_id)
    else:
        span.set_attribute("langdb.thread_id", current_state_dict['init_session_id'])
    return None

def langdb_before_model_cb(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    # Read/Write state example
    session_id = callback_context._invocation_context.session.id
    agent_name = callback_context.agent_name    
    invocation_id = callback_context._invocation_context.invocation_id
    
    current_state = callback_context.state
    current_state_dict = current_state.to_dict()
    init_session_id = session_id
    span = trace.get_current_span()
    if 'init_session_id' not in current_state_dict:
        callback_context.state['init_session_id'] = session_id
        span.set_attribute("langdb.thread_id", session_id)
    else:
        init_session_id = current_state_dict['init_session_id']
        span.set_attribute("langdb.thread_id", init_session_id)
   
    sequence_invocation_ids : list[str] = []
    # check if current_state_dict have sequence_invocation_ids
    if 'sequence_invocation_ids' in current_state_dict:
        sequence_invocation_ids = current_state_dict['sequence_invocation_ids']
       
    # add invocation_id to sequence_invocation_ids
    sequence_invocation_ids.append(invocation_id)
        
    # update current_state
    callback_context.state['sequence_invocation_ids'] = sequence_invocation_ids 
    # Create a new config dict if needed
    if not hasattr(llm_request, '_additional_args'):
        llm_request._additional_args = {}
    
    # Add session_id and agent_name to the additional args
    if init_session_id is not None and init_session_id != '':
        llm_request._additional_args['session_id'] = init_session_id
    if agent_name is not None and agent_name != '':
        llm_request._additional_args['agent_name'] = agent_name
        
    llm_request._additional_args['invocation_id'] = invocation_id
    
    
    return None # Allow model call to proceed

# Agent callbacks
def langdb_before_agent_cb(callback_context: CallbackContext) -> Optional[types.Content]:
   session_id = callback_context._invocation_context.session.id
   invocation_id = callback_context._invocation_context.invocation_id
   current_state = callback_context.state
   current_state_dict = current_state.to_dict()
   
   init_session_id = session_id
   span = trace.get_current_span()
   if 'init_session_id' not in current_state_dict:
       callback_context.state['init_session_id'] = session_id
       span.set_attribute("langdb.thread_id", session_id)
   else:
       init_session_id = current_state_dict['init_session_id']
       span.set_attribute("langdb.thread_id", init_session_id)
   
   sequence_invocation_ids : list[str] = []
   # check if current_state_dict have sequence_invocation_ids
   if 'sequence_invocation_ids' in current_state_dict:
       sequence_invocation_ids = current_state_dict['sequence_invocation_ids']


   # add invocation_id to sequence_invocation_ids
   sequence_invocation_ids.append(invocation_id)
        
   # update current_state
   callback_context.state['sequence_invocation_ids'] = sequence_invocation_ids    
   
   return None

def langdb_after_agent_cb(callback_context: CallbackContext) -> Optional[types.Content]:
    current_state = callback_context.state
    current_state_dict = current_state.to_dict()
    span = trace.get_current_span()
    if 'init_session_id' not in current_state_dict:
        span.set_attribute("langdb.thread_id", session_id)
    else:
        span.set_attribute("langdb.thread_id", current_state_dict['init_session_id'])
    return None

# Tool callbacks

def langdb_before_tool_cb( tool: BaseTool, args: Dict[str, Any], tool_context: CallbackContext) -> Optional[Dict]:
    session_id = tool_context._invocation_context.session.id
    invocation_id = tool_context._invocation_context.invocation_id
    span = trace.get_current_span()
    
    current_state = tool_context.state
    current_state_dict = current_state.to_dict()
    if 'init_session_id' not in current_state_dict:
       callback_context.state['init_session_id'] = session_id
       span.set_attribute("langdb.thread_id", session_id)
       span.set_attribute("langdb.run_id", invocation_id.replace("e-", "", 1))
    else:
        span.set_attribute("langdb.thread_id", current_state_dict['init_session_id'])
        span.set_attribute("langdb.run_id", invocation_id.replace("e-", "", 1))
    
    sequence_invocation_ids : list[str] = []
    # check if current_state_dict have sequence_invocation_ids
    if 'sequence_invocation_ids' in current_state_dict:
        sequence_invocation_ids = current_state_dict['sequence_invocation_ids']
        
    # remove invocation_id from sequence_invocation_ids
    sequence_invocation_ids.remove(invocation_id)
        
    # update current_state
    tool_context.state['sequence_invocation_ids'] = sequence_invocation_ids    

    return None

def langdb_after_tool_cb(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    session_id = tool_context._invocation_context.session.id
    invocation_id = tool_context._invocation_context.invocation_id
    current_state = tool_context.state
    current_state_dict = current_state.to_dict()
    span = trace.get_current_span()
    if 'init_session_id' not in current_state_dict:
        span.set_attribute("langdb.thread_id", session_id)
        span.set_attribute("langdb.run_id", invocation_id.replace("e-", "", 1))
    else:
        span.set_attribute("langdb.thread_id", current_state_dict['init_session_id'])
        span.set_attribute("langdb.run_id", invocation_id.replace("e-", "", 1))

    return None


original_init = Agent.__init__

# Agent class
def langdb_agent_init(*args, **kwargs):
    # get model from kwargs
    model = kwargs.get('model')
    if model is None:
        raise ValueError("model is required")
    # check if model is string or LangdbLlm
    if isinstance(model, str):
        model = LangDBLlm(model)
    elif isinstance(model, LangDBLlm):
        # do nothing
        pass
    else: 
        # raise error current only support string model
        raise ValueError("model must be a string")
        
    kwargs['model'] = model
    
    input_before_agent_callback = kwargs.get('before_agent_callback')
    if input_before_agent_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_before_agent_callback, list):
            # append langdb_before_agent_cb to the list
            input_before_agent_callback.append(langdb_before_agent_cb)
            kwargs['before_agent_callback'] = input_before_agent_callback
        else:
            kwargs['before_agent_callback'] = [input_before_agent_callback, langdb_before_agent_cb]
    else:
        kwargs['before_agent_callback'] = [langdb_before_agent_cb]
        
    input_after_agent_callback = kwargs.get('after_agent_callback')
    if input_after_agent_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_after_agent_callback, list):
            # append langdb_after_agent_cb to the list
            input_after_agent_callback.append(langdb_after_agent_cb)
            kwargs['after_agent_callback'] = input_after_agent_callback
        else:
            kwargs['after_agent_callback'] = [input_after_agent_callback, langdb_after_agent_cb]
    else:
        kwargs['after_agent_callback'] = [langdb_after_agent_cb]
    
    input_before_model_callback = kwargs.get('before_model_callback')
    if input_before_model_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_before_model_callback, list):
            # append langdb_before_model_cb to the list
            input_before_model_callback.append(langdb_before_model_cb)
            kwargs['before_model_callback'] = input_before_model_callback
        else:
            kwargs['before_model_callback'] = [input_before_model_callback, langdb_before_model_cb]
    else:
        kwargs['before_model_callback'] = [langdb_before_model_cb]
        
    input_after_model_callback = kwargs.get('after_model_callback')
    if input_after_model_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_after_model_callback, list):
            # append langdb_after_model_cb to the list
            input_after_model_callback.append(langdb_after_model_cb)
            kwargs['after_model_callback'] = input_after_model_callback
        else:
            kwargs['after_model_callback'] = [input_after_model_callback, langdb_after_model_cb]
    else:
        kwargs['after_model_callback'] = [langdb_after_model_cb]    
    
    
    input_before_tool_callback = kwargs.get('before_tool_callback')
    if input_before_tool_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_before_tool_callback, list):
            # append langdb_before_tool_cb to the list
            input_before_tool_callback.append(langdb_before_tool_cb)
            kwargs['before_tool_callback'] = input_before_tool_callback
        else:
            kwargs['before_tool_callback'] = [input_before_tool_callback, langdb_before_tool_cb]
    else:
        kwargs['before_tool_callback'] = [langdb_before_tool_cb]
    
    input_after_tool_callback = kwargs.get('after_tool_callback')
    if input_after_tool_callback is not None:
        # check if it is a list or a single callback
        if isinstance(input_after_tool_callback, list):
            # append langdb_after_tool_cb to the list
            input_after_tool_callback.append(langdb_after_tool_cb)
            kwargs['after_tool_callback'] = input_after_tool_callback
        else:
            kwargs['after_tool_callback'] = [input_after_tool_callback, langdb_after_tool_cb]
    else:
        kwargs['after_tool_callback'] = [langdb_after_tool_cb]
        
    original_init(*args, **kwargs)


def init_agent():
    Agent.__init__ = langdb_agent_init