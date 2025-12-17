"""Main orchestrator for the Research Agent System."""

import argparse
import os
from dotenv import load_dotenv
from agents.orchestrator_agent import OrchestratorAgent


def main():
    """Main function to orchestrate the research and reflection agents."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Research Agent System')
    parser.add_argument('--topic', type=str, required=True, help='Research topic')
    parser.add_argument('--requirements', type=str, default=None, help='Requirements for the research')
    parser.add_argument('--max-sources', type=int, default=None, help='Maximum number of sources per query (default: from TAVILY_MAX_SOURCES env var or 5)')
    parser.add_argument('--max-query-length', type=int, default=200, help='Maximum length for a single query before splitting (default: 200)')
    parser.add_argument('--output', type=str, default=None, help='Output file path (optional)')
    
    args = parser.parse_args()
    
    # Get max_sources from env if not provided via CLI
    if args.max_sources is None:
        args.max_sources = int(os.getenv('TAVILY_MAX_SOURCES', '5'))
    
    print("=" * 60)
    print("Research Agent System")
    print("=" * 60)
    print(f"\nTopic: {args.topic}")
    if args.requirements:
        print(f"Requirements: {args.requirements}")
    print("\n" + "-" * 60)
    
    try:
        # Initialize orchestrator (which manages all agents)
        print("\n[0/4] Initializing orchestrator and agents...")
        orchestrator = OrchestratorAgent()
        print("✓ Orchestrator initialized successfully")
        
        # Execute complete workflow
        results = orchestrator.execute_research_workflow(
            topic=args.topic,
            requirements=args.requirements,
            max_sources_per_query=args.max_sources,
            max_query_length=args.max_query_length
        )
        
        draft = results['draft']
        improved_draft = results['improved_draft']
        changes_summary = results.get('changes_summary', 'No changes summary available.')
        
        print("\n" + "=" * 60)
        print("\n--- Initial Draft ---")
        print(draft)
        print("\n" + "-" * 60)
        print("\n--- Final Improved Draft ---")
        print(improved_draft)
        print("\n" + "=" * 60)
        print("\n--- Changes Summary (For Review) ---")
        print(changes_summary)
        print("\n" + "=" * 60)
        print(f"\nSummary: {results['queries_count']} query/queries executed, {results['sources_count']} unique sources collected")
        
        # Save to file if output path is provided
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"Topic: {args.topic}\n")
                if args.requirements:
                    f.write(f"Requirements: {args.requirements}\n")
                f.write(f"\nQueries Executed: {results['queries_count']}\n")
                f.write(f"Sources Collected: {results['sources_count']}\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("INITIAL DRAFT\n")
                f.write("=" * 60 + "\n\n")
                f.write(draft)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("IMPROVED DRAFT\n")
                f.write("=" * 60 + "\n\n")
                f.write(improved_draft)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("CHANGES SUMMARY (FOR REVIEW)\n")
                f.write("=" * 60 + "\n\n")
                f.write(changes_summary)
            print(f"\n✓ Results saved to: {args.output}")
        
        print("\n✓ Research process completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


