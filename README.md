# pylangdb
`pylangdb` is a Python package for interacting with `LangDb` APIs. Please find out more at https://langdb.ai/.

## Installation
To install `pylangdb`, use pip:

```bash
pip install pylangdb
```

## Usage

### Initialize LangDb Client

```python
from pylangdb import LangDb

# Initialize with API key and project ID
client = LangDb(api_key="your_api_key", project_id="your_project_id")
```

### Chat Completions

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Say hello!"}
]

response = client.completion(
    model="gemini-1.5-pro-latest",
    messages=messages,
    temperature=0.7,
    max_tokens=100
)
```

### Thread Operations

#### Get Messages
Retrieve messages from a specific thread:

```python
messages = client.get_messages(thread_id="your_thread_id")

# Access message details
for message in messages:
    print(f"Type: {message.type}")
    print(f"Content: {message.content}")
    if message.tool_calls:
        for tool_call in message.tool_calls:
            print(f"Tool: {tool_call.function.name}")
```

#### Get Thread Cost
Get cost and token usage information for a thread:

```python
usage = client.get_usage(thread_id="your_thread_id")
print(f"Total cost: ${usage.total_cost:.4f}")
print(f"Input tokens: {usage.total_input_tokens}")
print(f"Output tokens: {usage.total_output_tokens}")
```

### Analytics

Get analytics data for specific tags:

```python
# Get raw analytics data
analytics = client.get_analytics(
    tags="model1,model2",
    start_time_us=None,  # Optional: defaults to 24 hours ago
    end_time_us=None     # Optional: defaults to current time
)

# Get analytics as a pandas DataFrame
df = client.get_analytics_dataframe(
    tags="model1,model2",
    start_time_us=None,
    end_time_us=None
)
```

## Development

### Setting up the environment

1. Clone the repository
2. Create a `.env` file with your credentials:
```bash
LANGDB_API_KEY="your_api_key"
LANGDB_PROJECT_ID="your_project_id"
```

### Running Tests

```bash
python -m unittest tests/client.py -v
```

## Publishing

```bash
poetry build
poetry publish