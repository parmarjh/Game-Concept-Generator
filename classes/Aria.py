import openai
import base64
from typing import Dict, List, Union

class Aria:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    def image_to_base64(self, image_path: str) -> str:
        """Converts an image to a base64-encoded string."""
        try:
            with open(image_path, "rb") as image_file:
                base64_string = base64.b64encode(image_file.read()).decode("utf-8")
            return base64_string
        except FileNotFoundError:
            return "Image file not found. Please check the path."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def chat(self, messages: List[Dict[str, Dict[str, str]]]) -> Union[Dict, str]:
        """Generate a response based on the provided chat messages."""
        try:
            response = openai.ChatCompletion.create(
                model="aria",
                messages=messages,
                stop=["<|im_end|>"],
                stream=False,
                temperature=0.6,
                max_tokens=1024,
                top_p=1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Request failed: {str(e)}"