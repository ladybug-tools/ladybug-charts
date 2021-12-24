"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heat_map, monthly_bar_chart, daily_bar_chart, \
    hourly_bar_chart, per_hour_bar_chart


HourlyContinuousCollection.heat_map = heat_map
HourlyDiscontinuousCollection.heat_map = heat_map
MonthlyCollection.bar_chart = monthly_bar_chart
DailyCollection.bar_chart = daily_bar_chart
HourlyContinuousCollection.bar_chart = hourly_bar_chart
HourlyContinuousCollection.per_hour_chart = per_hour_bar_chart
