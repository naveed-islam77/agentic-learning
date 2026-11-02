from openai import OpenAI
from dotenv import load_dotenv
import os
from rich.console import Console
import json

load_dotenv()

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")
)

checklist = []
completed = []

console = Console()


def show(text):
    try:
        console.print(text)
    except Exception:
        print(text)


def get_checklist_report() -> str:
    result = ""
    for index, item in enumerate(checklist):
        if completed[index]:
            result += f"✔️ {index + 1}: [green][strike]{item}[/strike][/green]\n"
        else:
            result += f"⚪ {index + 1}: {item}\n"
    show(result)
    return result


def create_checklist(descriptions: list[str]) -> str:
    checklist.extend(descriptions)
    completed.extend([False] * len(descriptions))
    return get_checklist_report()


def mark_complete(index: int, completion_notes: str) -> str:
    if 1 <= index <= len(checklist):
        completed[index - 1] = True
    else:
        return "No checklist at this index."
    console.print(completion_notes)
    return get_checklist_report()


create_checklist_json = {
    "name": "create_checklist",
    "description": "Add new checklist from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                "type": "array",
                "items": {"type": "string"},
                "title": "Descriptions of checklist items",
            }
        },
        "required": ["descriptions"],
        "additionalProperties": False,
    },
}


mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the checklist item at the given position (starting from 1) and return the full list",
    "parameters": {
        "properties": {
            "index": {
                "description": "The 1-based index of the checklist item to mark as complete",
                "title": "Index",
                "type": "integer",
            },
            "completion_notes": {
                "description": "Notes about how you completed the checklist item in rich console markup",
                "title": "Completion Notes",
                "type": "string",
            },
        },
        "required": ["index", "completion_notes"],
        "type": "object",
        "additionalProperties": False,
    },
}


tools = [
    {"type": "function", "function": create_checklist_json},
    {"type": "function", "function": mark_complete_json},
]


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}
        results.append(
            {
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id,
            }
        )
    return results



def loop(messages):
    response = openai.chat.completions.create(model="gpt-6-luna", messages=messages, tools=tools)
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model="gpt-6-luna", messages=messages, tools=tools)
    show(response.choices[0].message.content)


user_message = input("Enter User Message: ")

system_message = """
You are given a problem to solve, by using your checklist tools to plan a list of steps, then carrying out each step in turn.
Now create a plan, set the checklist, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""


messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]





loop(messages)