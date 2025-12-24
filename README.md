# Cooking Agent

A multi-agent cooking assistant built with LangChain/LangGraph that integrates with Mealie (recipe management) and Bring (shopping lists).

## Setup

### 1. Start Mealie (Local Development)

```bash
docker compose up -d
```

Then open http://localhost:9925, create an account, and generate an API token from User Profile → API Tokens.

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Install Dependencies

```bash
uv sync
```

## Usage

```bash
uv run -m cooking_agent
```

### Example Prompts

- "Search for pasta recipes"
- "What ingredients do I need for [recipe name]?"
- "Add the ingredients from [recipe] to my shopping list"
- "Show my shopping lists"

## Architecture

The system uses a multi-agent architecture:

- **Supervisor Agent**: Routes requests to specialized agents
- **Mealie Agent**: Handles recipe search, details, and ingredient extraction
- **Bring Agent**: Manages shopping list operations
