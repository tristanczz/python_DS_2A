# Les régions françaises les plus dynamiques : analyse de la création d’entreprises

Ce projet analyse les déterminants géographiques et économiques de la création d'entreprises en France métropolitaine sur la période **2015-2024**. Il a été réalisé dans le cadre du cours de **Python pour la Data Science** à l'**ENSAE Paris**.

## Auteurs
* **Tom Proust**
* **Tristan Czarnecki**
* **Thomas Favant**

## Objectifs du projet
Alors que l'Île-de-France et la région PACA affichent un fort dynamisme, d'autres régions peinent à renouveler leur tissu productif. Ce projet cherche à répondre à la question : **Quels sont les déterminants profonds de cette géographie entrepreneuriale ?**

La démarche s'articule autour de trois axes :
1. **Mesurer** les écarts de création à l'échelle régionale (taux normalisés pour 1 000 habitants).
2. **Identifier** les corrélations spatiales avec des variables socio-économiques (Chômage, Diplômes, Densité, Salaires).
3. **Modéliser** l'impact de ces variables via une approche économétrique (Régression linéaire, Lasso).

## Structure du dépôt
Le projet est organisé comme suit :

* `rendu_final.ipynb` : Le notebook principal contenant l'intégralité de l'analyse, des traitements de données aux modèles économétriques.
* `Extraction variables explicatives/` contient les fonctions utilisées pour le chargement et le nettoyage des données.
* `mes_fonctions.py` contient les fonctions implémentées pour l'analyse des données et leur interprétation propre.
* `data/` : Dossier contenant les jeux de données (données brutes INSEE et variables explicatives transformées).

## Installation et Prérequis
Le projet utilise **Python 3**. Pour faire tourner le notebook, il faudra installer les bibliothèques suivantes :
* **Manipulation de données** : `pandas`, `numpy`
* **Visualisation** : `matplotlib`, `seaborn`
* **Cartographie** : `geopandas`, `cartiflette`
* **Modélisation** : `statsmodels`, `scikit-learn`

Vous pouvez installer les dépendances principales via pip :
```bash
pip install pandas numpy matplotlib seaborn statsmodels geopandas cartiflette scikit-learn