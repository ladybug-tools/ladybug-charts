from plotly.graph_objects import Figure
from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time
from ladybug.datacollection import HourlyContinuousCollection
from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
from ladybug_charts.to_figure import bar_chart
from ladybug.color import Color


def test_hourly_continuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.heatmap()
    assert isinstance(fig, Figure)


def test_hourly_discontinuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.filter_by_conditional_statement('a>25').heatmap()
    assert isinstance(fig, Figure)


def test_monthly_to_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_monthly().barchart()
    assert isinstance(fig, Figure)


def test_daily_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_daily().barchart()
    assert isinstance(fig, Figure)


def test_barc_hart(epw):
    dbt = epw.dry_bulb_temperature

    _heat_base_ = 18
    _cool_base_ = 23

    hourly_heat = HourlyContinuousCollection.compute_function_aligned(
        heating_degree_time, [dbt, _heat_base_],
        HeatingDegreeTime(), 'degC-hours')
    hourly_heat.convert_to_unit('degC-days')

    hourly_cool = HourlyContinuousCollection.compute_function_aligned(
        cooling_degree_time, [dbt, _cool_base_],
        CoolingDegreeTime(), 'degC-hours')
    hourly_cool.convert_to_unit('degC-days')

    fig = bar_chart([hourly_heat.total_monthly(),
                    hourly_cool.total_monthly()],
                    chart_title='Degree-days',
                    colors=[Color(255, 0, 0), Color(0, 0, 255)], stack=True)
    assert isinstance(fig, Figure)
