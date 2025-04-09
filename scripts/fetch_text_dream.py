import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
# the above is so that I can test this code in isolation

from src.modeling.dreamSchema import Dream
from src.services.mongo import get_collection

# this connects to mongodb
dreams = get_collection("dreams")

dream = dreams.find_one({"dream_id": "dream_test_001"})

# the below shows the entire object in object form
if dream:
    print("Found dream:", dream)
else:
    print("No dream found with that ID")

# the below can be used to show see the printout of the structure of the info
parsed_dream = Dream(**dream)
print(parsed_dream.title)
print(parsed_dream.symbols[0].symbol)


# ---------multiple dreams------------------------------------------------------------

# user_dreams = list(dreams.find({"user_id": "user_abc123"}))
# parsed_dreams = [Dream(**d) for d in user_dreams]
