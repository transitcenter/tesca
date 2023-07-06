from datetime import datetime
import os
import pickle
import sys
import time
import yaml

from flask import Flask, render_template, redirect, send_from_directory, session, request
from flask_wtf.csrf import validate_csrf, CSRFProtect

from flask_executor import Executor
import pandas as pd
from werkzeug.utils import secure_filename
from tesca.analysis import CACHE_FOLDER, Analysis

from config import DevelopmentConfig
from forms import ConfigForm, OpportunitiesUploadForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["WTF_CSRF_SECRET_KEY"] = SECRET_KEY
csrf = CSRFProtect(app)

executor = Executor(app)


def run_validation(a):
    print("Validation run executed")
    # Let's run through the validation
    update_status(a.uid, "validating analysis area", value=10)
    a.validate_analysis_area()
    update_status(a.uid, "validating opportunities file", value=20)
    a.validate_opportunities()
    # update_status(a.uid, message="Validated opportunities", value=20)
    # a.validate_demographics()
    update_status(a.uid, "validating GTFS data", value=30)
    a.validate_gtfs_data()
    update_status(a.uid, message="awaiting validation review from user", value=100)
    with open(os.path.join(CACHE_FOLDER, a.uid, "analysis.p"), "wb") as outfile:
        pickle.dump(a, outfile)
    return True


def update_status(analysis_id, message, stage=None, value=None):
    if not os.path.exists(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml")):
        with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "w") as outfile:
            yaml.dump({"message": None, "status": None, "value": None}, outfile)

    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "r") as infile:
        status = yaml.safe_load(infile)

    status["message"] = message

    if stage is not None:
        status["stage"] = stage
    if value is not None:
        status["value"] = value

    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "w") as outfile:
        yaml.dump(status, outfile)


def get_status(analysis_id):
    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "r") as infile:
        return yaml.safe_load(infile)


@app.route("/", methods=["GET", "POST"])
def home():
    form = OpportunitiesUploadForm()

    print(form.errors)
    if form.validate_on_submit():
        print("Form Validated")
        analysis_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # Make a directory for the project
        upload_folder = os.path.join(CACHE_FOLDER, analysis_id)
        os.mkdir(upload_folder)

        # Initialize the analysis object
        with open("default_config.yml", "r") as infile:
            config = yaml.safe_load(infile)
        config["uid"] = analysis_id
        a = Analysis(config=config)

        # Store the opportunities data
        opportunities_filename = secure_filename(form.file.data.filename)
        form.file.data.save(os.path.join(upload_folder, opportunities_filename))

        # Create a status file
        update_status(analysis_id, "awaiting configuration", stage="configure", value=0)

        opp_df = pd.read_csv(os.path.join(upload_folder, "opportunities.csv"), dtype={"bg_id": str})

        # Fetch the block groups
        a.fetch_block_groups_from_bg_ids(opp_df["bg_id"].to_list())

        columns = [c for c in opp_df.columns if c != "bg_id"]
        opp_dict = dict()
        for c in columns:
            opp_dict[c] = {"method": None, "name": None, "parameters": []}

        config["opportunities"] = opp_dict

        # Write the analysis configured file
        with open(os.path.join(CACHE_FOLDER, analysis_id, "analysis.p"), "wb") as outfile:
            pickle.dump(a, outfile)

        return redirect(f"/configure/{analysis_id}")

    return render_template("home.jinja2", form=form)


@app.route("/configure/<analysis_id>", methods=["GET", "POST"])
def configure(analysis_id):
    # Unpickle the analysis
    with open(os.path.join(CACHE_FOLDER, analysis_id, "analysis.p"), "rb") as infile:
        a = pickle.load(infile)

    opp_fields = []
    opp_keys = list(a.config["opportunities"].keys())
    for o in opp_keys:
        opp_fields.append({"opportunity": o, "prettyname": o})
        # temp_form = OpportunityMeasureForm()
        # form.opportunities.append_entry(temp_form.data)

    form = ConfigForm(opportunities=opp_fields)

    for idx, f in enumerate(form.opportunities):
        f.opportunity.data = opp_keys[idx]

        print(form.errors)

    if form.validate_on_submit():
        print("Form Validated")
        upload_folder = os.path.join(CACHE_FOLDER, analysis_id)

        # Store the OSM Data
        form.osm.data.save(os.path.join(upload_folder, "osm.pbf"))

        # Store the impact area
        form.impact_area.data.save(os.path.join(upload_folder, "impact_area.csv"))

        # TODO: Handle the demographics file

        # Make the GTFS Scenario 0 folder and write the files
        for gtfs0_file in form.scenario0_gtfs.data:
            gtfs_filename = secure_filename(gtfs0_file.filename)
            gtfs0_file.save(os.path.join(upload_folder, "gtfs0", gtfs_filename))

        # Make the GTFS Scenario 1 folder and write the files
        for gtfs1_file in form.scenario1_gtfs.data:
            gtfs_filename = secure_filename(gtfs1_file.filename)
            gtfs1_file.save(os.path.join(upload_folder, "gtfs1", gtfs_filename))

        a.config["analyst"] = form.analyst.data
        a.config["project"] = form.project.data
        a.config["description"] = form.description.data
        a.config["uid"] = analysis_id
        a.config["infinity_value"] = form.infinity.data
        a.config["max_time_walking"] = form.max_time_walking.data

        a.config["scenarios"][0]["duration"] = form.scenario0_duration.data
        a.config["scenarios"][0]["name"] = form.scenario0_name.data
        a.config["scenarios"][0]["start_datetime"] = form.scenario0_start.data

        if "TRANSIT" in form.scenario0_modes.data:
            a.config["scenarios"][0]["transit_modes"] = ["TRANSIT"]
        else:
            a.config["scenarios"][0]["transit_modes"] = form.scenario0_modes.data

        a.config["scenarios"][1]["duration"] = form.scenario1_duration.data
        a.config["scenarios"][1]["name"] = form.scenario1_name.data
        a.config["scenarios"][1]["start_datetime"] = form.scenario1_start.data

        if "TRANSIT" in form.scenario1_modes.data:
            a.config["scenarios"][1]["transit_modes"] = ["TRANSIT"]
        else:
            a.config["scenarios"][1]["transit_modes"] = form.scenario1_modes.data

        with open(os.path.join(upload_folder, "config.yml"), "w") as outfile:
            yaml.dump(a.config, outfile)

        # Start the validation process
        executor.submit(run_validation, a=a)

        return redirect(f"/validate/{analysis_id}")
    return render_template("configure.jinja2", form=form, config_json={"analysis_id": analysis_id})


@app.route("/gtfs/<analysis_id>")
def gtfs(analysis_id):
    pass


@app.route("/validate/<analysis_id>")
def validate(analysis_id):
    return render_template("validate.jinja2", analysis_id=analysis_id)


@app.route("/status/<analysis_id>")
def status(analysis_id):
    return get_status(analysis_id)


@app.route("/info/<analysis_id>")
def log_info(analysis_id):
    info = pd.read_csv(os.path.join(CACHE_FOLDER, analysis_id, "info.log"), header=None)
    info.columns = ["timestamp", "level", "message"]
    info["timestamp"] = pd.to_datetime(info["timestamp"])
    info = info.sort_values("timestamp", ascending=True)
    return info.to_dict(orient="records")


@app.route("/cache/<path:path>")
def send_cache(path):
    # Get the full path:
    fullpath = os.path.join("cache", path)
    file = os.path.basename(fullpath)
    dir = os.path.dirname(fullpath)
    return send_from_directory(dir, file)


if __name__ == "__main__":
    app.run()
