"""Explanation service for generating natural language explanations of SEO issues.

This service uses LLM to transform technical SEO findings and issues into
natural language explanations that are easy to understand.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import json
import asyncio
from functools import lru_cache

from .llm_service import get_llm_service
from .llm_optimizer import get_llm_optimizer

# Set up logging
logger = logging.getLogger(__name__)

class ExplanationService:
    """Service for generating natural language explanations of SEO issues."""

    def __init__(self):
        """Initialize the explanation service."""
        self.llm_service = get_llm_service()
        self.llm_optimizer = get_llm_optimizer()
        logger.info("Explanation service initialized")

    async def explain_issue(self, issue: Union[str, Dict[str, Any]], 
                          context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a natural language explanation for an SEO issue.
        
        Args:
            issue: SEO issue as string or structured data
            context: Optional additional context about the site or page
            
        Returns:
            Natural language explanation of the issue
        """
        try:
            # Convert issue to string if it's a dict
            issue_str = issue if isinstance(issue, str) else json.dumps(issue)
            
            # Build the prompt with context
            context_str = ""
            if context:
                context_str = "ADDITIONAL CONTEXT:\n"
                for key, value in context.items():
                    context_str += f"{key}: {value}\n"
            
            prompt = f"""
            As an SEO expert, please explain the following SEO issue in simple, non-technical language 
            that a business owner without technical knowledge would understand.
            
            Explain the issue, why it matters, and what impact it has on the website's search performance.
            
            SEO ISSUE: {issue_str}
            
            {context_str}
            
            EXPLANATION:
            """
            
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(
                prompt=prompt, 
                max_tokens=300,
                use_cache=True
            )
            
            if response and "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"].strip()
            return f"Unable to generate explanation for: {issue_str}"
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return f"Error explaining issue: {str(e)}"

    async def explain_technical_term(self, term: str) -> str:
        """Generate an explanation for a technical SEO term.
        
        Args:
            term: Technical SEO term to explain
            
        Returns:
            Simple explanation of the term
        """
        try:
            prompt = f"""
            As an SEO expert, please explain the following technical SEO term in simple language
            that a non-technical person would understand.
            
            TECHNICAL TERM: {term}
            
            SIMPLE EXPLANATION:
            """
            
            # Cache these explanations as technical terms don't change
            response = await self.llm_optimizer.get_optimized_completion(
                prompt=prompt, 
                max_tokens=200,
                use_cache=True  # Ensure caching for technical terms
            )
            
            if response and "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"].strip()
            return f"Unable to generate explanation for: {term}"
        except Exception as e:
            logger.error(f"Error explaining term: {str(e)}")
            return f"Error explaining term: {str(e)}"

    async def summarize_analysis_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a natural language summary of analysis results.
        
        Args:
            results: Analysis results data
            
        Returns:
            Dictionary containing original results plus natural language summary
        """
        try:
            # Extract key information for the summary
            score = results.get('score', 0)
            issues = results.get('issues', [])
            warnings = results.get('warnings', [])
            recommendations = results.get('recommendations', [])
            
            # Build a prompt for the LLM
            issues_text = "\n".join([f"- {issue}" for issue in issues[:5]])
            warnings_text = "\n".join([f"- {warning}" for warning in warnings[:5]])
            recommendations_text = "\n".join([f"- {rec}" for rec in recommendations[:5]])
            
            # Optimize token usage by limiting the content
            if len(issues) > 5:
                issues_text += f"\n- ...and {len(issues) - 5} more issues"
            if len(warnings) > 5:
                warnings_text += f"\n- ...and {len(warnings) - 5} more warnings"
            if len(recommendations) > 5:
                recommendations_text += f"\n- ...and {len(recommendations) - 5} more recommendations"
            
            prompt = f"""
            As an SEO expert, please provide a concise, natural language summary of these SEO analysis results.
            Explain the overall performance, key issues, and most important recommendations in a way that
            a business owner would understand.
            
            ANALYSIS SCORE: {score}/100
            
            TOP ISSUES:
            {issues_text}
            
            TOP WARNINGS:
            {warnings_text}
            
            KEY RECOMMENDATIONS:
            {recommendations_text}
            
            SUMMARY:
            """
            
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(
                prompt=prompt, 
                max_tokens=400
            )
            
            if response and "choices" in response and response["choices"]:
                summary = response["choices"][0]["message"]["content"].strip()
                
                # Add the summary to the results
                results_with_summary = results.copy()
                results_with_summary['natural_language_summary'] = summary
                return results_with_summary
            return results
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return results

    async def explain_score_breakdown(self, score_components: Dict[str, float]) -> str:
        """Generate an explanation of how the SEO score was calculated.
        
        Args:
            score_components: Dictionary of score components and their values
            
        Returns:
            Natural language explanation of the score breakdown
        """
        try:
            # Format the score components
            components_text = "\n".join([f"- {component}: {value}" for component, value in score_components.items()])
            
            prompt = f"""
            As an SEO expert, please explain this SEO score breakdown in simple terms.
            Explain what each component means, why it's important, and how it contributes to the overall score.
            
            SCORE COMPONENTS:
            {components_text}
            
            EXPLANATION:
            """
            
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(
                prompt=prompt, 
                max_tokens=350,
                use_cache=True  # Score explanations can be cached as they're fairly static
            )
            
            if response and "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"].strip()
            return f"Unable to generate explanation for score breakdown"
        except Exception as e:
            logger.error(f"Error explaining score breakdown: {str(e)}")
            return f"Error explaining score breakdown: {str(e)}"

    async def batch_explain_issues(self, issues: List[str]) -> List[str]:
        """Batch process multiple issues for explanation.
        
        Args:
            issues: List of issues to explain
            
        Returns:
            List of explanations for each issue
        """
        if not issues:
            return []
            
        # Generate prompts for each issue
        prompts = []
        for issue in issues:
            prompt = f"""
            As an SEO expert, please explain the following SEO issue in simple, non-technical language 
            that a business owner without technical knowledge would understand.
            
            Explain the issue, why it matters, and what impact it has on the website's search performance.
            
            SEO ISSUE: {issue}
            
            EXPLANATION:
            """
            prompts.append(prompt)
            
        # Process in batch
        try:
            responses = await self.llm_optimizer.get_batched_completions(prompts)
            
            # Extract explanations from responses
            explanations = []
            for i, response in enumerate(responses):
                if isinstance(response, dict) and "error" in response and response["error"]:
                    explanations.append(f"Unable to explain issue: {issues[i]}")
                    continue
                    
                if response and "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"]["content"].strip()
                    explanations.append(content)
                else:
                    explanations.append(f"Unable to explain issue: {issues[i]}")
                    
            return explanations
        except Exception as e:
            logger.error(f"Error batch explaining issues: {str(e)}")
            # Fall back to sequential processing
            results = []
            for issue in issues:
                explanation = await self.explain_issue(issue)
                results.append(explanation)
            return results


@lru_cache(maxsize=1)
def get_explanation_service() -> ExplanationService:
    """Get or create an explanation service instance.
    
    Returns:
        ExplanationService instance
    """
    return ExplanationService() 