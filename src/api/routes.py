from fastapi import APIRouter, HTTPException
from src.api.schemas import DreamInput, Step0Input, Step1Input, Step2Input, Step3Input
from src.core.pipeline import process_dream_step
from src.core.session import get_session_context, save_session_context

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initializes the router where you'll attach your route handlers (like /analyze).
router = APIRouter(tags=["Dream Analysis"])

# This sets up a POST endpoint at /analyze. When a user makes a POST request to /analyze, it triggers this analyze_dream function
# 1. Accepts a JSON body matching DreamInput.
# 2. Gets session context based on the user_id.
# 3. Passes the input data to process_dream_step with the step and context.
# 4. Returns the response wrapped in a JSON dict.

# my origional test function
# @router.post("/analyze")
# def analyze_dream(input: DreamInput):
#     context = get_session_context(input.user_id)
#     response = process_dream_step(
#         step=input.step, data=input.input_data, context=context
#     )
#     return {"response": response}


# This sets up a POST endpoint at /analyze. When a user makes a POST request to /analyze, it triggers this analyze_dream function
# This takes the context of the conversation into account
@router.post("/analyze")
def analyze_dream(input: DreamInput):
    context = get_session_context(input.user_id, input.dream_id)
    convo_context = context.get("convo_context", "")
    step = input.step

    try:
        if step == 0:
            validated_data = Step0Input(**input.input_data).dict()
        elif step == 1:
            validated_data = Step1Input(**input.input_data).dict()
        elif step == 2:
            validated_data = Step2Input(**input.input_data).dict()
        elif step == 3:
            validated_data = Step3Input(**input.input_data).dict()
        else:
            raise HTTPException(status_code=422, detail="Invalid step")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid data: {e}")

    logger.info(f"[STEP {step}] User: {input.user_id} | Dream: {input.dream_id}")
    logger.info(f"[INPUT DATA]: {validated_data}")
    logger.info(f"[CONVO CONTEXT]: {convo_context[:200]}")

    response = process_dream_step(
        step=step, data=validated_data, convo_context=convo_context
    )

    # Update and save convo context
    new_entry = f"\nPaso {step}:\n{response}\n"
    context["convo_context"] = convo_context + new_entry
    save_session_context(input.user_id, input.dream_id, context)

    logger.info(f"[RESPONSE]: {response[:200]}")

    return {"response": response}
