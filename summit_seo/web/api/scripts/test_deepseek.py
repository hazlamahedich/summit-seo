#!/usr/bin/env python3
"""
Test script for Deepseek model integration via Ollama in Summit SEO.

This script tests the LiteLLM integration with local Deepseek model
running through Ollama by sending a simple prompt and printing the response.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path to allow importing the API modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from dotenv import load_dotenv
from summit_seo.web.api.services import get_llm_service
from summit_seo.web.api.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run the Deepseek Ollama test."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.warning(f"No .env file found at {env_path}")
    
    # Log current configuration
    logger.info(f"Using LiteLLM default model: {settings.LITELLM_DEFAULT_MODEL}")
    logger.info(f"Ollama enabled: {settings.OLLAMA_ENABLE}")
    logger.info(f"Ollama base URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"Ollama models: {settings.OLLAMA_MODELS}")
    
    # Initialize the LLM service
    try:
        llm_service = get_llm_service()
        logger.info("LLM service initialized successfully")
        
        # List available models
        models = llm_service.list_available_models()
        logger.info(f"Available Ollama models: {models.get('ollama', [])}")
        
        # Test a simple prompt
        prompt = "Generate 5 SEO tips for a small business website focused on local services."
        logger.info(f"Sending prompt to {settings.LITELLM_DEFAULT_MODEL}: {prompt}")
        
        response = llm_service.get_completion(prompt)
        
        logger.info("Response received:")
        print("\n" + "-" * 80)
        print("PROMPT:")
        print(prompt)
        print("\nRESPONSE:")
        print(response["choices"][0]["message"]["content"])
        print("-" * 80 + "\n")
        
        # Test a more complex prompt related to SEO security
        security_prompt = "What are the top 5 security considerations for an SEO-focused website?"
        logger.info(f"Sending security prompt to {settings.LITELLM_DEFAULT_MODEL}")
        
        security_response = llm_service.get_completion(security_prompt)
        
        logger.info("Security response received:")
        print("\n" + "-" * 80)
        print("SECURITY PROMPT:")
        print(security_prompt)
        print("\nRESPONSE:")
        print(security_response["choices"][0]["message"]["content"])
        print("-" * 80 + "\n")
        
        # Log additional information
        model_used = response.get("model", "unknown")
        tokens_used = response.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Model used: {model_used}")
        logger.info(f"Total tokens used: {tokens_used}")
        
    except Exception as e:
        logger.error(f"Error testing Deepseek via Ollama: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 