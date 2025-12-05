import requests
import pandas as pd

API_KEY = "2e19c44e-91b4-4c19-99c4-4e91b40c193f"  

def query_sirene(date_min="2024-01-01", date_max="2024-12-31", limit=1000):
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

df = query_sirene(limit=50)
print(df.head())