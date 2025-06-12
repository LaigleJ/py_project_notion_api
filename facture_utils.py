import requests
import os
from datetime import datetime
from notion_api import HEADERS

def create_invoice_page(client: str, interventions: list, total: float, invoice_number: str):
    children = []

    for item in interventions:
        props = item["properties"]
        
        # Récupération des infos par les bonnes clés
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
        "parent": {"database_id": os.getenv("DB_INVOICES_ID")},
        "properties": {
            "Nom du client": {
                "title": [{"text": {"content": client}}]
            },
            "Mois": {
                "rich_text": [{"text": {"content": datetime.now().strftime("%Y-%m")}}]
            },
            "Montant total": {
                "number": total
            },
            "ID de Facture": {
                "rich_text": [{"text": {"content": invoice_number}}]
            }
        },
        "children": children
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()