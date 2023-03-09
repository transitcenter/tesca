import os

os.environ["USE_PYGEOS"] = "0"
import geopandas as gpd
import pandas as pd

base_folder = os.path.join("cache", "chicago-test")

bgs = gpd.read_file(
    os.path.join(base_folder, "analysis_polygons.geojson"), dtype={"GEOID": str}
)
impact_area = pd.read_csv(
    os.path.join(base_folder, "impact_area.csv"), dtype={"bg_id": str}
)
demographics = pd.read_csv(
    os.path.join(base_folder, "demographics_raw.csv"), dtype={"bg_id": str}
)
opportunities = pd.read_csv(
    os.path.join(base_folder, "opportunities_raw.csv"), dtype={"bg_id": str}
)

msa = pd.read_csv(os.path.join(base_folder, "msa.csv"), dtype={"bg_id": str})

bgs = bgs[bgs["GEOID"].isin(msa["bg_id"])]
bgs = bgs[bgs["GEOID"].isin(opportunities["bg_id"])]

# First let's make sure the opportunities we have fit within the analysis area
bgs = bgs.to_crs(epsg=26916)
bgs = bgs.rename(columns={"GEOID": "id"})
bgs["geometry"] = bgs["geometry"].centroid
bgs = bgs.to_crs(epsg=4326)
bgs.to_file(os.path.join(base_folder, "analysis_centroids.geojson"), driver="GeoJSON")

demographics = demographics[demographics["bg_id"].isin(impact_area["bg_id"])]
demographics.to_csv(os.path.join(base_folder, "demographics.csv"), index=False)

opportunities = opportunities[opportunities["bg_id"].isin(bgs["id"])]
opportunities.to_csv(os.path.join(base_folder, "opportunities.csv"), index=False)

print(opportunities[~opportunities["bg_id"].isin(bgs["id"])])
