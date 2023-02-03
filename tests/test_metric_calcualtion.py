from tesca.analysis import Analysis


def test_cumulative_measure():
    assert Analysis.compute_cumulative_measure(30) == 60


def test_travel_time_measure():
    assert Analysis.compute_travel_time_measure(30) == 60
