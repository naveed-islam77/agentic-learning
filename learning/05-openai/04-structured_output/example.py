from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    OpenAIChatCompletionsModel,
    output_guardrail,
    GuardrailFunctionOutput,
)
import os
from pydantic import BaseModel, Field
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


class EmailReview(BaseModel):
    is_professional: bool = Field(
        description="Whether the email is professional and appropriate"
    )
    number_of_sentences: int = Field(
        description="The number of sentences in the body of the email, not including the greeting and signature"
    )
    contains_placeholders: bool = Field(
        description="Whether the email contains placeholders for personalization"
    )


EmailReview.model_json_schema()

email = """
Hi [first_name],

I'm hitting you up to see if you'd like to buy our product. It's really great. You'll miss out if you don't buy it.

Laters.

Naveed
"""


def email_checker(review: EmailReview):
    if not review.is_professional or review.contains_placeholders:
        return "The email is not professional or has placeholders and will not be sent"
    else:
        return "Email is good"


async def main():
    checker = Agent(
        name="Checker",
        instructions="You review potential sales emails",
        model=gpt_luna_model,
        output_type=EmailReview,
    )
    result = await Runner.run(checker, email)
    review = result.final_output
    email_checker_result = email_checker(review)
    print(email_checker_result)


if __name__ == "__main__":
    asyncio.run(main())
