import os
import requests
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession, OpenAIChatCompletionsModel
load_dotenv(override=True)
import asyncio

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if openrouter_api_key == "":
    raise Exception("Api Key Not Found")
else:
    print("Api key found!")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
openrouter_client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key)
openrouter_model = OpenAIChatCompletionsModel(model="gpt-6-luna", openai_client=openrouter_client)


# agent = Agent(name="Jokester", instructions="You are a joke teller", model=openrouter_model)





# Run Agent with asyncio ☑️

# async def main():
#     result = await Runner.run(agent, "Tell a joke about Autonomous AI Agents")

#     print(result.final_output)


# asyncio.run(main())


# Run agent with streaming ☑️

# async def main():
#     result = Runner.run_streamed(agent, "Please tell me 5 jokes about AI Agents.")

#     async for event in result.stream_events():
#         if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
#             print(event.data.delta, end="", flush=True)


# asyncio.run(main())


# Used model_tool to push notification  ☑️

# pushover_user = os.getenv("PUSHOVER_USER")
# pushover_token = os.getenv("PUSHOVER_TOKEN")
# pushover_url = "https://api.pushover.net/1/messages.json"


# if pushover_user:
#     if pushover_user.startswith("u"):
#         print("Pushover user found and looks good")
#     else:
#         print("Pushover user found but doesn't start with u")
# else:
#     print("Pushover user not found")

# if pushover_token:
#     if pushover_token.startswith("a"):
#         print("Pushover token found and looks good")
#     else:
#         print("Pushover token found but doesn't start with a")
# else:
#     print("Pushover token not found")



# @function_tool
# def push_tool(message: str) -> str:
#     """ Send the given message to the user as a push notification """
#     payload = {"user": pushover_user, "token": pushover_token, "message": message}
#     result = requests.post(pushover_url, data=payload).status_code
#     return f"Push sent with API status code {result}"



# async def main():
#     notifier = Agent(name="Notifier", model=openrouter_model, instructions="Notify Users upon requirement", tools=[push_tool])

#     await Runner.run(notifier, "Pizza has arrived. Please notify the user")


# asyncio.run(main())


# Memory ☑️

def get_session(id: str):
    session = SQLiteSession(id)
    return session

def create_agent() -> Agent:
    agent = Agent(name="Assistant", instructions="You are personal Asistant", model=openrouter_model)
    return agent

async def run_agent(sessionId):
    agent = create_agent()
    session = get_session(sessionId)

    while True:
        prompt = input("You: ")

        if prompt.lower() in ["exit", "quit"]:
            print("Bye!")
            break

        response = await Runner.run(agent, prompt, session=session)
        print("Agent:", response.final_output)


asyncio.run(run_agent("234"))