#!/usr/bin/env python3
"""
Direct test script for Deepseek model via Ollama in Summit SEO.

This script tests the Deepseek model running in Ollama directly through litellm,
bypassing the full Summit SEO service stack.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Import directly from litellm
import litellm
from litellm import completion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Run the Deepseek Ollama direct test."""
    # Configure litellm for Ollama
    model_name = "deepseek-r1:14b"  # Use deepseek-r1:14b or nezahatkorkmaz/deepseek-v3
    ollama_base_url = "http://localhost:11434"
    
    # Enable verbose mode for debugging
    litellm.verbose = True
    
    logger.info(f"Testing direct connection to Ollama model: {model_name}")
    logger.info(f"Ollama base URL: {ollama_base_url}")
    
    # Test a simple prompt
    try:
        # Direct approach without using register_model
        prompt = "Generate 5 SEO tips for a small business website focused on local services."
        logger.info(f"Sending prompt to ollama/{model_name}: {prompt}")
        
        start_time = time.time()
        response = completion(
            model=f"ollama/{model_name}",
            messages=[{"role": "user", "content": prompt}],
            api_base=ollama_base_url,
            temperature=0.7,
            max_tokens=500
        )
        end_time = time.time()
        
        logger.info(f"Response received in {end_time - start_time:.2f} seconds")
        print("\n" + "-" * 80)
        print("PROMPT:")
        print(prompt)
        print("\nRESPONSE:")
        print(response["choices"][0]["message"]["content"])
        print("-" * 80 + "\n")
        
        # Test a more complex prompt related to SEO security
        security_prompt = "What are the top 5 security considerations for an SEO-focused website?"
        logger.info(f"Sending security prompt to ollama/{model_name}")
        
        start_time = time.time()
        security_response = completion(
            model=f"ollama/{model_name}",
            messages=[{"role": "user", "content": security_prompt}],
            api_base=ollama_base_url,
            temperature=0.7,
            max_tokens=500
        )
        end_time = time.time()
        
        logger.info(f"Security response received in {end_time - start_time:.2f} seconds")
        print("\n" + "-" * 80)
        print("SECURITY PROMPT:")
        print(security_prompt)
        print("\nRESPONSE:")
        print(security_response["choices"][0]["message"]["content"])
        print("-" * 80 + "\n")
        
        # Log model information
        model_used = response.get("model", "unknown")
        tokens_used = response.get("usage", {}).get("total_tokens", 0)
        logger.info(f"Model used: {model_used}")
        logger.info(f"Total tokens used: {tokens_used}")
        
    except Exception as e:
        logger.error(f"Error testing Deepseek via Ollama: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 