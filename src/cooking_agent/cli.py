"""Interactive CLI for the cooking agent."""

import asyncio

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from cooking_agent.agents import create_supervisor_agent


console = Console()


def print_welcome() -> None:
    """Print welcome message."""
    console.print(
        Panel.fit(
            "[bold green]🍳 Cooking Agent[/bold green]\n"
            "[dim]Multi-agent assistant for recipes and shopping lists[/dim]\n\n"
            "Commands:\n"
            "  [cyan]quit[/cyan] or [cyan]exit[/cyan] - Exit the agent\n"
            "  [cyan]help[/cyan] - Show example prompts\n",
            title="Welcome",
            border_style="green",
        )
    )


def print_help() -> None:
    """Print help with example prompts."""
    console.print(
        Panel(
            "[bold]Example prompts:[/bold]\n\n"
            "📖 [cyan]Search for pasta recipes[/cyan]\n"
            "📖 [cyan]Show me the details for [recipe-slug][/cyan]\n"
            "📖 [cyan]What ingredients do I need for [recipe]?[/cyan]\n\n"
            "🛒 [cyan]Show my shopping lists[/cyan]\n"
            "🛒 [cyan]What's on my [list-name] list?[/cyan]\n"
            "🛒 [cyan]Add milk and eggs to my shopping list[/cyan]\n\n"
            "🔗 [cyan]Find a chicken recipe and add ingredients to my list[/cyan]",
            title="Help",
            border_style="blue",
        )
    )


async def run_agent_async(user_input: str, agent) -> str:
    """Run the agent with user input asynchronously.

    Args:
        user_input: The user's message
        agent: The supervisor agent

    Returns:
        The agent's response
    """
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )
    
    # Get the final message from the agent
    return result["messages"][-1].text


def run_cli() -> None:
    """Run the interactive CLI loop."""
    print_welcome()

    try:
        agent = create_supervisor_agent()
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        console.print("[dim]Make sure your .env file is configured correctly.[/dim]")
        return

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye! 👋[/dim]")
                break

            if user_input.lower() == "help":
                print_help()
                continue

            with console.status("[bold blue]Thinking...[/bold blue]"):
                response = asyncio.run(run_agent_async(user_input, agent))

            console.print()
            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'quit' to exit.[/dim]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    run_cli()
