import json
import pytest


@pytest.fixture
def analysis_config():
    import os

    with open(os.path.join("tests", "config", "config.json")) as infile:
        return json.load(infile)


@pytest.fixture
def blank_analysis(analysis_config):
    from tesca.analysis import Analysis

    return Analysis(analysis_config)
