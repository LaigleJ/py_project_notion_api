import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_INVOICES_ID = os.getenv("DB_INVOICES_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def create_invoice_page(client: str, interventions: list, total: float, invoice_number: str):
    """
    Crée une page de facture dans la base Notion "Invoices".

    Args:
        client (str): nom du client
        interventions (list): liste des interventions à inclure
        total (float): montant total à facturer
        invoice_number (str): numéro unique de facture

    Returns:
        dict: réponse JSON de l'API Notion
    """
    if not DB_INVOICES_ID:
        raise ValueError("❌ DB_INVOICES_ID manquant. Vérifie ton .env")

    children = []

    for item in interventions:
        props = item["properties"]

        # Extraction du nom du cours (champ Titre, donc une liste)
        cours = props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else "Sans nom"

        heures = props["Nombre heures"]["number"]
        tarif = props["Tarif horaire"]["number"]
        montant = heures * tarif

        ligne = f"{cours} - {heures}h x {tarif}€/h = {montant}€"

        # Bloc de paragraphe à insérer dans la facture
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": ligne}
                }]
            }
        })

    # Payload complet pour créer la facture
    payload = {
        "parent": {"database_id": DB_INVOICES_ID},
        "properties": {
            "Client": {
                "title": [{"text": {"content": client}}]
            },
            "Mois": {
                "rich_text": [{"text": {"content": datetime.now().strftime("%Y-%m")}}]
            },
            "Total Amount": {
                "number": total
            },
            "Invoice Number": {
                "rich_text": [{"text": {"content": invoice_number}}]
            }
        },
        "children": children
    }

    print("🛠️ Payload envoyé à Notion :")
    import json
    print(json.dumps(payload, indent=2))

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    response.raise_for_status()
    print("✅ Facture créée avec succès sur Notion.")
    return response.json()
