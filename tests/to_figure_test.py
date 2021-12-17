from ladybug_charts.to_figure import heatmap, DataPoint
from ladybug_pandas.dataframe import DataFrame
from ladybug.epw import EPW
from plotly.graph_objects import Figure


def test_heatmap():
    epw_path = r'tests/assets/weather/boston.epw'
    epw = EPW(epw_path)
    df = DataFrame.from_epw(epw)
    fig = heatmap(df, DataPoint.relative_humidity)
    assert isinstance(fig, Figure)
