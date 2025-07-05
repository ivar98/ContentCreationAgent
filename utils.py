import os
import torch
import chromadb
from dotenv import load_dotenv

# --- Updated LangChain Imports ---
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch  # CORRECTED IMPORT

# Load environment variables from .env file
load_dotenv()

# --- API Key Management ---
def check_api_keys():
    """
    Checks for necessary API keys in environment variables and returns a list of missing keys.
    """
    missing_keys = []
    if "TAVILY_API_KEY" not in os.environ:
        missing_keys.append("TAVILY_API_KEY")
    if "GOOGLE_API_KEY" not in os.environ:
        missing_keys.append("GOOGLE_API_KEY")
    return missing_keys

# --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, top_p=0.85)

# --- Initialize Embedding Model ---
device = 'cuda' if torch.cuda.is_available() else 'cpu'
embedding_function = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': device}
)

# --- Initialize Vector Stores and Retrievers ---
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
except Exception as e:
    print(f"Error initializing ChromaDB client: {e}")
    chroma_client = None

if chroma_client:
    research_collection = chroma_client.get_or_create_collection(name="research_cache")
    research_vector_store = Chroma(
        client=chroma_client,
        collection_name="research_cache",
        embedding_function=embedding_function,
    )
    research_retriever = research_vector_store.as_retriever(search_kwargs={"k": 5})

    style_guide_collection = chroma_client.get_or_create_collection(name="style_guide")
    style_guide_vector_store = Chroma(
        client=chroma_client,
        collection_name="style_guide",
        embedding_function=embedding_function,
    )
    style_guide_retriever = style_guide_vector_store.as_retriever(search_kwargs={"k": 2})
else:
    research_retriever = None
    style_guide_retriever = None
    style_guide_vector_store = None


# --- Initialize External Tools ---
# Tavily Search is used for real-time web research.
tavily_tool = TavilySearch(max_results=5)  # CORRECTED INITIALIZATION