import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.services.embedding import get_embedding

sample_text = "I was flying through a forest, feeling both scared and free."
embedding = get_embedding(sample_text)

if embedding:
    print("✅ Embedding created successfully!")
    print(f"Vector length: {len(embedding)}")
    print(f"First 5 values: {embedding[:5]}")
else:
    print("❌ Failed to generate embedding.")


# tested and working
