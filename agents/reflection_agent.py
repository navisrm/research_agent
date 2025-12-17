"""Reflection Agent - Validates drafts and makes improvements."""

import os
from typing import Tuple
from openai import OpenAI


class ReflectionAgent:
    """Agent responsible for validating drafts and making corrections/improvements."""
    
    def __init__(self, api_key: str = None, model_name: str = None):
        """
        Initialize the Reflection Agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from environment variable.
            model_name: OpenAI model name. If None, reads from OPENAI_MODEL env var (default: gpt-4o).
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.model_name = model_name or os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        self.client = OpenAI(api_key=self.api_key)
    
    def validate_and_improve(self, draft: str, topic: str, requirements: str = None) -> Tuple[str, str]:
        """
        Validate the draft against requirements and improve it.
        
        Args:
            draft: The initial draft to validate and improve
            topic: The original research topic
            requirements: Requirements to validate against
            
        Returns:
            Tuple of (improved_draft, changes_summary)
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
- Verify that factual statements have proper citations (e.g., [Source X])
- DO NOT remove text unless it is clearly not supported by any facts in the sources
- Be conservative: if a statement could be inferred from the sources, keep it
- Only remove statements that are clearly unsupported, speculative, or contradictory to the sources
- Validate that all citations reference actual sources from the draft
- Preserve the content and elaboration provided in the original draft

Please:
1. Validate the draft against the topic and requirements (if provided)
2. Check that factual statements are properly cited with source references
3. Identify any statements that are clearly unsupported by sources (be conservative - only flag obvious issues)
4. Identify any inaccuracies, gaps, or areas for improvement
5. Check for clarity, structure, and completeness
6. Make necessary corrections while preserving as much original content as possible
7. Enhance the content with better explanations, examples, or details where needed (all must be cited)
8. Ensure the draft meets all specified requirements
9. Verify the Sources section is complete and accurate

IMPORTANT: 
- Preserve the original content structure and elaboration
- Only make changes that are clearly necessary
- Do not remove content unless it is definitively unsupported by facts
- If you're unsure whether something is supported, keep it

Provide your response in the following format:

[IMPROVED_DRAFT]
[Your improved draft here]
[/IMPROVED_DRAFT]

[CHANGES_SUMMARY]
A detailed summary of all changes made, including:
- Any text removed and why (only if clearly unsupported)
- Any text added or modified and why
- Citation corrections made
- Structural improvements
- Any other modifications
If no changes were made, state "No changes required - draft is valid."
[/CHANGES_SUMMARY]"""

        try:
            # Use OpenAI to validate and improve the draft
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert editor and validator. You review content critically, verify that facts are properly cited, and improve drafts while being conservative about removing content. You only remove text that is clearly unsupported by sources. You preserve original content structure and elaboration."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower temperature for more focused improvements
                max_tokens=12000
            )
            
            response_text = response.choices[0].message.content
            
            # Parse the response to extract draft and changes summary
            if "[IMPROVED_DRAFT]" in response_text and "[CHANGES_SUMMARY]" in response_text:
                parts = response_text.split("[IMPROVED_DRAFT]")
                if len(parts) > 1:
                    draft_part = parts[1].split("[/IMPROVED_DRAFT]")[0].strip()
                    changes_part = parts[1].split("[CHANGES_SUMMARY]")
                    if len(changes_part) > 1:
                        changes_summary = changes_part[1].split("[/CHANGES_SUMMARY]")[0].strip()
                    else:
                        changes_summary = "Changes summary not found in response."
                else:
                    draft_part = response_text
                    changes_summary = "Could not parse changes summary from response."
            else:
                # Fallback: treat entire response as draft
                draft_part = response_text
                changes_summary = "Response format not recognized. Full response treated as draft."
            
            return draft_part, changes_summary
            
        except Exception as e:
            raise Exception(f"Error validating and improving draft: {str(e)}")


