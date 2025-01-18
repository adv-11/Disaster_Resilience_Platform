from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
client = TavilyClient(api_key=TAVILY_API_KEY)

response = client.search("What is the weather in New delhi?")

print(response)