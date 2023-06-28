import json
import os
import yaml

from tesca.analysis import Analysis
import pandas as pd

baltimore = {
    "Maryland": [
        "Baltimore City", 
        "Queen Anne",
        "Harford County",
        "Howard County",
        "Baltimore County",
        "Anne Arundel County",
        "Carroll County"
        ],  # Maryland
}

a = Analysis.from_config_file(os.path.join("cache", "baltimore-1", "config.yml"))
a.fetch_block_groups(baltimore, overwrite=True)
