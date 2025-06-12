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
    if not DB_INVOICES_ID:
        raise ValueError("❌ DB_INVOICES_ID manquant. Vérifie ton .env")

    children = []
    for item in interventions:
        props = item["properties"]
        cours = props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else "Sans nom"
        heures = props["Nombre heures"]["number"]
        tarif = props["Tarif horaire"]["number"]
        montant = heures * tarif

        ligne = f"{cours} - {heures}h x {tarif}€/h = {montant}€"

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
