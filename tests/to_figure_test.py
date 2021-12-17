from ladybug.epw import EPW
from plotly.graph_objects import Figure


def test_heatmap():
    fig = EPW('tests/assets/weather/boston.epw').dry_bulb_temperature.heatmap()
    assert isinstance(fig, Figure)
