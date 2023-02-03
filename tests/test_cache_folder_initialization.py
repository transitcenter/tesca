import os
import shutil

import pytest

from tesca.analysis import Analysis, CACHE_FOLDER


def test_cache_folder_initialization(analysis_config):
    a = Analysis(analysis_config)
    for idx, scenario in enumerate(analysis_config["scenarios"]):
        assert os.path.exists(
            os.path.join(CACHE_FOLDER, analysis_config["uid"], f"gtfs{idx}")
        )
    assert os.path.exists(
        os.path.join(CACHE_FOLDER, analysis_config["uid"], "error.log")
    )
    assert os.path.exists(
        os.path.join(CACHE_FOLDER, analysis_config["uid"], "info.log")
    )
    shutil.rmtree(os.path.join(CACHE_FOLDER, analysis_config["uid"]))
