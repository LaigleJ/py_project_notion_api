# main.py
from notion_api import query_database
import os
from dotenv import load_dotenv

load_dotenv()

DB_INTERVENTIONS_ID = os.getenv("DB_INTERVENTIONS_ID")

def main():
    print("🔍 Connexion à Notion...")
    interventions = query_database(DB_INTERVENTIONS_ID) # type: ignore
    print(f"✅ {len(interventions)} interventions trouvées.")
    
    for i, item in enumerate(interventions[:3], 1):
        nom_page = item['properties'].get('Nom', {}).get('title', [{}])[0].get('plain_text', 'Sans nom')
        print(f" - Intervention {i} : {nom_page}")

if __name__ == "__main__":
    main()
