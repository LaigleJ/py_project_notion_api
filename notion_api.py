import os
import requests
import pandas as pd

from datetime import datetime
from dotenv import load_dotenv

#constentes d'env : 
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ID = os.getenv("DB_INTERVENTIONS_ID")

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
    print("🔌 Connexion en cours à Notion...")
    data = get_database_properties(DB_ID)
    pprint(data)
    
# QUERY recupere les datas  facturés
def query_unbilled_entries(date_begin: str, date_end: str, a_ete_facture: bool):
    print("📡 Début de la requête vers Notion...")
    
    DB_ID = os.getenv("DB_INTERVENTIONS_ID")
    HEADERS = {
        "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Construction de la query
    if a_ete_facture is None:
        filters = [
            {
                "property": "Date de début",
                "date": {"on_or_after": date_begin}
            },
            {
                "property": "Date de début",
                "date": {"before": date_end}
            }
        ]
    else:
        filters = [
            {
                "property": "Facturé",
                "checkbox": {"equals": a_ete_facture}
            },
            {
                "property": "Date de début",
                "date": {"on_or_after": date_begin}
            },
            {
                "property": "Date de début",
                "date": {"before": date_end}
            }
        ]

    query = {"filter": {"and": filters}}

    response = requests.post(
        f"https://api.notion.com/v1/databases/{DB_ID}/query",
        headers=HEADERS,
        json=query
    )

    print(f"📦 Requête envoyée à l'API. Code de retour : {response.status_code}")
    if response.status_code != 200:
        print("❌ Erreur Notion :", response.status_code)
        print("Message :", response.text)
        response.raise_for_status()

    print("✅ Données bien récupérées !")
    return response.json()["results"]
  
  # Transformer les datas reçu en csv : 
# def extraire_interventions(results):
  # lignes = []
  # for item in results:
  #     props = item["properties"]

  #     # Extraction simple des propriétés utiles
  #     ligne = {
  #         "École": props["Ecole"]["title"][0]["plain_text"] if props["Ecole"]["title"] else "",
  #         "Ville": props["Ville"]["select"]["name"] if props["Ville"]["select"] else "",
  #         "Classe": props["Classe"]["rich_text"][0]["plain_text"] if props["Classe"]["rich_text"] else "",
  #         "Nombre heures": props["Nombre heures"]["number"],
  #         "Tarif horaire": props["Tarif horaire"]["number"],
  #         "Date de début": props["Date de début"]["date"]["start"],
  #         "Facturé": props["Facturé"]["checkbox"]
  #     }

  #     # Calcul du montant à facturer
  #     ligne["Montant"] = ligne["Nombre heures"] * ligne["Tarif horaire"] if ligne["Nombre heures"] and ligne["Tarif horaire"] else 0

  #     lignes.append(ligne)

  # return pd.DataFrame(lignes)