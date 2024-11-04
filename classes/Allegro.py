import httpx
from typing import Optional, Dict, Union

class Allegro:
    def __init__(self, api_key: str, request_id: Optional[str] = None):
        self.api_url_generate = "https://api.rhymes.ai/v1/generateVideoSyn"
        self.api_url_query = "https://api.rhymes.ai/v1/videoQuery"
        self.api_key = api_key
        self.request_id = request_id
        self.video_url = None

    def _get_headers(self) -> Dict[str, str]:
        """Generate the authorization and content headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def generate_video(self, data: Dict[str, Union[str, int, float]]) -> Union[Dict, str]:
        """Generate a video based on the provided data."""
        headers = self._get_headers()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url_generate, headers=headers, json=data)
            response.raise_for_status()
            self.request_id = response.json().get("data")
            return response.json()
        except httpx.HTTPStatusError as e:
            return f"Request failed with status {e.response.status_code}: {e.response.text}"
        except httpx.RequestError as e:
            return f"Request error: {str(e)}"

    async def query_video_status(self, request_id: str) -> Union[Dict, str]:
        """Check the status of a video generation request by ID."""
        headers = self._get_headers()
        params = {"requestId": request_id}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.api_url_query, headers=headers, params=params)
            response.raise_for_status()
            self.video_url = response.json().get("data")
            return response.json()
        except httpx.HTTPStatusError as e:
            return f"Request failed with status {e.response.status_code}: {e.response.text}"
        except httpx.RequestError as e:
            return f"Request error: {str(e)}"
