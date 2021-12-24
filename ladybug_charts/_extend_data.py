"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heatmap, monthly_bar_chart, daily_bar_chart, hourly_chart


HourlyContinuousCollection.heatmap = heatmap
HourlyDiscontinuousCollection.heatmap = heatmap
MonthlyCollection.barchart = monthly_bar_chart
DailyCollection.barchart = daily_bar_chart
HourlyContinuousCollection.barchart = hourly_chart
