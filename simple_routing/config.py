from langchain_ollama import ChatOllama
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Langfuse client
langfuse = get_client()

try:
    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
except Exception as e:
    print(f"Error authenticating Langfuse client: {e}")

# Initialize Langfuse CallbackHandler for Langchain (tracing)
langfuse_handler = CallbackHandler()

llm = ChatOllama(model="gpt-oss:120b", reasoning="low")