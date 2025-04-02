"""Recommendation enhancer service using LLM capabilities.

This service integrates LLM capabilities to enhance SEO recommendations with
detailed explanations, implementation guidance, and impacts.
"""

from typing import Dict, List, Any, Optional
import logging
import asyncio

from summit_seo.analyzer.recommendation import (
    Recommendation, 
    RecommendationBuilder,
    RecommendationSeverity,
    RecommendationPriority
)
from .llm_service import get_llm_service
from .llm_optimizer import get_llm_optimizer

# Set up logging
logger = logging.getLogger(__name__)

class RecommendationEnhancerService:
    """Service for enhancing recommendations using LLM capabilities."""

    def __init__(self):
        """Initialize the recommendation enhancer service."""
        self.llm_service = get_llm_service()
        self.llm_optimizer = get_llm_optimizer()
        logger.info("Recommendation enhancer service initialized")

    async def enhance_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """Enhance a recommendation with LLM-generated content.
        
        Args:
            recommendation: The original recommendation to enhance
            
        Returns:
            Enhanced recommendation with LLM-generated details
        """
        if not recommendation.description:
            logger.warning("Cannot enhance recommendation without description")
            return recommendation
            
        try:
            # Generate a more detailed explanation
            enhanced_description = await self._generate_enhanced_description(recommendation)
            if enhanced_description:
                recommendation.description = enhanced_description
                
            # Generate implementation steps if not already provided
            if not recommendation.steps:
                steps = await self._generate_implementation_steps(recommendation)
                if steps:
                    recommendation.steps = steps
                    
            # Generate impact assessment if not already provided
            if not recommendation.impact:
                impact = await self._generate_impact_assessment(recommendation)
                if impact:
                    recommendation.impact = impact
                    
            return recommendation
            
        except Exception as e:
            logger.error(f"Error enhancing recommendation: {str(e)}")
            return recommendation

    async def enhance_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Enhance multiple recommendations with LLM-generated content.
        
        Args:
            recommendations: List of recommendations to enhance
            
        Returns:
            List of enhanced recommendations
        """
        if not recommendations:
            return []
            
        # For a small number of recommendations, enhance them in parallel
        if len(recommendations) <= 3:
            tasks = [self.enhance_recommendation(rec) for rec in recommendations]
            return await asyncio.gather(*tasks)
            
        # For larger batches, use batched processing
        try:
            # First, prioritize generating descriptions in parallel
            await self._batch_enhance_descriptions(recommendations)
            
            # Then generate implementation steps for recommendations without them
            recs_without_steps = [rec for rec in recommendations if not rec.steps]
            if recs_without_steps:
                await self._batch_generate_steps(recs_without_steps)
                
            # Finally generate impact assessments for recommendations without them
            recs_without_impact = [rec for rec in recommendations if not rec.impact]
            if recs_without_impact:
                await self._batch_generate_impacts(recs_without_impact)
                
            return recommendations
        except Exception as e:
            logger.error(f"Error batch enhancing recommendations: {str(e)}")
            # Fall back to sequential processing if batching fails
            enhanced_recommendations = []
            for recommendation in recommendations:
                enhanced = await self.enhance_recommendation(recommendation)
                enhanced_recommendations.append(enhanced)
            return enhanced_recommendations

    async def _batch_enhance_descriptions(self, recommendations: List[Recommendation]) -> None:
        """Enhance descriptions for multiple recommendations in batch.
        
        Args:
            recommendations: List of recommendations to enhance
        """
        # Create prompts for all recommendations that need enhanced descriptions
        prompts = []
        rec_indices = []
        
        for i, rec in enumerate(recommendations):
            if not rec.description or len(rec.description) < 50:  # Only enhance short descriptions
                prompt = self._create_description_prompt(rec)
                prompts.append(prompt)
                rec_indices.append(i)
                
        if not prompts:
            return  # Nothing to enhance
            
        # Process in batch
        responses = await self.llm_optimizer.get_batched_completions(prompts)
        
        # Apply responses to recommendations
        for i, response in enumerate(responses):
            if isinstance(response, dict) and "error" in response and response["error"]:
                logger.warning(f"Error enhancing description: {response.get('error_message')}")
                continue
                
            if response and "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"].strip()
                if content:
                    recommendations[rec_indices[i]].description = content

    async def _batch_generate_steps(self, recommendations: List[Recommendation]) -> None:
        """Generate implementation steps for multiple recommendations in batch.
        
        Args:
            recommendations: List of recommendations to generate steps for
        """
        prompts = [self._create_steps_prompt(rec) for rec in recommendations]
        
        # Process in batch
        responses = await self.llm_optimizer.get_batched_completions(prompts)
        
        # Apply responses to recommendations
        for i, response in enumerate(responses):
            if isinstance(response, dict) and "error" in response and response["error"]:
                logger.warning(f"Error generating steps: {response.get('error_message')}")
                continue
                
            if response and "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"].strip()
                if content:
                    steps = self._parse_steps_from_content(content)
                    if steps:
                        recommendations[i].steps = steps

    async def _batch_generate_impacts(self, recommendations: List[Recommendation]) -> None:
        """Generate impact assessments for multiple recommendations in batch.
        
        Args:
            recommendations: List of recommendations to generate impact assessments for
        """
        prompts = [self._create_impact_prompt(rec) for rec in recommendations]
        
        # Process in batch
        responses = await self.llm_optimizer.get_batched_completions(prompts)
        
        # Apply responses to recommendations
        for i, response in enumerate(responses):
            if isinstance(response, dict) and "error" in response and response["error"]:
                logger.warning(f"Error generating impact: {response.get('error_message')}")
                continue
                
            if response and "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"].strip()
                if content:
                    recommendations[i].impact = content

    def _create_description_prompt(self, recommendation: Recommendation) -> str:
        """Create a prompt for generating an enhanced description.
        
        Args:
            recommendation: Recommendation to enhance
            
        Returns:
            Prompt for generating enhanced description
        """
        return f"""
        As an SEO expert, please enhance the following SEO recommendation with a more detailed explanation.
        Make it comprehensive, but concise and actionable. Include information about why this matters for SEO.
        
        RECOMMENDATION: {recommendation.title}
        
        CURRENT DESCRIPTION: {recommendation.description}
        
        ENHANCED DESCRIPTION:
        """

    def _create_steps_prompt(self, recommendation: Recommendation) -> str:
        """Create a prompt for generating implementation steps.
        
        Args:
            recommendation: Recommendation to generate steps for
            
        Returns:
            Prompt for generating implementation steps
        """
        return f"""
        As an SEO expert, please provide step-by-step instructions for implementing the following SEO recommendation.
        Provide 3-5 clear, specific, actionable steps. Each step should be concrete and implementable.
        
        RECOMMENDATION: {recommendation.title}
        
        DESCRIPTION: {recommendation.description}
        
        IMPLEMENTATION STEPS (number each step):
        """

    def _create_impact_prompt(self, recommendation: Recommendation) -> str:
        """Create a prompt for generating impact assessment.
        
        Args:
            recommendation: Recommendation to generate impact for
            
        Returns:
            Prompt for generating impact assessment
        """
        severity_context = {
            RecommendationSeverity.CRITICAL: "extremely important",
            RecommendationSeverity.HIGH: "very important",
            RecommendationSeverity.MEDIUM: "moderately important",
            RecommendationSeverity.LOW: "less critical but valuable",
            RecommendationSeverity.INFO: "informational"
        }
        
        severity_description = severity_context.get(recommendation.severity, "important")
        
        return f"""
        As an SEO expert, please write a brief impact assessment for the following {severity_description} SEO recommendation.
        Explain how implementing this recommendation will impact website performance, search rankings, or user experience.
        Be specific about benefits, but realistic about the potential impact.
        
        RECOMMENDATION: {recommendation.title}
        
        DESCRIPTION: {recommendation.description}
        
        IMPACT ASSESSMENT (1-2 sentences):
        """

    def _parse_steps_from_content(self, content: str) -> List[str]:
        """Parse implementation steps from content.
        
        Args:
            content: Response content to parse
            
        Returns:
            List of implementation steps
        """
        steps = []
        for line in content.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove the number or bullet and any following period or space
                step = line.lstrip("0123456789.-).").strip()
                if step:
                    steps.append(step)
        
        return steps

    async def _generate_enhanced_description(self, recommendation: Recommendation) -> Optional[str]:
        """Generate an enhanced description for a recommendation using the LLM optimizer.
        
        Args:
            recommendation: Recommendation to enhance
            
        Returns:
            Enhanced description or None if generation fails
        """
        prompt = self._create_description_prompt(recommendation)
        
        try:
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(prompt, max_tokens=300)
            if response and "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"].strip()
            return None
        except Exception as e:
            logger.error(f"Error generating enhanced description: {str(e)}")
            return None

    async def _generate_implementation_steps(self, recommendation: Recommendation) -> List[str]:
        """Generate implementation steps for a recommendation using the LLM optimizer.
        
        Args:
            recommendation: Recommendation to generate steps for
            
        Returns:
            List of implementation steps or empty list if generation fails
        """
        prompt = self._create_steps_prompt(recommendation)
        
        try:
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(prompt, max_tokens=400)
            if response and "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"].strip()
                return self._parse_steps_from_content(content)
            return []
        except Exception as e:
            logger.error(f"Error generating implementation steps: {str(e)}")
            return []

    async def _generate_impact_assessment(self, recommendation: Recommendation) -> Optional[str]:
        """Generate impact assessment for a recommendation using the LLM optimizer.
        
        Args:
            recommendation: Recommendation to assess impact for
            
        Returns:
            Impact assessment or None if generation fails
        """
        prompt = self._create_impact_prompt(recommendation)
        
        try:
            # Use the optimizer for token-efficient completion
            response = await self.llm_optimizer.get_optimized_completion(prompt, max_tokens=150)
            if response and "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"].strip()
            return None
        except Exception as e:
            logger.error(f"Error generating impact assessment: {str(e)}")
            return None


def get_recommendation_enhancer() -> RecommendationEnhancerService:
    """Get or create a recommendation enhancer service instance.
    
    Returns:
        RecommendationEnhancerService instance
    """
    return RecommendationEnhancerService() 