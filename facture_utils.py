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
            "rich_text": [{"type": "text", "text": {"content": "🧾 FACTURE"}}]
        }
    })

    # Informations client et mois
    children.extend([
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "👤"},
                "rich_text": [{"type": "text", "text": {"content": f"Client : {client}"}}]
            }
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"type": "emoji", "emoji": "📅"},
                "rich_text": [{"type": "text", "text": {"content": f"Période : {mois}"}}]
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📌 Détail des interventions"}}]
            }
        }
    ])

    # En-tête tableau simulé
    header = f"{'Cours'.ljust(30)} | {'Heures':^7} | {'Tarif':^10} | {'Total':^10}"
    separator = "-" * len(header)

    children.extend([
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": header}}]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": separator}}]
            }
        }
    ])

    # Détails des lignes
    for item in interventions:
        props = item["properties"]
        cours = props["Cours"]["title"][0]["text"]["content"] if props["Cours"]["title"] else "Sans nom"
        heures = props["Nombre heures"]["number"]
        tarif = props["Tarif horaire"]["number"]
        montant = heures * tarif

        ligne = f"{cours.ljust(30)} | {str(f'{heures:.1f}h'):>7} | {str(f'{tarif:.2f}€'):>10} | {str(f'{montant:.2f}€'):>10}"
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": ligne}}]
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

    # Ligne finale esthétique
    children.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": "✅ Merci de votre confiance !"}
            }]
        }
    })

    return children

# Etape 6 Fonction mark_as_billed(pages) : marquer les interventions comme facturées
def mark_as_billed(pages):
    """
    Met à jour chaque intervention pour cocher la case "Facturé".
    """
    for page in pages:
        page_id = page["id"]
        url = f"https://api.notion.com/v1/pages/{page_id}"

        payload = {
            "properties": {
                "Facturé": {
                    "checkbox": True
                }
            }
        }

        response = requests.patch(url, headers=HEADERS, json=payload)

        if response.status_code == 200:
            print(f"✅ Intervention {page_id} marquée comme facturée.")
        else:
            print(f"❌ Échec de la mise à jour pour {page_id}")
            print(response.text)