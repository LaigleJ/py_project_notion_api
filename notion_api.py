# notion_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def query_database(database_id: str, filters: dict = None): 
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    payload = {"filter": filters} if filters else {}

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()["results"]

def create_page(database_id: str, properties: dict, children: list = None):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": { "database_id": database_id },
        "properties": properties,
    }
    if children:
        payload["children"] = children

    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

def update_page(page_id: str, properties: dict):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = { "properties": properties }

    response = requests.patch(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()
