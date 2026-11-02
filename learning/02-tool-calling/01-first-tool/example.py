from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]
)


def get_current_time():
    return datetime.now().strftime("%I:%M %p")


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Computer ka current local time batata hai.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": "Agar user current time poochay, get_current_time tool istemal karo.",
    },
    {
        "role": "user",
        "content": input("Ask Anything: "),
    },
]

first = client.chat.completions.create(
    model="openai/gpt-6-luna",
    messages=messages,
    tools=tools,
)

assistant_message = first.choices[0].message

print("AI ne tool manga?", bool(assistant_message.tool_calls))
for call in assistant_message.tool_calls or []:
    print("Tool ka naam:", call.function.name)
    print("Tool ke inputs:", call.function.arguments)

if assistant_message.tool_calls:
    messages.append(
        {
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in assistant_message.tool_calls
            ],
        }
    )

    for call in assistant_message.tool_calls:
        if call.function.name == "get_current_time":
            result = get_current_time()
            print(f"Python Tool Chala {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                }
            )

    final = client.chat.completions.create(model="gpt-6-luna", messages=messages)
    print("AI:", final.choices[0].message.content)

else:
    print("AI:", assistant_message.content)
