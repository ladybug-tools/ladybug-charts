import pytest
from ladybug.epw import EPW


@pytest.fixture()
def epw():
    return EPW('./tests/assets/weather/boston.epw')
