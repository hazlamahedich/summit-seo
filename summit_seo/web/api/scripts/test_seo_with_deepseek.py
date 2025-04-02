#!/usr/bin/env python3
"""
Test script for using Deepseek model with SEO analysis tasks in Summit SEO.

This script tests using the Deepseek model via Ollama for SEO-specific tasks
like generating recommendations and analyzing SEO issues.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Import litellm directly
import litellm
from litellm import completion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Sample SEO data that would normally come from our analyzers
SAMPLE_SEO_DATA = {
    "page_title": "Premium Plumbing Services | Fast Local Repairs | Johnson Plumbing",
    "meta_description": "Professional plumbing services in Portland. 24/7 emergency repairs, installation & maintenance. Licensed plumbers with 15+ years experience. Call now!",
    "h1_tags": ["Portland's Most Trusted Plumbing Services", "Emergency Plumbing Repairs"],
    "content_sample": "Johnson Plumbing provides expert plumbing services to Portland and surrounding areas. Our licensed professionals handle everything from emergency repairs to new installations. With over 15 years of experience, we guarantee quality workmanship on every job.",
    "keywords": ["plumbing", "plumbing services", "emergency plumbing", "Portland plumber", "leaky pipes"],
    "issues": [
        {"severity": "medium", "issue": "Meta description is slightly over recommended length"},
        {"severity": "low", "issue": "Some images missing alt text"},
        {"severity": "high", "issue": "Mobile page load time exceeds 3 seconds"},
    ]
}

def generate_seo_recommendations(model_name, base_url, seo_data):
    """Generate SEO recommendations using LLM."""
    
    # Create a prompt for SEO recommendations
    prompt = f"""
    As an SEO expert, analyze this website data and provide 3 specific, actionable recommendations to improve search rankings:
    
    Page Title: {seo_data['page_title']}
    Meta Description: {seo_data['meta_description']}
    Main Heading(s): {', '.join(seo_data['h1_tags'])}
    Content Sample: {seo_data['content_sample']}
    Target Keywords: {', '.join(seo_data['keywords'])}
    
    Issues Found:
    {json.dumps(seo_data['issues'], indent=2)}
    
    For each recommendation:
    1. Clearly state what should be changed
    2. Explain why this change would improve SEO
    3. Provide a specific example of the implementation
    """
    
    logger.info(f"Sending SEO recommendation prompt to {model_name}")
    
    try:
        response = completion(
            model=f"ollama/{model_name}", 
            messages=[{"role": "user", "content": prompt}],
            api_base=base_url,
            temperature=0.3,
            max_tokens=800
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error generating SEO recommendations: {str(e)}")
        raise

def analyze_competitor_keywords(model_name, base_url, competitor_url, business_type):
    """Analyze competitor keywords using LLM."""
    
    # Create a prompt for competitor keyword analysis
    prompt = f"""
    As an SEO expert, analyze this competitor website and suggest keywords we should target:
    
    Competitor URL: {competitor_url}
    Our Business Type: {business_type}
    
    Please provide:
    1. 10 potential keywords we should target based on this competitor
    2. For each keyword, explain its relevance and difficulty level
    3. Suggest how we might create content to target these keywords
    """
    
    logger.info(f"Sending competitor analysis prompt to {model_name}")
    
    try:
        response = completion(
            model=f"ollama/{model_name}", 
            messages=[{"role": "user", "content": prompt}],
            api_base=base_url,
            temperature=0.4,
            max_tokens=1000
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"Error analyzing competitor keywords: {str(e)}")
        raise

def main():
    """Run the SEO with Deepseek test."""
    # Configure Ollama
    model_name = "deepseek-r1:14b"  # Use deepseek-r1:14b or nezahatkorkmaz/deepseek-v3
    ollama_base_url = "http://localhost:11434"
    
    # Enable verbose mode for debugging
    litellm.verbose = True
    
    logger.info(f"Testing SEO tasks with Ollama model: {model_name}")
    logger.info(f"Ollama base URL: {ollama_base_url}")
    
    try:
        # Test SEO recommendations
        print("\n" + "="*80)
        print("TESTING SEO RECOMMENDATIONS GENERATION")
        print("="*80)
        recommendations = generate_seo_recommendations(model_name, ollama_base_url, SAMPLE_SEO_DATA)
        print("\nSEO RECOMMENDATIONS:")
        print(recommendations)
        print("="*80)
        
        # Test competitor analysis
        print("\n" + "="*80)
        print("TESTING COMPETITOR KEYWORD ANALYSIS")
        print("="*80)
        competitor_analysis = analyze_competitor_keywords(
            model_name, 
            ollama_base_url, 
            "https://example-competitor.com", 
            "Local plumbing business in Portland"
        )
        print("\nCOMPETITOR ANALYSIS:")
        print(competitor_analysis)
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error in SEO tests: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 