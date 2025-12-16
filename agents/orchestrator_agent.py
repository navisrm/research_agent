"""Orchestrator Agent - Manages and coordinates research and reflection agents."""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from .research_agent import ResearchAgent
from .reflection_agent import ReflectionAgent


class OrchestratorAgent:
    """Orchestrator that manages query splitting and coordinates research and reflection agents."""
    
    def __init__(self, openai_api_key: str = None, tavily_api_key: str = None):
        """
        Initialize the Orchestrator Agent.
        
        Args:
            openai_api_key: OpenAI API key. If None, reads from environment variable.
            tavily_api_key: Tavily API key. If None, reads from environment variable.
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        self.research_agent = ResearchAgent(openai_api_key, tavily_api_key)
        self.reflection_agent = ReflectionAgent(openai_api_key)
    
    def split_query(self, topic: str, requirements: str = None, max_query_length: int = 200) -> List[str]:
        """
        Split a lengthy research request into multiple focused search queries.
        
        Args:
            topic: The main research topic
            requirements: Optional requirements that may need separate queries
            max_query_length: Maximum length for a single Tavily query
            
        Returns:
            List of focused search queries
        """
        # Combine topic and requirements
        full_request = topic
        if requirements:
            full_request += f"\n\nRequirements: {requirements}"
        
        # If the request is short enough, return as single query
        if len(full_request) <= max_query_length:
            return [topic]
        
        # Use LLM to intelligently split the query
        split_prompt = f"""You are a query optimization agent. Your task is to split a lengthy research request into multiple focused search queries that can be used with a search API.

Original Request:
{topic}

"""
        if requirements:
            split_prompt += f"Requirements:\n{requirements}\n\n"
        
        split_prompt += """Please split this into 2-5 focused search queries that:
1. Cover different aspects or sub-topics of the main request
2. Are specific and searchable (each under 200 characters)
3. Together comprehensively cover the original request
4. Can be executed independently

Return ONLY a numbered list of queries, one per line, like:
1. First focused query
2. Second focused query
3. Third focused query"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at breaking down complex research requests into focused, searchable queries."},
                    {"role": "user", "content": split_prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            queries_text = response.choices[0].message.content.strip()
            
            # Parse the numbered list
            queries = []
            for line in queries_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering (e.g., "1. " or "- ")
                    query = line.split('.', 1)[-1].strip() if '.' in line else line.lstrip('- ').strip()
                    if query and len(query) > 10:  # Valid query
                        queries.append(query)
            
            # Fallback: if parsing failed, use original topic
            if not queries:
                queries = [topic]
            
            return queries
            
        except Exception as e:
            # Fallback to original topic if splitting fails
            print(f"  Warning: Could not split query, using original topic: {str(e)}")
            return [topic]
    
    def collect_all_sources(self, queries: List[str], max_sources_per_query: int = 5) -> List[Dict[str, str]]:
        """
        Execute multiple search queries and collect all unique sources.
        
        Args:
            queries: List of search queries to execute
            max_sources_per_query: Maximum sources to retrieve per query
            
        Returns:
            Combined list of unique sources from all queries
        """
        all_sources = []
        seen_urls = set()
        
        for i, query in enumerate(queries, 1):
            print(f"  Query {i}/{len(queries)}: {query[:80]}...")
            sources = self.research_agent.search_sources(query, max_results=max_sources_per_query)
            
            # Deduplicate by URL
            for source in sources:
                url = source.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_sources.append(source)
                elif not url:  # Include sources without URLs (like Tavily summaries)
                    all_sources.append(source)
        
        return all_sources
    
    def execute_research_workflow(
        self,
        topic: str,
        requirements: str = None,
        max_sources_per_query: int = 5,
        max_query_length: int = 200
    ) -> Dict[str, str]:
        """
        Execute the complete research workflow: query splitting, research, and reflection.
        
        Args:
            topic: The research topic
            requirements: Optional requirements for the research
            max_sources_per_query: Maximum sources per search query
            max_query_length: Maximum length for a single query
            
        Returns:
            Dictionary with 'draft' and 'improved_draft' keys
        """
        print("\n[Orchestrator] Starting research workflow...")
        
        # Step 1: Split query if needed
        print("\n[1/4] Orchestrator: Analyzing request and splitting queries if needed...")
        queries = self.split_query(topic, requirements, max_query_length)
        print(f"  Generated {len(queries)} search query/queries")
        for i, q in enumerate(queries, 1):
            print(f"    {i}. {q}")
        
        # Step 2: Collect sources from all queries
        print(f"\n[2/4] Orchestrator: Collecting sources from {len(queries)} query/queries...")
        all_sources = self.collect_all_sources(queries, max_sources_per_query)
        print(f"  Collected {len(all_sources)} unique sources")
        
        # Step 3: Create draft using all sources
        print("\n[3/4] Research Agent: Creating initial draft from collected sources...")
        draft = self.research_agent.create_draft_from_sources(
            topic=topic,
            requirements=requirements,
            sources=all_sources
        )
        print("✓ Draft created successfully")
        
        # Step 4: Validate and improve draft
        print("\n[4/4] Reflection Agent: Validating and improving draft...")
        improved_draft = self.reflection_agent.validate_and_improve(
            draft=draft,
            topic=topic,
            requirements=requirements
        )
        print("✓ Draft validated and improved")
        
        return {
            'draft': draft,
            'improved_draft': improved_draft,
            'sources_count': len(all_sources),
            'queries_count': len(queries)
        }

