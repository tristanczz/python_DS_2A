import pandas as pd 
import cartiflette as ct
import magic
from cartiflette import carti_download

data = pd.read_csv("data/emploi_regions_2020.csv")
df = pd.DataFrame(data)

# Exemple d'utilisation de cartiflette pour télécharger les frontières des départements français
gdf = carti_download(
    values=["France"],
    borders="DEPARTEMENT",
    filter_by="FRANCE_ENSEMBLE",
    source="EXPRESS-COG-TERRITOIRE",
    vectorfile_format="geojson",
    year=2022
)




