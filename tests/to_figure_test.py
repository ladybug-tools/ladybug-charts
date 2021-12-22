from plotly.graph_objects import Figure


def test_hourly_continuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.heatmap()
    assert isinstance(fig, Figure)


def test_hourly_discontinuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.filter_by_conditional_statement('a>25').heatmap()
    assert isinstance(fig, Figure)


def test_monthly_to_barchart(epw):
    fig = epw.dry_bulb_temperature.average_monthly().barchart()
    assert isinstance(fig, Figure)
