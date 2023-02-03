import datetime
import geopandas 
import time

from r5py import TransportNetwork, TravelTimeMatrixComputer, TransitMode, LegMode


points = geopandas.read_file("ny_data/urban_centroid.geojson")
points['id'] = points['GEOID']


start = time.time()

tn = TransportNetwork(
    'ny_data/NewYork.osm.pbf',
    [
        "ny_data/feeds_2023-01-27/bronx.zip",
        "ny_data/feeds_2023-01-27/brooklyn.zip",
        "ny_data/feeds_2023-01-27/queens.zip",
        "ny_data/feeds_2023-01-27/lirr.zip",
        "ny_data/feeds_2023-01-27/staten_island.zip",
        "ny_data/feeds_2023-01-27/subway.zip"
    ]
)

ttmc = TravelTimeMatrixComputer(
    tn,
    origins=points,
    destinations=points,
    departure=datetime.datetime(2023,2,2,8,30),
    transport_modes=[TransitMode.TRANSIT, LegMode.WALK]
)

travel_time_matrix = ttmc.compute_travel_times()

end = time.time()
print(f"That took: {end-start}")

travel_time_matrix.to_csv("ny_data/ny_ttm.csv", index=False)
travel_time_matrix['travel_time'] = travel_time_matrix['travel_time'].astype('int64')
means = travel_time_matrix['from_id', 'travel_time'].groupby('from_id').mean()
means.to_csv('ny_data/ny_ttm_means.csv', index=False)

