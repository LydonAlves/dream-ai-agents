import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 📌 Model to use — this is the current recommended one (cheap + fast)
EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding(text: str) -> list[float]:
    try:
        response = openai.embeddings.create(input=text, model=EMBEDDING_MODEL)
        return response.data[0].embedding
    except Exception as e:
        print("X Error getting embedding:", e)
        return []


# ------------------------------------------------------------------------------
# 📌 REFERENCE — How to use `get_embedding(text)` in your app
# ------------------------------------------------------------------------------

# This utility can be used to embed ANY text-based input into a vector, including:

# | Type           | Example Input                                           | Stored in...             |
# |----------------|---------------------------------------------------------|---------------------------|
# | 🌙 Dream text   | "I was drowning in an endless ocean..."                | Pinecone (dream index)    |
# | 💬 AI Response | "This dream reflects fear of loss..."                  | Pinecone or MongoDB       |
# | 🧠 Symbol       | "casa: seguridad emocional"                            | Pinecone (symbol index)   |
# | 📚 Documentation| "In dream theory, water symbolizes emotion"            | Pinecone (docs index)     |
# | ❓ User query   | "What does it mean to dream about a locked door?"      | Used at search time only  |

# You can reuse this function anywhere to:
# ✅ Generate vectors
# ✅ Store them in your vector DB
# ✅ Query them for similarity using Pinecone

# ------------------------------------------------------------------------------
