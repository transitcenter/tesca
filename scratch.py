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

a = Analysis.from_config_file(os.path.join("cache", "20230706115529", "config.yml"))
a.validate_gtfs_data()
# a.fetch_block_groups_from_bg_ids(bg_ids)
# a.fetch_block_groups(baltimore, overwrite=True)
