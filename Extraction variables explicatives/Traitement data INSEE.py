import pandas as pd

# ======================
# 1. Lecture du fichier
# ======================

path = r"C:/Users/Tom/Desktop/ENSAE/2A/S1/Python Data Science/Data/Fichier INSEE.csv"

df = pd.read_csv(
    path,
    sep=";",
    dtype=str,
    low_memory=False
)

print("Colonnes :", df.columns)

# 1. Créations d'entreprises (unités légales)
df = df[df["SIDE_MEASURE"] == "BURE"]

# 2. Départements uniquement
df = df[df["GEO_OBJECT"] == "DEP"]

# 3. Années 2015–2024
df["TIME_PERIOD"] = df["TIME_PERIOD"].astype(int)
df = df[df["TIME_PERIOD"].between(2015, 2024)]

# 4. (Optionnel) total des formes juridiques si la colonne existe
if "LEGAL_FORM" in df.columns:
    # garder uniquement le total toutes formes si présent
    mask_total_forme = df["LEGAL_FORM"].eq("_T")
    if mask_total_forme.any():
        df = df[mask_total_forme]

# 5. Conversion de la valeur
df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")

# 6. Mapping département -> région
dep_to_region = {
    "01": "84", "02": "32", "03": "84", "04": "93", "05": "93", "06": "93",
    "07": "84", "08": "44", "09": "76", "10": "44", "11": "76", "12": "76",
    "13": "93", "14": "28", "15": "84", "16": "75", "17": "75", "18": "24",
    "19": "75", "21": "27", "22": "53", "23": "75", "24": "75", "25": "27",
    "26": "84", "27": "28", "28": "24", "29": "53", "2A": "94", "2B": "94",
    "30": "76", "31": "76", "32": "76", "33": "75", "34": "76", "35": "53",
    "36": "24", "37": "24", "38": "84", "39": "27", "40": "75", "41": "24",
    "42": "84", "43": "84", "44": "52", "45": "24", "46": "76", "47": "75",
    "48": "76", "49": "52", "50": "28", "51": "44", "52": "44", "53": "52",
    "54": "44", "55": "44", "56": "53", "57": "44", "58": "27", "59": "32",
    "60": "32", "61": "28", "62": "32", "63": "84", "64": "75", "65": "76",
    "66": "76", "67": "44", "68": "44", "69": "84", "70": "27", "71": "27",
    "72": "52", "73": "84", "74": "84", "75": "11", "76": "28", "77": "11",
    "78": "11", "79": "75", "80": "32", "81": "76", "82": "76", "83": "93",
    "84": "93", "85": "52", "86": "75", "87": "75", "88": "44", "89": "27",
    "90": "27", "91": "11", "92": "11", "93": "11", "94": "11", "95": "11",
}

df["REG_CODE"] = df["GEO"].map(dep_to_region)

# Vérif : il ne doit pas rester de départements sans région
print("Départements sans région :")
print(df[df["REG_CODE"].isna()]["GEO"].drop_duplicates())

# 7. Agrégat Région x Année
# si tu as un facteur 2 systématique, utilise .mean() au lieu de .sum()
y_reg_year = (
    df.groupby(["REG_CODE", "TIME_PERIOD"], as_index=False)["OBS_VALUE"]
      .sum()
      .rename(columns={"REG_CODE": "code_region", "OBS_VALUE": "nb_creations"})
)

print(y_reg_year.head())

y_reg_year.to_csv(
    r"C:/Users/Tom/Desktop/Fichier INSEE traité.csv",
    index=False,
    encoding="utf-8"
)
