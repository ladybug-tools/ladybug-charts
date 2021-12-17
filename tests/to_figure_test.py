from ladybug_charts.to_figure import heatmap
from ladybug_charts.to_dataframe import create_dataframe, DataPoint
from plotly.graph_objects import Figure


def test_heatmap():
    epw_path = r'tests/assets/weather/boston.epw'
    df = create_dataframe(epw_path)[0]
    fig = heatmap(df, DataPoint.relative_humidity)
    assert isinstance(fig, Figure)
