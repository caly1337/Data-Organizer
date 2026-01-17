"""
LLM Service - Multi-provider LLM integration
Supports Ollama, Gemini, and Claude
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from ollama import Client as OllamaClient
import google.generativeai as genai
from anthropic import Anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseLLMProvider:
    """Base class for LLM providers"""

    def __init__(self):
        self.provider_name = "base"
        self.model_name = ""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from LLM"""
        raise NotImplementedError


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM models"""

    def __init__(self, base_url: str = None, model: str = None):
        super().__init__()
        self.provider_name = "ollama"
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model_name = model or settings.OLLAMA_DEFAULT_MODEL

        # Ensure HTTP (not HTTPS) for Ollama - replace https with http
        if self.base_url:
            self.base_url = self.base_url.replace('https://', 'http://')
            if not self.base_url.startswith('http://'):
                self.base_url = f'http://{self.base_url}'

        self.client = OllamaClient(host=self.base_url)
        self.timeout = settings.OLLAMA_TIMEOUT

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Ollama"""
        try:
            start_time = datetime.now()

            # Build messages
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Generate response
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options=kwargs.get("options", {})
            )

            duration = (datetime.now() - start_time).total_seconds()

            return {
                "response": response["message"]["content"],
                "model": self.model_name,
                "provider": self.provider_name,
                "duration": duration,
                "tokens_used": response.get("eval_count", 0),
                "cost": 0.0,  # Ollama is free
                "metadata": {
                    "total_duration": response.get("total_duration"),
                    "load_duration": response.get("load_duration"),
                    "prompt_eval_count": response.get("prompt_eval_count"),
                    "eval_count": response.get("eval_count"),
                }
            }

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__()
        self.provider_name = "gemini"
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model or settings.GEMINI_DEFAULT_MODEL

        if not self.api_key:
            raise ValueError("Gemini API key not configured")

        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Gemini"""
        try:
            start_time = datetime.now()

            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            # Configure generation
            generation_config = {
                "max_output_tokens": kwargs.get("max_tokens", settings.GEMINI_MAX_TOKENS),
                "temperature": kwargs.get("temperature", 0.7),
            }

            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Calculate approximate cost (Gemini 2.5 Flash pricing)
            # Input: $0.075 per 1M tokens, Output: $0.30 per 1M tokens
            input_tokens = 0
            output_tokens = 0
            cost = 0.0

            # Try to get usage metadata if available
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                cost = (input_tokens * 0.075 / 1_000_000) + (output_tokens * 0.30 / 1_000_000)

            return {
                "response": response.text,
                "model": self.model_name,
                "provider": self.provider_name,
                "duration": duration,
                "tokens_used": input_tokens + output_tokens,
                "cost": cost,
                "metadata": {
                    "prompt_token_count": input_tokens,
                    "candidates_token_count": output_tokens,
                }
            }

        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str = None, model: str = None):
        super().__init__()
        self.provider_name = "claude"
        self.api_key = api_key or settings.CLAUDE_API_KEY
        self.model_name = model or settings.CLAUDE_DEFAULT_MODEL

        if not self.api_key:
            raise ValueError("Claude API key not configured")

        self.client = Anthropic(api_key=self.api_key)

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from Claude"""
        try:
            start_time = datetime.now()

            # Build messages
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # Generate response
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=kwargs.get("max_tokens", settings.CLAUDE_MAX_TOKENS),
                system=system_prompt if system_prompt else None,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Calculate cost (Claude Sonnet 4.5 pricing)
            # Input: $3 per 1M tokens, Output: $15 per 1M tokens
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            cost = (input_tokens * 3.0 / 1_000_000) + (output_tokens * 15.0 / 1_000_000)

            return {
                "response": response.content[0].text,
                "model": self.model_name,
                "provider": self.provider_name,
                "duration": duration,
                "tokens_used": input_tokens + output_tokens,
                "cost": cost,
                "metadata": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "stop_reason": response.stop_reason,
                }
            }

        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise


class LLMService:
    """Main LLM service coordinating all providers"""

    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize enabled LLM providers"""

        # Ollama
        if settings.OLLAMA_ENABLED:
            try:
                self.providers["ollama"] = OllamaProvider()
                logger.info(f"Ollama provider initialized: {settings.OLLAMA_BASE_URL}")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")

        # Gemini
        if settings.GEMINI_ENABLED and settings.GEMINI_API_KEY:
            try:
                self.providers["gemini"] = GeminiProvider()
                logger.info(f"Gemini provider initialized: {settings.GEMINI_DEFAULT_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

        # Claude
        if settings.CLAUDE_ENABLED and settings.CLAUDE_API_KEY:
            try:
                self.providers["claude"] = ClaudeProvider()
                logger.info(f"Claude provider initialized: {settings.CLAUDE_DEFAULT_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")

        if not self.providers:
            logger.warning("No LLM providers configured!")

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        """Get provider by name"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not available. Available: {list(self.providers.keys())}")
        return self.providers[provider_name]

    async def generate(
        self,
        prompt: str,
        provider: str = "ollama",
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from specified provider"""
        llm_provider = self.get_provider(provider)
        return await llm_provider.generate(prompt, system_prompt, **kwargs)

    async def compare_providers(
        self,
        prompt: str,
        providers: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Run same prompt across multiple providers for comparison"""
        results = []
        for provider_name in providers:
            try:
                result = await self.generate(prompt, provider_name, system_prompt, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                results.append({
                    "provider": provider_name,
                    "error": str(e)
                })
        return results

    def list_providers(self) -> List[Dict[str, Any]]:
        """List all available providers"""
        return [
            {
                "name": name,
                "provider": provider.provider_name,
                "model": provider.model_name,
                "enabled": True
            }
            for name, provider in self.providers.items()
        ]


# Global LLM service instance
llm_service = LLMService()
