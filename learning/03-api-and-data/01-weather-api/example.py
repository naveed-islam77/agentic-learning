from dotenv import load_dotenv
from openai import OpenAI
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
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


def get_weather(city):
    # Step 1: city name ko URL-safe query parameters mein badlo

    geoconding_parameters = urlencode(
        {"name": city, "count": 1, "language": "eng", "format": "json"}
    )

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search?" + geoconding_parameters
    )

    # Step 2: city ka latitude aur longitude dhoondo
    geocoding_request = Request(
        geocoding_url, headers={"User-Agent": "AgenticAILearning/1.0"}
    )

    with urlopen(geocoding_request, timeout=10) as response:
        geocoding_data = json.loads(response.read().decode("utf-8"))

    locations = geocoding_data.get("results", [])

    if not locations:
        return f"Weather error: '{city}' naam ka shehar nahi mila."

    location = locations[0]

    # Step 3: coordinates se current weather mangwao

    weather_parameters = urlencode(
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto",
        }
    )

    weather_url = (
        "https://api.open-meteo.com/v1/forecast?" + weather_parameters
    )

    weather_request = Request(
        weather_url,
        headers={"User-Agent": "AgenticAILearning/1.0"},
    )

    with urlopen(weather_request, timeout=10) as response:
        weather_data = json.loads(response.read().decode("utf-8"))

    current = weather_data["current"]
    units = weather_data["current_units"]

    # Step 4: API ke jawab ko agent ke liye readable banao
    return (
        f"City: {location['name']}, {location.get('country', '')}\n"
        f"Local time: {current['time']} "
        f"({weather_data.get('timezone', 'unknown timezone')})\n"
        f"Temperature: {current['temperature_2m']} "
        f"{units['temperature_2m']}\n"
        f"Feels like: {current['apparent_temperature']} "
        f"{units['apparent_temperature']}\n"
        f"Humidity: {current['relative_humidity_2m']} "
        f"{units['relative_humidity_2m']}\n"
        f"Wind speed: {current['wind_speed_10m']} "
        f"{units['wind_speed_10m']}\n"
        f"Weather code: {current['weather_code']}"
    )


# ---------- Tool definitions ----------

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_number",
            "description": "Add Two Numbers",
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
            "description": "multiply Two Numbers",
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
            "name": "get_weather",
            "description": (
                "Kisi shehar ka current weather API se hasil karta hai. "
                "Shehar ka naam city argument mein do."
            ),
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
]

question = input("Ask Question: ")

messages = [
    {
        "role": "system",
        "content": (
            "User ke sawal ke mutabiq available tools use karo. "
            "Agar weather poocha jaye to get_weather tool use karo. "
            "Agar shehar ka naam unclear ho to clarification mango. "
            "Weather jawab API se mile data par mabni hona chahiye."
        ),
    },
    {"role": "user", "content": question},
]


available_functions = {
    "add_number": add_number,
    "multiply": multiply,
    "get_weather": get_weather,
}

# ---------- Safe tool runner ----------


def run_tool_safely(tool_name, raw_arguments):
    tool_to_call = available_functions.get(tool_name)

    if tool_to_call is None:
        return f"Error {tool_name} is not available in available tools"

    try:
        arguments = json.loads(raw_arguments)
    except (json.JSONDecodeError, TypeError):
        return "Tool error: arguments valid JSON nahi hain."

    if not isinstance(arguments, dict):
        return "Tool error: arguments JSON object hone chahiye."

    if tool_name == "get_weather":
        if set(arguments.keys()) != {"city"}:
            return "Tool error: get_weather ko sirf 'city' argument chahiye."

        if not isinstance(arguments["city"], str):
            return "Tool error: city ka naam text hona chahiye."

        if not arguments["city"].strip():
            return "Tool error: city ka naam khali nahi ho sakta."

    else:
        if set(arguments.keys()) != {"a", "b"}:
            return "Tool error: math tools ko 'a' aur 'b' chahiye."

        for key, value in arguments.items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                return f"Tool error: '{key}' ki value number honi chahiye."

    try:
        return tool_to_call(**arguments)
    except (HTTPError, URLError, TimeoutError) as error:
        print("Local API error:", repr(error))
        return "Weather error: weather service se connection nahi ho saka."

    except Exception as error:
        print("Local tool error:", repr(error))
        return "Tool error: function execute nahi ho saki."


# ---------- Agent loop ----------

for round_numbers in range(1, MAX_TOOLS_ROUNDS + 1):

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
        tool_to_call = call.function.name
        arguments = call.function.arguments

        result = run_tool_safely(tool_name=tool_to_call, raw_arguments=arguments)

        print(f"Tool: {tool_to_call}")
        print(f"Arguments: {arguments}")
        print(f"Result:\n{result}")

        messages.append(
            {"role": "tool", "tool_call_id": call.id, "content": str(result)}
        )

else:
    final_response = client.chat.completions.create(
        model=model,
        messages=messages,
    )

    print("\nAI ka final jawab:", final_response.choices[0].message.content)
