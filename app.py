from datetime import datetime
import os
import pickle
import sys
import time
import yaml

from flask import Flask, render_template, redirect
import pandas as pd
from werkzeug.utils import secure_filename
from wtforms import Label

from tesca.analysis import CACHE_FOLDER, Analysis

from forms import ConfigForm, OpportunityConfigForm, OpportunitiesUploadForm, OpportunityMeasureForm

app = Flask(__name__)


SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY


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
        with open(os.path.join(upload_folder, "status.yml"), "w") as outfile:
            yaml.dump({"stage": "configuration"}, outfile)

        opp_df = pd.read_csv(os.path.join(upload_folder, "opportunities.csv"), dtype={"bg_id": str})
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


@app.route("/opportunities/<analysis_id>", methods=["GET", "POST"])
def opportunities(analysis_id):
    # TODO: Pull the geospatial data
    # a.fetch_block_groups()
    # TODO: Pull the demographic data
    form = OpportunityConfigForm()


@app.route("/configure/<analysis_id>", methods=["GET", "POST"])
def configure(analysis_id):
    # Unpickle the analysis
    with open(os.path.join(CACHE_FOLDER, analysis_id, "analysis.p"), "rb") as infile:
        a = pickle.load(infile)

    # form = ConfigForm()

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

        # Store the Block Group Data
        bg_filename = secure_filename(form.block_groups.data.filename)
        form.block_groups.data.save(os.path.join(upload_folder, bg_filename))

        # Store the OSM Data
        osm_filename = secure_filename(form.osm.data.filename)
        form.osm.data.save(os.path.join(upload_folder, osm_filename))

        # TODO: Handle the demographics file

        # Make the GTFS Scenario 0 folder and write the files
        os.mkdir(os.path.join(upload_folder, "gtfs0"))
        for gtfs0_file in form.scenario0_gtfs.data:
            gtfs_filename = secure_filename(gtfs0_file.filename)
            gtfs0_file.save(os.path.join(upload_folder, "gtfs0", gtfs_filename))

        # Make the GTFS Scenario 1 folder and write the files
        os.mkdir(os.path.join(upload_folder, "gtfs1"))
        for gtfs1_file in form.scenario1_gtfs.data:
            gtfs_filename = secure_filename(gtfs1_file.filename)
            gtfs1_file.save(os.path.join(upload_folder, "gtfs1", gtfs_filename))

        # Let's finish creating the config file:
        with open("default_config.yml", "r") as infile:
            config = yaml.safe_load(infile)

        config["analyst"] = form.analyst.data
        config["project"] = form.project.data
        config["description"] = form.description.data
        config["uid"] = analysis_id
        config["infinity_value"] = form.infinity.data
        config["max_time_walking"] = form.max_time_walking.data

        config["scenarios"][0]["duration"] = form.scenario0_duration.data
        config["scenarios"][0]["name"] = form.scenario0_name.data
        config["scenarios"][0]["start_datetime"] = form.scenario0_start.data
        if "TRANSIT" in form.scenario0_modes.data:
            config["scenarios"][0]["transit_modes"] = ["TRANSIT"]
        else:
            config["scenarios"][0]["transit_modes"] = form.scenario0_modes.data

        config["scenarios"][1]["duration"] = form.scenario1_duration.data
        config["scenarios"][1]["name"] = form.scenario1_name.data
        config["scenarios"][1]["start_datetime"] = form.scenario1_start.data
        if "TRANSIT" in form.scenario1_modes.data:
            config["scenarios"][1]["transit_modes"] = ["TRANSIT"]
        else:
            config["scenarios"][1]["transit_modes"] = form.scenario1_modes.data

        with open(os.path.join(upload_folder, "config.yml"), "w") as outfile:
            yaml.dump(config, outfile)

        return redirect(f"/validation/{analysis_id}")
    return render_template("configure.jinja2", form=form)


@app.route("/validation/<analysis_id>")
def validation(analysis_id):
    return render_template("validation.jinja2")


@app.route("/time")
def get_current_time():
    return {"time": time.time()}
