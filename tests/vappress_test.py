from Code.FUN import sat_vappressure
from Code.FUN import vappressure


def test_sat_vappressure_calc():
    assert round(sat_vappressure(22.3), 5) == 2.73277


def test_vappressure_calc():
    assert round(vappressure(34.2, 2.73277), 3) == 0.935
