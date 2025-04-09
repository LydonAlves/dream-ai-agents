import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
# the above is so that I can test this code in isolation

from llama_index.readers.notion import NotionPageReader
import os
from dotenv import load_dotenv
from notion_client import Client
import requests
# import shutil

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
notion = Client(auth=NOTION_TOKEN)


# function to fetch blocks
def get_blocks(PAGE_ID: str):
    blocks = []
    cursor = None
    while True:
        response = notion.blocks.children.list(block_id=PAGE_ID, start_cursor=cursor)
        blocks.extend(response["results"])
        cursor = response.get("next_cursor")
        if not response.get("has_more"):
            break
    return blocks


# Function to Download PDFs from the Blocks
def download_pdfs_from_blocks(blocks, save_folder="../data/raw"):
    os.makedirs(save_folder, exist_ok=True)
    downloaded_paths = []

    for block in blocks:
        if block["type"] == "file":
            file_info = block["file"]
            url = None
            if file_info["type"] == "external":
                url = file_info["external"]["url"]
            elif file_info["type"] == "file":
                url = file_info["file"]["url"]

            if url and ".pdf" in url:
                file_name = f"{block['id']}.pdf"
                file_path = os.path.join(save_folder, file_name)
                print(f"Downloading: {url}")
                with open(file_path, "wb") as f:
                    f.write(requests.get(url).content)
                downloaded_paths.append(file_path)

    return downloaded_paths


# Load Notion page text (optional)
reader = NotionPageReader(integration_token=NOTION_TOKEN)
docs = reader.load_data(["1cdb82a32896804e8282efc96fed1712"])

# for doc in docs:
#     print("✅ Title:", doc.metadata.get("title"))
#     print("📄 Text preview:", doc.text[:300], "...\n")

# Load PDFs from the same page
PAGE_ID = os.getenv("NOTION_PAGE_ID")
blocks = get_blocks(PAGE_ID)
for block in blocks:
    print("🔍 Block type:", block.get("type"))
    if block.get("type") == "file":
        print("   ✅ Found file block:", block)
pdf_paths = download_pdfs_from_blocks(blocks)

print("Pdfs downloaded:", pdf_paths)


# Optional: clean up this deletes the temporary file created
# shutil.rmtree("/tmp/notion_pdfs", ignore_errors=True)
