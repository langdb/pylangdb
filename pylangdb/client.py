from typing import Any, Dict, List
import requests
import json
import urllib3
import pandas as pd
import time
from os import getenv
from openai import OpenAI
from pylangdb.types import MessageRequest, Message, ThreadCost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_SERVER_URL = "https://api.us-east-1.langdb.ai"

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

    def __init__(self, api_key: str, project_id: str | None = None):
        self.api_key = api_key
        self.project_id = project_id
        if project_id:
            api_base = f"https://api.us-east-1.langdb.ai/{project_id}/v1"
        else:
            api_base = "https://api.us-east-1.langdb.ai/v1"

        self.client = OpenAI(api_key=api_key, api_base=api_base)

    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        headers: Any = None,
        extra_body: Any = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        response = self.client.chat.completions.create(
            model=model,  # Use the model
            messages=messages,  # Define the interaction
            temperature=temperature,  # Control the creativity of the response
            max_tokens=max_tokens,  # Limit the length of the response
            extra_headers=headers,
            extra_body=extra_body,
        )   
        return response.choices[0].message.content.strip()

    def get_analytics(self, tags: str, start_time_us: int | None = None, end_time_us: int | None = None) -> List[Dict[str, Any]]:
        """
        Fetch analytics data from /analytics/summary with the specified project_id and tags.

        :param tags: A comma-separated (or otherwise delimited) list of tags.
        :param start_time_us: Start time in microseconds. Defaults to 24 hours before end_time_us.
        :param end_time_us: End time in microseconds. Defaults to current time.
        :return: A list of dictionaries containing analytics data.
        """
        if not self.project_id:
            raise ValueError("project_id is required for analytics operations")

        url = f"{DEFAULT_SERVER_URL}/analytics/summary"
        
        # Set default end time to current time if not provided
        if end_time_us is None:
            end_time_us = int(time.time() * 1_000_000)
        
        # Set default start time to 24 hours before end time if not provided
        if start_time_us is None:
            start_time_us = end_time_us - (24 * 60 * 60 * 1_000_000)  # 24 hours earlier
        
        # Prepare the JSON payload
        payload = {
            "start_time_us": start_time_us,
            "end_time_us": end_time_us,
            "groupBy": ["tag"],
            "tag_keys": [tags]
        }
        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}"
        }
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        # Return the JSON response
        return response.json()

    def get_analytics_dataframe(self, tags: str, start_time_us: int | None = None, end_time_us: int | None = None) -> pd.DataFrame:
        """
        Calls get_analytics() and converts the returned 'summary' data into a Pandas DataFrame,
        with each row corresponding to one entry in the 'summary' list.

        :param tags: A comma-separated list of tags (e.g. "gpt-4,claude").
        :param start_time_us: Start time in microseconds. Defaults to 24 hours before end_time_us.
        :param end_time_us: End time in microseconds. Defaults to current time.
        :return: A Pandas DataFrame where each row is a summary record. 
                The 'tag_tuple' is flattened into a 'tag' column.
        """
        raw_json = self.get_analytics(tags, start_time_us, end_time_us)
        summary_list = raw_json.get("summary", [])

        df = pd.DataFrame(summary_list)

        if not df.empty:
            def clean_tag_tuple(tag_tuple):
                if isinstance(tag_tuple, list):
                    flat_list = [item for sublist in tag_tuple for item in (sublist if isinstance(sublist, list) else [sublist])]
                    cleaned_list = [item for item in flat_list if item not in (None, '')]
                    return cleaned_list if cleaned_list else None
                return None

            df["tag_tuple"] = df["tag_tuple"].apply(clean_tag_tuple)
            df = df[df["tag_tuple"].notnull()]

        return df

    def get_messages(self, thread_id: str) -> List[Message]:
        """
        Fetch messages for a specific thread using its ID.

        :param thread_id: The ID of the thread to fetch messages for.
        :return: A list of Message objects associated with the thread.
        """
        if not self.project_id:
            raise ValueError("project_id is required for thread operations")

        url = f"{DEFAULT_SERVER_URL}/threads/{thread_id}/messages"
        
        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return [Message.from_dict(msg) for msg in data]

    def get_cost(self, thread_id: str) -> ThreadCost:
        """
        Get the cost information for a specific thread.

        :param thread_id: The ID of the thread to get cost for.
        :return: A ThreadCost object containing cost and token usage information.
        """
        if not self.project_id:
            raise ValueError("project_id is required for thread operations")

        url = f"{DEFAULT_SERVER_URL}/threads/{thread_id}/cost"
        
        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return ThreadCost.from_dict(data)