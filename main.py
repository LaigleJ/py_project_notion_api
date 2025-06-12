# # main.py
import os
from pprint import pprint
from notion_api import query_unbilled_entries,  get_database_properties

import pandas as pd

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

# Facultatif : affichage partiel
for i, row in enumerate(results[:3]):
    pprint(row)

# Faire le csv
# results = query_unbilled_entries(date_debut, date_fin, facture)
# df = extraire_interventions(results)
# print(df.head())