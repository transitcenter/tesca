import os

from tesca.analysis import Analysis


# conn = cenpy.products.APIConnection("ACSDT5Y2021")
# data = conn.query(
#     ["B02009_001E"],
#     geo_unit="block group",
#     geo_filter={"state": "17", "county": "031"},
#     apikey="42d198a43a10e9c91fdf19fcc15c8f81f6bf55a2",
# )
# data["bg_id"] = data["state"] + data["county"] + data["tract"] + data["block group"]
# data[["bg_id", "B02009_001E"]].to_csv("chicago_black.csv", index=False)
# # acs.from_place("Chicago, IL", variables=["B02009_001"], level="block").to_csv(
# #     "chicago_black.csv"
# # )

a = Analysis.from_config_file(os.path.join("cache", "chicago-test", "config.json"))

# a.validate_gtfs_data()
# a.validate_demographics()
# a.validate_opportunities()

# a.compute_travel_times()
# a.compute_metrics()
# a.compare_scenarios()
a.compute_weighted_summaries()
