# pylangdb
`pylangdb` is a Python package for interacting with `LangDb` APIs. Please find out more at https://langdb.ai/.

## Installation
To install `pylangdb`, use pip:

```bash
pip install pylangdb
```

## Usage

Initialize `LangDb`

```python
from pylangdb import LangDb, MessageRequest

langdb = LangDb(CLIENT_ID, CLIENT_SECRET)
```

Query
```python
query = "select * from langdb.models"
self.langdb.query_df(query)
```

Execute View
```python
langdb.execute_view({
    "view_name": "view_name", 
    "params": {
        "param_a": ".."
    }
})
```

Invoke Model
```python
msg = MessageRequest(
            model_name='review',
            message='You are a terrible product',
            parameters={},
            include_history=False
        )
response = langdb.invoke_model(msg)
```


## Publish
```bash
poetry build
poetry publish
```