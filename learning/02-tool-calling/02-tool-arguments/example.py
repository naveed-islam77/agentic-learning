from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import os
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]
)


def add_numbers(a, b):
    return a + b


tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Do Numbers ko jama krta ha",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": "Jab user do numbers jama karne ko kahe, add_numbers tool istemal karo.",
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
        if call.function.name == "add_numbers":
            args = json.loads(call.function.arguments)
            result = add_numbers(args["a"], args["b"])
            print("Python tool chala:", args, "→", result)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    final = client.chat.completions.create(model="gpt-6-luna", messages=messages)
    print("AI:", final.choices[0].message.content)

else:
    print("AI:", assistant_message.content)
