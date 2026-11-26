import os
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
mcp = FastMCP("Weather MCP Server")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def _request_json(url: str, params: dict[str, str]) -> dict[str, Any]:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_current_weather(city: str):
    data = _request_json(
        "https://api.openweathermap.org/data/2.5/weather",
        {
            "q": city,
            "appid": OPENWEATHER_API_KEY or "",
            "units": "metric"
        }
    )

    return {
        "city": data["name"],
        "temperature_c": data["main"]["temp"],
        "feels_like_c": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }


@mcp.tool()
def get_forecast(
    city: str,
) -> dict[str, Any]:
    """
    Return the first five three-hour
    forecast entries for a city.
    """

    city = city.strip()

    if not city:
        raise ValueError(
            "city cannot be empty"
        )

    data = _request_json(
        "https://api.openweathermap.org/data/2.5/forecast",
        {
            "q": city,
            "appid": OPENWEATHER_API_KEY or "",
            "units": "metric",
        },
    )

    forecast = [
        {
            "datetime": item["dt_txt"],
            "temperature_c": item["main"]["temp"],
            "condition": item["weather"][0]["description"],
        }
        for item in data.get("list", [])[:5]
    ]

    return {
        "city": data.get(
            "city",
            {},
        ).get(
            "name",
            city,
        ),
        "forecast": forecast,
    }

if __name__ == "__main__":
    # mcp_client.py launches this as a stdio subprocess.
    mcp.run(
        transport="stdio",
    )