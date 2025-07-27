"""
AI Provider Manager for ResumeScan Application

This module manages AI providers (Google Gemini and OpenAI) with automatic fallback
and provides a unified interface for content generation.
"""

import os
import logging
from typing import Dict, Any, Optional
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider:
    """Manages AI providers with automatic fallback between Gemini and OpenAI."""
    
    def __init__(self):
        self.current_provider = None
        self.gemini_client = None
        self.openai_client = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available AI providers in order of preference."""
        # Try Gemini first
        if self._initialize_gemini():
            self.current_provider = "gemini"
            logger.info("Initialized Gemini AI provider")
        # Fallback to OpenAI
        elif self._initialize_openai():
            self.current_provider = "openai"
            logger.info("Initialized OpenAI provider (Gemini fallback)")
        else:
            raise Exception("No AI providers available. Please configure GEMINI_API_KEY or OPENAI_API_KEY")
    
    def _initialize_gemini(self) -> bool:
        """Initialize Google Gemini AI provider."""
        try:
            import google.generativeai as genai
            
            # Get API key from secrets or environment
            api_key = None
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
            else:
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                logger.warning("GEMINI_API_KEY not found")
                return False
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Get model name
            model_name = "gemini-1.5-flash"
            if hasattr(st, 'secrets') and 'GEMINI_MODEL_NAME' in st.secrets:
                model_name = st.secrets['GEMINI_MODEL_NAME']
            elif os.getenv('GEMINI_MODEL_NAME'):
                model_name = os.getenv('GEMINI_MODEL_NAME')
            
            self.gemini_client = genai.GenerativeModel(model_name)
            self.gemini_model_name = model_name
            return True
            
        except ImportError:
            logger.warning("Google Generative AI package not installed")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini: {e}")
            return False
    
    def _initialize_openai(self) -> bool:
        """Initialize OpenAI provider."""
        try:
            from openai import OpenAI
            
            # Get API key from secrets or environment
            api_key = None
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets['OPENAI_API_KEY']
            else:
                api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                logger.warning("OPENAI_API_KEY not found")
                return False
            
            # Get model name
            model_name = "gpt-4o-mini"
            if hasattr(st, 'secrets') and 'OPENAI_MODEL_NAME' in st.secrets:
                model_name = st.secrets['OPENAI_MODEL_NAME']
            elif os.getenv('OPENAI_MODEL_NAME'):
                model_name = os.getenv('OPENAI_MODEL_NAME')
            
            self.openai_client = OpenAI(api_key=api_key)
            self.openai_model_name = model_name
            return True
            
        except ImportError:
            logger.warning("OpenAI package not installed")
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {e}")
            return False
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using the available AI provider.
        
        Args:
            prompt: The input prompt for content generation
            
        Returns:
            Generated content as string
            
        Raises:
            Exception: If content generation fails
        """
        if self.current_provider == "gemini":
            return self._generate_with_gemini(prompt)
        elif self.current_provider == "openai":
            return self._generate_with_openai(prompt)
        else:
            raise Exception("No AI provider available")
    
    def _generate_with_gemini(self, prompt: str) -> str:
        """Generate content using Gemini."""
        try:
            response = self.gemini_client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            # Try fallback to OpenAI if available
            if self.openai_client:
                logger.info("Falling back to OpenAI")
                self.current_provider = "openai"
                return self._generate_with_openai(prompt)
            raise e
    
    def _generate_with_openai(self, prompt: str) -> str:
        """Generate content using OpenAI."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise e
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get information about the current AI provider."""
        if self.current_provider == "gemini":
            return {
                "provider": "Google Gemini",
                "model": self.gemini_model_name
            }
        elif self.current_provider == "openai":
            return {
                "provider": "OpenAI",
                "model": self.openai_model_name
            }
        else:
            return {
                "provider": "None",
                "model": "Not configured"
            }

# Global instance
ai_provider = AIProvider()
