import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def analyser_relation_chomage_creation(df, col_chomage='Taux de chômage par région', col_creation='creations_per_1000', region_col=None):
    """
    Génère un scatterplot avec régression et affiche la corrélation.
    
    Args:
        df (pd.DataFrame): Le dataset contenant les données.
        col_chomage (str): Nom de la colonne X (Chômage).
        col_creation (str): Nom de la colonne Y (Création).
        region_col (str, optionnel): Si fourni, colore les points par région.
    """
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
