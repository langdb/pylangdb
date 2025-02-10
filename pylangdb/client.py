from typing import Any, Dict, List
import requests
import urllib3
import pandas as pd
import time
from openai import OpenAI
from uuid import uuid4
from pylangdb.types import Message, ThreadCost

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

    def __init__(self, api_key: str, project_id: str | None = None, base_url: str | None = None):
        self.api_key = api_key
        self.project_id = project_id
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = DEFAULT_SERVER_URL
        if project_id:
            api_base = f"{self.base_url}/{project_id}/v1"
        else:
            api_base = f"{self.base_url}/v1"

        self.client = OpenAI(api_key=api_key, base_url=api_base)

    def completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        headers: Dict[str, Any] | None = None,
        extra_body: Dict[str, Any] | None = None,
        thread_id: str | None = None,
        **kwargs
    ) -> Dict[str, str]:
        """Create a completion using the LangDB API.

        Args:
            model: The model to use for completion
            messages: List of message dictionaries with role and content
            headers: Optional additional headers to send
            extra_body: Optional additional body parameters like external model providers
            thread_id: Optional thread ID for conversation tracking
            **kwargs: Additional parameters to pass to the OpenAI chat completion API (e.g. temperature, max_tokens)

        Returns:
            Dictionary containing completion content and thread ID
        """
        if headers is None:
            headers = {}

        # Set thread_id if not provided
        if thread_id is None:
            thread_id = str(uuid4())

        headers["x-thread-id"] = thread_id

        # Create completion request
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            extra_headers=headers,
            extra_body=extra_body,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content.strip(),
            "thread_id": thread_id,
        }

    def get_analytics(
        self,
        tags: str,
        start_time_us: int | None = None,
        end_time_us: int | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch analytics data from /analytics/summary with the specified project_id and tags.

        :param tags: A comma-separated (or otherwise delimited) list of tags.
        :param start_time_us: Start time in microseconds. Defaults to 24 hours before end_time_us.
        :param end_time_us: End time in microseconds. Defaults to current time.
        :return: A list of dictionaries containing analytics data.
        """
        if not self.project_id:
            raise ValueError("project_id is required for analytics operations")

        url = f"{self.base_url}/analytics/summary"

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
            "tag_keys": [tags],
        }
        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}",
        }
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    def get_analytics_dataframe(
        self,
        tags: str,
        start_time_us: int | None = None,
        end_time_us: int | None = None,
    ) -> pd.DataFrame:
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
                    flat_list = [
                        item
                        for sublist in tag_tuple
                        for item in (
                            sublist if isinstance(sublist, list) else [sublist]
                        )
                    ]
                    cleaned_list = [
                        item for item in flat_list if item not in (None, "")
                    ]
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

        url = f"{self.base_url}/threads/{thread_id}/messages"

        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        return [Message.from_dict(msg) for msg in data]

    def get_usage(self, thread_id: str) -> ThreadCost:
        """
        Get the cost information for a specific thread.

        :param thread_id: The ID of the thread to get cost for.
        :return: A ThreadCost object containing cost and token usage information.
        """
        if not self.project_id:
            raise ValueError("project_id is required for thread operations")

        url = f"{self.base_url}/threads/{thread_id}/cost"

        headers = {
            "x-project-id": self.project_id,
            "Authorization": f"Bearer {self.api_key}",
        }
        response = requests.get(url, headers=headers)

        response.raise_for_status()

        data = response.json()
        return ThreadCost.from_dict(data)

    def create_evaluation_df(self, thread_ids: List[str]) -> pd.DataFrame:
        """
        Create a DataFrame containing messages and cost information for multiple threads.

        :param thread_ids: List of thread IDs to analyze
        :return: DataFrame containing message details and associated costs for all threads
        """
        all_messages_data = []

        for thread_id in thread_ids:
            try:
                # Get messages and cost for each thread
                messages = self.get_messages(thread_id)
                thread_cost = self.get_usage(thread_id)

                # Process messages for this thread
                for msg in messages:
                    message_data = {
                        "message_id": msg.id,
                        "thread_id": msg.thread_id,
                        "type": msg.type,
                        "model": msg.model_name,
                        "content": msg.content,
                        "created_at": msg.created_at,
                        "user_id": msg.user_id,
                        "thread_total_cost": thread_cost.total_cost,
                        "thread_input_tokens": thread_cost.total_input_tokens,
                        "thread_output_tokens": thread_cost.total_output_tokens,
                    }
                    all_messages_data.append(message_data)
            except Exception as e:
                print(f"Error processing thread {thread_id}: {str(e)}")
                continue

        # Create DataFrame from all collected data
        df = pd.DataFrame(all_messages_data)

        # Sort by created_at to maintain chronological order
        if not df.empty:
            df["created_at"] = pd.to_datetime(df["created_at"])
            df = df.sort_values("created_at")

        return df

    def list_models(self) -> List[str]:
        """
        List available models from the API.

        :return: List of model names
        """
        response = self.client.models.list()
        return [model.id for model in response.data]
