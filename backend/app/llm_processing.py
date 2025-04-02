import os
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from .chat_model import AzureContainerChatModel
load_dotenv()
print(f"Using Endpoint: {os.getenv('AZURE_INFERENCE_ENDPOINT')}")

os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_INFERENCE_CREDENTIAL")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_INFERENCE_ENDPOINT")

# llm = AzureChatOpenAI(
#     api_version="2023-03-15-preview",
#     azure_deployment="gpt-4o-mini"
# )

llm = AzureContainerChatModel()

def parse_docs(text, question) -> str:
    print(f"Number of characters: {format(len(text))}")
    messages = [
        SystemMessage(content="""
                        You are an AI assistant that answers questions based on the given text. 
                        The answers are provided in Markdown format with a bullet point list wherever applicable.
                        Keep the answers minimally verbose.
                      """),
        HumanMessage(content=f"Here is the text: {text}\n\nNow, answer this question: {question}"),
    ]

    result = llm.invoke(messages)
    print("Result:", result.content)
    return result.content

def parse_docs_gemma(text, question) -> str:
    print(f"Number of characters: {format(len(text))}")
    messages = [
        SystemMessage(content="""
                        You are an AI assistant that answers questions based on the given text. 
                        The answers are provided in Markdown format with a bullet point list & proper table structures 
                        wherever applicable. Don't provide very long descriptions unless required by the question.
                      """),
        HumanMessage(content=f"Here is the text: {text}\n\nNow, answer this question: {question}"),
    ]

    result = llm.invoke(messages)
    print("Result:", result.content)
    return result.content