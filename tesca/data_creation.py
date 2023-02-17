import pandas as pd
import geopandas as gpd

hc = pd.read_csv("ny_data/healthcare.csv", dtype={"bg_id": str})

pop = pd.read_csv("ny_data/population.csv", dtype={"bg_id": str})

area = gpd.read_file(
    "cache/ny-test-3boroughs/analysis_centroids.geojson", dtype={"id": str}
)

print(area.shape[0])

hc = hc[hc.bg_id.isin(area["id"])]
pop = pop[pop.bg_id.isin(area["id"])][["bg_id", "pop_total"]]

print("Pop after filter:", pop.shape[0])
print("HC After filter:", hc.shape[0])

# op = op[op.bg_id.isin(area["id"])]
op = pd.merge(pop, hc, on="bg_id", how="outer")
op = op.fillna(0)
op["hospitals"] = op["hospitals"].astype(int)
op["pharmacies"] = op["pharmacies"].astype(int)
op["urgent_care_facilities"] = op["urgent_care_facilities"].astype(int)

print(op.shape[0])

op.to_csv("cache/ny-test-3boroughs/opportunities.csv", index=False)
