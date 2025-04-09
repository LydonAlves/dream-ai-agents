# from llama_index.core.indices.vector_store.base import VectorStoreIndex
# from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

# ---------------------------------------------------
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# ---------------------------------------------------

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(model="gpt-4o-mini", api_key=api_key)

# Load Jungian Knowledge
jungian_index = None

# Reads files from a jungian_knowledge folder and indexes them using a vector store
# The below would create the embeddins
# ----------------------------------------------------------------------------------------------
# def load_jungian_index():
#     docs = SimpleDirectoryReader("./data/jungian_knowledge").load_data()
#     return VectorStoreIndex.from_documents(docs)

# if jungian_index is None:
#     jungian_index = load_jungian_index()
#     jungian_engine = jungian_index.as_query_engine()
# ----------------------------------------------------------------------------------------------

# The below calls a databse (still need to set this up)
# Change ChromeVectorStore to Pinecone
# Initialize the vector store (e.g., Chroma, FAISS, etc.)
# vector_store = ChromaVectorStore(persist_dir="./db")  # update path as needed
# storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load the index from the persisted vector store
# jungian_index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
# jungian_engine = jungian_index.as_query_engine()


# The process_dream_step function analyzes a step in a dream interpretation process by generating a tailored prompt, querying
# a Jungian semantic engine for symbolic insight, and optionally falling back to a general language model if the Jungian response
# is insufficient. It returns a formatted interpretation combining both sources when needed.
# def process_dream_step(step: int, data: dict, context: dict) -> str:
#     query_str = build_prompt_from_step(step, data, context)
#     jungian_response = jungian_engine.query(query_str)
#     if len(jungian_response.response.strip()) > 100:
#         return f"**Jungian Interpretation:**\n{jungian_response.response.strip()}"
#     else:
#         fallback = llm.query(query_str)
#         return f"**Jungian Interpretation (Limited):**\n{jungian_response.response.strip()}\n\n**General Psychological Insight:**\n{fallback.response.strip()}"


# ----only until I have Jung documentation (above code to access DB)-----------------------
# The process_dream_step function generates a prompt based on the dream data and context, then uses a general language model
# to produce a psychological interpretation. It returns the result as a formatted string labeled "Psychological Insight."
def process_dream_step(step: int, data: dict, convo_context: dict) -> str:
    logger.info(f"[PROCESS STEP {step}] Input data: {data}")
    logger.info(
        f"[PROCESS STEP {step}] Convo context (truncated): {convo_context[:200]}"
    )

    query_str = build_prompt_from_step(step, data, convo_context)
    logger.info(f"[PROCESS STEP {step}] Built prompt:\n{query_str[:500]}")

    llm_response = llm.complete(query_str)
    response_text = llm_response.text.strip()  # this is only here so that I can log it
    logger.info(f"[PROCESS STEP {step}] LLM response:\n{response_text[:500]}")

    return f"**Psychological Insight:**\n{llm_response.text.strip()}"


# ------------------------------------------------------------------------

# This dynamically builds prompts based on which part of the dream interpretation process you're in. It tailors
# the language to match Jungian analysis at each step.


def build_prompt_from_step(step, data, convo_context):
    if step == 0:
        return (
            f"Responde en español (España).\n"
            f"Identifica y extrae los símbolos principales presentes en el siguiente sueño, "
            f"utilizando el enfoque de la teoría junguiana.\n"
            f"Devuelve solo un array de cadenas de texto con los símbolos extraídos (sin explicación u otro texto).\n\n"
            f"Sueño: {data.get('dream')}"
        )
    elif step == 1:
        # We need pure symbols because they can be interpreted with jungian meaning, and user meaning
        raw_symbols = data.get("symbols", [])
        symbols_only = [s["symbol"] for s in raw_symbols if "symbol" in s]
        user_meanings = "\n".join(
            [
                f" - {s['symbol']}: {s['meaning']}"
                for s in raw_symbols
                if s.get("meaning")
            ]
        )
        return (
            # The doubel \n\n is to create an emptly line between sections
            "Responde en español (España), aplicando teoría junguiana.\n\n"
            "Interpreta este sueño utilizando un enfoque junguiano. Da especial importancia a: "
            "(a) el contexto vital personal del soñador, "
            "(b) los símbolos principales en el sueño, y "
            "(c) las emociones principales.\n\n"
            "Los significados que el usuario ha asignado personalmente a los símbolos también deben tenerse en cuenta, ya que reflejan su interpretación subjetiva.\n\n"
            "El título generalmente indica el tema central o la dinámica subyacente.\n\n"
            # "Finalmente, proporciona una conclusión práctica conectada con su situación actual. Habla de forma directa al usuario, como si conversaras con él (sin consejos médicos o terapéuticos).\n\n"
            "Finalmente, proporciona una conclusión práctica conectada con su situación actual. Habla de forma directa al usuario(sin consejos médicos o terapéuticos). Habla siempre con el usuario como si estuvieras conversando directamente con él.\n\n"
            f"Título: {data.get('title')}\n"
            f"Sueño: {data.get('dream')}\n"
            f"Símbolos extraídos: {', '.join(symbols_only)}\n"
            f"Significados dados por el usuario:\n{user_meanings}\n"
            f"Emoción: {data.get('emotion')}\n"
            f"Contexto vital: {data.get('context')}"
        )

    elif step == 2:
        return (
            f"Responde en español (España), aplicando teoría junguiana.\n\n"
            f"Contexto de lo discutido hasta ahora:\n{convo_context}\n\n"
            f"El usuario ha resonado con: {data.get('resonated')}.\n"
            f"No ha estado de acuerdo con: {data.get('disagreed')}.\n"
            f"Ofrece una interpretación junguiana más profunda basándote en esta información.\n"
        )
    elif step == 3:
        return (
            f"Responde en español (España), aplicando teoría junguiana.\n\n"
            f"Contexto de lo discutido hasta ahora:\n{convo_context}\n\n"
            f"El usuario desea mejorar en: {data.get('goal')}.\n"
            f"Proporciona un consejo inspirado en la psicología junguiana relacionado con su sueño.\n"
        )
    else:
        return (
            "Responde en español (España), aplicando teoría junguiana.\n"
            "Analiza esta entrada desde la perspectiva de la psicología de los sueños.\n"
        )
