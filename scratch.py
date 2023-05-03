import json
import os
import yaml

from tesca.analysis import Analysis
import pandas as pd

a = Analysis.from_config_file(os.path.join("cache", "septa-redesign-weekend", "config.yml"))
print(a.settings)
a.fetch_demographic_data()
