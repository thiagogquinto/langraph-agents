from langchain_ollama import ChatOllama
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv

load_dotenv()

langfuse = get_client()

try:
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
except Exception as e:
    print(f"Error authenticating Langfuse client: {e}")

langfuse_handler = CallbackHandler()

llm = ChatOllama(model="gpt-oss:120b", temperature=0.1)
