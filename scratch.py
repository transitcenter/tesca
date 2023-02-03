import os

from tesca.analysis import Analysis

a = Analysis.from_config_file(os.path.join("cache", "ny-test", "config.json"))

a.compute_metrics()
