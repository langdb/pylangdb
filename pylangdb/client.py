from typing import Any, Dict
import requests
import json
import urllib3
import pandas as pd

from pylangdb.types import MessageRequest
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_SERVER_URL = "https://api.dev.langdb.ai"

class LangDb:
    """
    A client for interacting with the LangDb server.

    Args:
        client_id (str): The client ID for authentication.
        client_secret (str): The client secret for authentication.
        server_url (str, optional): The URL of the LangDb server. Defaults to None.

    Attributes:
        client_id (str): The client ID for authentication.
        client_secret (str): The client secret for authentication.
        server_url (str): The URL of the LangDb server.

    """

    def __init__(self, client_id: str, client_secret: str, server_url: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.server_url = server_url or DEFAULT_SERVER_URL

    def get_access_token(self) -> str:
        """
        Get the access token for authentication.

        Returns:
            str: The access token.

        Raises:
            Exception: If there is an error in getting the access token.

        """
        url = f"{self.server_url}/oauth2/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code > 299:
            text = response.text or "Failed to send message to the server"
            print("getAccessToken: RESPONSE ERROR", text)
            raise Exception(text)
        else:
            data = response.json()
            return data.get("access_token")

    def get_entities(self, entity_name: str) -> list:
        """
        Get the entities for a given entity name.

        Args:
            entity_name (str): The name of the entity.

        Returns:
            list: The list of entities.

        Raises:
            Exception: If there is an error in getting the entities.

        """
        headers = {"Content-Type": "application/json"}
        access_token = self.get_access_token()
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        url = f"{self.server_url}/{entity_name}"
        response = requests.post(url, headers=headers, data=json.dumps({}))
        
        if response.status_code > 299:
            text = response.text or "Failed to send message to the server"
            print("RESPONSE ERROR", text)
            raise Exception(text or f"{response.status_code}: {text}")

        return response.json()

    def query_df(self, query: str, params: dict = None) -> pd.DataFrame:
        """
        Execute a query and return the result as a pandas DataFrame.

        Args:
            query (str): The query to execute.
            params (dict, optional): The parameters for the query. Defaults to None.

        Returns:
            pd.DataFrame: The result of the query as a pandas DataFrame.

        """
        res = self.query(query, params)
        data = res.get('data', [])
        df = pd.DataFrame(data)        
        return df

    def query_with_trace_id(self, trace_id: str) -> dict:
        """
        Execute a query with a trace ID and return the result as a dictionary.

        Args:
            trace_id (str): The trace ID.

        Returns:
            dict: The result of the query as a dictionary.

        """
        query = f"""
        SELECT 
            operation_name,
            attribute['model'] AS model,
            JSONExtractInt(attribute['usage'], 'prompt_tokens') AS prompt_tokens,
            JSONExtractInt(attribute['usage'], 'completion_tokens') AS completion_tokens,
            JSONExtractInt(attribute['usage'], 'total_tokens') AS total_tokens,
            start_time_us,
            finish_time_us
        FROM langdb.traces 
        WHERE trace_id = '{trace_id}'
        ORDER BY start_time_us DESC 
        LIMIT 10
        """

        # Call the query function with the constructed query
        return self.query_df(query)    
        
    def query(self, query: str, params: dict = None) -> dict:
        """
        Execute a query and return the result as a dictionary.

        Args:
            query (str): The query to execute.
            params (dict, optional): The parameters for the query. Defaults to None.

        Returns:
            dict: The result of the query as a dictionary.

        """
        headers = {"Content-Type": "application/json"}
        access_token = self.get_access_token()
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        execute_request = {
            "query": query,
            "params": params or {}
        }
        url = f"{self.server_url}/query"
        response = requests.post(url, headers=headers, data=json.dumps(execute_request))
        
        if response.status_code > 299:
            text = response.text or "Failed to send message to the server"
            print("RESPONSE ERROR", text)
            raise Exception(text or f"{response.status_code}: {text}")

        return response.json()

    def execute_view(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a view with the given parameters and return the result as a dictionary.

        Args:
            params (Dict[str, Any]): The parameters for the view.

        Returns:
            Dict[str, Any]: The result of the view as a dictionary.

        """
        access_token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        url = f"{self.server_url}/views/execute"
        response = requests.post(url, headers=headers, data=json.dumps(params))

        if response.status_code > 299:
            text = response.text or "Failed to send message to the server"
            print("RESPONSE ERROR", text)
            raise Exception(text or f"{response.status_code}: {text}")

        data = response.json()    
        df = pd.DataFrame(data)
        return df

    def invoke_model(self, request: MessageRequest) -> str:
        """
        Invoke a model with the given request and return the result as a string.

        Args:
            request (MessageRequest): The request to invoke the model.

        Returns:
            str: The result of the model invocation as a string.

        """
        access_token = self.get_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        # Check if message is a string or a list and print appropriate info
        message_info = (
            f"Message: {request.message}" if isinstance(request.message, str) 
            else f"Images: {len(request.message)}"
        )

        # Convert the dataclass to a dictionary for JSON serialization
        request_dict = request.__dict__

        # Make the POST request
        url = f"{self.server_url}/invoke"
        response = requests.post(url, headers=headers, data=json.dumps(request_dict))

        if response.status_code > 299:
            text = response.text or "Failed to send message to the server"
            print("RESPONSE ERROR", text)
            raise Exception(text or f"{response.status_code}: {text}")

        message = response.text
        response_headers = response.headers
        return message