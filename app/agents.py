import os
import openai
import streamlit as st
from typing import Dict, Union
from abc import ABC, abstractmethod
import google.generativeai as genai

class Agent(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def init_model(self):
        pass

    @abstractmethod
    def generate(self, prompts: Union[Dict[str, str], str], temperature: float, max_token_usage: int) -> Dict[str, str]:
        pass

class OpenAIAgent(Agent):
    def init_model(self):
        self.client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    def generate(self, prompts: Union[Dict[str, str], str], temperature: float, max_token_usage: int) -> Dict[str, str]:
        if isinstance(prompts, str):
            prompts = {"user": prompts}
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": prompts.get("system", "")},
                {"role": "assistant", "content": prompts.get("assistant", "")},
                {"role": "user", "content": prompts.get("user", "")},
            ],
            temperature=temperature,
            max_tokens=max_token_usage,
        )
        return response.choices[0].message.content

class GeminiAgent(Agent):
    def init_model(self):
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(self.model_name)

    def generate(self, prompts: Union[Dict[str, str], str], temperature: float, max_token_usage: int) -> Dict[str, str]:
        """
        Generate content using the Gemini model.
        prompts has structure:
        {
            "system": "System prompt",
            "assistant": "Assistant prompt",
            "user": "User prompt"
        }
        Content of "system" should be put behind "[System Prompt]: "
        Content of "assistant" should be put behind "[Examples]: "
        Content of "user" should be put behind "[User Prompt]: "
        """
        if isinstance(prompts, str):
            prompt_string = prompts
        else:
            for k, v in prompts.items():
                if k == "system":
                    prompts[k] = f"[System Prompt]: {v}"
                elif k == "assistant":
                    prompts[k] = f"[Examples]: {v}"
                elif k == "user":
                    prompts[k] = f"[User Prompt]: {v}"
            prompt_string = "\n".join(prompts.values())
        response = self.model.generate_content(prompt_string)
        return response.text
