import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Model:
    """Interface for interacting with Large Language Models"""
    
    def __init__(self, model_provider: str = "anthropic"):
        """
        Initialize the model interface.
        
        Args:
            model_provider: Name/version of the model provider to use
        """
        self._model_provider = model_provider
        logger.info(f"Initialized model interface using: {model_provider}")

    def get_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Get a response from the model for the given prompt.
        
        Args:
            prompt: The input prompt text
            max_tokens: Maximum tokens in the response
            
        Returns:
            The model's response text, or None if the request fails
        """
        try:
            logger.debug(f"Sending prompt to {self._model_provider}")
            response = self.get_response_from_provider(self._model_provider, prompt, max_tokens)
            logger.debug(f"Received response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting model response: {str(e)}")
            return None

    def _get_openai_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Get response using OpenAI API"""
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self._model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None

    def _get_anthropic_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Get response using Anthropic Claude API"""
        try:
            from anthropic import Anthropic
            client = Anthropic()
            response = client.messages.create(
                model=self._model_name,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return None

    def _get_gemini_response(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Get response using Google's Gemini API"""
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel(self._model_name)
            response = model.generate_content(
                prompt,
                generation_config={"max_output_tokens": max_tokens}
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return None

    def _get_response_from_provider(self, provider: str, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """
        Route the request to appropriate provider.
        
        Args:
            provider: The LLM provider to use ('openai', 'anthropic', or 'gemini')
            prompt: The input prompt text
            max_tokens: Maximum tokens in response
            
        Returns:
            Model response or None if request fails
        """
        provider_map = {
            'openai': self._get_openai_response,
            'anthropic': self._get_anthropic_response,
            'gemini': self._get_gemini_response
        }
        
        if provider not in provider_map:
            logger.error(f"Unknown provider: {provider}")
            return None
            
        return provider_map[provider](prompt, max_tokens)

