#!/usr/bin/env python3
"""
Utility script for managing LLM models in Summit SEO.

This script helps users manage their custom LLM models, including:
- Listing available models
- Adding custom models
- Testing models
- Switching between Ollama and OpenRouter
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the parent directory to the path to allow importing the API modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from dotenv import load_dotenv
from summit_seo.web.api.services import get_llm_service, LLMServiceError
from summit_seo.web.api.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.warning(f"No .env file found at {env_path}, using existing environment variables")

def list_models():
    """List all available models grouped by provider."""
    llm_service = get_llm_service()
    available_models = llm_service.list_available_models()
    
    print("\n=== Available LLM Models ===\n")
    
    for provider, models in available_models.items():
        print(f"\n{provider.upper()} Models:")
        for model in models:
            print(f"  - {model}")
    
    print("\nDefault model:", settings.LITELLM_DEFAULT_MODEL)
    print("Default embedding model:", settings.LITELLM_DEFAULT_EMBEDDING_MODEL)
    print("Fallback models:", settings.LITELLM_FALLBACK_MODELS or "None")
    
    # Show provider status
    print("\n=== Provider Status ===\n")
    print(f"Ollama: {'ENABLED' if settings.OLLAMA_ENABLE else 'DISABLED'} ({settings.OLLAMA_BASE_URL})")
    print(f"OpenRouter: {'ENABLED' if settings.OPENROUTER_ENABLE else 'DISABLED'}")
    
def test_model(model_name: str, prompt: Optional[str] = None):
    """Test a specific model with a prompt."""
    if not prompt:
        prompt = "Generate 3 SEO tips for a small business website."
    
    llm_service = get_llm_service()
    
    try:
        print(f"\nTesting model: {model_name}")
        print(f"Prompt: {prompt}")
        print("\nGenerating response...\n")
        
        response = llm_service.get_completion(prompt=prompt, model=model_name)
        
        print(f"\n--- Response from {model_name} ---\n")
        print(response["choices"][0]["message"]["content"])
        print("\n---------------------------\n")
        
        # Show additional info
        model_used = response.get("model", "unknown")
        tokens_used = response.get("usage", {}).get("total_tokens", 0)
        print(f"Model used: {model_used}")
        print(f"Total tokens used: {tokens_used}")
        
        # If cost tracking is enabled, try to show the cost
        if settings.LITELLM_ENABLE_COST_TRACKING:
            try:
                from litellm import completion_cost
                cost = completion_cost(completion_response=response)
                print(f"Estimated cost: ${cost:.6f}")
            except Exception as e:
                print(f"Could not calculate cost: {str(e)}")
        
    except Exception as e:
        print(f"\n❌ Error testing model {model_name}: {str(e)}")

def add_custom_model(model_name: str, provider: str, base_model: str, 
                     api_base: Optional[str] = None, api_key: Optional[str] = None):
    """Add a custom model configuration."""
    if not model_name.startswith("summit-"):
        model_name = f"summit-{model_name}"
    
    # Prepare the configuration based on provider
    if provider == "ollama":
        if not api_base:
            api_base = settings.OLLAMA_BASE_URL
        
        model_config = {
            "litellm_params": {
                "model": f"ollama/{base_model}",
                "api_base": api_base
            },
            "description": f"Custom Ollama model - {base_model}"
        }
    elif provider == "openrouter":
        if not api_base:
            api_base = settings.OPENROUTER_BASE_URL
        
        if not api_key and settings.OPENROUTER_API_KEY:
            api_key = settings.OPENROUTER_API_KEY
        
        if not api_key:
            print("❌ Error: OpenRouter API key is required")
            return
        
        model_config = {
            "litellm_params": {
                "model": f"openrouter/{base_model}",
                "api_base": api_base,
                "api_key": api_key,
                "timeout": settings.OPENROUTER_TIMEOUT
            },
            "description": f"Custom OpenRouter model - {base_model}"
        }
    elif provider == "openai":
        if not api_key and settings.OPENAI_API_KEY:
            api_key = settings.OPENAI_API_KEY
            
        if not api_key:
            print("❌ Error: OpenAI API key is required")
            return
            
        model_config = {
            "litellm_params": {
                "model": base_model,
                "api_key": api_key
            },
            "description": f"Custom OpenAI model - {base_model}"
        }
    else:
        print(f"❌ Error: Unsupported provider: {provider}")
        print("Supported providers: ollama, openrouter, openai")
        return
    
    try:
        llm_service = get_llm_service()
        llm_service.register_custom_model(model_name, model_config)
        print(f"✅ Successfully registered custom model: {model_name}")
    except Exception as e:
        print(f"❌ Error registering custom model: {str(e)}")

def toggle_provider(provider: str, enable: bool):
    """Enable or disable a provider by updating the .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        return
    
    # Read the current .env file
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
    
    # Update the appropriate line(s)
    updated = False
    for i, line in enumerate(env_lines):
        if provider == "ollama" and line.startswith("OLLAMA_ENABLE="):
            env_lines[i] = f"OLLAMA_ENABLE={'true' if enable else 'false'}\n"
            updated = True
        elif provider == "openrouter" and line.startswith("OPENROUTER_ENABLE="):
            env_lines[i] = f"OPENROUTER_ENABLE={'true' if enable else 'false'}\n"
            updated = True
    
    if not updated:
        # If we didn't find the line, append it
        if provider == "ollama":
            env_lines.append(f"OLLAMA_ENABLE={'true' if enable else 'false'}\n")
        elif provider == "openrouter":
            env_lines.append(f"OPENROUTER_ENABLE={'true' if enable else 'false'}\n")
    
    # Write the updated .env file
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Successfully {'enabled' if enable else 'disabled'} {provider}")
    print("Restart your application for changes to take effect")

def set_default_model(model_name: str):
    """Set the default model by updating the .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        return
    
    # Read the current .env file
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
    
    # Update the appropriate line
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith("LITELLM_DEFAULT_MODEL="):
            env_lines[i] = f"LITELLM_DEFAULT_MODEL={model_name}\n"
            updated = True
    
    if not updated:
        # If we didn't find the line, append it
        env_lines.append(f"LITELLM_DEFAULT_MODEL={model_name}\n")
    
    # Write the updated .env file
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Successfully set default model to {model_name}")
    print("Restart your application for changes to take effect")

def set_fallback_models(models: List[str]):
    """Set fallback models by updating the .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        return
    
    # Join the models with commas
    models_str = ",".join(models)
    
    # Read the current .env file
    with open(env_path, 'r') as f:
        env_lines = f.readlines()
    
    # Update the appropriate line
    updated = False
    for i, line in enumerate(env_lines):
        if line.startswith("LITELLM_FALLBACK_MODELS="):
            env_lines[i] = f"LITELLM_FALLBACK_MODELS={models_str}\n"
            updated = True
    
    if not updated:
        # If we didn't find the line, append it
        env_lines.append(f"LITELLM_FALLBACK_MODELS={models_str}\n")
    
    # Write the updated .env file
    with open(env_path, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ Successfully set fallback models to: {models_str}")
    print("Restart your application for changes to take effect")

def main():
    """Run the LLM models management script."""
    parser = argparse.ArgumentParser(description="Manage LLM models for Summit SEO")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List available models")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a specific model")
    test_parser.add_argument("model", help="Name of the model to test")
    test_parser.add_argument("--prompt", "-p", help="Custom prompt to use for testing")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a custom model")
    add_parser.add_argument("name", help="Name for the custom model (will be prefixed with 'summit-' if not already)")
    add_parser.add_argument("provider", choices=["ollama", "openrouter", "openai"], help="Model provider")
    add_parser.add_argument("base_model", help="Base model identifier (e.g., 'llama2' for Ollama or 'anthropic/claude-3-opus' for OpenRouter)")
    add_parser.add_argument("--api-base", help="API base URL (defaults to provider's configured base)")
    add_parser.add_argument("--api-key", help="API key (defaults to provider's configured key)")
    
    # Enable/disable provider commands
    enable_parser = subparsers.add_parser("enable", help="Enable a provider")
    enable_parser.add_argument("provider", choices=["ollama", "openrouter"], help="Provider to enable")
    
    disable_parser = subparsers.add_parser("disable", help="Disable a provider")
    disable_parser.add_argument("provider", choices=["ollama", "openrouter"], help="Provider to disable")
    
    # Set default model
    default_parser = subparsers.add_parser("set-default", help="Set the default model")
    default_parser.add_argument("model", help="Name of the model to set as default")
    
    # Set fallback models
    fallback_parser = subparsers.add_parser("set-fallbacks", help="Set fallback models")
    fallback_parser.add_argument("models", nargs="+", help="Names of models to use as fallbacks (in order)")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_environment()
    
    # Execute the appropriate command
    if args.command == "list":
        list_models()
    elif args.command == "test":
        test_model(args.model, args.prompt)
    elif args.command == "add":
        add_custom_model(args.name, args.provider, args.base_model, args.api_base, args.api_key)
    elif args.command == "enable":
        toggle_provider(args.provider, True)
    elif args.command == "disable":
        toggle_provider(args.provider, False)
    elif args.command == "set-default":
        set_default_model(args.model)
    elif args.command == "set-fallbacks":
        set_fallback_models(args.models)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 