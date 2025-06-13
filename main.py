# # main.py
import os
import pandas as pd
from pprint import pprint
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

from notion_api import get_database_properties, query_unbilled_entries
from data_processing import extraire_interventions, analyse_par_ville, analyse_par_ecole_et_classe, analyse_par_mois, analyse_heures_et_montant_total
from facture_utils import create_invoice_page, create_invoice_page, generate_invoice_blocks, mark_as_billed

# Charger les variables d'environnement
load_dotenv()

# --- PARAMÈTRES ---
date_debut = "2024-01-01"
date_fin = "2024-12-31"
a_facturer = False  # ou None si on veut tout

# --- ÉTAPE 1 : Récupération des données ---
print("📥 Récupération des données Notion...")
results = query_unbilled_entries(date_debut, date_fin, a_facturer)
print(f"✅ {len(results)} interventions récupérées.")

# --- ÉTAPE 2 : Extraction en DataFrame ---
df = extraire_interventions(results)
print("📊 Données extraites dans un DataFrame.")

# --- ÉTAPE 3 : Analyses ---
print("\n🔎 Analyse par ville...")
analyse_ville = analyse_par_ville(df)
print(analyse_ville)

print("\n🏫 Analyse par école et classe...")
analyse_ecole_classe = analyse_par_ecole_et_classe(df)
print(analyse_ecole_classe)

print("\n🗓️ Analyse par mois (passé / futur)...")
analyse_mois = analyse_par_mois(df)
print(analyse_mois)

print("\n📈 Analyse globale des heures et montant total...")
analyse_globale = analyse_heures_et_montant_total(df)

# # --- ÉTAPE 4 : Export des résultats  ---
print("\n💾 Sauvegarde des analyses dans des fichiers CSV...")
analyse_ville.to_csv("analyse_par_ville.csv", index=False)
analyse_ecole_classe.to_csv("analyse_par_ecole_et_classe.csv", index=False)
analyse_mois.to_csv("analyse_par_mois.csv", index=False)
analyse_globale.to_csv("analyse_globale.csv", index=False)
print("✅ Fichiers CSV enregistrés.")

# --- ÉTAPE 5 : Création des factures Notion ---
print("\n🧾 Création des factures dans Notion...")

# Grouper les interventions par client
interventions_par_client = defaultdict(list)
for page in results:
    client = page["properties"]["Ecole"]["select"]["name"]  # ou adapte selon ta logique
    interventions_par_client[client].append(page)

# Créer une facture pour chaque client
for client, pages in interventions_par_client.items():
    total = 0
    for p in pages:
        heures = p["properties"]["Nombre heures"]["number"]
        tarif = p["properties"]["Tarif horaire"]["number"]
        total += (heures or 0) * (tarif or 0)

    mois = datetime.now().strftime("%Y-%m")
    # Générer un numéro auto incrémenté
    invoice_number = 1
    if os.path.exists("last_invoice_number.txt"):
        with open("last_invoice_number.txt", "r") as f:
            invoice_number = int(f.read().strip()) + 1
    with open("last_invoice_number.txt", "w") as f:
        f.write(str(invoice_number))
    invoice_number = f"FAC-{mois}-{invoice_number}-{client.replace(' ', '').upper()}"
    print(f"📄 Création de la facture pour {client} ({invoice_number}) : {total} €")

    create_invoice_page(client=client, interventions=pages, total=total, invoice_number=invoice_number)
# Marquer les interventions comme facturées
    mark_as_billed(pages)

print("✅ Toutes les factures ont été créées. 🎉")


# *****************************************************************************************
# Test debug connection 
# data = get_database_properties(os.getenv("DB_INVOICES_ID"))
# pprint(data)

