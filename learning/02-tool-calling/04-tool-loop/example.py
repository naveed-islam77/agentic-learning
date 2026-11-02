from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]
)

MAX_TOOLS_ROUNDS = 4
model = "gpt-6-luna"

# --- Pyhton Tools -------


def add_number(a, b):
    return a + b


def multiply(a, b):
    return a * b


# ---- Tool --------

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_number",
            "description": "Do numbers ko add karta hai.",
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
            "name": "multiply",
            "description": "Do numbers ko multiply karta hai.",
            "parameters": {
                "type": "object",
                "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                "required": ["a", "b"],
            },
        },
    },
]


available_functions = {
    "add_number": add_number,
    "multiply": multiply,
}

question = input("Ask Question: ")

messages = [
    {
        "role": "system",
        "content": (
            "Math ke liye available tools use karo. "
            "Agar calculation multiple steps ki ho to har step ka result "
            "aglay step mein istemal karo."
        ),
    },
    {"role": "user", "content": question},
]


# ---------- Agent Loop ------------

for round_number in range(1, MAX_TOOLS_ROUNDS + 1):
    print(f"\n--- Tool round {round_number} ---")

    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools
    )

    assistant_message = response.choices[0].message

    if not assistant_message.tool_calls:
        print("AI:", assistant_message.content)
        break

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
        tool_name = call.function.name

        # convert the json string to pthon dict
        arguments = json.loads(call.function.arguments)

        # find the function name according to tool name

        function_to_call = available_functions.get(tool_name)

        if function_to_call is None:
            result = f"Error: '{tool_name}' name is not available in tools"
        else:
            result = function_to_call(**arguments)

        print(f"Python tool chala: {tool_name}")
        print(f"Arguments: {arguments} → Result: {result}")

        messages.append(
            {"role": "tool", "tool_call_id": call.id, "content": str(result)}
        )
else:
    final_response = client.chat.completions.create(model=model, messages=messages)

    print("\nAI ka final jawab:", final_response.choices[0].message.content)
