"""LLM optimizer service for efficient language model use.

This service provides optimized access to LLM capabilities, implementing
efficient batching, caching, and context optimization strategies.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import json
import asyncio
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta

from .llm_service import get_llm_service, LLMServiceError

# Set up logging
logger = logging.getLogger(__name__)

class LLMOptimizer:
    """Service for optimizing LLM usage with caching and batching."""

    def __init__(self):
        """Initialize the LLM optimizer service."""
        self.llm_service = get_llm_service()
        self._cache = {}  # Simple in-memory cache
        self._cache_ttl = 86400  # 24 hours in seconds
        self._batch_size = 5  # Maximum number of requests to batch
        self._compression_enabled = True  # Enable prompt compression
        logger.info("LLM optimizer service initialized")

    def _get_cache_key(self, prompt: str, model: Optional[str] = None, 
                       max_tokens: Optional[int] = None) -> str:
        """Generate a unique cache key for a prompt and parameters.
        
        Args:
            prompt: The prompt text
            model: Optional model name
            max_tokens: Optional maximum tokens
            
        Returns:
            Hash-based cache key
        """
        # Create a consistent string with all parameters
        key_data = f"{prompt}|{model or 'default'}|{max_tokens or 0}"
        # Generate a hash of this string
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if a cached entry is still valid.
        
        Args:
            timestamp: The timestamp when the entry was cached
            
        Returns:
            Boolean indicating if the cache entry is still valid
        """
        return (datetime.now() - datetime.fromtimestamp(timestamp)).total_seconds() < self._cache_ttl

    def _optimize_prompt(self, prompt: str) -> str:
        """Optimize a prompt to reduce token usage.
        
        Args:
            prompt: The original prompt
            
        Returns:
            Optimized prompt with reduced token count
        """
        if not self._compression_enabled:
            return prompt
            
        # Remove excessive whitespace
        optimized = " ".join(prompt.split())
        
        # Remove redundant instructions (simplified example)
        redundant_phrases = [
            "As an AI language model",
            "Please provide",
            "I would like you to",
            "In this task",
            "For this request"
        ]
        
        for phrase in redundant_phrases:
            optimized = optimized.replace(phrase, "")
            
        return optimized.strip()

    async def get_optimized_completion(self, prompt: str, 
                                     model: Optional[str] = None,
                                     max_tokens: Optional[int] = None,
                                     temperature: Optional[float] = 0.3,
                                     use_cache: bool = True) -> Dict[str, Any]:
        """Get a completion with optimization and caching.
        
        Args:
            prompt: The prompt to send
            model: Optional model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for randomness
            use_cache: Whether to use cache
            
        Returns:
            Completion response
        """
        # Optimize the prompt
        optimized_prompt = self._optimize_prompt(prompt)
        
        # Check cache if enabled
        if use_cache:
            cache_key = self._get_cache_key(optimized_prompt, model, max_tokens)
            if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]["timestamp"]):
                logger.debug(f"Cache hit for prompt: {optimized_prompt[:50]}...")
                return self._cache[cache_key]["response"]
        
        try:
            # Get completion
            response = await self.llm_service.acompletion(
                prompt=optimized_prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Cache the response if caching is enabled
            if use_cache:
                cache_key = self._get_cache_key(optimized_prompt, model, max_tokens)
                self._cache[cache_key] = {
                    "response": response,
                    "timestamp": datetime.now().timestamp()
                }
            
            return response
        except Exception as e:
            logger.error(f"Error in optimized completion: {str(e)}")
            raise

    async def get_batched_completions(self, prompts: List[str],
                                    model: Optional[str] = None,
                                    max_tokens: Optional[int] = None,
                                    temperature: Optional[float] = 0.3,
                                    use_cache: bool = True) -> List[Dict[str, Any]]:
        """Process multiple prompts efficiently in batches.
        
        Args:
            prompts: List of prompts to process
            model: Optional model to use
            max_tokens: Maximum tokens in response
            temperature: Temperature for randomness
            use_cache: Whether to use cache
            
        Returns:
            List of completion responses
        """
        if not prompts:
            return []
            
        # Optimize all prompts
        optimized_prompts = [self._optimize_prompt(p) for p in prompts]
        
        # Check cache for each prompt
        results = [None] * len(optimized_prompts)
        batch_prompts = []
        batch_indices = []
        
        # First check cache and collect uncached prompts
        for i, prompt in enumerate(optimized_prompts):
            if use_cache:
                cache_key = self._get_cache_key(prompt, model, max_tokens)
                if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key]["timestamp"]):
                    results[i] = self._cache[cache_key]["response"]
                    continue
                    
            # Not in cache, add to batch for processing
            batch_prompts.append(prompt)
            batch_indices.append(i)
        
        # Process uncached prompts in batches
        if batch_prompts:
            try:
                # Split into manageable batches
                for i in range(0, len(batch_prompts), self._batch_size):
                    sub_batch_prompts = batch_prompts[i:i+self._batch_size]
                    sub_batch_indices = batch_indices[i:i+self._batch_size]
                    
                    # Process this batch
                    batch_responses = await asyncio.gather(*[
                        self.llm_service.acompletion(
                            prompt=prompt,
                            model=model,
                            max_tokens=max_tokens,
                            temperature=temperature
                        ) for prompt in sub_batch_prompts
                    ], return_exceptions=True)
                    
                    # Store results and cache them
                    for j, response in enumerate(batch_responses):
                        idx = sub_batch_indices[j]
                        
                        if isinstance(response, Exception):
                            logger.error(f"Error in batch completion: {str(response)}")
                            results[idx] = {"error": True, "message": str(response)}
                            continue
                            
                        results[idx] = response
                        
                        # Cache this response
                        if use_cache:
                            cache_key = self._get_cache_key(sub_batch_prompts[j], model, max_tokens)
                            self._cache[cache_key] = {
                                "response": response,
                                "timestamp": datetime.now().timestamp()
                            }
            except Exception as e:
                logger.error(f"Error in batched completions: {str(e)}")
                # Fill any missing results with error
                for i, result in enumerate(results):
                    if result is None:
                        results[i] = {"error": True, "message": str(e)}
        
        # Return all results (cached + newly processed)
        return results

    def clear_cache(self) -> None:
        """Clear the optimization cache."""
        self._cache = {}
        logger.info("LLM optimizer cache cleared")

    def set_cache_ttl(self, ttl_seconds: int) -> None:
        """Set the time-to-live for cache entries.
        
        Args:
            ttl_seconds: Number of seconds entries should remain valid
        """
        self._cache_ttl = ttl_seconds
        logger.info(f"Cache TTL set to {ttl_seconds} seconds")

    def set_batch_size(self, batch_size: int) -> None:
        """Set the maximum batch size for batched processing.
        
        Args:
            batch_size: Maximum number of requests in a batch
        """
        self._batch_size = max(1, min(batch_size, 10))  # Clamp between 1 and 10
        logger.info(f"Batch size set to {self._batch_size}")

    def toggle_compression(self, enabled: bool) -> None:
        """Enable or disable prompt compression.
        
        Args:
            enabled: Whether compression should be enabled
        """
        self._compression_enabled = enabled
        logger.info(f"Prompt compression {'enabled' if enabled else 'disabled'}")

# Singleton instance
_llm_optimizer_instance = None

def get_llm_optimizer() -> LLMOptimizer:
    """
    Get a singleton instance of the LLMOptimizer.
    
    Returns:
        LLMOptimizer instance
    """
    global _llm_optimizer_instance
    if _llm_optimizer_instance is None:
        _llm_optimizer_instance = LLMOptimizer()
    return _llm_optimizer_instance 