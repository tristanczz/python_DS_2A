import requests
import pandas as pd
from urllib.parse import quote


API_KEY = "2e19c44e-91b4-4c19-99c4-4e91b40c193f"  
BASE_URL = "https://api.insee.fr/api-sirene/3.11/siret"


def query_sirene0(date_min="2024-01-01", date_max="2024-12-31", limit=1000):
    url = "https://api.insee.fr/api-sirene/3.11/siret"
    query = f"dateCreationEtablissement:[{date_min} TO {date_max}]"

    headers = {
        "X-INSEE-Api-Key-Integration": API_KEY
    }

    params = {
        "q": query,
        "nombre": limit
    }

    r = requests.get(url, headers=headers, params=params)

    if r.status_code != 200:
        raise Exception(f"Erreur API ({r.status_code}) : {r.text}")

    data = r.json()
    etabs = data.get("etablissements", [])

    df = pd.DataFrame([{
        "siret": e.get("siret"),
        "date_creation": e.get("dateCreationEtablissement"),
        "region": e["periodesEtablissement"][0].get("regionImplantationEtablissement"),
        "activite": e["periodesEtablissement"][0].get("activitePrincipaleEtablissement")
    } for e in etabs])

    df["date_creation"] = pd.to_datetime(df["date_creation"], errors="coerce")

    return df


def query_sirene(year, limit=5000):
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

def query_sirene_rnd(year, region=None, limit=5000):
    url = "https://api.insee.fr/api-sirene/3.11/siret"

    # Filtre NAF R&D
    query_parts = ['activitePrincipaleEtablissement:72']
    if year:
        query_parts.append(f'dateCreationEtablissement:[{year}-01-01 TO {year}-12-31]')
    if region:
        query_parts.append(f'regionImplantationEtablissement:{region}')

    q = " AND ".join(query_parts)
    q_encoded = quote(q)  # encode les caractères spéciaux

    headers = {"X-INSEE-Api-Key-Integration": API_KEY}

    # On met q directement dans l'URL encodé
    full_url = f"{url}?q={q_encoded}&nombre={limit}"

    r = requests.get(full_url, headers=headers)
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





df = query_sirene(2023, limit=5000)
df.to_csv("sirene_rnd_2023_test.csv", index=False)
