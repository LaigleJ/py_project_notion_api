
---

```markdown
<!-- Marie-Charlotte et Jérémy -->

# 📘 Journal de bord – Projet Python x API Notion

---

## 📅 Plan 

| Étape         | Description                                     | Statut     | Date         |
|-------------- |-------------------------------------------------|------------|--------------|
| ✅ Étape 1   | Connexion à l'API Notion via fichier `.env`     | Terminé    | 2025-06-12   |
| ✅ Étape 2   | Fonction `query_unbilled_entries()`             | Terminé    | -            |
| ✅ -         | Analyse avec `pandas`                           | Terminé    | 2025-06-12   |
| ✅ Étape 3   | Génération de factures + export CSV             | Terminé    | -            |
| ✅ -         | Ecriture des factures sur notion                | Terminé    | 2025-06-12   |
| ⏳ Étape 4   | Mise en page : generate_invoice_blocks          | À faire    | -            |
| ⏳ Étape 5   | Mise en page : def create_invoice_page          | À faire    | -            |
| ⏳ Étape 6   | Mise à joour : mark_as_billed(pages)            | À faire    | -            |
| 🔄 Étape 7   | Orchestrer tout le processus dans le main       | En cours   | 2025-06-12   |

---

## 📁 Structure du projet (provisoire)


📦 py\_project\_notion\_api/
├── 📄 .env
├── 📄 main.py
├── 📄 notion\_api.py
├── 📄 journal\_de\_bord.md
└── 📁 assets/
└── 📸 capture\_api\_ok.png

---


### Étape 0 & 1– Configuration de l’environnement & Définir les entêtes pour l’API Notion

## ✅ Fonctionnalités implémentées

- [x] Connexion sécurisée à l'API Notion via clé secrète
- [x] Requête filtrée selon la colonne **Facturé** + plage de dates
- [x] Analyse des résultats avec `pandas`
- [x] Export en `.csv` automatique

---

## 🧪 Tests & validation

- 🔄 Vérification manuelle dans le terminal (print & logs)
- ✅ Code retour HTTP 200 → données bien récupérées


## 📸 Capture – Connexion à l'API réussie

> Exemple de connexion réussie à Notion, avec récupération des propriétés de la base :

![Connexion API OK](./assets/capture_api_ok.png)

---


### Étape 2 – Fonction query_unbilled_entries(date_begin : str, date_end : str, a_ete_facture : bool)

## 🔍 Code – Requête des interventions non facturées + CSV

```python
def query_unbilled_entries(date_begin: str, date_end: str, a_ete_facture: bool):
    print("📡 Début de la requête vers Notion...")

    # Construction dynamique du filtre
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

    if a_ete_facture is not None:
        filters.insert(0, {
            "property": "Facturé",
            "checkbox": {"equals": a_ete_facture}
        })

    query = {"filter": {"and": filters}}

    response = requests.post(
        f"https://api.notion.com/v1/databases/{DB_ID}/query",
        headers=HEADERS,
        json=query
    )

    print(f"📦 Code de retour API : {response.status_code}")
    if response.status_code != 200:
        print("❌ Erreur API :", response.text)
        response.raise_for_status()

    results = response.json().get("results", [])
    if not results:
        print("⚠️ Aucune donnée trouvée.")
        return []

    # ➕ Export CSV avec pandas
    df = pd.json_normalize(results)
    csv_filename = f"interventions_{date_begin}_to_{date_end}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"✅ CSV généré : {csv_filename}")

    return results
````


## 🧭 Prochaines étapes

➡️ Nettoyage et transformation des données avec `pandas`
➡️ Préparation des templates de factures (PDF ou CSV)
➡️ Documentation finale & README complet

---

##  🔍 Questions pour analyse :
### récupérer les résultats et montrez via des DataFrames :
par ville, le nombre d’écoles, le nombre d’heures données et la somme à facturer

> Exemple de la premiere récuperation data triées:

![DataFrame datas](./assets/recup_data_1.png)
![CSV datas](./assets/capture_csv_datas_1.png)


## 🔍 Code – Extrait du code de la premiere récuperation data triées + CSV

```python
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

    return pd.DataFrame(lignes)
    ````

  > Exemple de la premiere récuperation data triées:

![DataFrame datas](./assets/capture_terminal_data_triees.png)
![CSV datas](./assets/capture_csv_datas_1.png)

## ANALYSES data_processing.py::
```PYTHON
import pandas as pd
from datetime import datetime

# Fonction pour extraire les interventions dans un DataFrame
def extraire_interventions(results):
    lignes = []
    for item in results:
        props = item["properties"]

        ligne = {
            "Ecole": props["Ecole"]["select"]["name"] if props["Ecole"]["select"] else "",
            "Ville": props["Ville"]["select"]["name"] if props["Ville"]["select"] else "",
            "Classe": props["Classe"]["select"]["name"] if props["Classe"]["select"] else "",
            "Nombre heures": props["Nombre heures"]["number"],
            "Tarif horaire": props["Tarif horaire"]["number"],
            "Date de début": props["Date de début"]["date"]["start"],
            "Facturé": props["Facturé"]["checkbox"]
        }

        ligne["Montant"] = (ligne["Nombre heures"] or 0) * (ligne["Tarif horaire"] or 0)
        lignes.append(ligne)

    df = pd.DataFrame(lignes)
    df.to_csv("file_data_ecole.csv", index=False)
    print("✅ Fichier CSV créé : file_data_ecole.csv")
    return df

# Analyse par ville : nombre d'écoles, heures, montant
def analyse_par_ville(df):
    if df is None or df.empty:
        return pd.DataFrame()
    
    stats = df.groupby("Ville").agg({
        "Ecole": pd.Series.nunique,
        "Nombre heures": "sum",
        "Montant": "sum"
    }).rename(columns={"Ecole": "Nombre d'écoles"})
    
    print("\n📊 Analyse par ville:")
    print(stats)
    return stats.reset_index()


# Analyse par école et classe
def analyse_par_ecole_et_classe(df):
    if df is None or df.empty:
        return pd.DataFrame()
    
    stats = df.groupby(["Ecole", "Classe"]).agg({
        "Nombre heures": "sum"
    }).rename(columns={"Nombre heures": "Total heures"})
    
    print("\n📊 Analyse par école et classe:")
    print(stats)
    return stats.reset_index()

  
# Analyse par mois (passé et futur)
def analyse_par_mois(df):
    if df is None or df.empty:
        return pd.DataFrame()
    
    df["Date de début"] = pd.to_datetime(df["Date de début"])
    df["Mois"] = df["Date de début"].dt.to_period("M")

    aujourd_hui = pd.Timestamp.today()
    df["Futur"] = df["Date de début"] > aujourd_hui

    futur_stats = df.groupby(["Futur", "Mois"])["Nombre heures"].sum().reset_index()
    
    print("\n📆 Heures par mois (passé/futur):")
    print(futur_stats)
    return futur_stats
  
  
  
# Analyse globale : total des heures enseignées et somme à facturer
def analyse_heures_et_montant_total(df):
    if df is None or df.empty:
        return pd.DataFrame()
    
    total_heures = df["Nombre heures"].sum()
    total_montant = df["Montant"].sum()

    resume = pd.DataFrame([{
        "Total heures enseignées": total_heures,
        "Montant total à facturer (€)": total_montant
    }])
    
    print("\n📈 Total général :")
    print(resume)

    return resume
````
Total heures enseignées       Montant total à facturer
235.5 h	                      2 312.5 €


## Analyse par ville : nombre d'écoles, heures, montant
[Analyse par ville](./assets/CSV/analyse_par_ville.csv)
## Analyse par école et classe
[Analyse par ville](./assets/CSV/analyse_par_ecole_et_classe.csv)
## Analyse par mois (passé et futur)
[Analyse par ville](./assets/CSV/analyse_par_mois.csv)
## Analyse globale : total des heures enseignées et somme à facturer
[Analyse par ville](./assets/CSV/analyse_globale.csv)

### ETAPE 3 : Première fonction de création de factures dans Notion 

## Extrait du code facture_utils.py ::
```PYTHON
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

````

##Capture Ecran de la db invoices de notion
![Capture écran des facures dans notion](./assets/capture_db_invoices_remplies.png)

---