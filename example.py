"""Example usage of the Research Agent System."""

import os
from dotenv import load_dotenv
from agents.research_agent import ResearchAgent
from agents.reflection_agent import ReflectionAgent


def example_usage():
    """Example of how to use the research agent system programmatically."""
    # Load environment variables
    load_dotenv()
    
    # Example topic and requirements
    topic = "The impact of artificial intelligence on healthcare"
    requirements = """
    - Focus on recent developments (last 5 years)
    - Include specific examples of AI applications
    - Discuss both benefits and challenges
    - Keep the content accessible to general audience
    """
    
    print("Example: Research Agent System")
    print("=" * 60)
    
    try:
        # Initialize agents
        research_agent = ResearchAgent()
        reflection_agent = ReflectionAgent()
        
        # Step 1: Create draft
        print("\n[Step 1] Research Agent creating draft...")
        draft = research_agent.search_and_create_draft(
            topic=topic,
            requirements=requirements
        )
        print(f"\nDraft length: {len(draft)} characters")
        
        # Step 2: Validate and improve
        print("\n[Step 2] Reflection Agent validating and improving...")
        improved_draft = reflection_agent.validate_and_improve(
            draft=draft,
            topic=topic,
            requirements=requirements
        )
        print(f"\nImproved draft length: {len(improved_draft)} characters")
        
        print("\n✓ Example completed successfully!")
        
        return draft, improved_draft
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return None, None


if __name__ == "__main__":
    example_usage()


