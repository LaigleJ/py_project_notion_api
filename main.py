# # main.py
import os
import pandas as pd
from pprint import pprint

from notion_api import query_unbilled_entries
from data_processing import extraire_interventions, analyse_par_ville, analyse_par_ecole_et_classe, analyse_par_mois, analyse_heures_et_montant_total

#Pour récup les noms des collumn
# db_info = get_database_properties(os.getenv("DB_INTERVENTIONS_ID"))
# for name, value in db_info["properties"].items():
#     print(name)

# pour tester la query recuperer les datat facturé
date_debut = "2025-01-01"
date_fin = "2025-12-31"
facture = False

results = query_unbilled_entries(date_debut, date_fin, facture)

# Juste pour voir combien de lignes sont récupérées :
print(f"✅ {len(results)} interventions récupérées.")

# affichage partiel
# for i, row in enumerate(results[:3]):
#     pprint(row)

# Extraire interventions dans un DataFrame
df = extraire_interventions(results)
print(df.head())


# --- PARAMÈTRES ---
date_debut = "2024-01-01"
date_fin = "2025-12-31"
a_facturer = False  # ou None si on veut tout

# --- ÉTAPE 1 : Récupération des données ---
print("📥 Récupération des données Notion...")
results = query_unbilled_entries(date_debut, date_fin, a_facturer)
print(f"✅ {len(results)} entrées récupérées.")

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
analyse_ville.to_csv("analyse_par_ville.csv", index=False)
analyse_ecole_classe.to_csv("analyse_par_ecole_et_classe.csv", index=False)
analyse_mois.to_csv("analyse_par_mois.csv", index=False)
print("✅ Fichiers CSV enregistrés.")

print("\n📈 Analyse globale des heures et montant total...")
analyse_globale = analyse_heures_et_montant_total(df)
analyse_globale.to_csv("analyse_globale.csv", index=False)


# --- ÉTAPE 4 : Export des résultats  ---
print("\n💾 Sauvegarde des analyses dans des fichiers CSV...")