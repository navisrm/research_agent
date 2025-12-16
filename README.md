# Research Agent System

A simple multi-agent system for research and content creation with validation.

## Architecture

The system consists of three main components:

1. **Orchestrator Agent**: Manages the workflow, splits lengthy queries into multiple focused searches, and coordinates other agents
2. **Research Agent**: Uses Tavily search to find sources on topics and creates initial drafts with strict fact-based citations
3. **Reflection Agent**: Validates the draft, verifies all citations, removes unsupported claims, and improves the content

### Key Features

- **Query Splitting**: Automatically splits lengthy research requests into multiple focused Tavily queries
- **Source Collection**: Aggregates sources from multiple queries and deduplicates them
- **Fact-Based Content**: Strict requirement that all statements must be cited from sources
- **Citation Validation**: Reflection agent verifies that every factual claim has proper source attribution

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

   You can get your Tavily API key from: https://tavily.com/

## Usage

Basic usage:
```bash
python main.py --topic "Your research topic" --requirements "Your specific requirements"
```

With custom number of sources per query:
```bash
python main.py --topic "Your research topic" --requirements "Your requirements" --max-sources 10
```

Customize query splitting threshold:
```bash
python main.py --topic "Your research topic" --max-query-length 150
```

Save output to file:
```bash
python main.py --topic "Your research topic" --output research_output.txt
```

### How Query Splitting Works

When a research request is too lengthy (exceeds `--max-query-length`), the orchestrator:
1. Analyzes the request using an LLM
2. Splits it into 2-5 focused, searchable queries
3. Executes each query via Tavily
4. Collects and deduplicates all sources
5. Passes all sources to the Research Agent for draft creation

## Project Structure

```
research_agent/
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py  # Orchestrator that manages workflow and query splitting
│   ├── research_agent.py      # Agent for research and draft creation
│   └── reflection_agent.py    # Agent for validation and improvement
├── main.py                     # Main entry point
├── requirements.txt
├── .env.example
└── README.md
```


