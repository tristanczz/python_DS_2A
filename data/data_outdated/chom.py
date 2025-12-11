import pandas as pd

# Charger le CSV
df = pd.read_csv("data/data_outdated/valeurs_trimestrielles.csv", sep=';', encoding='utf-8')  # adapter le séparateur

# Supprimer les lignes où 'Libellé' contient 'Codes'
df = df[~df['Libellé'].str.contains('Codes', na=False)]

# Garder seulement les colonnes de 2015-T1 à 2025-T2 + la colonne Libellé
colonnes_a_garder = ['Libellé'] + [col for col in df.columns if col.startswith(tuple(str(y) for y in range(2015, 2026)))]
df = df[colonnes_a_garder]

# mettre des floats (vs obj)
for col in df.columns:
    if col != "Libellé":
        df[col] = pd.to_numeric(df[col], errors='raise')

    
# Créer de nouvelles colonnes pour les moyennes annuelles
annees = range(2015, 2026)
trimestres = ['T1', 'T2', 'T3', 'T4']

for annee in annees:
    colonnes_annee = [f"{annee}-{t}" for t in trimestres]
    # S'assurer que toutes les colonnes trimestrielles existent avant de calculer la moyenne
    colonnes_existantes = [col for col in colonnes_annee if col in df.columns]
    if colonnes_existantes:
        df[f"Moyenne_{annee}"] = df[colonnes_existantes].mean(axis=1)
    else:
        # Si aucune colonne trimestrielle n'existe pour l'année, la moyenne est NaN
        df[f"Moyenne_{annee}"] = float('nan')

# Supprimer les colonnes trimestrielles
colonnes_trimestres = [col for col in df.columns if '-' in col]  # ex: 2015-T1, 2024-T3
df = df.drop(columns=colonnes_trimestres)


#sauvergarde
df = df.round(3)        # arrondissement pour les floats trop longs (999999999 ou 000000001)
df.to_csv("data/taux_chomage_2015_2025.csv", index=False, sep=';', encoding='utf-8')
