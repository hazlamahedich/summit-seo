#!/usr/bin/env python3
"""
Test script for LiteLLM integration in Summit SEO.

This script tests the LiteLLM integration by sending a simple prompt
to the configured LLM service and printing the response.
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
    """Run the LiteLLM test."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.warning(f"No .env file found at {env_path}")
    
    # Log current configuration
    logger.info(f"Using LiteLLM default model: {settings.LITELLM_DEFAULT_MODEL}")
    logger.info(f"Using fallback models: {settings.LITELLM_FALLBACK_MODELS if settings.LITELLM_FALLBACK_MODELS else 'None'}")
    
    # Check if API keys are set
    if not os.environ.get("OPENAI_API_KEY") and not settings.OPENAI_API_KEY:
        logger.error("No OpenAI API key found. Please set OPENAI_API_KEY in your environment or .env file.")
        return
    
    # Initialize the LLM service
    try:
        llm_service = get_llm_service()
        logger.info("LLM service initialized successfully")
        
        # Test a simple prompt
        prompt = "Generate 3 SEO tips for a small business website."
        logger.info(f"Sending prompt to {settings.LITELLM_DEFAULT_MODEL}: {prompt}")
        
        response = llm_service.get_completion(prompt)
        
        logger.info("Response received:")
        print("\n" + "-" * 50)
        print("PROMPT:")
        print(prompt)
        print("\nRESPONSE:")
        print(response["choices"][0]["message"]["content"])
        print("-" * 50 + "\n")
        
        # Log additional information
        model_used = response.get("model", "unknown")
        tokens_used = response.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Model used: {model_used}")
        logger.info(f"Total tokens used: {tokens_used}")
        
    except Exception as e:
        logger.error(f"Error testing LiteLLM: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 