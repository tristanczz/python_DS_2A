import pandas as pd 
import cartiflette as ct 



data = pd.read_csv("data/emploi_regions_2020.csv")
df = pd.DataFrame(data)


carte = ct.CarteEmploi(
    df,
    valeur="emploi_total",
    region="region_code",
    annee=2020,
    title="Emploi total par région en 2020",
    subtitle="Source : INSEE - Données d'emploi par région",
    unit="nombre d'emplois",
)

carte.plot()