import argparse
import os
import traceback

import yaml

from tesca.analysis import Analysis, CACHE_FOLDER

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ID", help="Analysis id")
args = parser.parse_args()
analysis_id = args.ID


def update_status(analysis_id, message, stage=None, value=None):
    if not os.path.exists(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml")):
        with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "w") as outfile:
            yaml.dump({"message": None, "stage": None, "value": None}, outfile)

    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "r") as infile:
        status = yaml.safe_load(infile)

    status["message"] = message

    if stage is not None:
        status["stage"] = stage
    if value is not None:
        status["value"] = value

    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "w") as outfile:
        yaml.dump(status, outfile)


# Run the actual analysis!
try:
    a = Analysis.from_config_file(os.path.join("cache", analysis_id, "config.yml"))

    update_status(a.uid, "computing travel times", stage="run", value=0)
    a.compute_travel_times()

    update_status(a.uid, "computing metrics", value=60)
    a.compute_metrics()

    update_status(a.uid, "performing scenario comparison", value=70)
    a.compare_scenarios()

    update_status(a.uid, "downloading demographic data", value=80)
    a.fetch_demographic_data()

    update_status(a.uid, "computing demographic summaries", value=90)
    a.compute_summaries()

    update_status(a.uid, message="finished running analysis!", stage="results", value=100)

except Exception as e:
    update_status(a.uid, f"broken: {e}", stage="error")
    traceback.print_exc()
