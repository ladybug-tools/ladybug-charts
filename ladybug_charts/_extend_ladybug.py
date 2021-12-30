"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heat_map, monthly_bar_chart, daily_bar_chart, \
    hourly_line_chart, per_hour_line_chart, wind_rose, psych_chart
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart

HourlyContinuousCollection.heat_map = heat_map
HourlyDiscontinuousCollection.heat_map = heat_map
MonthlyCollection.bar_chart = monthly_bar_chart
DailyCollection.bar_chart = daily_bar_chart
HourlyContinuousCollection.line_chart = hourly_line_chart
HourlyContinuousCollection.per_hour_line_chart = per_hour_line_chart
WindRose.plot = wind_rose
PsychrometricChart.plot = psych_chart
