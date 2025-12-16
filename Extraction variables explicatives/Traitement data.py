import pandas as pd

df = pd.read_csv(r"C:/Users/Tom/Desktop/ENSAE/2A/S1/Python Data Science/Data/Fichier INSEE traité.csv")

# 1. Dictionnaire nom officiel des 13 régions
region_names = {
    "11": "Île-de-France",
    "24": "Centre-Val de Loire",
    "27": "Bourgogne-Franche-Comté",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhône-Alpes",
    "93": "Provence-Alpes-Côte d’Azur",
    "94": "Corse",
}

# 2. Codes courts (super pratiques pour les graphes)
region_short = {
    "11": "IDF",
    "24": "CVL",
    "27": "BFC",
    "28": "NOR",
    "32": "HDF",
    "44": "GES",
    "52": "PDL",
    "53": "BRE",
    "75": "NAQ",
    "76": "OCC",
    "84": "AURA",
    "93": "PACA",
    "94": "COR",
}

# 3. Mapping dans ton dataframe
df["nom_region"] = df["code_region"].astype(str).map(region_names)
df["code_court"] = df["code_region"].astype(str).map(region_short)

# 4. Trier pour un fichier plus propre
df = df.sort_values(["code_region", "TIME_PERIOD"])

# 5. Export propre
df.to_csv(r"C:/Users/Tom/Desktop/ENSAE/2A/S1/Python Data Science/Data/Fichier INSEE traité & clean.csv", index=False, encoding="utf-8-sig")

df.head()
