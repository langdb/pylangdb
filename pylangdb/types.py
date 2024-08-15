from dataclasses import dataclass, field
from typing import Union, List, Optional, Dict, Any, Tuple
from enum import Enum

# Enums
class MessageContentType(Enum):
    Text = 'Text'
    ImageUrl = 'ImageUrl'

class MessageType(Enum):
    SystemMessage = "system"
    AIMessage = "ai"
    HumanMessage = "human"

# Type Aliases
TextType = str
ImageUrlType = str
MessageContentPart = Tuple[MessageContentType, Union[TextType, ImageUrlType], Optional[dict]]

InnerMessage = Union[str, List[MessageContentPart]]

Entity = Union['providers', 'models', 'views', 'prompts']

InvokeResponse = Dict[str, Any]  # { message: str, headers: Any }

# Dataclasses
@dataclass
class ResizeOptions:
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class MessageRequest:
    model_name: str
    message: InnerMessage
    user_id: str = ''
    thread_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    include_history: bool = False
    history_length: Optional[int] = None

@dataclass
class ExecutionOptions:
    retries: int

@dataclass
class Tool:
    name: str
    description: str
    passed_args: List[Any] = field(default_factory=list)

@dataclass
class Model:
    description: str
    execution_options: ExecutionOptions
    input_args: str
    model_name: str
    model_type: str
    name: str
    prompt_name: str
    provider_name: str
    model_params: Dict[str, Any] = field(default_factory=dict)    
    tools: List[Tool] = field(default_factory=list)
