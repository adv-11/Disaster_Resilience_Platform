
from langchain_core.tools import tool
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.tools.render import render_text_description_and_args
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_ibm import WatsonxLLM
from datetime import datetime
import nasapy
import os
from dotenv import load_dotenv
load_dotenv()
from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials

credentials = Credentials(
                   url = "https://api.au-syd.assistant.watson.cloud.ibm.com/instances/60c760f5-7751-4b31-9087-bd8f5218a54b",
                   username = "advait_shinde_comp@moderncoe.edu.in",
                   password = "2/Atomandjerry",
                   instance_id = "openshift",
                   version = "5.1",
                   bedrock_url = "https://bedrock.au-syd.assistant.watson.cloud.ibm.com"
                  )


client = APIClient(credentials)


n = nasapy.Nasa(key= os.environ.get("NASA_API_KEY"))

param = {
    "decoding_method": "greedy",
    "temperature": 0,
    "min_new_tokens": 5,
    "max_new_tokens": 250,
    "stop_sequences": ["\n\n"]
}

@tool
def get_todays_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    date = datetime.now().strftime("%Y-%m-%d")
    return date


@tool(return_direct=True)
def get_astronomy_image(date: str):
    """Get NASA's Astronomy Picture of the Day on given date. The date is formatted as YYYY-MM-DD."""
    apod = n.picture_of_the_day(date, hd=True)
    return apod['url']


tools = [get_todays_date, get_astronomy_image]

model = WatsonxLLM(

    model_id = "ibm/granite-13b-chat-v2",
    url = os.environ.get("watson_url"),
    apikey = os.environ.get("WATSON_API_KEY_2"),


    params = param
)

system_prompt = """Respond to the human as helpfully and accurately as possible. You have access to the following tools: {tools}
Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).
Valid "action" values: "Final Answer" or {tool_names}
Provide only ONE action per $JSON_BLOB, as shown:"
```
{{
  "action": $TOOL_NAME,
  "action_input": $INPUT
}}
```
Follow this format:
Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
  "action": "Final Answer",
  "action_input": "Final response to human"
}}
Begin! Reminder to ALWAYS respond with a valid json blob of a single action.
Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""

human_prompt = """{input}
{agent_scratchpad}
(reminder to always respond in a JSON blob)"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", human_prompt),
    ]
)

prompt = prompt.partial(
    tools=render_text_description_and_args(list(tools)),
    tool_names=", ".join([t.name for t in tools]),
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chain = ( RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        chat_history=lambda x: memory.chat_memory.messages,
    )
    | prompt | model | JSONAgentOutputParser()
)

agent_executor = AgentExecutor(agent=chain, tools=tools, verbose=True, memory=memory, handle_parsing_errors=True)

agent_executor.invoke({"input": "What is today's date?"})