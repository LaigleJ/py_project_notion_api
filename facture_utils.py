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

    mois = datetime.now().strftime("%Y-%m")  # utilisé dans le contenu, pas besoin de passer en paramètre
    children = generate_invoice_blocks(interventions, total, client, mois)

    payload = {
        "parent": {"database_id": DB_INVOICES_ID},
        "properties": {
            "Client": {
                "title": [{"text": {"content": client}}]
            },
            "Mois": {
                "rich_text": [{"text": {"content": mois}}]
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


# ETAPE 4 Ameliorer visu facture

def generate_invoice_blocks(interventions, total, client, mois):
    children = []

    # Titre principal
    children.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "🧾 FACTURE"}
            }]
        }
    })

    # Bloc info client et mois
    children.extend([
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "👤"},
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"Client : {client}"}
                }]
            }
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📅"},
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"Mois de facturation : {mois}"}
                }]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "📌 Détail des interventions"}
                }]
            }
        }
    ])

    # En-tête formaté manuellement
    header = f"{'Cours'.ljust(30)}{'Heures'.rjust(8)}{'Tarif'.rjust(10)}{'Total'.rjust(10)}"
    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": header}
            }]
        }
    })

    # Ligne de séparation visuelle
    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "-" * 60}
            }]
        }
    })

    # Lignes de détail
    for item in interventions:
        props = item["properties"]
        cours = props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else "Sans nom"
        heures = props["Nombre heures"]["number"]
        tarif = props["Tarif horaire"]["number"]
        montant = heures * tarif

        ligne = f"{cours.ljust(30)}{str(f'{heures:.1f}h').rjust(8)}{str(f'{tarif:.2f}€').rjust(10)}{str(f'{montant:.2f}€').rjust(10)}"
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

    # Total final
    children.append({
        "object": "block",
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "💰"},
            "rich_text": [{
                "type": "text",
                "text": {"content": f"Total à payer : {total:.2f} €"}
            }]
        }
    })

    return children
