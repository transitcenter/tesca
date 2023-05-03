# This script demonstrates how to run a project

import os

from tesca.analysis import Analysis

from config import CENSUS_API_KEY

a = Analysis.from_config_file(os.path.join("cache", "project-id", "config.yml"))

# Create a demographics CSV file using the config demographic keys
a.fetch_demographic_data()

#  DATA VALIDATION  #
# Fist, data validation can happen on the GTFS files
a.validate_gtfs_data()

# Validation for internal data consistency
a.validate_analysis_area()

# Validation for demographic coverage of impact area
a.validate_demographics()

# Validation for opportunity coverage of analysis area
a.validate_opportunities()

#  ANALYSIS  #
# Compute the travel time matrix - this takes a while
a.compute_travel_times()
# Compute the access metrics as configured in the config.yml file
a.compute_metrics()
# Compute the scenario comparison of the metrics
a.compare_scenarios()
# Summarize these metrics (and comparison) across imapct area demographics
a.compute_summaries()
# Compute unreachable destinations
a.compute_unreachable()
