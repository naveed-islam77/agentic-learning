from dotenv import load_dotenv
import requests
from agents import (
    Agent,
    Runner,
    function_tool,
    ModelSettings,
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


def create_agent(name, instructions, model, **kwargs) -> Agent:
    agent = Agent(
        name=name,
        instructions=instructions,
        model=model,
        **kwargs
    )
    return agent


async def generate_emails(message):
    agent1 = create_agent("Professional Sales Agent", instructions1, openrouter_model)
    agent2 = create_agent("Humorous Sales Agent", instructions2, openrouter_model)
    agent3 = create_agent("Executive Sales Agent", instructions3, openrouter_model)

    results = await asyncio.gather(
        Runner.run(agent1, message),
        Runner.run(agent2, message),
        Runner.run(agent3, message),
    )

    outputs = [result.final_output for result in results]

    emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

    return emails


async def find_best_email(emails):
    decision = """
    You pick the best cold sales email from the given options.
    Imagine you are a customer and pick the one you are most likely to respond to.
    Do not give an explanation; reply with the selected email only.
    """

    require_tool = ModelSettings(tool_choice="required")

    sales_picker = create_agent(
        "Sales_picker",
        instructions=decision,
        model=openrouter_model,
        tools=[send_email_tool],
        model_settings=require_tool,
    )

    await Runner.run(sales_picker, emails)


async def main():
    prompt = input("You :")

    emails = await generate_emails(prompt)
    await find_best_email(emails)


if __name__ == "__main__":
    asyncio.run(main())
