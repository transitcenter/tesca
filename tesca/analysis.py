import datetime as dt
from functools import reduce
import json
import logging
import os
import time

import geopandas as gpd
import pandas as pd

from r5py import TransportNetwork, TravelTimeMatrixComputer, TransitMode, LegMode


log_formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S"
)

CACHE_FOLDER = "cache"
MAX_TIME = dt.timedelta(
    hours=2
)  # The maximum trip time for the analysis (could make adjustable later)
STREAM_LOG = logging.DEBUG


class Analysis:
    def __init__(self, config):
        self.config = config
        self.uid = str(config["uid"])
        self.cache_folder = os.path.join(CACHE_FOLDER, self.uid)

        new_cache_folder = False
        # Let's first set up the folder structure
        if not os.path.exists(self.cache_folder):
            os.mkdir(self.cache_folder)
            new_cache_folder = True

        # Set up the logging
        self._setup_logging()

        if new_cache_folder is True:
            self.log.debug(
                f"Created cache folder at {os.path.join(CACHE_FOLDER, self.config['uid'])}"
            )

        # Create a GTFS folder for each scenario if it doesn't already have one
        for idx, scenario in enumerate(self.config["scenarios"]):
            if not os.path.exists(
                os.path.join(CACHE_FOLDER, self.config["uid"], f"gtfs{idx}")
            ):
                os.mkdir(os.path.join(CACHE_FOLDER, self.config["uid"], f"gtfs{idx}"))
                self.log.info(f"Created empty gtfs{idx} folder")

    @classmethod
    def from_config_file(cls, config_file):
        with open(config_file) as infile:
            config = json.load(infile)

        a = cls(config)
        a.log.info(f"Created analysis instance from {config_file}")
        return a

    def _setup_logging(self):
        """Set up the loggers for the session"""
        # Set up the logging
        self.log = logging.getLogger(self.config["uid"])
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.log.addHandler(stream_handler)

        handler_info = logging.FileHandler(os.path.join(self.cache_folder, "info.log"))
        handler_info.setFormatter(log_formatter)
        handler_info.setLevel(logging.INFO)
        self.log.addHandler(handler_info)

        handler_error = logging.FileHandler(
            os.path.join(self.cache_folder, "error.log")
        )
        handler_error.setFormatter(log_formatter)
        handler_error.setLevel(logging.ERROR)
        self.log.addHandler(handler_error)

        self.log.setLevel(STREAM_LOG)

    def validate_data(self):
        # TODO: Add validation data
        pass

    def compute_travel_times(self):
        self.log.info("Starting travel time matrix computations")
        origins = gpd.read_file(
            os.path.join(self.cache_folder, "analysis_centroids.geojson")
        )
        self.log.debug(f"There are {origins.shape[0]} origins")

        for idx, scenario in enumerate(self.config["scenarios"]):
            self.log.info(f"{scenario['name']}: Building analysis network")
            start_time = dt.datetime.strptime(
                scenario["start_datetime"], "%Y-%m-%d %H:%M"
            )

            gtfs = []
            for path in os.listdir(os.path.join(self.cache_folder, f"gtfs{idx}")):
                if (
                    os.path.isfile(os.path.join(self.cache_folder, path))
                    and os.path.splitext(os.path.join(self.cache_folder, path))[1]
                    == ".zip"
                ):
                    gtfs.append(os.path.join(self.cache_folder, path))
            duration = dt.timedelta(minutes=int(scenario["duration"]))
            tn = TransportNetwork(
                os.path.join(self.cache_folder, "osm.pbf"),
                gtfs,
            )

            ttmc = TravelTimeMatrixComputer(
                tn,
                origins=origins,
                destinations=origins,
                departure=start_time,
                departure_time_window=duration,
                max_time=MAX_TIME,
                transport_modes=[TransitMode.TRANSIT, LegMode.WALK],
            )
            self.log.info(f"{scenario['name']}: Computing travel time matrix")
            start = time.time()
            travel_time_matrix = ttmc.compute_travel_times()
            end = time.time()

            self.log.debug(
                f"{scenario['name']}: Matrix calcualtion took {end-start} seconds"
            )
            travel_time_matrix.to_csv(
                os.path.join(CACHE_FOLDER, self.uid, f"matrix{idx}.csv"),
                index=False,
            )
            self.log.info(f"{scenario['name']}: Matrix written to matrix{idx}.csv")

    def compute_metrics(self):
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
                    "opportunities.csv",
                ),
                dtype={"bg_id": str},
            )
            for opportunity in self.config["opportunities"]:
                self.log.debug(
                    f"{scenario['name']}: Computing {self.config['opportunities'][opportunity]['method']} access to {self.config['opportunities'][opportunity]['name']}"
                )
                if self.config["opportunities"][opportunity]["method"] == "cumulative":
                    for threshold in self.config["opportunities"][opportunity][
                        "parameters"
                    ]:
                        measure_df = Analysis.compute_cumulative_measure(
                            matrix, opportunity_df, opportunity, threshold
                        )
                        metrics.append(measure_df)

            # Merge all dataframes together.
            metrics = reduce(lambda df1, df2: pd.merge(df1, df2, on="bg_id"), metrics)
            metrics.to_csv(
                os.path.join(self.cache_folder, f"metrics{idx}.csv"), index=False
            )

    @staticmethod
    def compute_cumulative_measure(matrix, opportunity_df, opportunity_name, threshold):
        # First thing is to drop all travel times larger than the threshold
        matrix = matrix[matrix["travel_time"] <= threshold]
        # Joining matrix in
        mx_opportunity = pd.merge(
            matrix, opportunity_df, left_on="from_id", right_on="bg_id"
        )
        result = (
            mx_opportunity[["from_id", opportunity_name]]
            .groupby("from_id", as_index=False)
            .sum()
        )
        result.columns = ["bg_id", f"{opportunity_name}_{threshold}"]
        return result

    @staticmethod
    def compute_travel_time_measure(nth=1):
        pass
