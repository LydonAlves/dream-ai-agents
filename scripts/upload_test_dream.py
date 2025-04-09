import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
# the above is so that I can test this code in isolation

from src.modeling.dreamSchema import Dream, Symbol
from src.services.mongo import get_collection
from datetime import datetime
import time


dreams = get_collection("dreams")


# This is to upload a dream
dream = Dream(
    user_id="user_abc123",
    dream_id="dream_test_001",
    title="La Casa Inundada",
    dream_text="Estoy en la casa donde crecí, pero está abandonada y deteriorada. Empieza a llover torrencialmente...",
    symbols=[
        Symbol(symbol="casa", meaning="El yo interior o estado emocional actual"),
        Symbol(symbol="agua", meaning="Emociones y cambios subconscientes"),
    ],
    emotion="Angustia, nostalgia, deseo de protección",
    context="Estoy mudándome a otra ciudad, cerrando un ciclo personal. Mucha incertidumbre.",
    date=int(time.time()),  # UNIX timestamp as an int
    finalInterpretation="El sueño refleja una transición emocional intensa y la necesidad de aferrarse a tus raíces.",
    created_at=datetime.utcnow(),
)

# Insert into MongoDB
result = dreams.insert_one(dream.dict())
print("✅ Dream uploaded with ID:", result.inserted_id)
