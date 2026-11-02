from dotenv import load_dotenv
from openai import OpenAI
import os
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]
)

question = input("Ask Anything: ")


def add_numbers(a, b):
    return a + b


def multiply_numbers(a, b):
    return a * b


tools = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Do Numbers ko add krna ha",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Do Numbers ko multiply krna ha",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    },
]

messages = [
    {
        "role": "system",
        "content": "Jama karne ke liye add_numbers aur multiply karne ke liye multiply_numbers tool istemal karo.",
    },
    {"role": "user", "content": question},
]

first = client.chat.completions.create(
    model="gpt-6-luna", tools=tools, messages=messages
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
                        "parameters": call.function.arguments,
                    },
                }
                for call in assistant_message.tool_calls
            ],
        }
    )

    for call in assistant_message.tool_calls:
        if call.function.name in ("add_numbers", "multiply_numbers"):
            args = json.loads(call.function.arguments)

            if call.function.name == "add_numbers":
                result = add_numbers(args["a"], args["b"])
            if call.function.name == "multiply_numbers":
                result = multiply_numbers(args["a"], args["b"])

            print("Python ne yeh tool chalaya:", call.function.name)
            print("Inputs:", args, "→ Result:", result)

            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": str(result)}
            )

    final = client.chat.completions.create(model="gpt-6-luna", messages=messages)
    print("AI:", final.choices[0].message.content)

else:
    print("AI:", assistant_message.content)
