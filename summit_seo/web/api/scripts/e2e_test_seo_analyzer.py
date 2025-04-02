#!/usr/bin/env python3
"""
End-to-end test script for Summit SEO analysis with Deepseek.

This script performs a complete end-to-end test of the SEO analysis pipeline:
1. Analyzes a sample website
2. Runs all SEO analyzers
3. Generates recommendations using the Deepseek model
4. Provides a comprehensive report

This validates the integration between the Summit SEO analyzer components and the
Deepseek LLM model running via Ollama.
"""

import os
import sys
import json
import logging
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup

# Add the parent directory to the path to allow importing the API modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# Import services
from dotenv import load_dotenv
from summit_seo.web.api.services import get_llm_service
from summit_seo.web.api.core.config import settings

# Import the analyzer modules (assuming they exist)
try:
    from summit_seo.web.api.analyzers.base_analyzer import BaseAnalyzer
    from summit_seo.web.api.analyzers.analyzer_factory import AnalyzerFactory
    from summit_seo.web.api.analyzers.security_analyzer import SecurityAnalyzer
    from summit_seo.web.api.analyzers.seo_analyzer import SEOAnalyzer
    from summit_seo.web.api.analyzers.performance_analyzer import PerformanceAnalyzer
    from summit_seo.web.api.analyzers.content_analyzer import ContentAnalyzer
    from summit_seo.web.api.analyzers.accessibility_analyzer import AccessibilityAnalyzer
    HAS_ANALYZERS = True
except ImportError:
    HAS_ANALYZERS = False
    print("Warning: SEO analyzers not found. Using mock data for testing.")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Mock sample data in case the actual analyzers aren't available
MOCK_ANALYZER_RESULTS = {
    "security": {
        "score": 78,
        "findings": [
            {"severity": "high", "issue": "HTTPS not enabled", "remediation": "Enable HTTPS by installing an SSL certificate"},
            {"severity": "medium", "issue": "Some pages don't force HTTPS", "remediation": "Implement proper redirects"},
            {"severity": "low", "issue": "Missing Content-Security-Policy header", "remediation": "Add appropriate CSP headers"}
        ]
    },
    "seo": {
        "score": 85,
        "findings": [
            {"severity": "medium", "issue": "Meta descriptions too long on 3 pages", "remediation": "Shorten meta descriptions to under 160 characters"},
            {"severity": "medium", "issue": "Missing alt text on 8 images", "remediation": "Add descriptive alt text to all images"},
            {"severity": "low", "issue": "URLs contain uppercase characters", "remediation": "Convert URLs to lowercase"}
        ]
    },
    "performance": {
        "score": 65,
        "findings": [
            {"severity": "high", "issue": "Mobile page load time exceeds 3 seconds", "remediation": "Optimize images and implement lazy loading"},
            {"severity": "medium", "issue": "Render-blocking JavaScript detected", "remediation": "Defer non-critical JavaScript"},
            {"severity": "medium", "issue": "No browser caching implemented", "remediation": "Add cache-control headers"}
        ]
    },
    "content": {
        "score": 92,
        "findings": [
            {"severity": "low", "issue": "Keyword density could be improved", "remediation": "Increase primary keyword usage without keyword stuffing"},
            {"severity": "low", "issue": "Some heading structure issues", "remediation": "Maintain proper H1-H6 hierarchy"}
        ]
    },
    "accessibility": {
        "score": 88,
        "findings": [
            {"severity": "medium", "issue": "Low contrast text in some areas", "remediation": "Increase contrast ratio to at least 4.5:1"},
            {"severity": "low", "issue": "Some form fields missing labels", "remediation": "Add appropriate labels to all form fields"}
        ]
    }
}

def fetch_website_content(url: str) -> Optional[str]:
    """Fetch website content from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

def parse_html_content(html_content: str) -> Dict[str, Any]:
    """Parse HTML content and extract key SEO elements."""
    if not html_content:
        return {}
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract key SEO elements
    parsed_data = {
        "title": soup.title.string if soup.title else None,
        "meta_description": None,
        "h1_tags": [h1.get_text(strip=True) for h1 in soup.find_all('h1')],
        "h2_tags": [h2.get_text(strip=True) for h2 in soup.find_all('h2')],
        "img_count": len(soup.find_all('img')),
        "img_missing_alt": len([img for img in soup.find_all('img') if not img.get('alt')]),
        "links": len(soup.find_all('a')),
        "external_links": len([a for a in soup.find_all('a') if a.get('href') and a.get('href').startswith(('http', 'https')) and not url in a.get('href')]),
        "content_sample": soup.get_text()[:1000] if soup.body else ""
    }
    
    # Get meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        parsed_data["meta_description"] = meta_desc.get('content')
    
    return parsed_data

def analyze_website(url: str) -> Dict[str, Any]:
    """Analyze a website using Summit SEO analyzers or mock data."""
    logger.info(f"Analyzing website: {url}")
    
    # Fetch website content
    html_content = fetch_website_content(url)
    if not html_content:
        logger.error(f"Failed to fetch content from {url}, using mock data")
        return {
            "url": url,
            "analyzed": False,
            "error": "Failed to fetch content",
            "results": MOCK_ANALYZER_RESULTS
        }
    
    # Parse content
    parsed_data = parse_html_content(html_content)
    logger.info(f"Successfully parsed content from {url}")
    
    # Run analyzers if available
    if HAS_ANALYZERS:
        logger.info("Using actual SEO analyzers")
        
        # Create analyzer factory
        factory = AnalyzerFactory()
        
        # Get all analyzer instances
        analyzers = {
            "security": factory.get_analyzer("security"),
            "seo": factory.get_analyzer("seo"),
            "performance": factory.get_analyzer("performance"),
            "content": factory.get_analyzer("content"),
            "accessibility": factory.get_analyzer("accessibility")
        }
        
        # Run each analyzer
        analysis_results = {}
        for name, analyzer in analyzers.items():
            if analyzer:
                try:
                    logger.info(f"Running {name} analyzer")
                    result = analyzer.analyze(url, html_content, parsed_data)
                    analysis_results[name] = result
                except Exception as e:
                    logger.error(f"Error running {name} analyzer: {str(e)}")
                    analysis_results[name] = {"error": str(e), "score": 0, "findings": []}
    else:
        logger.info("Using mock analyzer data")
        analysis_results = MOCK_ANALYZER_RESULTS
    
    return {
        "url": url,
        "analyzed": True,
        "timestamp": time.time(),
        "parsed_data": parsed_data,
        "results": analysis_results
    }

def generate_recommendations(analysis_data: Dict[str, Any]) -> str:
    """Generate recommendations using the LLM service."""
    logger.info("Generating recommendations using LLM")
    
    # Initialize the LLM service
    llm_service = get_llm_service()
    
    # Create a prompt from the analysis data
    parsed_data = analysis_data.get("parsed_data", {})
    results = analysis_data.get("results", {})
    
    # Extract issues from analysis results
    all_findings = []
    for analyzer_name, analyzer_result in results.items():
        if "findings" in analyzer_result:
            for finding in analyzer_result["findings"]:
                all_findings.append({
                    "analyzer": analyzer_name,
                    "severity": finding.get("severity", "unknown"),
                    "issue": finding.get("issue", "Unknown issue"),
                    "remediation": finding.get("remediation", "No remediation provided")
                })
    
    # Build the prompt
    prompt = f"""
    As an advanced SEO consultant, analyze this website data and provide 5 specific, actionable recommendations to improve search rankings and overall website quality:
    
    Website URL: {analysis_data.get('url', 'Unknown URL')}
    Page Title: {parsed_data.get('title', 'No title found')}
    Meta Description: {parsed_data.get('meta_description', 'No meta description found')}
    Main Headings: {', '.join(parsed_data.get('h1_tags', ['No H1 tags found']))}
    
    Analysis Scores:
    {json.dumps({name: data.get('score', 0) for name, data in results.items()}, indent=2)}
    
    Top Issues Found:
    {json.dumps(all_findings[:10], indent=2)}
    
    For each recommendation:
    1. Clearly state what should be changed
    2. Explain why this change would improve SEO and overall website performance
    3. Provide specific implementation steps
    4. Estimate the potential impact (High/Medium/Low)
    
    Format your recommendations as 5 numbered points, each with clear headers and implementation steps.
    """
    
    # Get recommendations from LLM
    try:
        response = llm_service.get_completion(
            prompt=prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        recommendations = response["choices"][0]["message"]["content"]
        return recommendations
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return f"Error generating recommendations: {str(e)}"

def generate_competitor_analysis(url: str, competitors: List[str]) -> str:
    """Generate competitor analysis using the LLM service."""
    logger.info(f"Generating competitor analysis for {url} against {competitors}")
    
    # Initialize the LLM service
    llm_service = get_llm_service()
    
    # Create a prompt for competitor analysis
    prompt = f"""
    As an SEO expert, analyze this website and its competitors:
    
    Main Website: {url}
    Competitor Websites: {', '.join(competitors)}
    
    Please provide:
    
    1. Competitive Gap Analysis: Identify 3 key areas where competitors may have an advantage
    
    2. Keyword Opportunities: Suggest 5 keywords the main website should target based on competitor positioning
    
    3. Content Strategy Recommendations: Recommend 3 specific content initiatives to gain advantage over competitors
    
    4. Technical SEO Comparison: Identify technical aspects where competitors may be performing better
    
    5. Action Plan: Provide a prioritized list of 5 actions to improve competitive positioning
    
    Format your analysis with clear headings and bullet points.
    """
    
    # Get competitor analysis from LLM
    try:
        response = llm_service.get_completion(
            prompt=prompt,
            temperature=0.4,
            max_tokens=1500
        )
        
        analysis = response["choices"][0]["message"]["content"]
        return analysis
    except Exception as e:
        logger.error(f"Error generating competitor analysis: {str(e)}")
        return f"Error generating competitor analysis: {str(e)}"

def run_tests(url: str, competitors: List[str]) -> None:
    """Run the complete end-to-end test."""
    start_time = time.time()
    logger.info(f"Starting end-to-end test for {url}")
    
    try:
        # Step 1: Load environment variables
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            logger.info(f"Loading environment from {env_path}")
            load_dotenv(dotenv_path=env_path)
        else:
            logger.warning(f"No .env file found at {env_path}")
        
        # Log configuration info
        logger.info(f"Using LiteLLM default model: {settings.LITELLM_DEFAULT_MODEL}")
        logger.info(f"Ollama enabled: {settings.OLLAMA_ENABLE}")
        logger.info(f"Ollama base URL: {settings.OLLAMA_BASE_URL}")
        logger.info(f"Ollama models: {settings.OLLAMA_MODELS}")
        
        # Step 2: Analyze the website
        logger.info("Starting website analysis")
        analysis_result = analyze_website(url)
        
        # Step 3: Generate recommendations
        logger.info("Generating SEO recommendations")
        recommendations = generate_recommendations(analysis_result)
        
        # Step 4: Generate competitor analysis if competitors provided
        competitor_analysis = None
        if competitors:
            logger.info("Generating competitor analysis")
            competitor_analysis = generate_competitor_analysis(url, competitors)
        
        # Step 5: Output the results
        print("\n" + "="*80)
        print(f"END-TO-END TEST RESULTS FOR {url}")
        print("="*80)
        
        # Print analysis scores
        print("\n📊 ANALYSIS SCORES:")
        for analyzer_name, analyzer_result in analysis_result["results"].items():
            if "score" in analyzer_result:
                print(f"{analyzer_name.capitalize()}: {analyzer_result['score']}/100")
            
        # Print top findings
        print("\n🔍 TOP FINDINGS:")
        finding_count = 0
        for analyzer_name, analyzer_result in analysis_result["results"].items():
            if "findings" in analyzer_result:
                for finding in analyzer_result["findings"]:
                    severity = finding.get("severity", "unknown").upper()
                    severity_symbol = "🔴" if severity == "HIGH" else "🟠" if severity == "MEDIUM" else "🟡"
                    print(f"{severity_symbol} [{analyzer_name.capitalize()}] {finding.get('issue')}")
                    finding_count += 1
                    if finding_count >= 10:
                        break
                if finding_count >= 10:
                    break
                    
        # Print recommendations
        print("\n💡 RECOMMENDATIONS:")
        print(recommendations)
        
        # Print competitor analysis if available
        if competitor_analysis:
            print("\n🥇 COMPETITOR ANALYSIS:")
            print(competitor_analysis)
            
        # Print completion time
        end_time = time.time()
        print("\n⏱️ Test completed in {:.2f} seconds".format(end_time - start_time))
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error in end-to-end test: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}")

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run an end-to-end test of Summit SEO with Deepseek")
    parser.add_argument("--url", type=str, default="https://example.com", 
                        help="URL to analyze (default: https://example.com)")
    parser.add_argument("--competitors", type=str, nargs="*", 
                        help="List of competitor URLs to analyze")
    
    args = parser.parse_args()
    run_tests(args.url, args.competitors)

if __name__ == "__main__":
    main() 