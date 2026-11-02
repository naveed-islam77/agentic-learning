from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    function_tool,
    OpenAIChatCompletionsModel,
)
from agents.extensions.visualization import draw_graph
from openai.types.responses import ResponseTextDeltaEvent
from openai import AsyncOpenAI
import os
import asyncio
import smtplib
from email.message import EmailMessage

load_dotenv(override=True)


openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

if openrouter_api_key == "":
    raise Exception("Api Key Not Found")
else:
    print("Api key found!")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
openrouter_client = AsyncOpenAI(
    base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key
)
openrouter_model = OpenAIChatCompletionsModel(
    model="gpt-6-luna", openai_client=openrouter_client
)


EMAIL_ADDRESS = os.getenv("USER_GMAIL")
EMAIL_SMTP_SERVER = os.getenv("GOOGLE_SMTP")
EMAIL_APP_PASSWORD = os.getenv("GOOGLE_APP_PASSWORD")

if EMAIL_ADDRESS:
    print("Email address is set")
else:
    print("Email address is not set")

if EMAIL_SMTP_SERVER:
    print("SMTP server is set")
else:
    print("SMTP server is not set")

if EMAIL_APP_PASSWORD:
    print("App password is set")
else:
    print("App password is not set")

USE_EMAIL = EMAIL_ADDRESS and EMAIL_SMTP_SERVER and EMAIL_APP_PASSWORD

if USE_EMAIL:
    print("Email is set up and we will try using it")
else:
    print("Email is not set up; we will send push notifications instead")


intro = """
You are a sales agent working for TradeLenzAI,
a company that provides a SaaS tool for Journal the trades and find the best pattern in their trades, powered by AI.
You write emails.
"""

instructions1 = (
    intro + "Your email style is professional, serious, with gravitas and credibility."
)
instructions2 = intro + "Your email style is witty, engaging, and humorous."
instructions3 = (
    intro
    + "Your email style is concise, to the point, in the style of a busy senior executive."
)


def send_email(subject, text_body, html_body):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg=msg)


@function_tool
def send_email_tool(subject: str, text_body: str, html_body: str) -> str:
    """
    Send out an email with the given subject and body to all sales prospects

    Args:
        subject: The subject of the email
        text_body: The body of the email as plain text
        html_body: The HTML body of the email
    """
    send_email(subject, text_body, html_body)
    return "Email sent successfully"


def create_agent(name, instructions, model, **kwargs) -> Agent:
    agent = Agent(name=name, instructions=instructions, model=model, **kwargs)
    return agent


def create_tool(name: str, agent: Agent):
    description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

    tool = agent.as_tool(tool_name=name, tool_description=description)

    return tool


def generate_tools():
    agent1 = create_agent(
        "Professional Sales Agent", instructions=instructions1, model=openrouter_model
    )
    agent2 = create_agent(
        "Humorous Sales Agent", instructions=instructions2, model=openrouter_model
    )
    agent3 = create_agent(
        "Executive Sales Agent", instructions=instructions3, model=openrouter_model
    )

    tool1 = create_tool("sales_email_writer_1", agent=agent1)
    tool2 = create_tool("sales_email_writer_2", agent=agent2)
    tool3 = create_tool("sales_email_writer_3", agent=agent3)

    tools = [tool1, tool2, tool3, send_email_tool]

    return tools


instructions = """
You are a Sales Manager at TradeLenz. Your goal is to find the single best cold sales email using the sales_writer tools.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.
"""


def create_sales_manager_agent():
    tools = generate_tools()

    sales_manager = Agent(
        name="Sales Manager",
        instructions=instructions,
        tools=tools,
        model=openrouter_model,
    )

    return sales_manager


async def main():
    sales_manager_agent = create_sales_manager_agent()

    await Runner.run(sales_manager_agent, task)


if __name__ == "__main__":
    asyncio.run(main())
