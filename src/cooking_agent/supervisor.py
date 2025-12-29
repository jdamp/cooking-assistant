"""Supervisor agent that orchestrates Mealie and Bring agents."""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from cooking_agent.config import get_settings
from cooking_agent.mealie.agent import mealie_recipes
from cooking_agent.bring.agent import bring_shopping


SUPERVISOR_SYSTEM_PROMPT = """You are a cooking assistant supervisor that coordinates between recipe management and shopping list operations.

You manage two specialized agents:
1. **mealie** - Handles recipe search, viewing recipe details, and getting ingredients
2. **bring** - Handles shopping list management (viewing lists, adding items)

For each user request, decide which agent(s) should handle it:
- Recipe questions → mealie
- Shopping list questions → bring  
- "Add recipe ingredients to shopping list" → First mealie (get ingredients), then bring (add to list)

After delegating to agents, synthesize their responses for the user.

IMPORTANT: For multi-step tasks (like adding recipe ingredients to a shopping list):
1. First route to mealie to get the ingredients
2. Then route to bring to add them to the list
3. Finally, provide a summary to the user"""

def create_supervisor_agent():
    llm = init_chat_model(model=get_settings().model_name, api_key=get_settings().openai_api_key)
    supervisor_agent = create_agent(
        llm,
        tools=[
            mealie_recipes,
            bring_shopping,
        ],
        system_prompt=SUPERVISOR_SYSTEM_PROMPT,
    )
    return supervisor_agent
