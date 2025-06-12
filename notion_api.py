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

def get_database_properties(database_id): 
    url = f"https://api.notion.com/v1/databases/{database_id}" 
    response = requests.get(url, headers=HEADERS) 
    response.raise_for_status() 
    print("good tutututu")
    return response.json()
  
if __name__ == "__main__":
    from pprint import pprint
    load_dotenv()  # ← Requis ici aussi si tu exécutes ce fichier seul
    DB_ID = os.getenv("DB_INTERVENTIONS_ID")
    print("🔌 Connexion en cours à Notion...")
    data = get_database_properties(DB_ID)
    pprint(data)