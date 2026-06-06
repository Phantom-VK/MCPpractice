import asyncio
import os

from agents import Agent, Runner, trace, OpenAIChatCompletionsModel
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
from mcp.shared.exceptions import McpError
from openai import AsyncOpenAI

load_dotenv()

async def get_fetch_server_tools():
    fetch_params = {"command": "uv", "args": ["tool", "run", "mcp-server-fetch"]}
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=30) as server:
        fetch_tools = await server.session.list_tools()
        fetch_prompts = await server.session.list_prompts()

    print(fetch_tools.tools)
    print(fetch_prompts.prompts)


async def get_playwright_tools():
    fetch_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=30) as server:
        fetch_tools = await server.session.list_tools()
        try:
            fetch_prompts = await server.session.list_prompts()
        except McpError:
            fetch_prompts = None

    for tool in fetch_tools.tools:
        print(tool.model_dump())
    print(fetch_prompts.prompts if fetch_prompts else "This server does not expose prompts.")

async def get_sandbox_tools():
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox")) # Create this directory manually
    files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.session.list_tools()

    for tool in fetch_tools.tools:
        print(tool.model_dump())


# This is specially for Deepseek, we are wrapping deepseek client using AsyncOpenaAI first and then passing as a model.
async def run_agent_with_mcp():
    prompt = """
    You browse the internet to accomplish your instructions.
    You are highly capable at browsing the internet independently to accomplish your task, 
    including accepting all cookies and clicking 'not now' as
    appropriate to get to the content you need. If one website isn't fruitful, try another. 
    Be persistent until you have solved your assignment,
    trying different options and sites as needed.
    When you need to write files, you do that inside the sandbox folder only.
    """
    playwright_params = {"command": "npx", "args": ["@playwright/mcp@latest"]}
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))  # Create this directory manually
    files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as sandbox_server:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=30) as playwright_server:
            deepseek_model = OpenAIChatCompletionsModel(
                    model="deepseek-v4-pro",
                    openai_client= AsyncOpenAI(
                        api_key=os.environ.get("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1"
                    )
                )
            agent = Agent(
                        name="Pro DeepSeek Agent",
                        instructions=prompt,
                        model=deepseek_model,
                mcp_servers=[sandbox_server, playwright_server]
                )
            result = await Runner.run(agent,
                                      "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md")
            print(result.final_output)



if __name__ == "__main__":
    asyncio.run(run_agent_with_mcp())
