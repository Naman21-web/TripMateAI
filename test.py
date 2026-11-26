# from tools.tavily_tool import tavily_search
# from tools.flight_tool import search_flights
# from backend import run_travel_agent

# res = tavily_search("Best hotels in India")
# print(res)

# res = search_flights("Plan a 7 days Japan trip from India")
# print(res)

# user_input = "Enter Travel Request: " 
# res = run_travel_agent(
#     user_input=user_input,
#     thread_id="test_user"
# )
# print(res)

# import asyncio
# from mcp_client_test import get_all_tools,tavily_mcp_search

# if __name__ == "__main__":
#     # asyncio.run(get_all_tools())
#     asyncio.run(tavily_mcp_search("Who won Fifa wc 2026"))

import asyncio
from mcp_client import get_all_tools

if __name__ == "__main__":
    asyncio.run(get_all_tools())