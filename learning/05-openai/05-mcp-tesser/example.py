from agents.mcp import MCPServerStreamableHttp
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
)
import asyncio

load_dotenv(override=True)

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if openrouter_api_key:
    print(f"OpenRouter API Key exists and begins {openrouter_api_key[:6]}")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
openrouter_client = AsyncOpenAI(
    base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key
)

gpt_luna_model = OpenAIChatCompletionsModel(
    model="gpt-6-luna", openai_client=openrouter_client
)



async def main():
    user_input = input("Ask :")

    params = {"url": "https://mcp.context7.com/mcp", "timeout": 60}

    async with MCPServerStreamableHttp(name="Context7", params=params) as mcp_server:

        agent = Agent(
            "Expert",
            instructions=(
                "Answer the questions with proper guidance. Use the connected MCP"
                " tools to look up technical references or library docs when"
                " needed."
            ),
            model=gpt_luna_model,
            mcp_servers=[mcp_server],
        )

        result = await Runner.run(agent, user_input)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
