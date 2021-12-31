"""Add capability to generate a Figures from ladybug data objects. """

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug_charts.to_figure import heat_map, monthly_bar_chart, daily_bar_chart, \
    hourly_line_chart, per_hour_line_chart, wind_rose, psych_chart, bar_chart
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart


HourlyContinuousCollection.heat_map = heat_map
HourlyDiscontinuousCollection.heat_map = heat_map
MonthlyCollection.bar_chart = monthly_bar_chart
DailyCollection.bar_chart = daily_bar_chart
HourlyContinuousCollection.line_chart = hourly_line_chart
HourlyContinuousCollection.per_hour_line_chart = per_hour_line_chart
WindRose.plot = wind_rose
PsychrometricChart.plot = psych_chart


def hourly_plot(self):
    hourly_data = self.data_collection
    return heat_map(hourly_data)


HourlyPlot.plot = hourly_plot


def plot_monthly_chart(self):
    data = self.data_collections
    return bar_chart(data)


MonthlyChart.plot = plot_monthly_chart
