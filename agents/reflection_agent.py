"""Reflection Agent - Validates drafts and makes improvements."""

import os
from openai import OpenAI


class ReflectionAgent:
    """Agent responsible for validating drafts and making corrections/improvements."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Reflection Agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from environment variable.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def validate_and_improve(self, draft: str, topic: str, requirements: str = None) -> str:
        """
        Validate the draft against requirements and improve it.
        
        Args:
            draft: The initial draft to validate and improve
            topic: The original research topic
            requirements: Requirements to validate against
            
        Returns:
            An improved and validated draft
        """
        # Build the validation and improvement prompt
        prompt = f"""You are a reflection and validation agent. Your task is to review, validate, and improve a research draft.

Original Topic: {topic}

Initial Draft:
---
{draft}
---
"""
        
        if requirements:
            prompt += f"\nRequirements to validate against:\n{requirements}\n"
        
        prompt += """
CRITICAL VALIDATION REQUIREMENTS:
- Verify that EVERY factual statement has a proper citation (e.g., [Source X])
- Remove or flag any statements that are not supported by sources
- Ensure no unsupported claims, speculation, or assumptions are present
- Validate that all citations reference actual sources from the draft

Please:
1. Validate the draft against the topic and requirements (if provided)
2. Check that EVERY factual statement is properly cited with source references
3. Identify any statements without citations and either remove them or request sources
4. Identify any inaccuracies, gaps, or areas for improvement
5. Check for clarity, structure, and completeness
6. Make necessary corrections while maintaining strict adherence to cited facts
7. Enhance the content with better explanations, examples, or details (all must be cited)
8. Ensure the draft meets all specified requirements
9. Verify the Sources section is complete and accurate

Provide an improved version of the draft that:
- Addresses all validation issues
- Ensures every fact is properly cited
- Removes any uncited claims
- Incorporates enhancements while maintaining fact-based rigor"""

        try:
            # Use OpenAI to validate and improve the draft
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert editor and validator. You review content critically, verify that all facts are properly cited, remove unsupported claims, and improve drafts while maintaining strict adherence to cited sources and accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower temperature for more focused improvements
                max_tokens=10000
            )
            
            improved_draft = response.choices[0].message.content
            return improved_draft
            
        except Exception as e:
            raise Exception(f"Error validating and improving draft: {str(e)}")


