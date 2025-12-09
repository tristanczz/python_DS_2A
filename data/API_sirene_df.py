import requests
import pandas as pd
from urllib.parse import quote


API_KEY = "2e19c44e-91b4-4c19-99c4-4e91b40c193f"  
BASE_URL = "https://api.insee.fr/api-sirene/3.11/siret"


def query_sirene(year, limit=10000):
    """
    Récupère les établissements créés dans l'année donnée, éventuellement filtré par région.
    """
    date_min = f"{year}-01-01"
    date_max = f"{year}-12-31"

    # Construction de la requête
    query_parts = [f"dateCreationEtablissement:[{date_min} TO {date_max}]"]


    query = " AND ".join(query_parts)

    headers = {"X-INSEE-Api-Key-Integration": API_KEY}
    params = {"q": query, "nombre": limit}

    r = requests.get(BASE_URL, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"Erreur API ({r.status_code}) : {r.text}")

    data = r.json()
    etabs = data.get("etablissements", [])

    df = pd.DataFrame([{
        "siret": e.get("siret"),
        "date_creation": e.get("dateCreationEtablissement"),
        "region": e["periodesEtablissement"][0].get("regionImplantationEtablissement"),
        "naf": e["periodesEtablissement"][0].get("activitePrincipaleEtablissement")
    } for e in etabs])

    df["date_creation"] = pd.to_datetime(df["date_creation"], errors="coerce")

    return df




def query_sirene_all(year, departement=None, limit=5000):
    """
    Récupère les établissements créés dans l'année donnée, éventuellement filtré par département.
    
    Parameters:
    - year : int, année de création
    - departement : str ou int, code département (ex: "34" pour Hérault)
    - limit : int, nombre d'établissements max à récupérer (max 1000 par requête)
    
    Retourne :
    - DataFrame pandas avec siret, date_creation, code_postal, naf, region
    """
    date_min = f"{year}-01-01"
    date_max = f"{year}-12-31"

    # Construction de la requête
    query_parts = [f"dateCreationEtablissement:[{date_min} TO {date_max}]"]
    
    # Filtre par département si fourni
    if departement:
        # Le filtre sur code postal avec wildcard (ex: "34*") pour tout le département
        query_parts.append(f"codePostalEtablissement:{departement}*")

    query = " AND ".join(query_parts)

    headers = {"X-INSEE-Api-Key-Integration": API_KEY}
    params = {"q": query, "nombre": limit}  # nombre max par requête = 1000

    r = requests.get(BASE_URL, headers=headers, params=params)
    if r.status_code != 200:
        raise Exception(f"Erreur API ({r.status_code}) : {r.text}")

    data = r.json()
    etabs = data.get("etablissements", [])

    df = pd.DataFrame([{
        "siret": e.get("siret"),
        "date_creation": e.get("dateCreationEtablissement"),
        "code_postal": e.get("adresseEtablissement", {}).get("codePostalEtablissement")
                       or e.get("Adresse", {}).get("codePostalEtablissement"),
        "naf": e["periodesEtablissement"][0].get("activitePrincipaleEtablissement"),
        "region": e["periodesEtablissement"][0].get("regionImplantationEtablissement")
    } for e in etabs])

    df["date_creation"] = pd.to_datetime(df["date_creation"], errors="coerce")
    return df

def query_sirene_batch(year, departement=None):
    """
    Récupère tous les établissements pour une année et un département donné,
    sauvegarde dans un seul DataFrame et supprime les doublons.
    """
    date_min = f"{year}-01-01"
    date_max = f"{year}-12-31"

    query_parts = [f"dateCreationEtablissement:[{date_min} TO {date_max}]"]
    if departement:
        query_parts.append(f"codePostalEtablissement:{departement}*")

    query = " AND ".join(query_parts)
    headers = {"X-INSEE-Api-Key-Integration": API_KEY}

    all_rows = []
    last_siret = None
    batch_num = 0

    while True:
        batch_num += 1
        params = {"q": query, "nombre": 1000}
        if last_siret:
            params["q"] += f" AND siret:[{int(last_siret)+1} TO *]"

        r = requests.get(BASE_URL, headers=headers, params=params)
        if r.status_code != 200:
            raise Exception(f"Erreur API ({r.status_code}) : {r.text}")

        data = r.json()
        etabs = data.get("etablissements", [])
        if not etabs:
            print("Plus de résultats")
            break

        df_batch = pd.DataFrame([{
            "siret": e.get("siret"),
            "date_creation": e.get("dateCreationEtablissement"),
            "code_postal": e.get("adresseEtablissement", {}).get("codePostalEtablissement")
                           or e.get("Adresse", {}).get("codePostalEtablissement"),
            "naf": e["periodesEtablissement"][0].get("activitePrincipaleEtablissement"),
            "region": e["periodesEtablissement"][0].get("regionImplantationEtablissement")
        } for e in etabs])

        all_rows.append(df_batch)
        last_siret = etabs[-1]["siret"]

    # Concaténer tous les batches
    df_all = pd.concat(all_rows, ignore_index=True)

    # Supprimer les doublons par SIRET
    df_all = df_all.drop_duplicates(subset="siret").reset_index(drop=True)

    # Sauvegarde unique
    df_all.to_csv(f"sirene_{year}_{departement}.csv", index=False)
    print(f"Fichier final sirene_{year}_{departement}.csv créé, {len(df_all)} lignes uniques")

    return df_all



""" exemple d'utilisation """
#df1 = query_sirene(2023, limit = 10000)
#print(df1)

#data = pd.read_csv("data/emploi_regions_2020.csv")
#df2 = pd.DataFrame(data)
#print(df2.head())

#df3 = query_sirene_all(2024, 34)
#print(df3)

df_herault = query_sirene_batch(2023, departement="34")
print(f"Nombre d'établissements Hérault 2023 : {len(df_herault)}")
print(df_herault.head())



"""####### Codes API #######""" 
# Nomenclature unité légale : "PME,ETI,GE,null"
# auto-entrepreneurs: 'Sexe pour les personnes physiques sinon null', "M,F,[ND],null"