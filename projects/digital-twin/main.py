import gradio as gr
from twin_lab import tools
from twin_lab import config, prompts


def chat(message, history):
    messages = (
        [{"role": "system", "content": prompts.system_prompt}]
        + history
        + [{"role": "user", "content": message}]
    )
    response = config.openai.chat.completions.create(
        model="gpt-6-luna", messages=messages, tools=prompts.tools
    )
    while response.choices[0].finish_reason == "tool_calls":
        message = response.choices[0].message
        tool_calls = message.tool_calls
        results = tools.handle_tool_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = config.openai.chat.completions.create(
            model="gpt-6-luna", messages=messages, tools=prompts.tools
        )
    return response.choices[0].message.content


gr.ChatInterface(chat).launch(inbrowser=True)
