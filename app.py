#!python

from datetime import datetime, timedelta
import json
import os
import pickle
import shutil
import subprocess
import traceback
import yaml


from flask import Flask, render_template, redirect, send_from_directory, send_file, request, Response
from flask_wtf.csrf import validate_csrf, CSRFProtect

from flask_executor import Executor
import pandas as pd
from pygris import block_groups
from werkzeug.utils import secure_filename

from tesca.analysis import CACHE_FOLDER, Analysis

from config import DevelopmentConfig
from forms import ConfigForm, OpportunitiesUploadForm

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["WTF_CSRF_SECRET_KEY"] = SECRET_KEY
app.config["EXECUTOR_PROPAGATE_EXCEPTIONS"] = True

csrf = CSRFProtect(app)
executor = Executor(app)

# ---------------------#
## UTILITY FUNCTIONS ##
# ---------------------#


def run_validation(analysis_id):
    print("Validation run executed")
    a = Analysis(config=get_config(analysis_id))
    # Let's run through the validation
    update_status(a.uid, "validating analysis area", stage="validate", value=10)
    a.validate_analysis_area()
    update_status(a.uid, "validating opportunities file", value=20)
    a.validate_opportunities()
    update_status(a.uid, "validating GTFS data", value=30)
    a.validate_gtfs_data()
    update_status(a.uid, message="awaiting validation review from user", value=100)
    return True


# Try this again using the object already created?
@executor.job
def run_analysis(a):
    print("Analysis run executed")
    try:
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

        update_status(a.uid, "computing unreachable destinations", value=95)
        a.compute_unreachable()

        update_status(a.uid, message="finished running analysis!", stage="results", value=100)

    except Exception as e:
        update_status(a.uid, f"broken: {e}", stage="error")
        traceback.print_exc()
    return True


def run_analysis_as_subprocess(analysis_id):
    try:
        subprocess.Popen(["python", "do_analysis.py", "--ID", str(analysis_id)])
    except Exception as e:
        update_status(analysis_id, f"broken: {e}", stage="error")
        traceback.print_exc()
    return True


SUFFIXES = {1: "st", 2: "nd", 3: "rd"}


def get_ordinal(i):
    if 10 <= i % 100 <= 20:
        return "th"
    else:
        return SUFFIXES.get(i % 10, "th")


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


def get_status(analysis_id):
    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "status.yml"), "r") as infile:
        return yaml.safe_load(infile)


def get_config(analysis_id):
    with open(os.path.join(CACHE_FOLDER, str(analysis_id), "config.yml"), "r") as infile:
        return yaml.safe_load(infile)


# ----------#
## ROUTES ##
# ----------#


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
        # with open(os.path.join(CACHE_FOLDER, analysis_id, "analysis.p"), "wb") as outfile:
        #     pickle.dump(a, outfile)

        a.write_config_file()

        return redirect(f"/configure/{analysis_id}")

    return render_template("home.jinja2", form=form)


@app.route("/cache/<path:path>")
def send_cache(path):
    # Get the full path:
    fullpath = os.path.join("cache", path)
    file = os.path.basename(fullpath)
    dir = os.path.dirname(fullpath)
    return send_from_directory(dir, file)


@app.route("/config/<analysis_id>")
def config(analysis_id):
    return get_config(analysis_id)


@app.route("/configure/<analysis_id>", methods=["GET", "POST"])
def configure(analysis_id):
    a = Analysis(config=get_config(analysis_id))

    opp_fields = []
    opp_keys = list(a.config["opportunities"].keys())

    for o in opp_keys:
        opp_fields.append({"opportunity": o, "prettyname": o, "unit": ""})

    form = ConfigForm(opportunities=opp_fields)

    for idx, f in enumerate(form.opportunities):
        f.opportunity.data = opp_keys[idx]

    if form.validate_on_submit():
        print("Form Validated")
        upload_folder = os.path.join(CACHE_FOLDER, analysis_id)

        # Store the OSM Data
        form.osm.data.save(os.path.join(upload_folder, "osm.pbf"))

        # Store the impact area
        form.impact_area.data.save(os.path.join(upload_folder, "impact_area.csv"))

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

        # Opportunity configuration
        a.config["opportunities"] = dict()
        for opportunity_form in form.opportunities:
            this_opportunity = dict()
            this_opportunity["method"] = opportunity_form.method.data
            this_opportunity["name"] = opportunity_form.prettyname.data
            # this_opportunity["description"] = opportunity_form.description.data
            this_opportunity["parameters"] = [int(x.strip()) for x in opportunity_form.parameters.data.split(",")]
            if this_opportunity["method"] == "travel_time":
                this_opportunity["unit"] = "minutes"
            else:
                this_opportunity["unit"] = opportunity_form.unit.data
            a.config["opportunities"][opportunity_form.opportunity.data] = this_opportunity

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

        a.write_config_file()

        # Start the validation process
        executor.submit(run_validation, analysis_id=analysis_id)

        return redirect(f"/validate/{analysis_id}")
    return render_template("configure.jinja2", form=form, config_json={"analysis_id": analysis_id})


@app.route("/counties/", methods=["GET", "POST"])
def counties():
    context = {"gh": "as"}
    if request.method == "POST":
        data_type = request.form.get("data-type")
        print(data_type)
        selected_counties = request.form.getlist("selected-counties")
        counties_by_state = {}
        bg_dfs = []
        for county in selected_counties:
            state_fp = county[:2]
            county_fp = county[2:]
            if state_fp not in counties_by_state.keys():
                counties_by_state[state_fp] = [county_fp]
            else:
                counties_by_state[state_fp].append(county_fp)

        with open("settings.yml", "r") as infile:
            settings = yaml.safe_load(infile)

        for state in counties_by_state.keys():
            bgs = block_groups(state=state, county=counties_by_state[state], year=settings["census_year"], cb=False)
            bg_dfs.append(bgs)

        bg_df = pd.concat(bg_dfs, axis="index")
        bg_df = bg_df.rename(columns={"GEOID": "bg_id"})
        bg_df = bg_df[["bg_id", "geometry"]]

        if data_type == "polygons":
            return Response(
                bg_df.to_json(),
                mimetype="application/json",
                headers={"Content-Disposition": "attachment;filename=block_groups.geojson"},
            )
        else:
            return Response(
                bg_df.to_csv(),
                mimetype="text/csv",
                headers={"Content-disposition": "attachment; filename=block_groups.csv"},
            )

    return render_template("counties.jinja2", **context)


@app.route("/delete/<analysis_id>")
def delete_project(analysis_id):
    confirm = request.args.get("confirm")
    if confirm == "yes":
        shutil.rmtree(os.path.join(CACHE_FOLDER, analysis_id))
        return redirect("/projects")
    config = get_config(analysis_id)
    status = get_status(analysis_id)
    date_started = datetime.strptime(analysis_id, "%Y%m%d%H%M%S").strftime("%B %d, %Y at %H:%M")
    info = {"config": config, "status": status, "date_started": date_started}
    return render_template("delete.jinja2", info=info)


@app.route("/info/<analysis_id>")
def log_info(analysis_id):
    info = pd.read_csv(os.path.join(CACHE_FOLDER, analysis_id, "info.log"), header=None)
    info.columns = ["timestamp", "level", "message"]
    info["timestamp"] = pd.to_datetime(info["timestamp"])
    info = info.sort_values("timestamp", ascending=True)
    return info.to_dict(orient="records")


@app.route("/guide/", defaults={"filename": "index.html"})
@app.route("/guide/<path:filename>")
def guide(filename):
    print(filename)
    path = os.path.join("docs/build/html", filename)
    return send_from_directory(os.path.join(os.path.dirname(__file__), "docs", "build", "html"), filename)


@app.route("/gtfs/<analysis_id>")
def gtfs(analysis_id):
    # Compile the appropriate reports into the appropriate JSON
    # TODO: Add code for when there hasn't been any validation yet.
    # Scenario 0
    gtfs_json = dict()
    gtfs0_folder = os.path.join(CACHE_FOLDER, analysis_id, "gtfs0")
    gtfs0 = dict()
    for path in os.listdir(gtfs0_folder):
        gtfs_filepath = os.path.join(gtfs0_folder, path)
        if os.path.isfile(gtfs_filepath) and os.path.splitext(gtfs_filepath)[1] == ".zip":
            gtfs_validation_foldername = os.path.splitext(path)[0]
            print(gtfs_validation_foldername)
            gtfs0[gtfs_validation_foldername] = {
                "ERROR": {"total_count": 0, "unique_count": 0},
                "WARNING": {"total_count": 0, "unique_count": 0},
                "INFO": {"total_count": 0, "unique_count": 0},
            }
            # Now grab the number of errors, warnings, etc
            with open(
                os.path.join(
                    CACHE_FOLDER,
                    analysis_id,
                    "validation",
                    "gtfs_validation0",
                    gtfs_validation_foldername,
                    "report.json",
                )
            ) as validation_report_file:
                validation_report = json.load(validation_report_file)

            for notice in validation_report["notices"]:
                gtfs0[gtfs_validation_foldername][notice["severity"]]["total_count"] += notice["totalNotices"]
                gtfs0[gtfs_validation_foldername][notice["severity"]]["unique_count"] += 1

    gtfs_json["0"] = gtfs0

    gtfs1_folder = os.path.join(CACHE_FOLDER, analysis_id, "gtfs1")
    gtfs1 = dict()
    for path in os.listdir(gtfs1_folder):
        gtfs_filepath = os.path.join(gtfs1_folder, path)
        if os.path.isfile(gtfs_filepath) and os.path.splitext(gtfs_filepath)[1] == ".zip":
            gtfs_validation_foldername = os.path.splitext(path)[0]
            gtfs1[gtfs_validation_foldername] = {
                "ERROR": {"total_count": 0, "unique_count": 0},
                "WARNING": {"total_count": 0, "unique_count": 0},
                "INFO": {"total_count": 0, "unique_count": 0},
            }
            # Now grab the number of errors, warnings, etc
            with open(
                os.path.join(
                    CACHE_FOLDER,
                    analysis_id,
                    "validation",
                    "gtfs_validation1",
                    gtfs_validation_foldername,
                    "report.json",
                )
            ) as validation_report_file:
                validation_report = json.load(validation_report_file)

            for notice in validation_report["notices"]:
                gtfs1[gtfs_validation_foldername][notice["severity"]]["total_count"] += notice["totalNotices"]
                gtfs1[gtfs_validation_foldername][notice["severity"]]["unique_count"] += 1

    gtfs_json["1"] = gtfs1

    return render_template("gtfs.jinja2", gtfs=gtfs_json, analysis_id=analysis_id)


@app.route("/projects")
def analyses():
    # Take a look at the cache folder
    cache = []
    for d in os.listdir("cache"):
        if os.path.isdir(os.path.join("cache", d)):
            try:
                date_started = datetime.strptime(d, "%Y%m%d%H%M%S").strftime("%B %d, %Y at %H:%M")
                status = get_status(d)
                try:
                    config = get_config(d)
                except FileNotFoundError:
                    config = None
                cache.append(
                    {
                        "analysis_id": d,
                        "date_started": date_started,
                        "stage": status["stage"],
                        "message": status["message"],
                        "config": config,
                    }
                )
            except ValueError:
                pass

    cache = sorted(cache, key=lambda x: int(x["analysis_id"]), reverse=True)
    return render_template("projects.jinja2", cache=cache)


@app.route("/results/<analysis_id>")
def results(analysis_id):
    # Let's grab the opportunities information
    config = get_config(analysis_id)
    date_started = datetime.strptime(config["uid"], "%Y%m%d%H%M%S").strftime("%B %d, %Y")
    # Let's pre-format the dates here
    start_datetime0 = config["scenarios"][0]["start_datetime"]
    end_datetime0 = start_datetime0 + timedelta(minutes=config["scenarios"][1]["duration"])
    start_datetime1 = config["scenarios"][0]["start_datetime"]
    end_datetime1 = start_datetime1 + timedelta(minutes=config["scenarios"][1]["duration"])
    window0 = (
        f"{start_datetime0.strftime('%A, %B %-d at %-H:%M%p')} to {end_datetime0.strftime('%A, %B %-d at %-H:%M%p')}"
    )
    window1 = (
        f"{start_datetime1.strftime('%A, %B %-d at %-H:%M%p')} to {end_datetime1.strftime('%A, %B %-d at %-H:%M%p')}"
    )

    opp_params = {}
    for opp_key in config["opportunities"].keys():
        if config["opportunities"][opp_key]["method"] == "cumulative":
            opp_params[opp_key] = [str(s) for s in config["opportunities"][opp_key]["parameters"]]
        else:
            opp_params[opp_key] = [f"{s}{get_ordinal(s)}" for s in config["opportunities"][opp_key]["parameters"]]

    print(opp_params)

    return render_template(
        "results.jinja2",
        analysis_id=analysis_id,
        config=config,
        date_started=date_started,
        windows=[window0, window1],
        opp_params=opp_params,
    )


@app.route("/run/<analysis_id>")
def run(analysis_id):
    status = get_status(analysis_id)
    if status["stage"] == "validate" and status["value"] == 100:
        # Load analysis and initiate
        a = Analysis.from_config_file(os.path.join("cache", analysis_id, "config.yml"))
        # run_analysis.submit(a)
        executor.submit(run_analysis_as_subprocess, analysis_id=analysis_id)
    return render_template("run.jinja2", analysis_id=analysis_id)


@app.route("/status/<analysis_id>")
def status(analysis_id):
    return get_status(analysis_id)


@app.route("/validate/<analysis_id>")
def validate(analysis_id):
    return render_template("validate.jinja2", analysis_id=analysis_id)


if __name__ == "__main__":
    app.run()
