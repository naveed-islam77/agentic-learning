from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader 
from IPython.display import Markdown, display
import json 
import os 
import gradio as gr


load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

RESOURCES = Path(__file__).resolve().parents[3] / "resources"
reader = PdfReader(RESOURCES / "Profile.pdf")

linkedin = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text


with open(RESOURCES / "summry.txt", "r", encoding="utf-8") as f:
    summary = f.read()


# messages = [
#     {"role": "system", "content": "You are a snarky, witty assistant"},
#     {"role": "user", "content": "Hi, my name is Naveed Islam"}
# ]

# messages = [
#     {"role": "system", "content": "You are a snarky, witty assistant"},
#     {"role": "user", "content": "What's my name?"}
# ]

# messages = [
#     {"role": "system", "content": "You are a snarky, witty assistant"},
#     {"role": "user", "content": "Hi, my name is Ed"},
#     {"role": "assistant", "content": "Well hi there, Ed. It's nice to meet you."},
#     {"role": "user", "content": "What's my name?"}
# ]

# response = client.chat.completions.create(model="gpt-6-luna", messages=messages)
# print(response.choices[0].message.content)



system_prompt = f"""

# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's LinkedIn profile so that you can answer questions:

{linkedin}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
"""


# display(Markdown(system_prompt))


# messages = [
#     {"role": "system", "content": system_prompt},
#     {"role": "user", "content": "Hi - please tell me about yourself"},
# ]


# response = client.chat.completions.create(model="gpt-6-luna", messages=messages)
# display(response.choices[0].message.content)

def record_email_tool(email):
    print("Tool Call", email)
    with open("emails.txt", "a") as file:
        file.write(email + "\n")
    return "Email Recieved"


tool = {
    "name": "record_email_tool",
    "description": "call this function to save the emails in file",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Email Type"}
        },
        "required": ["email"]
    }
}

tools = [{"type": "function", "function": tool}]


def chat(message, history):
    
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = client.chat.completions.create(model="gpt-6-luna", messages=messages, tools=tools)

    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        messages.append(message)
        for tool_call in message.tool_calls:
            email = json.load(tool_call.function.arguments).get("email")
            record_email_tool(email=email)
            messages.append({"role": "tool", "content": "Email recorded", "tool_call_id": tool_call.id})
        response = client.chat.completions.create(model="gpt-6-luna", messages=messages, tools=tools)

    return response.choices[0].message.content


gr.ChatInterface(chat).launch(inbrowser=True)