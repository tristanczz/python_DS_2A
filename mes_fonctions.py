import pandas as pd


def load_insee_head(path, n=5):
    """
    Charge le fichier INSEE brut et renvoie les n premières lignes.
    """
    df = pd.read_csv(
        path,
        sep=";",
        dtype=str,
        low_memory=False
    )
    return df.head(n)



def build_y_insee_region_year(
    path,
    year_min=2015,
    year_max=2024,
):
    # ======================
    # 1. Lecture du fichier
    # ======================

    df = pd.read_csv(
        path,
        sep=";",
        dtype=str,
        low_memory=False
    )


    # 1. Créations d'entreprises (unités légales)
    df = df[df["SIDE_MEASURE"] == "BURE"]

    # 2. Départements uniquement
    df = df[df["GEO_OBJECT"] == "DEP"]
    df = df[~df["GEO"].isin(["971", "972", "973", "974", "976"])]

    # 3. Années
    df["TIME_PERIOD"] = df["TIME_PERIOD"].astype(int)
    df = df[df["TIME_PERIOD"].between(year_min, year_max)]

    # 4. (Optionnel) total des formes juridiques
    if "LEGAL_FORM" in df.columns:
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

    # 7. Agrégat Région x Année
    y_reg_year = (
        df.groupby(["REG_CODE", "TIME_PERIOD"], as_index=False)["OBS_VALUE"]
          .sum()
          .rename(columns={"REG_CODE": "code_region", "OBS_VALUE": "nb_creations"})
    )

    return y_reg_year


def clean_y_insee_region_year(df):
    """
    Prend en entrée la sortie de build_y_insee_region_year (code_region, TIME_PERIOD, nb_creations)
    et renvoie un tableau plus lisible avec nom_region + code_court.
    """
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

    # Copie pour éviter les effets de bord
    out = df.copy()

    # 3. Mapping dans ton dataframe
    out["nom_region"] = out["code_region"].astype(str).map(region_names)
    out["code_court"] = out["code_region"].astype(str).map(region_short)

    # 4. Trier pour un fichier plus propre
    out = out.sort_values(["code_region", "TIME_PERIOD"]).reset_index(drop=True)

    return out

import pandas as pd


def construire_Y_taux_creation(
    path_creation_csv: str,
    path_population_csv: str,
    out_path_panel: str | None = None,
    out_path_avg: str | None = None,
    col_region_creation: str = "region_nom",
    col_time_creation: str = "TIME_PERIOD",
    col_y_creation: str = "nb_creations",
    col_region_pop: str = "region_nom",
    col_time_pop: str = "TIME_PERIOD",
    col_pop: str = "population",
    facteur: float = 1000.0,
    arrondi: int = 2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Construit une version normalisée de la variable cible Y (créations d'entreprises),
    sous forme de taux pour 'facteur' habitants (par défaut 1000), puis calcule la moyenne
    par région sur toute la période disponible.

    Paramètres
    ----------
    path_creation_csv : str
        CSV contenant au minimum [col_region_creation, col_time_creation, col_y_creation]
    path_population_csv : str
        CSV contenant au minimum [col_region_pop, col_time_pop, col_pop]
    out_path_panel : str | None
        Si fourni, exporte le panel (région x année) avec 'creations_per_1000' (ou facteur)
    out_path_avg : str | None
        Si fourni, exporte la moyenne par région
    facteur : float
        Base de normalisation (1000 -> "par 1000 habitants")
    arrondi : int
        Nombre de décimales pour l'arrondi de la variable normalisée

    Retour
    ------
    merged_df : pd.DataFrame
        Données panel (région x période) avec la colonne 'creations_per_1000'
    avg_df : pd.DataFrame
        Données transversales (une ligne par région) avec la moyenne de 'creations_per_1000'
    """

    # --- Lecture
    creation_df = pd.read_csv(path_creation_csv)
    pop_df = pd.read_csv(path_population_csv)

    # --- Normalisation colonnes (au cas où)
    # Ex : parfois 'nom_region' au lieu de 'region_nom'
    if "nom_region" in creation_df.columns and col_region_creation not in creation_df.columns:
        creation_df = creation_df.rename(columns={"nom_region": col_region_creation})

    # --- Nettoyage types / clés de merge
    creation_df[col_region_creation] = (
        creation_df[col_region_creation].astype(str).str.replace("’", "'", regex=False).str.strip()
    )
    pop_df[col_region_pop] = (
        pop_df[col_region_pop].astype(str).str.replace("’", "'", regex=False).str.strip()
    )

    creation_df[col_time_creation] = pd.to_numeric(creation_df[col_time_creation], errors="coerce")
    pop_df[col_time_pop] = pd.to_numeric(pop_df[col_time_pop], errors="coerce")

    # --- Sélection minimale côté population
    pop_df = pop_df[[col_region_pop, col_time_pop, col_pop]].copy()

    # --- Merge (inner => conserve uniquement les couples région/période présents dans les 2)
    merged_df = pd.merge(
        creation_df,
        pop_df,
        left_on=[col_region_creation, col_time_creation],
        right_on=[col_region_pop, col_time_pop],
        how="inner",
    )

    # --- Harmoniser les noms de colonnes dans merged_df (on garde region_nom / TIME_PERIOD)
    if col_region_pop != col_region_creation:
        merged_df = merged_df.drop(columns=[col_region_pop])
    if col_time_pop != col_time_creation:
        merged_df = merged_df.drop(columns=[col_time_pop])

    # --- Construction de Y normalisée
    # Protection simple contre divisions par 0 ou valeurs manquantes
    merged_df["creations_per_1000"] = (merged_df[col_y_creation] / merged_df[col_pop]) * facteur
    merged_df["creations_per_1000"] = merged_df["creations_per_1000"].round(arrondi)

    # --- Export panel
    if out_path_panel is not None:
        merged_df.to_csv(out_path_panel, index=False)

    # --- Moyenne par région (version transversale)
    avg_df = (
        merged_df.groupby(col_region_creation, as_index=False)["creations_per_1000"]
        .mean()
        .round({"creations_per_1000": arrondi})
    )

    # --- Export moyenne
    if out_path_avg is not None:
        avg_df.to_csv(out_path_avg, index=False)

    return merged_df, avg_df


def afficher_top_bottom(
    avg_df: pd.DataFrame,
    col_region: str = "region_nom",
    col_val: str = "creations_per_1000",
    k: int = 3,
) -> None:
    """
    Affiche les k plus faibles et k plus élevées régions selon col_val.
    """
    df_trie = avg_df.sort_values(by=col_val, ascending=True)
    print(f"--- Les {k} plus faibles ---")
    print(df_trie[[col_region, col_val]].head(k))
    print(f"\n--- Les {k} plus élevés ---")
    print(df_trie[[col_region, col_val]].tail(k))


def load_population_region_year(path):
    """
    Charge les données de population par région et par année (INSEE).
    """
    df = pd.read_csv(
        path,
        sep=";",
        dtype=str,
        low_memory=False
    )
    return df



def build_region_name_mapping(region_codes_csv_path):
    """Étape 2 — Construire le mapping 'code région' -> 'nom de région' via le fichier GEO."""
    import numpy as np
    region = pd.read_csv(region_codes_csv_path, sep=";", dtype=str, low_memory=False)

    region_reg = region[region["code"].astype(str).str.contains("REG", na=False)].copy()
    region_reg["code_num"] = (
        region_reg["code"].str.replace("REG-", "", regex=False).astype(int).astype(str)
    )

    if "libelle français" in region_reg.columns:
        lib_col = "libelle français"
    elif "libelle_fr" in region_reg.columns:
        lib_col = "libelle_fr"
    else:
        raise ValueError("Libellé région introuvable (attendu: 'libelle français' ou 'libelle_fr').")

    mapping = dict(zip(region_reg["code_num"], region_reg[lib_col]))
    return mapping


def build_population_region_year(df_raw, mapping, year_min=2014, year_max=2025):
    """
    Étape 3 — Filtrer (années + régions + totaux) puis agréger pour obtenir population par région et par année
    + variation % et densité.
    """
    import numpy as np

    df = df_raw.copy()

    # Filtre: années + GEO_OBJECT région
    df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    df = df[
        df["TIME_PERIOD"].between(year_min, year_max)
        & df["GEO_OBJECT"].astype(str).str.contains("REG", na=False)
    ].copy()

    # Appliquer nom de région
    df["GEO_str"] = df["GEO"].astype(str).str.strip()
    df["region_nom"] = df["GEO_str"].map(mapping)

    # Garder totaux AGE/SEX (si colonnes présentes)
    if "AGE" in df.columns and "SEX" in df.columns:
        df = df[(df["AGE"] == "_T") & (df["SEX"] == "_T")].copy()

    # Agrégation
    df["OBS_VALUE"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    pop = (
        df.groupby(["TIME_PERIOD", "region_nom"], as_index=False)["OBS_VALUE"]
        .sum()
        .rename(columns={"OBS_VALUE": "population"})
        .sort_values(["region_nom", "TIME_PERIOD"])
        .reset_index(drop=True)
    )

    # Variation %
    pop["pop_prev"] = pop.groupby("region_nom")["population"].shift(1)
    pop["variation_population_pourcentage"] = (
        (pop["population"] - pop["pop_prev"]) / pop["pop_prev"] * 100
    ).replace([np.inf, -np.inf], np.nan).round(2)

    # Densité (surface fixe)
    region_areas = {
        "La Réunion": 2505,
        "Corse": 8722,
        "Martinique": 1089,
        "Île-de-France": 12069,
        "Hauts-de-France": 31935,
        "Nouvelle-Aquitaine": 84747,
        "Normandie": 30139,
        "Guadeloupe": 1634,
        "Pays de la Loire": 32430,
        "Centre-Val de Loire": 39530,
        "Grand Est": 57725,
        "Guyane": 83543,
        "Provence-Alpes-Côte d'Azur": 31840,
        "Mayotte": 366,
        "Bretagne": 27498,
        "Bourgogne-Franche-Comté": 48059,
        "Occitanie": 73366,
        "Auvergne-Rhône-Alpes": 71134,
    }

    pop["surface_km2"] = pop["region_nom"].map(region_areas)
    pop["densite_population"] = (pop["population"] / pop["surface_km2"]).replace(
        [np.inf, -np.inf], np.nan
    ).round(2)

    return pop

def plot_population_region(pop_df, region_name):
    import matplotlib.pyplot as plt

    df_region = pop_df[pop_df["region_nom"] == region_name]

    plt.plot(df_region["TIME_PERIOD"], df_region["population"])
    plt.xlabel("Année")
    plt.ylabel("Population")
    plt.title(f"Population en {region_name} de {df_region['TIME_PERIOD'].min()} à {df_region['TIME_PERIOD'].max()}")
    plt.show()


import pandas as pd
import matplotlib.pyplot as plt


def carte_chomage_creation(
    regions_gdf,
    path_chomage: str,
    path_creation: str,
    col_region_geo: str = "LIBELLE_REGION",
    col_region_data: str = "region_nom",
    col_chomage: str = "Taux de chômage par région",
    col_creation: str = "Création moyenne d'entreprise par an entre 2015 et 2025 par 1000 habitants",
):
    """
    Affiche deux cartes côte à côte :
    - taux de chômage moyen par région
    - taux moyen de création d'entreprises par région
    """

    # Harmonisation du nom de région côté géo
    regions = regions_gdf.rename(columns={col_region_geo: col_region_data})

    # Lecture des données
    chomage = pd.read_csv(path_chomage)
    creation = pd.read_csv(path_creation)

    # Moyenne du chômage par région
    chomage_moy = (
        chomage
        .groupby("Region")[col_chomage]
        .mean()
        .reset_index()
        .rename(columns={"Region": col_region_data})
    )

    creation = creation.rename(columns={"Region": col_region_data})

    # Merge géo + données
    gdf_chomage = regions.merge(chomage_moy, on=col_region_data, how="left")
    gdf_creation = regions.merge(creation, on=col_region_data, how="left")

    # Figure
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Carte chômage
    gdf_chomage.plot(
        column=col_chomage,
        cmap="OrRd",
        linewidth=0.8,
        edgecolor="0.8",
        legend=True,
        legend_kwds={"label": "Taux de chômage (%)", "orientation": "horizontal", "shrink": 0.7},
        ax=axes[0],
    )
    axes[0].set_title("Taux de chômage moyen (2015–2025)", fontsize=14, fontweight="bold")
    axes[0].set_axis_off()

    # Carte création
    gdf_creation.plot(
        column=col_creation,
        cmap="OrRd",
        linewidth=0.8,
        edgecolor="0.8",
        legend=True,
        legend_kwds={"label": "Créations pour 1 000 habitants", "orientation": "horizontal", "shrink": 0.7},
        ax=axes[1],
    )
    axes[1].set_title("Taux de création d'entreprises moyen", fontsize=14, fontweight="bold")
    axes[1].set_axis_off()

    plt.tight_layout()
    plt.show()


def analyser_relation_chomage_creation(df, col_chomage='Taux de chômage par région', col_creation='creations_per_1000', region_col=None):
    """
    Génère un scatterplot avec régression et affiche la corrélation.
    
    Args:
        df (pd.DataFrame): Le dataset contenant les données.
        col_chomage (str): Nom de la colonne X (Chômage).
        col_creation (str): Nom de la colonne Y (Création).
        region_col (str, optionnel): Si fourni, colore les points par région.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt

    # 1. Calcul de la corrélation
    corr = df[[col_chomage, col_creation]].corr().iloc[0, 1]
    print(f"--- Analyse Statistique ---")
    print(f"Coefficient de corrélation (Pearson) : {corr:.2f}")
    
    # Interprétation automatique simple
    if corr < -0.3:
        print("Tendance : Inverse (Plus le chômage est haut, moins on crée).")
    elif corr > 0.3:
        print("Tendance : Positive (Le chômage pousse à la création).")
    else:
        print("Tendance : Faible ou neutre.")

    # 2. Création du Graphique
    plt.figure(figsize=(10, 6))
    
    # Si on veut colorer par région (optionnel)
    if region_col:
        # Scatterplot coloré par région + ligne de régression globale (astuce seaborn)
        sns.scatterplot(data=df, x=col_chomage, y=col_creation, hue=region_col, alpha=0.6)
        sns.regplot(data=df, x=col_chomage, y=col_creation, scatter=False, line_kws={'color': 'red'})
    else:
        # Version simple
        sns.regplot(
            data=df, 
            x=col_chomage, 
            y=col_creation, 
            scatter_kws={'alpha': 0.6}, 
            line_kws={'color': 'red'}
        )

    plt.title(f'Relation : Chômage vs Création (Corr: {corr:.2f})')
    plt.xlabel(f'{col_chomage}')
    plt.ylabel(f'{col_creation}')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()


import pandas as pd


def build_regression1_csv(
    path_diplome: str,
    path_chomage: str,
    path_creation_per_1000: str,
    path_population: str,
    out_csv_path: str,
    drop_domtom: bool = True,
) -> pd.DataFrame:
    """
    Construit la table regression1 (panel région x année) et l'exporte en CSV.
    Retourne aussi le DataFrame pour usage direct dans le notebook.

    Contenu regression1 :
    - creations_per_1000
    - Pourcentage_diplomes_superieur
    - Taux de chômage par région
    - variation_population_pourcentage
    - densité de population
    - TIME_PERIOD
    - region_nom
    """

    diplome = pd.read_csv(path_diplome)
    chomage = pd.read_csv(path_chomage)
    creation_per_1000 = pd.read_csv(path_creation_per_1000)
    population = pd.read_csv(path_population)

    # Harmonisation noms colonnes
    chomage = chomage.rename(columns={"Region": "region_nom", "TIME_VALUE": "TIME_PERIOD"})

    # Nettoyage minimal des clés (sécurité)
    for df in (diplome, chomage, creation_per_1000, population):
        if "region_nom" in df.columns:
            df["region_nom"] = (
                df["region_nom"].astype(str).str.replace("’", "'", regex=False).str.strip()
            )
        if "TIME_PERIOD" in df.columns:
            df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

    # Option : retirer DOM-TOM
    if drop_domtom:
        dom_tom = ["Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"]
        for df in (diplome, chomage, creation_per_1000, population):
            if "region_nom" in df.columns:
                df.drop(df[df["region_nom"].isin(dom_tom)].index, inplace=True)

    # Merge diplôme (pas de TIME_PERIOD => constant sur toute la période)
    regression = pd.merge(
        creation_per_1000,
        diplome[["region_nom", "Pourcentage_diplomes_superieur"]],
        on="region_nom",
        how="left",
    )

    # Merge chômage (région x année)
    regression = pd.merge(
        regression,
        chomage[["region_nom", "TIME_PERIOD", "Taux de chômage par région"]],
        on=["region_nom", "TIME_PERIOD"],
        how="left",
    )

    # Merge population (région x année)
    regression = pd.merge(
        regression,
        population[["region_nom", "TIME_PERIOD", "variation_population_pourcentage", "densité de population"]],
        on=["region_nom", "TIME_PERIOD"],
        how="left",
    )

    # Table finale
    regression_finale = regression[
        [
            "creations_per_1000",
            "Pourcentage_diplomes_superieur",
            "Taux de chômage par région",
            "variation_population_pourcentage",
            "densité de population",
            "TIME_PERIOD",
            "region_nom",
        ]
    ].copy()

    # Export CSV (création/écrasement)
    regression_finale.to_csv(out_csv_path, index=False)

    return regression_finale

import pandas as pd


def build_regression2_csv(
    path_diplome: str,
    path_chomage: str,
    path_creation_per_1000: str,
    path_population: str,
    path_salaires: str,
    out_csv_path: str,
    drop_domtom: bool = True,
) -> pd.DataFrame:
    """
    Construit la table regression2 (panel région x année) et l'exporte en CSV.
    Retourne aussi le DataFrame pour usage direct dans le notebook.

    Features de regression2 :
    - Taux de chômage par région
    - Pourcentage_diplomes_superieur
    - variation_population_pourcentage
    - SALAIRE

    + y = creations_per_1000
    + clés : TIME_PERIOD, region_nom
    """

    diplome = pd.read_csv(path_diplome)
    chomage = pd.read_csv(path_chomage)
    creation_per_1000 = pd.read_csv(path_creation_per_1000)
    population = pd.read_csv(path_population)
    salaires = pd.read_csv(path_salaires, sep=";")

    # Harmonisation noms colonnes
    chomage = chomage.rename(columns={"Region": "region_nom", "TIME_VALUE": "TIME_PERIOD"})
    salaires = salaires.rename(columns={"REGION_NOM": "region_nom", "ANNEE1": "TIME_PERIOD"})

    # Nettoyage minimal des clés (sécurité)
    for df in (diplome, chomage, creation_per_1000, population, salaires):
        if "region_nom" in df.columns:
            df["region_nom"] = (
                df["region_nom"].astype(str).str.replace("’", "'", regex=False).str.strip()
            )
        if "TIME_PERIOD" in df.columns:
            df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

    # Fix libellé PACA si besoin (comme dans ton code)
    if "region_nom" in salaires.columns:
        salaires["region_nom"] = salaires["region_nom"].str.replace(
            "Provence-Alpes-Côte d_Azur", "Provence-Alpes-Côte d'Azur", regex=False
        )

    # Option : retirer DOM-TOM
    if drop_domtom:
        dom_tom = ["Guadeloupe", "Martinique", "Guyane", "La Réunion", "Mayotte"]
        for df in (diplome, chomage, creation_per_1000, population, salaires):
            if "region_nom" in df.columns:
                df.drop(df[df["region_nom"].isin(dom_tom)].index, inplace=True)

    # Merge diplôme (constant sur toute la période)
    df = pd.merge(
        creation_per_1000,
        diplome[["region_nom", "Pourcentage_diplomes_superieur"]],
        on="region_nom",
        how="left",
    )

    # Merge chômage (région x année)
    df = pd.merge(
        df,
        chomage[["region_nom", "TIME_PERIOD", "Taux de chômage par région"]],
        on=["region_nom", "TIME_PERIOD"],
        how="left",
    )

    # Merge population (région x année) -> on garde seulement variation_population_pourcentage
    df = pd.merge(
        df,
        population[["region_nom", "TIME_PERIOD", "variation_population_pourcentage"]],
        on=["region_nom", "TIME_PERIOD"],
        how="left",
    )

    # Merge salaires (région x année)
    df = pd.merge(
        df,
        salaires[["region_nom", "TIME_PERIOD", "SALAIRE"]],
        on=["region_nom", "TIME_PERIOD"],
        how="left",
    )

    # Table finale regression2
    regression2 = df[
        [
            "creations_per_1000",
            "Taux de chômage par région",
            "Pourcentage_diplomes_superieur",
            "variation_population_pourcentage",
            "SALAIRE",
            "TIME_PERIOD",
            "region_nom",
        ]
    ].copy()

    regression2 = regression2.dropna()
    regression2.to_csv(out_csv_path, index=False)

    return regression2
