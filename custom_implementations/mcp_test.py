import asyncio
from pathlib import Path

from agents.agent import Agent
from agents.mcp import MCPServerStdio
from agents.run import Runner

from llm.deepseek_client import deepseek_model


async def test_custom_mcp():
    project_root = Path(__file__).resolve().parent.parent

    params = {
        "command": "uv",
        "args": ["--directory", str(project_root), "run", "python", "-m", "custom_implementations.custom_mcp_server"]
    }
    async with MCPServerStdio(params=params) as server:
        tools = await server.session.list_tools()
    print(tools)


async def run_agent_with_custom_mcp():
    prompt = """
    You browse the datasource directory and available PDF documents to accomplish your instructions.
    You are highly capable at reading the PDF documents independently to accomplish your task
    Be persistent until you have solved your assignment,
    trying different options and tools as needed.
    Utilize tools to get detailed information from available data sources.
    """
    project_root = Path(__file__).resolve().parent.parent

    params = {
        "command": "uv",
        "args": ["--directory", str(project_root), "run", "python", "-m", "custom_implementations.custom_mcp_server"]
    }
    async with MCPServerStdio(params=params) as custom_mcp_server:
            agent = Agent(
                        name="Personal Document Reader",
                        instructions=prompt,
                        model=deepseek_model,
                mcp_servers=[custom_mcp_server]
                )
            result = await Runner.run(agent,
                                      "Summarize the fourht page of C vs Kotlin.")
            print(result.final_output)

if __name__ == "__main__":
    asyncio.run(run_agent_with_custom_mcp())
