from plotly.graph_objects import Figure
from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time
from ladybug.datacollection import HourlyContinuousCollection
from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
from ladybug_charts.to_figure import bar_chart
from ladybug_charts._helper import ColorSet
from ladybug_charts.utils import Strategy
from ladybug.color import Color
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.sunpath import Sunpath
from ladybug_comfort.chart.polygonpmv import PolygonPMV


def test_hourly_continuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.heat_map()
    assert isinstance(fig, Figure)


def test_hourly_discontinuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.filter_by_conditional_statement('a>25').heat_map()
    assert isinstance(fig, Figure)


def test_hourly_to_per_hour_chart(epw):
    fig = epw.dry_bulb_temperature.per_hour_line_chart()
    assert isinstance(fig, Figure)


def test_hourly_to_line_chart(epw):
    fig = epw.dry_bulb_temperature.line_chart()
    assert isinstance(fig, Figure)


def test_monthly_to_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_monthly().bar_chart()
    assert isinstance(fig, Figure)


def test_daily_to_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_daily().bar_chart()
    assert isinstance(fig, Figure)


def test_bar_chart_multiple_monthly_data(epw):
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
                    title='Degree-days', show_title=True,
                    colors=[Color(255, 0, 0), Color(0, 0, 255)], stack=True)
    assert isinstance(fig, Figure)


def test_bar_chart_multiple_daily_data(epw):
    dbt = epw.dry_bulb_temperature.average_daily()
    rh = epw.relative_humidity.average_daily()
    fig = bar_chart([dbt, rh])
    assert isinstance(fig, Figure)


def test_hourly_plot(epw):
    hp = HourlyPlot(epw.dry_bulb_temperature)
    fig = hp.plot()
    assert isinstance(fig, Figure)


def test_monthly_chart_plot(epw):
    dbt_monthly = epw.dry_bulb_temperature.average_monthly()
    rh_monthly = epw.relative_humidity.average_monthly()
    mc = MonthlyChart([dbt_monthly, rh_monthly])
    fig = mc.plot()
    assert isinstance(fig, Figure)


def test_wind_rose(epw):
    lb_wind_rose = WindRose(epw.wind_direction, epw.wind_speed)
    fig = lb_wind_rose.plot()
    assert isinstance(fig, Figure)


def test_psych_chart(epw):
    lb_psy = PsychrometricChart(epw.dry_bulb_temperature, epw.relative_humidity)
    fig = lb_psy.plot()
    assert isinstance(fig, Figure)


def test_psych_chart_with_data(epw):
    lb_psy = PsychrometricChart(epw.dry_bulb_temperature, epw.relative_humidity)
    pmv = PolygonPMV(lb_psy)
    fig = lb_psy.plot(data=epw.direct_normal_radiation, polygon_pmv=pmv,
                      strategies=[
                          Strategy.comfort,
                          Strategy.evaporative_cooling,
                          Strategy.mas_night_ventilation,
                          Strategy.occupant_use_of_fans,
                          Strategy.capture_internal_heat,
                          Strategy.passive_solar_heating, ],
                      solar_data=epw.direct_normal_radiation,)
    assert isinstance(fig, Figure)


def test_sunpath(epw):
    lb_sunpath = Sunpath.from_location(epw.location)
    fig = lb_sunpath.plot(data=epw.dry_bulb_temperature, colorset=ColorSet.nuanced,
                          min_range=0, max_range=50, title='SUNPATH')
    assert isinstance(fig, Figure)
