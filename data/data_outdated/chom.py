import pandas as pd

# Charger le CSV
df = pd.read_csv("valeurs_trimestrielles.csv", sep=';', encoding='utf-8')  # adapter le séparateur

# Supprimer les lignes où 'Libellé' contient 'Codes'
df = df[~df['Libellé'].str.contains('Codes', na=False)]

# Garder seulement les colonnes de 2015-T1 à 2025-T2 + la colonne Libellé
colonnes_a_garder = ['Libellé'] + [col for col in df.columns if col.startswith(tuple(str(y) for y in range(2015, 2026)))]
df = df[colonnes_a_garder]

# Réinitialiser l'index si besoin
df = df.reset_index(drop=True)

# Sauvegarder le CSV filtré
df.to_csv("taux_chomage_2015_2025.csv", index=False, sep=';')