import json
import os
import yaml

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

a = Analysis.from_config_file(os.path.join("cache", "20230707105554", "config.yml"))
a.compute_travel_times()
# Compute the travel time matrix - this takes a while
# a.compute_travel_times()
# Compute the access metrics as configured in the config.yml file
# a.compute_metrics()
# Compute the scenario comparison of the metrics
# a.compare_scenarios()
# a.fetch_demographic_data()
# Summarize these metrics (and comparison) across imapct area demographics
# a.compute_summaries()
# Compute unreachable destinations
# a.compute_unreachable()
