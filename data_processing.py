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