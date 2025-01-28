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

@dataclass
class ToolCallFunction:
    name: str
    arguments: str

@dataclass
class ToolCall:
    id: str
    type: str
    function: ToolCallFunction

@dataclass
class Message:
    id: str
    model_name: str
    thread_id: str
    user_id: str
    content_type: str
    content: str
    content_array: List[Any]
    type: str
    tool_call_id: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    created_at: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        if data.get('tool_calls'):
            tool_calls = [
                ToolCall(
                    id=tc['id'],
                    type=tc['type'],
                    function=ToolCallFunction(
                        name=tc['function']['name'],
                        arguments=tc['function']['arguments']
                    )
                )
                for tc in data['tool_calls']
            ]
        else:
            tool_calls = None
            
        return cls(
            id=data['id'],
            model_name=data['model_name'],
            thread_id=data['thread_id'],
            user_id=data['user_id'],
            content_type=data['content_type'],
            content=data['content'],
            content_array=data['content_array'],
            type=data['type'],
            tool_call_id=data.get('tool_call_id'),
            tool_calls=tool_calls,
            created_at=data['created_at']
        )

@dataclass
class ThreadCost:
    total_cost: float
    total_output_tokens: int
    total_input_tokens: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ThreadCost':
        return cls(
            total_cost=float(data['total_cost']),
            total_output_tokens=int(data['total_output_tokens']),
            total_input_tokens=int(data['total_input_tokens'])
        )
