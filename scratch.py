import os

from tesca.analysis import Analysis

a = Analysis.from_config_file(os.path.join("cache", "ny-test-3b-modes", "config.json"))

a.compute_travel_times()
a.compute_metrics()
a.compare_scenarios()
a.weighted_summaries()
