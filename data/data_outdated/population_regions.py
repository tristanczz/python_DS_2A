import pandas as pd
import re

# --- CONFIGURATION ---
nom_fichier = "data/data_outdated/estim-pop-nreg-sexe-gca-1975-2025.xlsx"  # Nom exact de votre fichier Excel
nom_sortie = "data/population_regions_1975_2025.csv"

# Dictionnaire de correspondance (Région -> Code INSEE)
region_codes = {
    "Auvergne-Rhône-Alpes": "84",
    "Bourgogne-Franche-Comté": "27",
    "Bretagne": "53",
    "Centre-Val-de-Loire": "24",
    "Corse": "94",
    "Grand Est": "44",
    "Hauts-de-France": "32",
    "Île-de-France": "11",
    "Normandie": "28",
    "Nouvelle-Aquitaine": "75",
    "Occitanie": "76",
    "Pays de la Loire": "52",
    "Provence-Alpes-Côte d'Azur": "93",
    "Guadeloupe": "01",
    "Martinique": "02",
    "Guyane": "03",
    "La Réunion": "04",
    "Mayotte": "06",
    "France métropolitaine": "FM",
    "France": "FR" # Parfois "France entière"
}

def nettoyer_population(valeur):
    """Nettoie les valeurs de population (enlève les espaces, gère les NaN)"""
    if pd.isna(valeur):
        return None
    # Convertir en string, enlever les espaces insécables ou normaux
    val_str = str(valeur).replace(" ", "").replace("\u202f", "").replace("\xa0", "")
    try:
        # Tenter de convertir en entier (ignorer les .0 si flottant)
        return int(float(val_str))
    except ValueError:
        return None

try:
    print(f"Lecture du fichier : {nom_fichier} ...")
    # On charge le fichier Excel pour obtenir la liste des onglets (sheet_names)
    xl = pd.ExcelFile(nom_fichier)
    
    toutes_les_donnees = []

    for sheet in xl.sheet_names:
        # On vérifie si l'onglet ressemble à une année (4 chiffres)
        if not re.match(r'^\d{4}$', sheet):
            continue
            
        annee = sheet
        print(f"Traitement de l'année {annee}...")

        # Lecture de l'onglet.
        # header=4 signifie qu'on utilise la 5ème ligne comme en-tête (index 4)
        # C'est souvent là que se trouvent "Régions", "Ensemble", etc.
        df = xl.parse(sheet_name=sheet, header=4)

        # La colonne 0 est la région, la colonne 6 est le Total "Ensemble" -> "Total"
        # Attention : Pandas nomme les colonnes souvent par leur contenu.
        # On va plutôt utiliser les index de colonnes pour être sûr (iloc)
        # Col 0 = Région, Col 6 = Total Population
        
        # Sélection par position (plus robuste que par nom de colonne qui peut changer)
        df_subset = df.iloc[:, [0, 6]].copy()
        df_subset.columns = ['region', 'population']
        
        # Nettoyage
        df_subset = df_subset.dropna(subset=['region']) # Enlever les lignes vides
        df_subset['region'] = df_subset['region'].astype(str).str.strip()
        
        # Mapping du code région
        df_subset['region_code'] = df_subset['region'].map(region_codes)
        
        # On ne garde que les lignes où on a trouvé un code région (filtre les notes de bas de page)
        df_subset = df_subset.dropna(subset=['region_code'])
        
        # Ajout de l'année
        df_subset['year'] = annee
        
        # Nettoyage de la population
        df_subset['population'] = df_subset['population'].apply(nettoyer_population)

        # Réorganisation
        df_subset = df_subset[['region', 'region_code', 'year', 'population']]
        
        toutes_les_donnees.append(df_subset)

    # Concaténation finale
    if toutes_les_donnees:
        df_final = pd.concat(toutes_les_donnees, ignore_index=True)
        
        # Tri
        df_final = df_final.sort_values(by=['year', 'region'])
        
        # Export CSV
        df_final.to_csv(nom_sortie, index=False, encoding='utf-8')
        print(f"\nSuccès ! Fichier créé : {nom_sortie}")
        print(f"Nombre total de lignes : {len(df_final)}")
    else:
        print("Aucune donnée n'a été extraite. Vérifiez le format du fichier.")

except FileNotFoundError:
    print(f"Erreur : Le fichier '{nom_fichier}' est introuvable.")
except Exception as e:
    print(f"Une erreur est survenue : {e}")