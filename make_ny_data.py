import geopandas as gpd
import pandas as pd

bgs = gpd.read_file("ny_data/block_group_poly.geojson")
urban = pd.read_csv("ny_data/urban.csv", dtype={'bg_id':'str'})
equity = pd.read_csv("ny_data/equity.csv", dtype={'bg_id':'str'})

urban_bgs = bgs[bgs['GEOID'].astype('str').isin(urban['bg_id'])].copy()
urban_bgs.to_file("ny_data/urban_bg.geojson", driver="GeoJSON")
urban_bgs['geometry'] = urban_bgs['geometry'].centroid
urban_bgs.to_file("ny_data/urban_centroid.geojson", driver="GeoJSON")

brooklyn = bgs[bgs['CGEOID'].astype('str') == "36047"].copy()
brooklyn.to_file("ny_data/brooklyn.geojson", driver="GeoJSON")