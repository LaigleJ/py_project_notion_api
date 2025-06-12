import os
import requests
import pandas as pd

from pprint import pprint
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
    print("[get_database_properties]")
    return response.json()
  
if __name__ == "__main__":
    from pprint import pprint
    load_dotenv()  
    print("🔌 Connexion en cours à Notion...")
    data = get_database_properties(DB_ID)
    pprint(data)
    
# QUERY recupere les datas  facturés
def query_unbilled_entries(date_begin: str, date_end: str, a_ete_facture: bool):
    print("📡 Début de la requête vers Notion...")

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

    # création d'un fichier csv avec les données récupérées
        print("📄 Création du fichier CSV...")
    results = response.json().get("results", [])
    if not results:
        print("⚠️ Aucune donnée trouvée pour cette période.")
        return []   
    # Convertir les résultats en DataFrame
    df = pd.json_normalize(results)
    # Enregistrer le DataFrame en CSV
    csv_filename = f"interventions_{date_begin}_to_{date_end}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"✅ Fichier CSV créé : {csv_filename}")

    print("✅ Données bien récupérées !")
    pprint(response.json())
    return response.json()["results"]
  
# Fonction pour extraire les interventions dans un DataFrame
def extraire_interventions(results):
    lignes = []
    for item in results:
        props = item["properties"]

        # Extraction simple des propriétés utiles
        ligne = {
            "Ecole": props["Ecole"]["select"]["name"] if props["Ecole"]["select"]["name"] else "",
            "Ville": props["Ville"]["select"]["name"] if props["Ville"]["select"] else "",
            "Classe": props["Classe"]["select"]["name"] if props["Classe"]["select"]["name"] else "",
            "Nombre heures": props["Nombre heures"]["number"],
            "Tarif horaire": props["Tarif horaire"]["number"],
            "Date de début": props["Date de début"]["date"]["start"],
            "Facturé": props["Facturé"]["checkbox"]
        }

        # Calcul du montant à facturer
        ligne["Montant"] = ligne["Nombre heures"] * ligne["Tarif horaire"] if ligne["Nombre heures"] and ligne["Tarif horaire"] else 0

        lignes.append(ligne)
        
    # Convertir les résultats en DataFrame
    df = pd.DataFrame(lignes)
    # Enregistrer le DataFrame en CSV
    csv_filename = f"file_data_ecole.csv"
    df.to_csv(csv_filename, index=False)
    print(f"✅ Fichier CSV créé : {csv_filename}")
      
    return df