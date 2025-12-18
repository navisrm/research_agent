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

3. Create a `.env` file with your API keys (see `.env.example` for template):
```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o                    # Optional: OpenAI model to use (default: gpt-4o)
TAVILY_API_KEY=your_tavily_api_key_here
TAVILY_MAX_SOURCES=5                    # Optional: Max sources per query (default: 5)
SECRET_KEY=your-secret-key-here         # Required: Secret key for JWT tokens (use a strong random string)
ADMIN_USERNAME=admin                     # Optional: Admin panel username (default: admin)
ADMIN_PASSWORD=admin                     # Optional: Admin panel password (default: admin)

# Optional: OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
FACEBOOK_CLIENT_ID=your_facebook_client_id
FACEBOOK_CLIENT_SECRET=your_facebook_client_secret
```

   You can get your Tavily API key from: https://tavily.com/
   
   **Note**: The `OPENAI_MODEL` and `TAVILY_MAX_SOURCES` are optional and will use defaults if not set.
   
   **OAuth Setup** (Optional):
   - **Google OAuth**: 
     1. Go to [Google Cloud Console](https://console.cloud.google.com/)
     2. Create a new project or select existing one
     3. Enable Google+ API
     4. Create OAuth 2.0 credentials
     5. Add authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
     6. Copy Client ID and Client Secret to `.env`
   
   - **Facebook OAuth**:
     1. Go to [Facebook Developers](https://developers.facebook.com/)
     2. Create a new app
     3. Add Facebook Login product
     4. Set Valid OAuth Redirect URIs: `http://localhost:8000/api/auth/facebook/callback`
     5. Copy App ID and App Secret to `.env`

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

## Web Application

The system includes a FastAPI web application with a modern, user-friendly interface.

### Starting the Web Server

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start the FastAPI server
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then open your browser and navigate to: `http://localhost:8000`

### Database Admin Panel

The application includes a web-based database admin interface powered by SQLAdmin.

**Access the admin panel:**
- URL: `http://localhost:8000/admin`
- Default credentials (set in `.env`):
  - Username: `admin` (or set `ADMIN_USERNAME` in `.env`)
  - Password: `admin` (or set `ADMIN_PASSWORD` in `.env`)

**Features:**
- View and manage users
- View and manage research history
- Search and filter records
- Edit and delete records
- View detailed information

**Security Note:** Change the default admin credentials in production by setting `ADMIN_USERNAME` and `ADMIN_PASSWORD` in your `.env` file.

### Web App Features

- **Modern UI**: Clean, responsive interface with gradient design
- **Real-time Processing**: Shows loading indicator during research
- **Results Display**: Shows initial draft, improved draft, and changes summary
- **Download Options**: Download results as:
  - Markdown (`.md`) file
  - Word Document (`.docx`) file
- **Statistics**: Displays queries executed and sources collected

## Project Structure

```
research_agent/
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py  # Orchestrator that manages workflow and query splitting
│   ├── research_agent.py      # Agent for research and draft creation
│   └── reflection_agent.py   # Agent for validation and improvement
├── templates/
│   └── index.html             # Web application UI
├── static/                     # Static files directory
├── downloads/                  # Generated research files
├── app.py                     # FastAPI web application
├── main.py                     # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```


