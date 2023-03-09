import pytest


@pytest.mark.parametrize(
    ("scenario_index, result"),
    [
        (
            0,
            {
                "cache/test-cache/gtfs0/brooklyn.zip",
                "cache/test-cache/gtfs0/subway.zip",
            },
        ),
        (1, {"cache/test-cache/gtfs1/lirr.zip"}),
    ],
)
def test_assemble_gtfs(analysis, scenario_index, result):
    assert set(analysis.assemble_gtfs_files(scenario_index)) == result
