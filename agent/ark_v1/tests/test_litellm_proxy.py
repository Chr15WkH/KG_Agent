import os

from langchain_litellm import ChatLiteLLM
from langchain_core.messages import HumanMessage

chat_model = ChatLiteLLM(
    model="openai/qwen3.8:27b",
    api_base="http://agiprobot.ifl.kit.edu:4000",
    api_key=os.environ["LITELLM_API_KEY"],
)

messages = [
    HumanMessage(content="Hello! How are you tracking this request?")
]

response = chat_model.invoke(messages)

print(response.content)