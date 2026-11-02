from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"]
)


messages = [{"role": "system", "content": "Hamesha simple Roman Urdu mein jawab do."}]

while True:
    question = input("Ask Anything: ")

    if question.lower() == "exit":
        break
    if not question:
        continue

    messages.append({"role": "user", "content": question})

    res = client.chat.completions.create(model="gpt-6-luna", messages=messages)

    print(messages)

    print(res.choices[0].message.content)
