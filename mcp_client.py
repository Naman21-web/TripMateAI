import os
import asyncio
import sys
from pathlib import Path
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUEST_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
UVX_EXECUTABLE = Path(sys.executable).with_name("uvx.exe" if os.name == "nt" else "uvx")
WEATHER_SERVER = Path(__file__).with_name("custom_weather_mcp_server.py").resolve()

if not UVX_EXECUTABLE.is_file():
    raise FileNotFoundError(
        f"uvx executable not found at {UVX_EXECUTABLE}. "
        f"Install project requirements with '{sys.executable} -m pip install -r requirements.txt'."
    )

#LLM
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    api_key=GROQ_API_KEY,
    max_tokens=1536,
)

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",#STDIO for local MCP server
            "url": f"https://mcp.tavily.com/mcp?tavilyApiKey={TAVILY_API_KEY}"
        },
        "aviationstack": {
            "transport": "stdio",
            "command": str(UVX_EXECUTABLE),
            "args": [
                "aviationstack-mcp"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATIONSTACK_API_KEY
            }
        },
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(WEATHER_SERVER)],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)

# async def get_all_tools():
#     tools = await client.get_tools()
#     print("Available MCP Tools: ")
#     for tool in tools:
#         print(tool.name)
#     return tools

search_tool = None
aviation_tools = {}

async def initialize_mcp():
    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("Available tools: ")

    for tool in tools:
        print(tool.name)

    search_tool = next(
        tool
        for tool in tools
        if tool.name == "tavily_search"
    )        

    aviation_tools = {
        tool.name: tool 
        for tool in tools
        if tool.name != "tavily_search"
    }

#used to call tavily_search_tool with query
async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke({
        "query": query
    })  
    # print(result)
    return result 

async def aviation_mcp_call(
        tool_name: str,
        tool_args: dict = None
):
    tools = await client.get_tools()

    tool = next(
        t for t in tools
        if t.name == tool_name 
    )

    result = await tool.ainvoke(
        tool_args or {}
    )

    return result

# Waether Tools 
weather_tool = None
forecast_tool = None

async def initialize_weather_tools():
    global weather_tool, forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(
        t for t in tools
        if t.name == "get_current_weather"
    )

    forecast_tool = next(
        t for t in tools
        if t.name == "get_forecast"
    )

async def weather_mcp_search(city:str):
    await initialize_weather_tools()

    return await weather_tool.ainvoke(
        {
            "city": city
        }
    )

async def forecast_mcp_search(city: str):
    await initialize_weather_tools()
    return await forecast_tool.ainvoke(
        {
            "city":city
        }
    )

# Destination Extractor
def extract_destination(query: str):
    prompt = f"""
        Extract only the destination city or country.

        Query:
        {query}

        Return only destination name.
    """ 

    response = llm.invoke(prompt)
    return response.content.strip()

# MCP_CLIENT 
# MCP_SERVER
# Tools
# API