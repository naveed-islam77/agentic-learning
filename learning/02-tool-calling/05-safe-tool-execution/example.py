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


def add_number(a, b):
    return a + b


def multiply(a, b):
    return a * b


tools = [
    {
        "type": "function",
        "function": {
            "name": "add_number",
            "description": "Do numbers ko add kr do",
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
            "name": "add_number",
            "description": "Do numbers ko add kr do",
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


def run_tool_safely(tool_name, raw_arguments):
    # first check if the tool call is allowed or not
    function_to_call = available_functions.get(tool_name)

    if function_to_call is None:
        return f"Tool error: '{tool_name}' available nahi hai."

    # convert the arguments into python dict

    try:
        arguments = json.loads(raw_arguments)
    except:
        return "Tool error: arguments valid JSON nahi hain."

    if not isinstance(arguments, dict):
        return "Tool error: arguments must be json object"

    if set(arguments.keys()) != {"a", "b"}:
        return "Tool Error : arguments must be a and b"

    for key, value in arguments.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return f"Tool error: '{key}' ki value number honi chahiye."

    try:
        return function_to_call(a=arguments["a"], b=arguments["b"])
    except Exception as error:
        print("Local tool error:", repr(error))
        return "Tool error: function execute nahi ho saki."


# ---------- User input and conversation ----------

question = input("Ask Question: ")


messages = [
    {
        "role": "system",
        "content": (
            "Math ke liye available tools use karo. "
            "Agar calculation multiple steps ki ho to har step ka result "
            "aglay step mein istemal karo. Tool error mile to usay samajh kar "
            "user ko seedha batao."
        ),
    },
    {
        "role": "user",
        "content": question,
    },
]


for round_number in range(1, MAX_TOOLS_ROUNDS + 1):
    print(f"\n--- Tool round {round_number} ---")

    response = client.chat.completions.create(
        model=model, messages=messages, tools=tools
    )

    assistant_res = response.choices[0].message

    # Tool call na ho to model ka jawab final hai
    if not assistant_res.tool_calls:
        print("AI:", assistant_res.content)
        break

    messages.append(
        {
            "role": "assistant",
            "content": assistant_res.content,
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "parameters": call.function.arguments,
                    },
                }
                for call in assistant_res.tool_calls
            ],
        }
    )

    for call in assistant_res.tool_calls:
        tool_name = call.function.name
        arguments= call.function.arguments

        result = run_tool_safely(tool_name=tool_name, raw_arguments=arguments)

        print(f"Tool: {tool_name}")
        print(f"Raw arguments: {arguments}")
        print(f"Result: {result}")

        # Success ho ya error, result model ko tool message mein wapas do
        messages.append(
            {"role": "tool", "tool_call_id": call.id, "content": str(result)}
        )

else:
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    print("\nAI ka final jawab:", final_response.choices[0].message.conten)
