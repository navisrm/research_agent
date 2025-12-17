"""Research Agent - Searches on topics and creates initial drafts."""

import os
from typing import List, Dict
from openai import OpenAI
from tavily import TavilyClient


class ResearchAgent:
    """Agent responsible for researching topics and creating initial drafts."""
    
    def __init__(self, openai_api_key: str = None, tavily_api_key: str = None, model_name: str = None):
        """
        Initialize the Research Agent.
        
        Args:
            openai_api_key: OpenAI API key. If None, reads from environment variable.
            tavily_api_key: Tavily API key. If None, reads from environment variable.
            model_name: OpenAI model name. If None, reads from OPENAI_MODEL env var (default: gpt-4o).
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.tavily_api_key = tavily_api_key or os.getenv('TAVILY_API_KEY')
        if not self.tavily_api_key:
            raise ValueError("Tavily API key is required. Set TAVILY_API_KEY environment variable.")
        
        self.model_name = model_name or os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        self.client = OpenAI(api_key=self.openai_api_key)
        self.tavily_client = TavilyClient(api_key=self.tavily_api_key)
    
    def search_sources(self, topic: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for sources related to the research topic using Tavily.
        
        Args:
            topic: The research topic to search for
            max_results: Maximum number of search results to return
            
        Returns:
            List of dictionaries containing source information (url, title, content)
        """
        try:
            response = self.tavily_client.search(
                query=topic,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False
            )
            
            sources = []
            
            # Extract sources from results
            if 'results' in response:
                for result in response['results']:
                    source = {
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'content': result.get('content', '')
                    }
                    sources.append(source)
            
            # Include answer if available
            if 'answer' in response and response['answer']:
                sources.insert(0, {
                    'url': 'Tavily Summary',
                    'title': 'Search Summary',
                    'content': response['answer']
                })
            
            return sources
            
        except Exception as e:
            raise Exception(f"Error searching for sources: {str(e)}")
    
    def search_and_create_draft(self, topic: str, requirements: str = None, max_sources: int = 5) -> str:
        """
        Research a topic using Tavily search, identify sources, and create an initial draft.
        
        Args:
            topic: The research topic to investigate
            requirements: Optional requirements to consider during research
            max_sources: Maximum number of sources to search for
            
        Returns:
            A draft document as a string with source citations
        """
        # Step 1: Search for sources using Tavily
        print(f"  Searching for sources on: {topic}")
        sources = self.search_sources(topic, max_results=max_sources)
        print(f"  Found {len(sources)} sources")
        
        # Step 2: Build the research prompt with source information
        prompt = f"""You are a research agent. Your task is to research the following topic and create a comprehensive draft document using the provided sources.

Topic: {topic}
"""
        
        if requirements:
            prompt += f"\nRequirements to consider:\n{requirements}\n"
        
        # Include source information
        if sources:
            prompt += "\n\nSources found:\n"
            for i, source in enumerate(sources, 1):
                prompt += f"\nSource {i}:\n"
                prompt += f"Title: {source.get('title', 'N/A')}\n"
                prompt += f"URL: {source.get('url', 'N/A')}\n"
                prompt += f"Content: {source.get('content', '')[:1000]}\n"  # Limit content length
                prompt += "-" * 50 + "\n"
        
        prompt += """
CRITICAL REQUIREMENTS:
- Stick strictly to facts that are cited in the provided sources
- DO NOT make any statement unless it is directly supported by a source
- Every factual claim MUST be followed by a citation (e.g., [Source 1], [Source 3])
- If information is not available in the sources, do not include it
- Do not add speculation, assumptions, or unsupported claims

Please create a well-structured draft that includes:
1. An introduction to the topic
2. Key findings and insights based ONLY on the sources provided
3. Relevant details and examples from the sources (with citations)
4. A conclusion summarizing the main points (all must be cited)
5. A "Sources" section listing all referenced sources with URLs

Make sure to:
- Cite sources appropriately when using information from them (use [Source X] format)
- Synthesize information from multiple sources only when facts align
- Ensure the content is informative, accurate, and well-organized
- Include proper attribution to sources for EVERY factual statement
- If a source contradicts another, note the discrepancy with citations"""

        try:
            # Use OpenAI to generate the draft based on sources
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert researcher and content creator. You create comprehensive, well-structured research documents based ONLY on provided sources, with proper citations. You never make unsupported claims and stick strictly to facts that are cited in the sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=3000  # Increased to accommodate source citations
            )
            
            draft = response.choices[0].message.content
            return draft
            
        except Exception as e:
            raise Exception(f"Error creating draft: {str(e)}")
    
    def create_draft_from_sources(
        self,
        topic: str,
        sources: List[Dict[str, str]],
        requirements: str = None
    ) -> str:
        """
        Create a draft from pre-collected sources (used by orchestrator).
        
        Args:
            topic: The research topic
            sources: Pre-collected list of sources
            requirements: Optional requirements to consider during research
            
        Returns:
            A draft document as a string with source citations
        """
        # Build the research prompt with source information
        prompt = f"""You are a research agent. Your task is to research the following topic and create a comprehensive draft document using the provided sources.

Topic: {topic}
"""
        
        if requirements:
            prompt += f"\nRequirements to consider:\n{requirements}\n"
        
        # Include source information
        if sources:
            prompt += "\n\nSources found:\n"
            for i, source in enumerate(sources, 1):
                prompt += f"\nSource {i}:\n"
                prompt += f"Title: {source.get('title', 'N/A')}\n"
                prompt += f"URL: {source.get('url', 'N/A')}\n"
                prompt += f"Content: {source.get('content', '')[:1000]}\n"  # Limit content length
                prompt += "-" * 50 + "\n"
        else:
            raise ValueError("No sources provided. Cannot create draft without sources.")
        
        prompt += """
CRITICAL REQUIREMENTS:
- Base all statements on facts identified in the provided sources
- Every factual claim MUST be followed by a citation (e.g., [Source 1], [Source 3])
- Make meaningful statements and insights based on the facts, not just list facts
- For each finding or fact identified, provide multiple related statements that explain, contextualize, or elaborate on that finding
- Ensure a decent amount of content per finding (aim for 3-5 statements per major finding)
- Do not add speculation, assumptions, or unsupported claims beyond what the sources provide
- If information is not available in the sources, do not include it

Using only the provided sources, produce a well-structured, evidence-based research draft on the given topic.

The document should:
	•	Begin with a concise introduction that defines the topic and scope based on the sources
	•	Present the core findings, observations, and documented issues drawn from the sources
	•	For each finding, provide multiple statements that:
		- State the fact clearly
		- Explain its significance or context
		- Describe related details or implications
		- Connect it to other findings when relevant
		- Provide examples or specifics when available

For the main body of the document:
	•	Do NOT follow a fixed or predefined structure
	•	Instead, derive a logical structure that best fits the research topic and the nature of the evidence
	•	Organize content into clear, meaningful sections (with headings) such as:
		- Documented events or incidents
		- Reported impacts or consequences
		- Regulatory actions, enforcement, or responses
		- Patterns, frequency, or trends explicitly noted in the sources
		- Geographic, temporal, or community-specific details
	•	Section titles and ordering should emerge naturally from what the sources emphasize

    Each section must:
	•	Contain source-supported facts with multiple statements per finding
	•	Include citations for every factual statement
	•	Provide adequate elaboration and context for each finding
	•	Synthesize multiple sources when they provide related information

Conclusion
	•	Provide a comprehensive summary of the documented facts and findings
	•	Do not introduce new information
	•	All statements must be cited

Sources
	•	Include a clearly labeled "Sources" section
	•	List all referenced sources with their URLs
	•	Use consistent numbering that matches in-text citations (e.g., [Source 1])

Make sure to:
- Cite sources appropriately when using information from them (use [Source X] format)
- Synthesize information from multiple sources when they provide related facts
- Ensure the content is comprehensive, informative, accurate, and well-organized
- Include proper attribution to sources for EVERY factual statement
- Provide sufficient elaboration and context for each finding (aim for 3-5 statements per major finding)
- If a source contradicts another, note the discrepancy with citations"""

        try:
            # Use OpenAI to generate the draft based on sources
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert researcher and content creator. You create comprehensive, well-structured research documents based on facts from provided sources, with proper citations. You make meaningful statements and insights from the facts, providing adequate elaboration (3-5 statements per major finding) while ensuring all claims are supported by sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=10000  # Increased to accommodate source citations
            )
            
            draft = response.choices[0].message.content
            return draft
            
        except Exception as e:
            raise Exception(f"Error creating draft: {str(e)}")


