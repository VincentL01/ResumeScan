import openai
from typing import Dict, Union
from abc import ABC, abstractmethod
from app.configs import CHAT_API_KEY, BASE_URL

class Agent(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.init_model()

    @abstractmethod
    def init_model(self):
        pass

    @abstractmethod
    def generate(self, prompts: Union[Dict[str, str], str], temperature: float, max_token_usage: int) -> str:
        pass

class OpenAIAgent(Agent):
    def init_model(self):
        self.client = openai.OpenAI(api_key=CHAT_API_KEY, base_url=BASE_URL)

    def generate(self, prompts: Union[Dict[str, str], str], temperature: float = 0.7, max_token_usage: int = 1024) -> str:
        if isinstance(prompts, str):
            prompts = {"user": prompts}
        
        messages = []
        if "system" in prompts and prompts["system"]:
            messages.append({"role": "system", "content": prompts["system"]})
        if "assistant" in prompts and prompts["assistant"]:
            messages.append({"role": "assistant", "content": prompts["assistant"]})
        if "user" in prompts and prompts["user"]:
            messages.append({"role": "user", "content": prompts["user"]})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_token_usage,
        )   
        return response.choices[0].message.content
