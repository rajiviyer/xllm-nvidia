import logging
import requests
import time
import json
from typing import Generator, Union
from .settings import LLM_ENDPOINT, LLM_MODEL, LLM_TEMPERATURE, LLM_TOP_P

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ResponseGenerator")


class ResponseGenerator:
    """
    A class to interact with Azure-hosted Ollama container using /api/generate.
    """

    def __init__(self, info_cards: str = "", user_question: str = ""):
        self.base_url = LLM_ENDPOINT
        self.info_cards = info_cards
        self.user_question = user_question
        logger.debug(f"Initializing ResponseGenerator with model: {LLM_MODEL}")

    def _create_prompt(self) -> str:
        """Create the prompt template - separated for clarity and testing"""
        return f"""
        You are a helpful assistant for company employees, responding to their questions in a human-like and thoughtful way. Your answers should be based strictly on the information provided below, even if it's not directly related to the question—use reasoning to connect relevant details.

        Your response must:
        - Begin with a clear, well-crafted sentence that directly answers the question.
        - Be easy to understand, concise, and well-organized.
        - Avoid being too verbose or overly long.

        <information>
        {self.info_cards}
        </information>

        Now, please answer the following employee question using only the information above:
        {self.user_question}
        """

    def chat(self) -> Union[str, Generator[str, None, None]]:
        """
        Perform a chat conversation using the /api/generate endpoint.
        Returns either a complete response or streams partial responses
        """
        payload = {
            "model": LLM_MODEL,
            "prompt": self._create_prompt(),
            "options": {"temperature": LLM_TEMPERATURE, "top_p": LLM_TOP_P},
            # "stream": False,  # Commented out but could be a parameter
        }

        url = f"{self.base_url}/api/generate"
        start_time = time.time()
        logger.info(f"Sending request to LLM API")

        try:
            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()

            # Process streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        parsed = json.loads(line.decode("utf-8"))
                        chunk = parsed.get("response", "")
                        full_response += chunk
                        yield chunk
                    except json.JSONDecodeError:
                        logger.warning("Received invalid JSON from API")
                        continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            yield "Error: Failed to connect to endpoint."
        finally:
            end_time = time.time()
            logger.info(f"Request completed in {end_time - start_time:.2f} seconds")
