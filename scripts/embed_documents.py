import os
import json
import hashlib
import datetime
from dotenv import load_dotenv
from typing import List

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Document,
)
from llama_index.readers.notion import NotionPageReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from pinecone import Pinecone, ServerlessSpec

# ================================
# 🔐 Load environment variables
# ================================
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAR_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PAGE_ID = os.getenv("NOTION_PAGE_ID")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")

# ================================
# 📌 Index and model config
# ================================
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
CHUNK_DIM = 1536
# EMBEDDING_MODEL = "text-embedding-3-small"
CACHE_PATH = "../data/document_cache.json"
embedding_model = OpenAIEmbedding(model="text-embedding-3-small")


# ================================
# 💾 Load or create doc cache: creates a JSON file that tracks all embeddings created
# ================================
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        doc_hash_cache = json.load(f)
else:
    doc_hash_cache = {}


def get_doc_hash(text: str) -> str:
    """Generate a hash of the document text for change detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def generate_doc_id(doc: Document) -> str:
    """Create a unique ID for each document based on source."""
    source = doc.metadata.get("source", "unknown")
    identifier = (
        doc.metadata.get("title", "")
        if source == "notion"
        else doc.metadata.get("file", "unknown")
    )
    return f"{source}::{identifier[:40]}::{get_doc_hash(doc.text)}"


# ================================
# 🧠 Initialize Pinecone
# ================================
pc = Pinecone(api_key=PINECONE_API_KEY)
if INDEX_NAME not in [idx["name"] for idx in pc.list_indexes()]:
    print(f"Creating Pinecone index: {INDEX_NAME}")
    pc.create_index(
        name=INDEX_NAME,
        dimension=CHUNK_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )


pinecone_index = pc.Index(INDEX_NAME)

stats = pinecone_index.describe_index_stats()
print(
    f"📊 Pinecone Index '{INDEX_NAME}' now contains {stats['total_vector_count']} vectors."
)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)


# ================================
# 📥 Load documents
# ================================
all_docs: List[Document] = []

# Load Notion docs
notion_reader = NotionPageReader(integration_token=NOTION_TOKEN)
notion_docs = notion_reader.load_data(page_ids=[PAGE_ID])
for doc in notion_docs:
    doc.metadata = {
        "source": "notion",
        "title": doc.metadata.get("title", "Untitled"),
        "synced_at": str(datetime.datetime.now()),
    }
all_docs.extend(notion_docs)

# ================================
# 📥 Load local Markdown / PDFs
# ================================
local_docs = []

local_path = "../data/raw"
if os.path.exists(local_path) and os.listdir(local_path):
    try:
        local_docs = SimpleDirectoryReader(input_dir="../data/raw").load_data()
        for doc in local_docs:
            doc.metadata = {
                "source": "local",
                "file": doc.metadata.get("file_name", "unknown"),
                "type": "reference",
            }
        print(f"Loaded {len(local_docs)} local document(s).")
    except ValueError:
        print("No documents found in ../data/raw. Skipping local embedding.")
else:
    print("../data/raw directroy does not exist.")


# ================================
# 🧠 Combine with Notion docs
# ================================
all_docs.extend(local_docs)

# ✅ Remove empty documents (blank Notion pages, failed loads, etc.)
all_docs = [doc for doc in all_docs if doc.text.strip() != ""]
print(f"✅ {len(all_docs)} non-empty documents retained for syncing.")


# ================================
# 🧼 Remove deleted document vectors
# ================================

# Detect deleted documents
current_doc_ids = {generate_doc_id(doc) for doc in all_docs}
print(f"\n📂 Total current_docs: {len(current_doc_ids)}")
# this is all the doc IDs from the last run (based on cache)
previous_doc_ids = set(doc_hash_cache.keys())
print(f"🗃️  Total previous_docs: {len(previous_doc_ids)}")
# Everything that’s missing now but existed before
deleted_doc_ids = previous_doc_ids - current_doc_ids
print(f"🗑️  Marked for deletion: {len(deleted_doc_ids)}")

# Remove deleted docs from Pinecone and cache
if deleted_doc_ids:
    print(
        f"🗑️ Removing {len(deleted_doc_ids)} outdated vectors from Pinecone using filters..."
    )
    for doc_id in deleted_doc_ids:
        print("   → Deleting doc_id:", doc_id)
        pinecone_index.delete(filter={"doc_id": {"$in": list(deleted_doc_ids)}})
        del doc_hash_cache[doc_id]


# ================================
# 🧠 Filter changed documents only
# ================================
# ------------------------------------------------------------------------------------
# docs_to_embed = []

# for doc in all_docs:
#     doc_id = generate_doc_id(doc)
#     current_hash = get_doc_hash(doc.text)

#     if doc_id in doc_hash_cache and doc_hash_cache[doc_id] == current_hash:
#         print(f" => Skipping unchanged doc: {doc_id}")
#         continue

#     print(f"Embedding new or changed doc: {doc_id}")
#     doc_hash_cache[doc_id] = current_hash
#     docs_to_embed.append(doc)


# -----------THE ABOVE WAS REPLACED WITH THE BELOW-------------------------------------------------------------------------
parser = SentenceSplitter(chunk_size=512, chunk_overlap=100)
all_nodes = []

for doc in all_docs:
    doc_id = generate_doc_id(doc)
    current_hash = get_doc_hash(doc.text)

    if doc_id in doc_hash_cache and doc_hash_cache[doc_id] == current_hash:
        print(f" => Skiping unchanged doc: {doc_id}")
        continue

    print(f"Embedding new or changed doc: {doc_id}")
    doc_hash_cache[doc_id] = current_hash

    # ✅ Chunk and tag each node with its doc ID
    nodes = parser.get_nodes_from_documents([doc])
    for i, node in enumerate(nodes):
        node.metadata["doc_id"] = doc_id
        node.metadata["chunk_index"] = i
        all_nodes.append(node)


# ================================
# 🚀 Embed and push to Pinecone
# ================================
# This was added to make sure that when the docs are split up each chunk recieves an ID so
# they can be found and deleted after
# for doc in docs_to_embed:
#     doc.metadata["doc_id"] = generate_doc_id(doc)
#     doc.excluded_embed_metadata_keys = []

# if docs_to_embed:
#     index = VectorStoreIndex.from_documents(
#         docs_to_embed,
#         embed_model=OpenAIEmbedding(model=EMBEDDING_MODEL),
#         storage_context=storage_context,
#     )
#     print(f"✅ Embedded and indexed {len(docs_to_embed)} document(s) to Pinecone.")
# else:
#     print("✅ All documents are up to date. No re-embedding needed.")

# -----------THE ABOVE WAS REPLACED WITH THE BELOW-------------------------------------------------------------------------
# Embed the chunked text
texts = [node.text for node in all_nodes]
embeddings = embedding_model.get_text_embedding_batch(texts)

# Format for Pinecone upload
vectors = [
    {
        "id": f"{node.metadata['doc_id']}::chunk-{node.metadata['chunk_index']}",
        "values": emb,
        "metadata": node.metadata,
    }
    for node, emb in zip(all_nodes, embeddings)
]

if vectors:
    pinecone_index.upsert(vectors=vectors)
    print(f"✅ Embedded and uploaded {len(vectors)} vectors to Pinecone.")
else:
    print("✅ All documents are up to date. No re-embedding needed.")


# ================================
# 💾 Save updated hash cache
# ================================
# When you use with open(...) as f, Python will automatically close the file for you after that block is done — no need for f.close().
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

with open(CACHE_PATH, "w") as f:
    json.dump(doc_hash_cache, f, indent=2)
