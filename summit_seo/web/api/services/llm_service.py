"""LLM service for interacting with language models through LiteLLM.

This service provides a unified interface for interacting with various LLM providers
through LiteLLM's unified API. It handles configuration, completion requests,
embeddings, and provides fallback strategies.
"""

from typing import Dict, List, Any, Optional, Union, Callable
import os
import json
import logging
from functools import lru_cache
import requests
from requests.exceptions import RequestException

import litellm
from litellm import completion, acompletion
from litellm.exceptions import (
    APIError, 
    RateLimitError, 
    ServiceUnavailableError,
    APIConnectionError, 
    InvalidRequestError
)

from ..core.config import settings

# Set up logging
logger = logging.getLogger(__name__)

class LLMServiceError(Exception):
    """Base exception for LLM service errors."""
    pass

class LLMService:
    """Service for interacting with Large Language Models via LiteLLM."""

    def __init__(self):
        """Initialize the LLM service with configuration from settings."""
        self._initialize_config()
        self._setup_fallback_models()
        self._setup_caching()
        self._configure_litellm()
        logger.info("LLM service initialized successfully")

    def _initialize_config(self):
        """Load and initialize LiteLLM configuration."""
        self.default_model = settings.LITELLM_DEFAULT_MODEL
        self.api_keys = {
            "openai": settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None,
            "anthropic": settings.ANTHROPIC_API_KEY if hasattr(settings, 'ANTHROPIC_API_KEY') else None,
            "azure": settings.AZURE_API_KEY if hasattr(settings, 'AZURE_API_KEY') else None,
            "cohere": settings.COHERE_API_KEY if hasattr(settings, 'COHERE_API_KEY') else None,
            "openrouter": settings.OPENROUTER_API_KEY if hasattr(settings, 'OPENROUTER_API_KEY') else None,
        }
        
        # Remove None values from api_keys
        self.api_keys = {k: v for k, v in self.api_keys.items() if v is not None}
        
        # Ollama configuration
        self.ollama_enabled = settings.OLLAMA_ENABLE
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_models = []
        if settings.OLLAMA_MODELS:
            if isinstance(settings.OLLAMA_MODELS, str):
                self.ollama_models = [model.strip() for model in settings.OLLAMA_MODELS.split(',')]
            elif isinstance(settings.OLLAMA_MODELS, list):
                self.ollama_models = settings.OLLAMA_MODELS
        
        # OpenRouter configuration
        self.openrouter_enabled = settings.OPENROUTER_ENABLE
        self.openrouter_base_url = settings.OPENROUTER_BASE_URL
        self.openrouter_timeout = settings.OPENROUTER_TIMEOUT
        
        # Cost tracking
        self.enable_cost_tracking = settings.LITELLM_ENABLE_COST_TRACKING
        self.max_budget = settings.LITELLM_MAX_BUDGET if hasattr(settings, 'LITELLM_MAX_BUDGET') else float('inf')
        
        # Load model configuration if available
        self.model_configs = {}
        if hasattr(settings, 'LITELLM_MODEL_CONFIG_PATH') and settings.LITELLM_MODEL_CONFIG_PATH:
            try:
                with open(settings.LITELLM_MODEL_CONFIG_PATH, 'r') as f:
                    self.model_configs = json.load(f)
                logger.info(f"Loaded model configurations from {settings.LITELLM_MODEL_CONFIG_PATH}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logger.error(f"Failed to load model configuration: {str(e)}")
                
    def _setup_fallback_models(self):
        """Configure fallback models for reliability."""
        self.fallback_models = []
        if hasattr(settings, 'LITELLM_FALLBACK_MODELS') and settings.LITELLM_FALLBACK_MODELS:
            # Parse comma-separated list of models
            if isinstance(settings.LITELLM_FALLBACK_MODELS, str):
                self.fallback_models = [m.strip() for m in settings.LITELLM_FALLBACK_MODELS.split(',')]
            # Or use list directly
            elif isinstance(settings.LITELLM_FALLBACK_MODELS, list):
                self.fallback_models = settings.LITELLM_FALLBACK_MODELS
                
        logger.info(f"Configured fallback models: {self.fallback_models}")
            
    def _setup_caching(self):
        """Configure caching for LLM responses."""
        self.enable_caching = settings.LITELLM_ENABLE_CACHING
        self.cache_params = {
            "type": settings.LITELLM_CACHE_TYPE if hasattr(settings, 'LITELLM_CACHE_TYPE') else "redis",
            "host": settings.LITELLM_CACHE_HOST if hasattr(settings, 'LITELLM_CACHE_HOST') else None,
            "port": settings.LITELLM_CACHE_PORT if hasattr(settings, 'LITELLM_CACHE_PORT') else None,
            "password": settings.LITELLM_CACHE_PASSWORD if hasattr(settings, 'LITELLM_CACHE_PASSWORD') else None,
        }
        
    def _configure_litellm(self):
        """Set up LiteLLM with our configuration."""
        # Set API keys
        for provider, key in self.api_keys.items():
            if key:
                os.environ[f"{provider.upper()}_API_KEY"] = key
        
        # Configure logging
        litellm.verbose = settings.LITELLM_VERBOSE
        
        # Configure caching if enabled
        if self.enable_caching and self.cache_params.get("host"):
            try:
                litellm.cache = litellm.Cache(
                    type=self.cache_params["type"],
                    host=self.cache_params["host"],
                    port=self.cache_params.get("port"),
                    password=self.cache_params.get("password"),
                )
                logger.info(f"LiteLLM caching enabled with {self.cache_params['type']}")
            except Exception as e:
                logger.error(f"Failed to initialize caching: {str(e)}")
                
        # Configure cost tracking
        if self.enable_cost_tracking:
            litellm.success_callback = [self._track_cost]
            
        # Load custom configurations from model config
        for model_name, config in self.model_configs.items():
            litellm.register_model(model_name=model_name, **config)
            
        # Auto-discover Ollama models if enabled
        if self.ollama_enabled:
            discovered_models = self._discover_ollama_models()
            if discovered_models:
                # Only use discovered models if we found any
                self.ollama_models = discovered_models
                logger.info(f"Discovered Ollama models: {self.ollama_models}")
                
            # Register Ollama models that weren't in the config
            for model in self.ollama_models:
                model_key = f"summit-ollama-{model}"
                if model_key not in self.model_configs:
                    logger.info(f"Auto-registering Ollama model: {model}")
                    litellm.register_model(
                        model_name=model_key,
                        litellm_params={
                            "model": f"ollama/{model}",
                            "api_base": self.ollama_base_url
                        }
                    )
        
    def _discover_ollama_models(self) -> List[str]:
        """Discover available models from local Ollama instance.
        
        Returns:
            List of model names available in Ollama
        """
        if not self.ollama_enabled or not self.ollama_base_url:
            return []
            
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models_data = response.json()
                if "models" in models_data and isinstance(models_data["models"], list):
                    return [model["name"] for model in models_data["models"]]
                else:
                    # Handle older Ollama API version
                    return [model["name"] for model in models_data.get("models", [])]
            else:
                logger.warning(f"Failed to fetch Ollama models. Status code: {response.status_code}")
                return []
        except RequestException as e:
            logger.warning(f"Error connecting to Ollama: {str(e)}")
            return []
            
    def _track_cost(self, kwargs, completion_response, start_time, end_time):
        """Callback to track cost of LLM requests."""
        try:
            cost = litellm.completion_cost(completion_response=completion_response)
            logger.info(f"Request cost: ${cost:.6f} - Model: {kwargs.get('model')}")
            # Here you could implement budget tracking, store costs in a database, etc.
        except Exception as e:
            logger.error(f"Error tracking cost: {str(e)}")
            
    def get_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        use_fallbacks: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Get a completion from the language model.
        
        Args:
            prompt: The prompt to send to the model
            model: The specific model to use (default: configured default model)
            max_tokens: Maximum tokens in the response
            temperature: Randomness of the generation (0.0-1.0)
            use_fallbacks: Whether to try fallback models on failure
            **kwargs: Additional parameters to pass to the LiteLLM completion function
            
        Returns:
            A dictionary containing the LLM response
            
        Raises:
            LLMServiceError: If all model attempts fail
        """
        model_to_use = model or self.default_model
        errors = []
        
        # First try the requested model
        try:
            response = completion(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response
        except (APIError, ServiceUnavailableError, APIConnectionError, RateLimitError) as e:
            error_msg = f"Error with model {model_to_use}: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)
            
            # Only try fallbacks if enabled and there was a service-level error
            if not use_fallbacks or not self.fallback_models:
                raise LLMServiceError(f"LLM request failed: {str(e)}")
        
        # Try fallback models if the primary model failed
        for fallback_model in self.fallback_models:
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                response = completion(
                    model=fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                return response
            except (APIError, ServiceUnavailableError, APIConnectionError, RateLimitError) as e:
                error_msg = f"Error with fallback model {fallback_model}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # If we get here, all models failed
        raise LLMServiceError(f"All LLM models failed. Errors: {', '.join(errors)}")
    
    async def get_completion_async(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        use_fallbacks: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of get_completion."""
        model_to_use = model or self.default_model
        errors = []
        
        # First try the requested model
        try:
            response = await acompletion(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            return response
        except (APIError, ServiceUnavailableError, APIConnectionError, RateLimitError) as e:
            error_msg = f"Error with model {model_to_use}: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)
            
            # Only try fallbacks if enabled and there was a service-level error
            if not use_fallbacks or not self.fallback_models:
                raise LLMServiceError(f"LLM request failed: {str(e)}")
        
        # Try fallback models if the primary model failed
        for fallback_model in self.fallback_models:
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                response = await acompletion(
                    model=fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                return response
            except (APIError, ServiceUnavailableError, APIConnectionError, RateLimitError) as e:
                error_msg = f"Error with fallback model {fallback_model}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        
        # If we get here, all models failed
        raise LLMServiceError(f"All LLM models failed. Errors: {', '.join(errors)}")
        
    def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """Get an embedding vector for the input text.
        
        Args:
            text: The text to embed
            model: The specific embedding model to use
            
        Returns:
            A list of floats representing the embedding vector
            
        Raises:
            LLMServiceError: If the embedding request fails
        """
        model_to_use = model or settings.LITELLM_DEFAULT_EMBEDDING_MODEL
        
        try:
            embedding_response = litellm.embedding(
                model=model_to_use,
                input=text
            )
            
            if "data" in embedding_response and embedding_response["data"]:
                return embedding_response["data"][0]["embedding"]
            
            raise LLMServiceError("Embedding response missing data")
        except (APIError, ServiceUnavailableError, APIConnectionError, InvalidRequestError) as e:
            logger.error(f"Embedding error: {str(e)}")
            raise LLMServiceError(f"Failed to generate embedding: {str(e)}")
    
    def list_available_models(self) -> Dict[str, List[str]]:
        """List all available models by provider.
        
        Returns:
            Dictionary of provider names to list of model names
        """
        models = {
            "openai": [],
            "anthropic": [],
            "azure": [],
            "cohere": [],
            "ollama": self.ollama_models.copy() if hasattr(self, 'ollama_models') else [],
            "openrouter": [],
            "local": []
        }
        
        # Add discovered models from configuration
        for model_name, config in self.model_configs.items():
            if "provider" in config:
                provider = config["provider"]
                if provider in models:
                    models[provider].append(model_name)
                else:
                    models[provider] = [model_name]
                    
        # Add predefined models
        if hasattr(self, 'api_keys'):
            if self.api_keys.get("openai"):
                models["openai"].extend(["gpt-3.5-turbo", "gpt-4"])
            if self.api_keys.get("anthropic"):
                models["anthropic"].extend(["claude-instant-1", "claude-2"])
            if self.api_keys.get("cohere"):
                models["cohere"].extend(["command", "command-light"])
                
        # Add OpenRouter models if enabled
        if hasattr(self, 'openrouter_enabled') and self.openrouter_enabled:
            models["openrouter"].extend([
                "openai/gpt-3.5-turbo",
                "openai/gpt-4",
                "anthropic/claude-2",
                "google/palm-2",
                "meta-llama/llama-2-70b-chat"
            ])
                
        return models
        
    def register_custom_model(self, model_name: str, model_config: Dict[str, Any]) -> None:
        """Register a custom model configuration.
        
        Args:
            model_name: Name to register the model under
            model_config: Configuration dictionary with litellm_params and description
            
        Raises:
            LLMServiceError: If the model cannot be registered
        """
        try:
            # Validate model config
            if "litellm_params" not in model_config:
                raise LLMServiceError("Model configuration must include 'litellm_params'")
                
            if "model" not in model_config["litellm_params"]:
                raise LLMServiceError("litellm_params must include 'model'")
                
            # Register the model
            litellm.register_model(model_name=model_name, **model_config)
            logger.info(f"Registered custom model: {model_name}")
            
            # Add to model configs if we have a model config file
            if hasattr(settings, 'LITELLM_MODEL_CONFIG_PATH') and settings.LITELLM_MODEL_CONFIG_PATH:
                try:
                    with open(settings.LITELLM_MODEL_CONFIG_PATH, 'r') as f:
                        model_configs = json.load(f)
                    
                    model_configs[model_name] = model_config
                    
                    with open(settings.LITELLM_MODEL_CONFIG_PATH, 'w') as f:
                        json.dump(model_configs, f, indent=4)
                        
                    logger.info(f"Updated model configuration file with {model_name}")
                except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
                    logger.error(f"Failed to update model configuration file: {str(e)}")
        except Exception as e:
            logger.error(f"Error registering custom model: {str(e)}")
            raise LLMServiceError(f"Failed to register custom model: {str(e)}")

    async def get_batch_completions_async(
        self,
        prompts: List[str],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Get completions for multiple prompts in a batch (more efficient).
        
        Args:
            prompts: List of prompts to send
            model: The specific model to use (default: configured default model)
            max_tokens: Maximum tokens in the responses
            temperature: Randomness of the generation (0.0-1.0)
            **kwargs: Additional parameters to pass to the LiteLLM completion function
            
        Returns:
            List of responses containing the LLM responses
            
        Raises:
            LLMServiceError: If all model attempts fail
        """
        model_to_use = model or self.default_model
        results = []
        errors = []
        
        # Prepare messages for batch processing
        messages_list = []
        for prompt in prompts:
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt  # Assume it's already in message format
            messages_list.append(messages)
        
        # Attempt batch processing with the primary model
        try:
            import litellm
            import asyncio
            
            # Create the requests
            requests = [
                litellm.acompletion(
                    model=model_to_use,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                for messages in messages_list
            ]
            
            # Process in parallel
            responses = await asyncio.gather(*requests, return_exceptions=True)
            
            # Process the responses
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    # Individual request failed, will be handled separately
                    errors.append(f"Error with prompt {i}: {str(response)}")
                    # Add a placeholder result
                    results.append({
                        "error": True,
                        "error_message": str(response),
                        "prompt_index": i
                    })
                else:
                    results.append(response)
                    
            return results
            
        except Exception as e:
            error_msg = f"Batch processing failed with model {model_to_use}: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)
            
            # Fall back to sequential processing
            return await self._process_batch_sequentially(
                prompts, model_to_use, max_tokens, temperature, **kwargs
            )
            
    async def _process_batch_sequentially(
        self,
        prompts: List[str],
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Process prompts sequentially as fallback for batch processing.
        
        Args:
            prompts: List of prompts to process
            model: Model to use
            max_tokens: Maximum tokens in responses
            temperature: Temperature parameter
            **kwargs: Additional parameters
            
        Returns:
            List of results
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                # Process each prompt individually
                response = await self.get_completion_async(
                    prompt=prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                results.append(response)
            except Exception as e:
                logger.warning(f"Error processing prompt {i}: {str(e)}")
                # Add error result
                results.append({
                    "error": True,
                    "error_message": str(e),
                    "prompt_index": i
                })
                
        return results

    async def acreate_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Create a completion asynchronously with the given messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to pass to the litellm async completion function
            
        Returns:
            Response from the LLM
            
        Raises:
            LLMServiceError: If there's an error creating the completion
        """
        model = kwargs.pop('model', self.default_model)
        
        try:
            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            return response
        except (APIError, ServiceUnavailableError, APIConnectionError) as e:
            logger.error(f"Async completion error: {str(e)}")
            raise LLMServiceError(f"Failed to create async completion: {str(e)}")
            
    async def aget_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        Get an embedding for the given text asynchronously.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            List of floats representing the embedding
            
        Raises:
            LLMServiceError: If there's an error generating the embedding
        """
        model_to_use = model or settings.LITELLM_DEFAULT_EMBEDDING_MODEL
        
        try:
            embedding_response = await litellm.aembedding(
                model=model_to_use,
                input=text
            )
            
            if "data" in embedding_response and embedding_response["data"]:
                return embedding_response["data"][0]["embedding"]
            
            raise LLMServiceError("Embedding response missing data")
        except (APIError, ServiceUnavailableError, APIConnectionError, InvalidRequestError) as e:
            logger.error(f"Async embedding error: {str(e)}")
            raise LLMServiceError(f"Failed to generate async embedding: {str(e)}")

# Create a singleton instance
@lru_cache()
def get_llm_service() -> LLMService:
    """Get or create the LLM service singleton."""
    return LLMService() 