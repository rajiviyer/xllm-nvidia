import os
import requests
from typing import List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.runnables import Runnable
from dotenv import load_dotenv
import json

load_dotenv()

# Configs
API_URL = "http://gemma3-demo.brazilsouth.azurecontainer.io:11434"
FULL_URL = f"{API_URL}/api/generate"
MODEL_NAME = "gemma3:4b"

class AzureContainerChatModel(BaseChatModel):

    model: str = MODEL_NAME
    endpoint_url: str = FULL_URL

    def _combine_messages(self, messages: List[BaseMessage]) -> str:
        combined = ""
        for msg in messages:
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            combined += f"{role}: {msg.content}\n"
        return combined.strip()

    def _call_model(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt
        }

        # Enable streaming response parsing
        response = requests.post(self.endpoint_url, json=payload, stream=True)
        response.raise_for_status()

        final_response = ""

        for line in response.iter_lines():
            if line:
                try:
                    parsed = json.loads(line.decode('utf-8'))
                    final_response += parsed.get("response", "")
                except json.JSONDecodeError as e:
                    print("Skipping invalid JSON line:", line)
                    continue

        return final_response.strip()


    def invoke(self, messages: List[BaseMessage], **kwargs) -> AIMessage:
        prompt = self._combine_messages(messages)
        response_text = self._call_model(prompt)
        return AIMessage(content=response_text)

    @property
    def _llm_type(self) -> str:
        return "azure_container_custom_llm"

    def _generate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        response = self.invoke(messages)
        return ChatResult(generations=[ChatGeneration(message=response)])

