import os
import pinecone
from dotenv import load_dotenv

load_dotenv()

# 🔐 Initialize Pinecone with your secret API key and environment (from Pinecone dashboard
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT")
)

# 🧠 Connect to the specific index you created (e.g., "dream-info")
index = pinecone.Index(os.getenv("PINECONE_INDEX_NAME"))


def upsert_embedding(id: str, embedding: list[float], metadata: dict):
    """
    Adds (or updates) a record in the vector index.

    Args:
        id (str): A unique identifier for the vector (e.g., dream_id or doc_id)
        embedding (list[float]): A list (array) that contains only floating-point numbers. The actual vector representation (1536-dim for OpenAI)
        metadata (dict): Extra info you want to attach for filtering (e.g., user_id, emotion)
    """
    index.upsert([id, embedding, metadata])


def query_embedding(vector: list[float], top_k=5):
    """
    Searches the index for the closest vectors to the input vector.

    Args:
        vector (list[float]): The query embedding (usually from user input or dream)
        top_k (int): Number of similar results to return

    Returns:
        dict: List of top matching vectors + metadata
    """
    return index.query(vector=vector, top_k=top_k, include_metadata=True)
