import requests
import pandas as pd
from urllib.parse import quote


KEY_emploi = "06a0cb6f7d2073abb2bb208a2dc4f6b2b121fe2875f95808111c93cfa553e18b"
KEY_marché_du_travail = "06a0cb6f7d2073abb2bb208a2dc4f6b2b121fe2875f95808111c93cfa553e18b"
URL_emploi = "https://api.francetravail.io/partenaire/stats-perspectives-retour-emploi/v1/indicateur/stat-acces-emploi"

def get_token(client_id, client_secret):
    url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "statsretouremploi"
    }

    r = requests.post(url, data=data)

    if r.status_code != 200:
        raise Exception(f"Erreur token ({r.status_code}) : {r.text}")

    return r.json()["access_token"]


def query_FT(year, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "annee": year
    }

    r = requests.get(URL_emploi, headers=headers, params=params)

    if r.status_code != 200:
        raise Exception(f"Erreur API ({r.status_code}) : {r.text}")

    return r.json()



query_FT(2015, "06a0cb6f7d2073abb2bb208a2dc4f6b2b121fe2875f95808111c93cfa553e18b")
