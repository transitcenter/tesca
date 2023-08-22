import json
import os
import yaml

import pygris

from tesca.analysis import Analysis
import pandas as pd

# baltimore = {
#     "Maryland": [
#         "Baltimore City",
#         "Queen Anne",
#         "Harford County",
#         "Howard County",
#         "Baltimore County",
#         "Anne Arundel County",
#         "Carroll County"
#         ],  # Maryland
# }

# opp = pd.read_csv(os.path.join("cache", "septa-redesign-half-mile", "opportunities.csv"), dtype={"bg_id": str})
# bg_ids = opp.bg_id.to_list()

a = Analysis.from_config_file(os.path.join("cache", "20230822091044", "config.yml"))
# a.fetch_demographic_data()
# a.compute_travel_times()
# Compute the travel time matrix - this takes a while
a.compute_travel_times()
# Compute the access metrics as configured in the config.yml file
# a.compute_metrics()
# # Compute the scenario comparison of the metrics
# a.compare_scenarios()
# a.fetch_demographic_data()
# # Summarize these metrics (and comparison) across imapct area demographics
# a.compute_summaries()
# # Compute unreachable destinations
# a.compute_unreachable()

# us_counties = pygris.counties(cb=True, resolution="20m", cache=True, year=2021)

# us_counties.drop("geometry", axis=1).to_csv("states_counties.csv", index=False)

# lodes = pd.read_csv("https://lehd.ces.census.gov/data/lodes/LODES7/pa/wac/pa_wac_S000_JT00_2019.csv.gz")
# print(lodes.head())
