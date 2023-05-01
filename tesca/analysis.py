"""
The analysis object is used to initalize and perform a comparative data analysis. 
It contains a number of validation and helper functions as well as analysis functions.
    
    
"""

import datetime as dt
from functools import reduce
from itertools import combinations
import json
import logging
import os
import pathlib
import subprocess
import time
import yaml

os.environ["USE_PYGEOS"] = "0"

import geopandas as gpd
from gtfslite import GTFS
import pandas as pd
import numpy as np
from pygris import block_groups
from pygris.data import get_census
from r5py import TransportNetwork, TravelTimeMatrixComputer

LOG_FORMATTER = logging.Formatter("%(name)-12s %(levelname)-8s %(message)s")

#: Cache folder for project storage
CACHE_FOLDER = "cache"
#: Validation subfolder name for validation outputs
VALIDATION_SUBFOLDER = "validation"
#: Validation subsubfolder for GTFS validation outputs
GTFS_VALIDATION_SUBFOLDER = "gtfs_validation"
#: Expected filename of the centroids for matrix generation
CENTROIDS_FILENAME = "analysis_centroids.geojson"
#: Output filename of compared access metrics
COMPARED_FILENAME = "compared.csv"
#: Expected input filename for demographic data
DEMOGRAPHICS_FILENAME = "demographics.csv"
#: Expected input filename for opportunities data
OPPORTUNITIES_FILENAME = "opportunities.csv"
#: Expected input file name for impact area zone list
IMPACT_AREA_FILENAME = "impact_area.csv"
#: Expected file name for the JAR file for MobilityData validation
MOBILITY_DATA_VALIDATOR_JAR = "gtfs-validator-4.0.0-cli.jar"
#: Output filename of summary data
SUMMARY_FILENAME = "summary.csv"
#: Settings location
SETTINGS_FILENAME = "settings.yml"

MAX_TIME = dt.timedelta(hours=2)  # The maximum trip time for the analysis (could make adjustable later)
STREAM_LOG = logging.DEBUG


class Analysis:
    """The analysis object"""

    def __init__(self, config):
        self.config = config
        self.uid = str(config["uid"])
        self.cache_folder = os.path.join(CACHE_FOLDER, self.uid)

        # Pull in settings file
        with open(SETTINGS_FILENAME) as settings_file:
            self.settings = yaml.safe_load(settings_file)

        new_cache_folder = False
        # Let's first set up the folder structure
        if not os.path.exists(self.cache_folder):
            os.mkdir(self.cache_folder)
            new_cache_folder = True

        # Set up the logging
        self._setup_logging()

        if new_cache_folder is True:
            self.log.debug(f"Created cache folder at {os.path.join(CACHE_FOLDER, self.config['uid'])}")

        # Create a GTFS folder for each scenario if it doesn't already have one
        for idx, scenario in enumerate(self.config["scenarios"]):
            if not os.path.exists(os.path.join(CACHE_FOLDER, self.config["uid"], f"gtfs{idx}")):
                os.mkdir(os.path.join(CACHE_FOLDER, self.config["uid"], f"gtfs{idx}"))
                self.log.info(f"Created empty gtfs{idx} folder")

        if not os.path.exists(os.path.join(self.cache_folder, VALIDATION_SUBFOLDER)):
            os.mkdir(os.path.join(self.cache_folder, VALIDATION_SUBFOLDER))
            self.log.info("Created validation folder")

    @classmethod
    def from_config_file(cls, config_file):
        """Create an analysis object from a yaml configuration file.

        Parameters
        ----------
        config_file : str
            Path to the yaml configuration file

        Returns
        -------
        Analysis
            The instantiated analysis object
        """
        with open(config_file, "r") as infile:
            config = yaml.safe_load(infile)

        a = cls(config)
        a.log.info(f"Created analysis instance from {config_file}")
        return a

    def _setup_logging(self):
        """Set up the loggers for the session"""
        # Set up the main logger
        self.log = logging.getLogger(self.config["uid"])
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(LOG_FORMATTER)
        if self.config["verbosity"] == "DEBUG":
            stream_handler.setLevel(logging.DEBUG)
        else:
            stream_handler.setLevel(logging.INFO)
        self.log.addHandler(stream_handler)

        handler_info = logging.FileHandler(os.path.join(self.cache_folder, "info.log"))
        handler_info.setFormatter(LOG_FORMATTER)
        handler_info.setLevel(logging.INFO)
        self.log.addHandler(handler_info)

        handler_error = logging.FileHandler(os.path.join(self.cache_folder, "error.log"))
        handler_error.setFormatter(LOG_FORMATTER)
        handler_error.setLevel(logging.ERROR)
        self.log.addHandler(handler_error)
        self.log.setLevel(STREAM_LOG)

    def assemble_gtfs_files(self, scenario_idx: int) -> list:
        self.log.info("  Assembling GTFS Files")
        gtfs = []
        gtfs_folder = os.path.join(self.cache_folder, f"gtfs{scenario_idx}")
        for path in os.listdir(gtfs_folder):
            gtfs_filepath = os.path.join(gtfs_folder, path)
            if os.path.isfile(gtfs_filepath) and os.path.splitext(gtfs_filepath)[1] == ".zip":
                self.log.debug(f"    Including GTFS: {gtfs_filepath}")
                gtfs.append(gtfs_filepath)
        return gtfs

    def compute_travel_times(self):
        """Compute the travel times for the provided scenarios"""
        self.log.info("Starting travel time matrix computations")
        origins = gpd.read_file(os.path.join(self.cache_folder, CENTROIDS_FILENAME), dtype={"id": str})
        self.log.debug(f"There are {origins.shape[0]} origins")

        for idx, scenario in enumerate(self.config["scenarios"]):
            gtfs = self.assemble_gtfs_files(idx)
            self.log.info(f"{scenario['name']}: Building analysis network")
            start_time = dt.datetime.strptime(scenario["start_datetime"], "%Y-%m-%d %H:%M")

            tn = TransportNetwork(
                os.path.join(self.cache_folder, "osm.pbf"),
                gtfs,
            )

            # Build the transport modes starting as always with walking
            transport_modes = ["WALK"]
            for tm in scenario["transit_modes"]:
                transport_modes.append(tm)

            self.log.debug(f"  Transport Modes: {', '.join(transport_modes)}")

            ttmc = TravelTimeMatrixComputer(
                tn,
                origins=origins,
                destinations=origins,
                departure=start_time,
                departure_time_window=dt.timedelta(minutes=int(scenario["duration"])),
                max_time=MAX_TIME,
                max_time_walking=dt.timedelta(minutes=int(self.config["max_time_walking"])),
                transport_modes=transport_modes,
            )
            self.log.info(f"{scenario['name']}: Computing travel time matrix")
            start = time.time()
            travel_time_matrix = ttmc.compute_travel_times()
            end = time.time()

            self.log.debug(f"{scenario['name']}: Matrix calcualtion took {end-start} seconds")
            travel_time_matrix.to_csv(
                os.path.join(CACHE_FOLDER, self.uid, f"matrix{idx}.csv"),
                index=False,
            )
            self.log.info(f"{scenario['name']}: Matrix written to matrix{idx}.csv")

    def compute_metrics(self):
        """Compute the access to opportunity metrics using the calcualted matrices"""
        # Now that the metrics are built...
        self.log.info("Computing metrics for all scenarios")
        for idx, scenario in enumerate(self.config["scenarios"]):
            metrics = []
            matrix = pd.read_csv(
                os.path.join(self.cache_folder, f"matrix{idx}.csv"),
                dtype={"from_id": str, "to_id": str, "travel_time": "float64"},
            )
            matrix.dropna(subset=["from_id", "to_id"])
            opportunity_df = pd.read_csv(
                os.path.join(
                    self.cache_folder,
                    OPPORTUNITIES_FILENAME,
                ),
                dtype={"bg_id": str},
            )
            for opportunity in self.config["opportunities"]:
                if self.config["opportunities"][opportunity]["method"] == "cumulative":
                    for threshold in self.config["opportunities"][opportunity]["parameters"]:
                        self.log.debug(
                            f"{scenario['name']}: Computing {self.config['opportunities'][opportunity]['method']} ({threshold}) access to {self.config['opportunities'][opportunity]['name']}"
                        )
                        metric_df = Analysis.compute_cumulative_measure(matrix, opportunity_df, opportunity, threshold)
                        self.log.debug(f"Result has {metric_df.shape[0]} rows.")
                        metrics.append(metric_df)
                elif self.config["opportunities"][opportunity]["method"] == "travel_time":
                    for n in self.config["opportunities"][opportunity]["parameters"]:
                        self.log.debug(
                            f"{scenario['name']}: Computing {self.config['opportunities'][opportunity]['method']} ({n}) access to {self.config['opportunities'][opportunity]['name']}"
                        )
                        metric_df = Analysis.compute_travel_time_measure(matrix, opportunity_df, opportunity, n=n)
                        self.log.debug(f"Result has {metric_df.shape[0]} rows.")
                        metrics.append(metric_df)
                else:
                    raise KeyError(
                        f"Invalid method specification {self.config['opportunities'][opportunity]['method']} for metrics calculation"
                    )

            # Merge all dataframes together.
            metrics = reduce(lambda df1, df2: pd.merge(df1, df2, on="bg_id"), metrics)
            metrics.to_csv(os.path.join(self.cache_folder, f"metrics{idx}.csv"), index=False)

    @staticmethod
    def compute_cumulative_measure(
        matrix: pd.DataFrame,
        opportunity_df: pd.DataFrame,
        opportunity_name: str,
        threshold: int,
    ) -> pd.DataFrame:
        """Calcualte the cumulative number of opportunities for each origin within the destination threshold.

        Parameters
        ----------
        matrix : pd.DataFrame
            The travel time matrix
        opportunity_df : pd.DataFrame
            The opportunity locations
        opportunity_name : str
            The name of the opportunity. This will be appended with _ct, where 't' is the threshold
        threshold : int
            The travel time threshold cutoff, in minutes.

        Returns
        -------
        pd.DataFrame
            A dataframe containing each origin and a count of reachable opportunities
        """
        # Keep only travel times under the threshold
        matrix = matrix[matrix["travel_time"] <= threshold]
        # Joining matrix in
        mx_opportunity = pd.merge(matrix, opportunity_df, left_on="to_id", right_on="bg_id")
        result = mx_opportunity[["from_id", opportunity_name]].groupby("from_id", as_index=False).sum()
        result.columns = ["bg_id", f"{opportunity_name}_c{threshold}"]

        # Ensure we return a complete dataframe
        result = pd.merge(result, opportunity_df[["bg_id"]], how="right")
        result[f"{opportunity_name}_c{threshold}"] = result[f"{opportunity_name}_c{threshold}"].fillna(0)
        return result

    @staticmethod
    def compute_travel_time_measure(
        matrix: pd.DataFrame,
        opportunty_df: pd.DataFrame,
        opportunity_name: str,
        n: int = 1,
    ) -> pd.DataFrame:
        """Calculate travel time to nth nearest destination

        Parameters
        ----------
        matrix : pd.DataFrame
            A dataframe containing the travel time matrix
        opportunty_df : pd.DataFrame
            A dataframe containing the opportunities (1 or greater indicates opportunity is located there)
        opportunity_name : str
            The name of the opportunity to be used in the header. This will be appended with a '_tn' where n is as described below.
        infinity_value : int
            The value to use for infinite travel times
        n : int, optional
            The nth nearest item to use (e.g. 1 is closest, 3 is 3rd closest), by default 1

        Returns
        -------
        pd.DataFrame
            A dataframe containing the minimum travel time to the nth nearest destination for each origin
        """

        # First we perform a many-to-one join on the destinations
        matrix_dest = pd.merge(
            matrix,
            opportunty_df[["bg_id", opportunity_name]],
            left_on="to_id",
            right_on="bg_id",
            how="right",
        )
        matrix_dest = matrix_dest[matrix_dest[opportunity_name] > 0]
        matrix_dest = matrix_dest.sort_values(["from_id", "travel_time"], ascending=True, na_position="last")

        def get_nth(df, o, n):
            df = df.sort_values(by="travel_time", ascending=True)
            df["cumsum"] = df[o].cumsum()
            df = df[df["cumsum"] >= n]
            return df["travel_time"].min()

        result = (
            matrix_dest[["from_id", "travel_time", opportunity_name]]
            .groupby("from_id", as_index=False)
            .apply(get_nth, o=opportunity_name, n=n)
        )
        result.columns = ["bg_id", f"{opportunity_name}_t{n}"]
        return result

    def compute_unreachable(self):
        """Compute the number of individuals in the impact area who cannot reach their desired travel time destination"""

        self.log.info("Computing unreachable destinations")
        # Grab the "metrics" file for each one
        demographics = pd.read_csv(os.path.join(self.cache_folder, DEMOGRAPHICS_FILENAME), dtype={"bg_id": str})
        impact_area = pd.read_csv(os.path.join(self.cache_folder, IMPACT_AREA_FILENAME), dtype={"bg_id": str})

        unreachable_dfs = []
        for idx, scenario in enumerate(self.config["scenarios"]):
            metrics = pd.read_csv(
                os.path.join(self.cache_folder, f"metrics{idx}.csv"),
                dtype={"bg_id": str},
            )
            # Shrink file to the analysis area
            metrics = metrics[metrics["bg_id"].isin(impact_area["bg_id"])]
            # Let's join the metrics with the demographics now
            metrics_demo = pd.merge(metrics, demographics, on="bg_id")

            # If the measure is travel time, let's find the unreachables
            for opportunity in self.config["opportunities"]:
                if self.config["opportunities"][opportunity]["method"] == "travel_time":
                    for parameter in self.config["opportunities"][opportunity]["parameters"]:
                        # Filter dataframe to only keep where this parameter is NA
                        na_metrics = metrics_demo[metrics_demo[f"{opportunity}_t{parameter}"].isna()]
                        # Sum all the demographic keys
                        na_metrics_sum = na_metrics[[i for i in self.config["demographics"].keys()]].sum().to_frame().T
                        # na_metrics_sum.columns = ["unreachable"]
                        na_metrics_sum["scenario"] = idx
                        na_metrics_sum["metric"] = f"{opportunity}_t{parameter}"
                        unreachable_dfs.append(na_metrics_sum)

        result = pd.concat(unreachable_dfs, axis="index").reset_index(drop=True)
        result[result.columns[::-1]].to_csv(os.path.join(self.cache_folder, "unreachable.csv"), index=False)

    def compare_scenarios(self):
        """Compute the differences between all scenarios"""
        self.log.info("Computing Scenario Comparisons")
        idxs = [i for i in range(len(self.config["scenarios"]))]
        compared_dfs = []
        for pair in combinations(idxs, 2):
            metrics_a = pd.read_csv(
                os.path.join(self.cache_folder, f"metrics{pair[0]}.csv"),
                dtype={"bg_id": str},
            )
            metrics_b = pd.read_csv(
                os.path.join(self.cache_folder, f"metrics{pair[1]}.csv"),
                dtype={"bg_id": str},
            )
            metrics = pd.merge(
                metrics_a,
                metrics_b,
                on="bg_id",
                suffixes=[f"_{pair[0]}", f"_{pair[1]}"],
            )

            metrics = metrics.fillna(self.config["infinity_value"])

            for opportunity in self.config["opportunities"]:
                if self.config["opportunities"][opportunity]["method"] == "cumulative":
                    method = "c"
                else:
                    method = "t"
                for parameter in self.config["opportunities"][opportunity]["parameters"]:
                    series_a = metrics[f"{opportunity}_{method}{parameter}_{pair[1]}"]
                    series_b = metrics[f"{opportunity}_{method}{parameter}_{pair[0]}"]
                    metrics[f"{opportunity}_{method}{parameter}_{pair[1]}-{pair[0]}"] = series_a - series_b

            compared_dfs.append(metrics)

        compared = reduce(lambda df1, df2: pd.merge(df1, df2, on="bg_id"), compared_dfs)
        compared.to_csv(os.path.join(self.cache_folder, COMPARED_FILENAME), index=False)

    def compute_summaries(self):
        # Take the compared metrics and summarize all of them
        compared = pd.read_csv(
            os.path.join(self.cache_folder, COMPARED_FILENAME),
            dtype={"bg_id": str},
            index_col="bg_id",
        )
        demographics = pd.read_csv(
            os.path.join(self.cache_folder, DEMOGRAPHICS_FILENAME),
            dtype={"bg_id": str},
            index_col="bg_id",
        )
        impact_area = pd.read_csv(
            os.path.join(self.cache_folder, IMPACT_AREA_FILENAME),
            dtype={"bg_id": str},
            index_col="bg_id",
        )

        # Filter out non-impact area and non-used demographic values
        compared = compared[compared.index.isin(impact_area.index)]
        demographics = demographics[demographics.index.isin(impact_area.index)]

        # Normalize to get fractional amounts
        demographics = demographics / demographics.sum()

        # Join to get scores
        weighted = demographics.join(compared)

        weighted_dfs = []
        for demographic in self.config["demographics"].keys():
            mult = weighted[compared.columns].multiply(weighted[demographic], axis=0)
            mult = mult.sum()
            weighted_dfs.append(mult)

        result = pd.concat(weighted_dfs, axis=1)
        result.columns = demographics.columns
        result.index.name = "metric"
        result.to_csv(os.path.join(self.cache_folder, SUMMARY_FILENAME))

    def fetch_block_groups(self, counties_by_state: dict, overwrite=False):
        # Fetch all block groups based on a list of states/counties
        # TODO: Check if analysis file already exists?
        if overwrite == False:
            if os.path.exists(os.path.join(self.cache_folder, CENTROIDS_FILENAME)):
                raise FileExistsError("An analysis centroids file already exists")
        bg_dfs = []
        for state in counties_by_state.keys():
            bgs = block_groups(
                state=str(state), county=counties_by_state[state], year=self.settings["census_year"], cb=True
            )
            bg_dfs.append(bgs)

        bg_df = pd.concat(bg_dfs, axis="index")
        bg_df.to_file("bg_2021.geojson")

    def fetch_demographic_data(self, api_key):
        # See: https://api.census.gov/data/2021/acs/acs5
        # Read in the analysis centroids
        self.log.info("Fetching Demographic Data")
        impact_area_bgs = pd.read_csv(os.path.join(self.cache_folder, IMPACT_AREA_FILENAME), dtype={"bg_id": str})
        impact_area_bgs["state"] = impact_area_bgs["bg_id"].str[:2]
        impact_area_bgs["county"] = impact_area_bgs["bg_id"].str[2:5]
        states_and_counties = impact_area_bgs[["state", "county"]].drop_duplicates().sort_values("state")
        all_data = []
        variables = [i for i in self.config["demographics"].keys()]
        print(variables)
        for idx, area in states_and_counties.iterrows():
            self.log.debug(f"  Fetching State: {area['state']} County: {area['county']}")
            data = get_census(
                dataset="acs/acs5",
                year="2021",
                variables=variables,
                params={
                    "for": "block group:*",
                    "in": f"state:{area['state']} county:{area['county']}",
                    "key": api_key,
                },
                return_geoid=True,
            )
            all_data.append(data)

        result = pd.concat(all_data, axis="index")
        # Rename our GEOID
        result = result.rename(columns={"GEOID": "bg_id"})
        result = result[result["bg_id"].isin(impact_area_bgs["bg_id"])]
        result.to_csv(os.path.join(self.cache_folder, DEMOGRAPHICS_FILENAME), index=False)
        return result

    def validate_analysis_area(self):
        # Open up the analysis area and the geojson
        self.log.info("Validating Analysis Area")
        analysis_area = gpd.read_file(
            os.path.join(self.cache_folder, CENTROIDS_FILENAME),
            dtype={"id": str},
        )
        impact_area = pd.read_csv(os.path.join(self.cache_folder, IMPACT_AREA_FILENAME), dtype={"bg_id": str})
        # Check to make sure the ID string is long enough to be a block group
        wrong_length = analysis_area[analysis_area["id"].str.len() != 12]
        if wrong_length.shape[0] > 0:
            wrong_length_filename = os.path.join(
                self.cache_folder,
                VALIDATION_SUBFOLDER,
                "length_error_analysis_area.csv",
            )
            wrong_length.to_csv(wrong_length_filename, index=False)
            self.log.error(
                f"  There are {wrong_length.shape[0]} rows in the analysis area with invalid zone IDs. See {wrong_length_filename} for a list."
            )
        wrong_length = impact_area[impact_area["bg_id"].str.len() != 12]
        if wrong_length.shape[0] > 0:
            wrong_length_filename = os.path.join(
                self.cache_folder, VALIDATION_SUBFOLDER, "length_error_impact_area.csv"
            )
            wrong_length.to_csv(wrong_length_filename, index=False)
            self.log.error(
                f"  There are {wrong_length.shape[0]} rows in the impact area with invalid zone IDs. See {wrong_length_filename} for a list."
            )
        impact_not_in_analysis = impact_area[~impact_area["bg_id"].isin(analysis_area["id"])]
        if impact_not_in_analysis.shape[0] > 0:
            impact_not_in_analysis_filename = os.path.join(
                self.cache_folder,
                VALIDATION_SUBFOLDER,
                "impact_not_in_analysis_area.csv",
            )
            impact_not_in_analysis.to_csv(impact_not_in_analysis_filename, index=False)
            self.log.error(
                f"  There are {impact_not_in_analysis.shape[0]} zones in the impact area that are not in the analysis area. See {impact_not_in_analysis_filename} for a list."
            )

    def validate_demographics(self):
        # Let's pull the demographics file and the equity file
        self.log.info("Validating Demographic Data")
        demographics = pd.read_csv(os.path.join(self.cache_folder, DEMOGRAPHICS_FILENAME), dtype={"bg_id": str})
        impact_area = pd.read_csv(os.path.join(self.cache_folder, IMPACT_AREA_FILENAME), dtype={"bg_id": str})
        no_demographics = impact_area[~impact_area["bg_id"].isin(demographics["bg_id"])]
        if no_demographics.shape[0] > 0:
            invalid_demographics_file = os.path.join(
                self.cache_folder,
                VALIDATION_SUBFOLDER,
                f"missing_{DEMOGRAPHICS_FILENAME}",
            )
            no_demographics.to_csv(invalid_demographics_file, index=False)
            self.log.error(
                f"  There are {no_demographics.shape[0]} impact area zones that do not have demographic data. See {invalid_demographics_file} for zones with missing data."
            )
        self.log.info("Demographic data validation complete")

    def validate_gtfs_data(self):
        # TODO: Check or report on total number of routes/trips in each of the provided datasets

        # Run a mobility data validator check
        for idx, scenario in enumerate(self.config["scenarios"]):
            gtfs_list = self.assemble_gtfs_files(idx)
            for g in gtfs_list:
                # Create an output folder in the cache
                validator_folder = os.path.join(
                    self.cache_folder,
                    VALIDATION_SUBFOLDER,
                    f"{GTFS_VALIDATION_SUBFOLDER}{idx}",
                )
                if not os.path.exists(validator_folder):
                    os.mkdir(validator_folder)

                gtfs_filename = pathlib.Path(g).stem
                output_folder = os.path.join(validator_folder, gtfs_filename)
                if not os.path.exists(output_folder):
                    os.mkdir(output_folder)
                self.log.info(f"Running MobilityData Validator on {g}")
                try:
                    subprocess.call(
                        [
                            "java",
                            "-jar",
                            MOBILITY_DATA_VALIDATOR_JAR,
                            "-i",
                            f"{g}",
                            "-o",
                            f"{output_folder}",
                        ],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.STDOUT,
                    )
                except Exception as e:
                    self.log.exception(e)

                # First let's check for system errors
                with open(os.path.join(output_folder, "system_errors.json")) as system_errors_file:
                    system_errors = json.load(system_errors_file)
                    self.log.info(f"  There were {len(system_errors['notices'])} system errors.")
                    for i in system_errors["notices"]:
                        self.log.error(f"{i}")

                # Next let's go through the notices
                with open(os.path.join(output_folder, "report.json")) as validation_report_file:
                    validation_report = json.load(validation_report_file)
                    # Let's sort the relevant outputs
                    levels = {
                        "ERROR": {"total_count": 0, "unique_count": 0, "codes": []},
                        "WARNING": {"total_count": 0, "unique_count": 0, "codes": []},
                        "INFO": {"total_count": 0, "unique_count": 0, "codes": []},
                    }
                    for notice in validation_report["notices"]:
                        levels[notice["severity"]]["total_count"] += notice["totalNotices"]
                        levels[notice["severity"]]["unique_count"] += 1
                        levels[notice["severity"]]["codes"].append(notice["code"])

                    self.log.info(
                        f"  There are {levels['ERROR']['total_count']} errors, {levels['WARNING']['total_count']} warnings, and {levels['INFO']['total_count']} infos."
                    )
                    self.log.info(f"  Please see {os.path.join(output_folder, 'report.html')} for details.")

                    # for code in levels["ERROR"]["codes"]:
                    #     self.log.error(f"  {code}")
                    # for code in levels["WARNING"]["codes"]:
                    #     self.log.warning(f"  {code}")
                    # for code in levels["INFO"]["codes"]:
                    #     self.log.info(f"  {code}")

                self.log.info(f"Performing additional GTFS validation on {g}")
                # Load the thing into gtfs-lite
                gtfs_lite = GTFS.load_zip(g)
                # Get the scenario that's going to be run
                start_time = dt.datetime.strptime(self.config["scenarios"][idx]["start_datetime"], "%Y-%m-%d %H:%M")
                end_time = start_time + dt.timedelta(minutes=self.config["scenarios"][idx]["duration"])
                if gtfs_lite.valid_date(start_time.date()) == False or gtfs_lite.valid_date(end_time.date()) == False:
                    self.log.error(f"  Start or end date of analysis {idx} is invalid")
                # Analysis date

    def validate_open_street_map(self):
        raise NotImplementedError

    def validate_opportunities(self):
        # Let's pull the demographics file and the equity file
        self.log.info("Validating Opporutnities Data")
        opportunities = pd.read_csv(
            os.path.join(self.cache_folder, OPPORTUNITIES_FILENAME),
            dtype={"bg_id": str},
        )
        analysis_area = gpd.read_file(os.path.join(self.cache_folder, CENTROIDS_FILENAME), dtype={"bg_id": str})
        no_opportunities = analysis_area[~analysis_area["id"].isin(opportunities["bg_id"])]
        if no_opportunities.shape[0] > 0:
            no_opportunities_filename = os.path.join(self.cache_folder, VALIDATION_SUBFOLDER, "no_opportunities.csv")
            no_opportunities[["id"]].to_csv(no_opportunities_filename, index=False)
            self.log.error(
                f"  There are {no_opportunities.shape[0]} analysis area zones that do not have opportunity data. See {no_opportunities_filename} for zones with missing data."
            )
