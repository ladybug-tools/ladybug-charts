"""Create plotly figures from pandas Dataframe."""


import numpy as np
import pandas as pd


from math import ceil, floor, cos, radians
from typing import Union, List, Tuple
from random import randint
from datetime import timedelta

import plotly.io as pio
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.graph_objects import Bar
from plotly.subplots import make_subplots

from ._to_dataframe import dataframe, Frequency, MONTHS
from ._helper import discontinuous_to_continuous, rgb_to_hex, ColorSet, color_set,\
    get_monthly_values, group_monthly
from ._helper_chart import get_dummy_trace
from ._psych import _psych_chart
from .utils import Strategy, StrategyParameters

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection, BaseCollection
from ladybug.windrose import WindRose
from ladybug.color import Color, Colorset, ColorRange
from ladybug_pandas.series import Series
from ladybug.sunpath import Sunpath
from ladybug.psychchart import PsychrometricChart
from ladybug.dt import DateTime
from ladybug_comfort.chart.polygonpmv import PolygonPMV
from ladybug.psychrometrics import wet_bulb_from_db_rh
from ladybug.datatype.temperature import WetBulbTemperature

from ladybug.epw import EPW


# set white background in all charts
pio.templates.default = 'plotly_white'


def heat_map(
    hourly_data: Union[HourlyContinuousCollection, HourlyDiscontinuousCollection],
    min_range: float = None, max_range: float = None,
    colors: List[Color] = None, title: str = None, show_title: bool = False,
    num_labels: int = None, labels: List[float] = None
) -> Figure:
    """Create a plotly heat map figure from Ladybug Hourly data.

    Args:
        hourly_data: A Ladybug HourlyContinuousCollection object or a Ladybug
            HourlyDiscontinuousCollection object.
        min_range: The minimum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        max_range: The maximum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        colors: A list of Ladybug Color objects. Defaults to None.
        title: A string to be used as the title of the plot. If not set, the name
            of the data will be used. Defaults to None.
        show_title: A boolean to show or hide the title of the chart. Defaults to False.
        num_labels: The number of labels to be used in the legend. Defaults to None.
        labels: A list of floats to be used as labels for the legend. Defaults to None.

    Returns:
        A plotly figure.
    """
    assert isinstance(hourly_data, (HourlyContinuousCollection,
                      HourlyDiscontinuousCollection)), 'Only Ladybug'\
        ' HourlyContinuousCollection and HourlyDiscontinuousCollection are supported.'\
        f' Instead got {type(hourly_data)}'

    if isinstance(hourly_data, HourlyDiscontinuousCollection):
        hourly_data, data_range = discontinuous_to_continuous(hourly_data)
    else:
        data_range = [hourly_data.min, hourly_data.max]

    var = hourly_data.header.data_type.name
    df = dataframe()
    series = Series(hourly_data)
    df[var] = series.values
    var_unit = df[var].dtype.name.split('(')[-1].split(')')[0]

    range_z = [data_range[0], data_range[1]]
    if min_range is not None:
        range_z[0] = min_range
    if max_range is not None:
        range_z[1] = max_range

    if not colors:
        colors = color_set[ColorSet.original.value]

    nticks = num_labels
    dtick = labels

    fig = go.Figure(
        data=go.Heatmap(
            y=df["hour"],
            x=df["UTC_time"].dt.date,
            z=df[var],
            zmin=range_z[0],
            zmax=range_z[1],
            colorscale=[rgb_to_hex(color) for color in colors],
            customdata=np.stack((df["month_names"], df["day"]), axis=-1),
            hovertemplate=(
                "<b>"
                + var
                + ": %{z} "
                + var_unit
                + "</b><br>Month: %{customdata[0]}<br>Day: %{customdata[1]}<br>"
                + "Hour: %{y}:00<br>"
            ),
            name="",
            colorbar=dict(title=var_unit, nticks=nticks, dtick=dtick, thickness=10),
        )
    )

    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_yaxes(title_text="Hours of the day")

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else var,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(
        template='plotly_white',
        margin=dict(
            l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title=fig_title,
        title_pad=dict(t=5)
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def _monthly_bar(data: MonthlyCollection, var: str, var_unit: str,
                 color: Color = None) -> Bar:
    """Create a monthly chart figure data from Ladybug Monthly data.

    Args:
        data: A Ladybug MonthlyCollection object.
        var: A Ladybug variable name.
        var_unit: A Ladybug variable unit.
        color: A Ladybug Color object. Defaults to None.

    Returns:
        A plotly Bar object.
    """

    df = dataframe(Frequency.MONTHLY)
    color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))

    return go.Bar(
        x=df['month_names'],
        y=[round(val, 2) for val in data.values],
        customdata=np.stack((df["month_names"],), axis=-1),
        hovertemplate=(
            '<br>%{y} '
            + var_unit
            + ' ' + var
            + '<extra></extra>'),
        marker_color=rgb_to_hex(color),
        marker_line_color='black',
        name=var
    )


def _daily_bar(data: DailyCollection, var: str, var_unit: str,
               color: Color = None) -> Bar:
    """Create a daily chart figure data from Ladybug Daily data.

    Args:
        data: A Ladybug DailyCollection object.
        var: A Ladybug variable name.
        var_unit: A Ladybug variable unit.
        color: A Ladybug Color object. Defaults to None.

    Returns:
        A plotly Bar object.
    """

    df = dataframe(Frequency.DAILY)
    color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))

    return go.Bar(
        x=df["UTC_time"].dt.date,
        y=[round(val, 2) for val in data.values],
        customdata=np.stack((df["month_names"], df["day"]), axis=-1),
        hovertemplate=(
            '<br>%{y} '
            + var_unit
            + ' on %{customdata[0]}'
            + ' %{customdata[1]} <br>'
            + '<extra></extra>'),
        marker_color=rgb_to_hex(color),
        name=var + ' ' + var_unit
    )


def bar_chart(data: Union[List[MonthlyCollection], List[DailyCollection]],
              min_range: float = None, max_range: float = None,
              colors: List[Color] = None,
              title: str = None,
              center_title: bool = False,
              stack: bool = False) -> Figure:
    """Create a plotly bar chart figure from multiple ladybug monthly or daily data.

    Args:
        data: A list of either ladybug MonthlyCollection data or DailyCollection data.
        min_range: Minimum value for the legend. If None, it is autocalculated
            from the data. (Default: None).
        max_range: Maximum value for the legend. If None, it is autocalculated
            from the data. (Default: None).
        colors: A list of ladybug color objects that matches the length of data
            argument. If None, random colors will be used. (Default: None).
        title: A string to be used as the title of the plot. (Default: None).
        center_title: A boolean to set whether to center the title of the
            chart. (Default: False).
        stack: A boolean to determine whether to stack the data. (Default: False).

    Returns:
        A plotly figure.
    """
    assert len(data) > 0 and all([isinstance(item, (MonthlyCollection, DailyCollection))
                                  for item in data]), 'Only a list of ladybug '\
        f' monthly data or ladybug daily data is supported. Instead got {type(data)}'

    if colors:
        assert len(colors) == len(data), 'Length of colors argument needs to match'\
            f' the length of data argument. Instead got {len(colors)} and {len(data)}'

    # set the range of y-axis and get the title if provided
    y_range = None if min_range is None or max_range is None else [min_range, max_range]
    y_title = '{} ({})'.format(data[0].header.data_type, data[0].header.unit)

    fig = go.Figure()
    for count, item in enumerate(data):
        var = item.header.metadata['type'] if 'type' in \
            item.header.metadata else str(item.header.data_type)
        var_unit = item.header.unit
        color = colors[count] if colors else None
        bar = _monthly_bar(item, var, var_unit, color) \
            if isinstance(item, MonthlyCollection) \
            else _daily_bar(item, var, var_unit, color)
        fig.add_trace(bar)

    # set the title for the figure
    fig_title = None
    if title is not None:
        fig_title = {
            'text': title,
            'y': 1,
            'x': 0,
            'yanchor': 'top'
        }
        if center_title:
            fig_title['x'] = 0.5
            fig_title['xanchor'] = 'center'

    # move legend upwards as mode data is loaded
    leg = {'x': 0, 'y': 1.2} if len(data) <= 3 else {}
    fig.update_layout(
        barmode='relative' if stack else 'group',
        template='plotly_white',
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title=fig_title,
        legend=leg
    )
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period",
                     showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1,
                     linecolor="black", mirror=True, range=y_range,
                     title_text=y_title)

    return fig


def _bar_chart_single_data(data: Union[MonthlyCollection, DailyCollection],
                           chart_type: str = 'monthly', title: str = None,
                           show_title: bool = False,
                           color: Color = None) -> Figure:
    """Create a plotly bar chart figure from a ladybug monthly or daily data object.

    Args:
        data: A ladybug monthly or daily data object.
        chart_type: A string to determine the type of chart to be created.
            Accepted values are 'monthly' and 'daily'. Defaults to 'monthly'.
        title: A string to be used as the title of the plot. If not set, the
            names of data will be used to create a title for the chart. Defaults to None.
        show_title: A boolean to set whether to show the title of the chart.
            Defaults to False.
        color: A ladybug color object. If not set, random colors will be used.

    Returns:
        A plotly figure.
    """

    if chart_type == 'monthly':
        var = data.header.data_type.name
        var_unit = data.header.unit
        bar = _monthly_bar(data, var, var_unit, color)
    else:
        var = data.header.data_type.name
        var_unit = data.header.unit
        bar = _daily_bar(data, var, var_unit, color)

    chart_title = title if title else var

    fig = go.Figure(bar)
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_yaxes(title_text='('+var_unit+')')

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title=fig_title,
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def monthly_bar_chart(data: MonthlyCollection,
                      title: str = None,
                      show_title: bool = False,
                      color: Color = None) -> Figure:
    """Create a plotly  bar chart figure from a ladybug monthly data object.

    Args:
        data: A ladybug MonthlyCollection object.
        title: A string to be used as the title of the plot. If not set, the name
            of the data will be used. Defaults to None.
        show_title: A boolean to set whether to show the title of the chart.
            Defaults to False.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """
    assert isinstance(data, MonthlyCollection), 'Only ladybug monthly data is'\
        f' supported. Instead got {type(data)}'

    return _bar_chart_single_data(data, 'monthly', title, show_title, color=color)


def daily_bar_chart(data: DailyCollection,
                    title: str = None,
                    show_title: bool = False,
                    color: Color = None) -> Figure:
    """Create a plotly bar chart figure from a ladybug daily data object.

    Args:
        data: A ladybug DailyCollection object.
        title: A string to be used as the title of the plot. If not set, the name
            of the data will be used. Defaults to None.
        show_title: A boolean to determine whether to show the title of the plot.
            Defaults to False.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """
    assert isinstance(data, DailyCollection), 'Only ladybug daily data is'\
        f' supported. Instead got {type(data)}'

    return _bar_chart_single_data(data, 'daily', title, show_title, color)


def hourly_line_chart(data: HourlyContinuousCollection, color: Color = None,
                      title: str = None, show_title: bool = False) -> Figure:
    """Create a plotly line chart figure from a ladybug hourly continuous data object.

    Args:
        data: A ladybug HourlyContinuousCollection object.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.
        title: A string to be used as the title of the plot. Defaults to None.
        show_title: A boolean to determine whether to show the title of the plot.
            Defaults to False.

    Returns:
        A plotly figure.
    """

    assert isinstance(data, HourlyContinuousCollection), \
        f'Only ladybug hourly continuous data is supported. Instead got {type(data)}'

    var = data.header.data_type.name
    var_unit = data.header.unit
    var_color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))

    df = dataframe()
    series = Series(data)
    df[var] = series.values
    df[var] = df[var].astype(float)

    data_max = 5 * ceil(df[var].max() / 5)
    data_min = 5 * floor(df[var].min() / 5)
    range_y = [data_min, data_max]

    # Get min, max, and mean of each day
    dbt_day = df.groupby(np.arange(len(df.index)) // 24)[var].agg(
        ["min", "max", "mean"]
    )
    trace1 = go.Bar(
        x=df["UTC_time"].dt.date.unique(),
        y=dbt_day["max"] - dbt_day["min"],
        base=dbt_day["min"],
        marker_color=rgb_to_hex(var_color),
        marker_opacity=0.3,
        name=var + " Range",
        customdata=np.stack(
            (dbt_day["mean"], df.iloc[::24, :]["month_names"], df.iloc[::24, :]["day"]),
            axis=-1,
        ),
        hovertemplate=(
            "Max: %{y:.2f} "
            + var_unit
            + "<br>Min: %{base:.2f} "
            + var_unit
            + "<br><b>Ave : %{customdata[0]:.2f} "
            + var_unit
            + "</b><br>Month: %{customdata[1]}<br>Day: %{customdata[2]}<br>"
            + "<extra></extra>"
        ),
    )

    trace2 = go.Scatter(
        x=df["UTC_time"].dt.date.unique(),
        y=dbt_day["mean"],
        name="Average " + var,
        mode="lines",
        marker_color=rgb_to_hex(var_color),
        marker_opacity=1,
        customdata=np.stack(
            (dbt_day["mean"], df.iloc[::24, :]["month_names"], df.iloc[::24, :]["day"]),
            axis=-1,
        ),
        hovertemplate=(
            "<b>Ave : %{customdata[0]:.2f} "
            + var_unit
            + "</b><br>Month: %{customdata[1]}<br>Day: %{customdata[2]}<br>"
            + "<extra></extra>"
        ),
    )

    data = [trace1, trace2]

    fig = go.Figure(
        data=data, layout=go.Layout(barmode="overlay", bargap=0, margin=dict(
            l=20, r=20, t=33, b=20))
    )

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else var,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_xaxes(
        dtick="M1",
        tickformat="%b",
        ticklabelmode="period",
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )
    fig.update_yaxes(
        range=range_y,
        title_text=f'({var_unit})',
        showline=True,
        linewidth=1,
        linecolor="black",
        mirror=True,
    )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template='plotly_white',
        title=fig_title
    )

    return fig


def diurnal_average_chart_from_hourly(
    data: HourlyContinuousCollection, title: str = None,
    show_title: bool = False,
    color: Color = None
) -> Figure:
    """Create a diurnal average chart from a ladybug hourly continuous data.

    Args:
        data: A ladybug HourlyContinuousCollection object.
        title: A string to be used as the title of the plot. Defaults to None.
        show_title: A boolean to determine whether to show the title of the plot.
            Defaults to False.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """

    assert isinstance(data, HourlyContinuousCollection), \
        f'Only ladybug hourly continuous data is supported. Instead got {type(data)}'

    # get monthly per hour average data
    monthly_values = get_monthly_values(data.average_monthly_per_hour())
    monthly_lower_values = get_monthly_values(data.percentile_monthly_per_hour(0))
    monthly_higher_values = get_monthly_values(data.percentile_monthly_per_hour(100))

    var = data.header.data_type.name
    var_unit = data.header.unit
    var_color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))
    var_color = rgb_to_hex(var_color)

    fig = go.Figure()

    for i in range(12):
        x = [[MONTHS[i]]*24, list(range(0, 24))]

        # add lower range
        fig.add_trace(
            go.Scatter(
                x=x,
                y=monthly_lower_values[i],
                line_color=var_color,
                line_width=0,
                opacity=0.2,
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + var+' low'
                    + ": %{y:.2f} "
                    + var_unit
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ),
            )
        )

        # add higher range
        fig.add_trace(
            go.Scatter(
                x=x,
                y=monthly_higher_values[i],
                line_color=var_color,
                fill='tonexty',
                line_width=0,
                opacity=0.1,
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + var + ' high'
                    + ": %{y:.2f} "
                    + var_unit
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ),)
        )

        # add MonthlyPerHour average dry-bulb temperature
        fig.add_trace(
            go.Scatter(
                x=x,
                y=monthly_values[i],
                line_color=var_color,
                line_width=2,
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + var
                    + ": %{y:.2f} "
                    + var_unit
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else var + f' ({var_unit})',
            'y': 0.85,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(

        xaxis=dict(
            showdividers=False,
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickson='boundaries',
            tickwidth=1,
            ticklen=5),

        yaxis=dict(
            showline=True,
            linecolor='black',
            linewidth=1,
            title=var_unit),

        title=fig_title,

    )
    return fig


def diurnal_average_chart(
    epw: EPW, title: str = None, show_title: bool = False,
    colors: Union[List[Color], Tuple[Color]] = Colorset.original()
) -> Figure:
    """Create a diurnal average chart from a ladybug EPW object.

    Args:
        epw: A ladybug EPW object.
        title: A string to be used as the title of the plot. Defaults to None.
        show_title: A boolean to determine whether to show the title of the plot.
            Defaults to False.
        colorset: A ColorSet object. Defaults to ColorSet.original.

    Returns:
        A plotly figure.
    """

    # reset colors if length of colors is less than 5
    if len(colors) < 5:
        color_range = ColorRange(colors, domain=[0, 5])
        num_of_colors: int = len(colors)*2 if len(colors)*2 >= 5 else 5
        colors: List[Color] = [color_range.color(i) for i in range(num_of_colors)]

    dbt_color = rgb_to_hex(colors[-1])
    wbt_color = rgb_to_hex(colors[-2])
    glob_hor_rad_color = rgb_to_hex(colors[-3])
    dir_nor_rad_color = rgb_to_hex(colors[-4])
    diff_hor_rad_color = rgb_to_hex(colors[-5])
    spread_color = rgb_to_hex(Color(149, 152, 156))

    # get monthly per hour average data
    glob_hor_rad = get_monthly_values(
        epw.global_horizontal_radiation.average_monthly_per_hour())

    dir_nor_rad = get_monthly_values(
        epw.direct_normal_radiation.average_monthly_per_hour())

    diff_hor_rad = get_monthly_values(
        epw.diffuse_horizontal_radiation.average_monthly_per_hour())

    dry_bulb_temp = get_monthly_values(
        epw.dry_bulb_temperature.average_monthly_per_hour())

    dry_bulb_temp_low = get_monthly_values(
        epw.dry_bulb_temperature.percentile_monthly_per_hour(0))

    dry_bulb_temp_high = get_monthly_values(
        epw.dry_bulb_temperature.percentile_monthly_per_hour(100))

    wet_bulb = HourlyContinuousCollection.compute_function_aligned(
        wet_bulb_from_db_rh, [epw.dry_bulb_temperature,
                              epw.relative_humidity, epw.atmospheric_station_pressure],
        WetBulbTemperature(), 'C')
    wet_bulb_temp = get_monthly_values(wet_bulb.average_monthly_per_hour())

    fig = go.Figure()

    for i in range(12):
        x = [[MONTHS[i]]*24, list(range(0, 24))]

        # add lower dry-bulb temperature
        fig.add_trace(
            go.Scatter(
                x=x,
                y=dry_bulb_temp_low[i],
                line_color=spread_color,
                line_width=0,
                opacity=0.2,
                yaxis='y2',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Dry-bulb temperature low'
                    + ": %{y:.2f} "
                    + 'C'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ),
            )
        )

        # add higher dry-bulb temperature
        fig.add_trace(
            go.Scatter(
                x=x,
                y=dry_bulb_temp_high[i],
                line_color=spread_color,
                fill='tonexty',
                line_width=0,
                opacity=0.1,
                yaxis='y2',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Dry-bulb temperature high'
                    + ": %{y:.2f} "
                    + 'C'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ),)
        )

        # add global horizontal radiation
        fig.add_trace(
            go.Scatter(
                x=x,
                y=glob_hor_rad[i],
                fill='tozeroy',
                line_width=1,
                line_color=glob_hor_rad_color,
                yaxis='y',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Monthly per hour average Global horizontal radiation'
                    + ": %{y:.2f} "
                    + 'Wh/m2'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

        # add direct normal radiation
        fig.add_trace(
            go.Scatter(
                x=x,
                y=dir_nor_rad[i],
                fill='tozeroy',
                line_width=1,
                line_color=dir_nor_rad_color,
                yaxis='y',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Monthly per hour average Direct normal radiation'
                    + ": %{y:.2f} "
                    + 'Wh/m2'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

        # add diffuse horizontal radiation
        fig.add_trace(
            go.Scatter(
                x=x,
                y=diff_hor_rad[i],
                fill='tozeroy',
                line_width=1,
                line_color=diff_hor_rad_color,
                yaxis='y',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Monthly per hour average Diffused horizontal radiation'
                    + ": %{y:.2f} "
                    + 'Wh/m2'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

        # add MonthlyPerHour average dry-bulb temperature
        fig.add_trace(
            go.Scatter(
                x=x,
                y=dry_bulb_temp[i],
                line_color=dbt_color,
                line_width=2,
                yaxis='y2',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Monthly per hour average dry-bulb temperature'
                    + ": %{y:.2f} "
                    + 'C'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

        # add MonthlyPerHour average wet-bulb temperature
        fig.add_trace(
            go.Scatter(
                x=x,
                y=wet_bulb_temp[i],
                line_color=wbt_color,
                line_width=2,
                yaxis='y2',
                showlegend=False,
                hovertemplate=(
                    "<b>"
                    + 'Monthly per hour average wet-bulb temperature'
                    + ": %{y:.2f} "
                    + 'C'
                    + "</b><br>Month: %{x[0]}<br>Hour: %{x[1]}:00<br>"
                    + "<extra></extra>"
                ))
        )

    # Add dummy traces to create legend
    fig.add_trace(get_dummy_trace(
        'Diffused horizontal radiation', diff_hor_rad_color))
    fig.add_trace(get_dummy_trace(
        'Direct normal radiation', dir_nor_rad_color))
    fig.add_trace(get_dummy_trace(
        'Global horizontal radiation', glob_hor_rad_color))
    fig.add_trace(get_dummy_trace(
        'Wet-bulb temperature', wbt_color))
    fig.add_trace(get_dummy_trace(
        'Dry-bulb temperature', dbt_color))

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else 'Diurnal Average',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(

        xaxis=dict(
            showdividers=False,
            showline=True,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickson='boundaries',
            tickwidth=1,
            ticklen=5),

        yaxis=dict(
            range=[0, 1600],
            tick0=0,
            dtick=100,
            title='Radiation Wh/m2',
            showline=True,
            linecolor='black',
            linewidth=1),

        yaxis2=dict(
            range=[-20, 60],
            tick0=-20,
            dtick=5,
            title='Temperature C',
            overlaying='y',
            side='right',
            showline=True,
            linecolor='black',
            linewidth=1),

        title=fig_title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )

    )

    return fig


def _speed_labels(bins, units):
    """Return labels for a wind speed range."""
    labels = []
    for left, right in zip(bins[:-1], bins[1:]):
        if left == bins[0]:
            labels.append("calm")
        elif np.isinf(right):
            labels.append(">{} {}".format(left, units))
        else:
            labels.append("{} - {} {}".format(left, right, units))
    return labels


def wind_rose(
    wind_rose: WindRose, title: str = None, show_title: bool = False
) -> Figure:
    """Create a windrose plot.

    Args:
        wind_rose: A ladybug WindRose object.
        title: A title for the plot. Defaults to None.
        show_title: A boolean to show or hide the title. Defaults to False.

    Returns:
        A plotly figure.
    """

    assert isinstance(wind_rose, WindRose), 'Ladybug WindRose object is required.'
    f' Instead got {type(wind_rose)}'

    wind_speed = wind_rose.analysis_data_collection
    wind_dir = wind_rose.direction_data_collection

    if isinstance(wind_speed, HourlyDiscontinuousCollection):
        wind_speed = discontinuous_to_continuous(wind_speed)[0]
        wind_dir = discontinuous_to_continuous(wind_dir)[0]

    df = dataframe()
    series = Series(wind_speed)
    df['wind_speed'] = series.values
    series = Series(wind_dir)
    df['wind_dir'] = series.values

    start_month = wind_rose.analysis_period.st_month
    end_month = wind_rose.analysis_period.end_month
    start_hour = wind_rose.analysis_period.st_hour
    end_hour = wind_rose.analysis_period.end_hour

    if start_month <= end_month:
        df = df.loc[(df["month"] >= start_month) & (df["month"] <= end_month)]
    else:
        df = df.loc[(df["month"] <= end_month) | (df["month"] >= start_month)]
    if start_hour <= end_hour:
        df = df.loc[(df["hour"] >= start_hour) & (df["hour"] <= end_hour)]
    else:
        df = df.loc[(df["hour"] <= end_hour) | (df["hour"] >= start_hour)]

    spd_bins = [-1, 0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, np.inf]
    # Create a color range if the colorset does not have 11 colors
    if len(wind_rose.legend_parameters.colors) < 11:
        domain = [spd_bins[0], spd_bins[-2]+1]
        color_range = ColorRange(
            colors=wind_rose.legend_parameters.colors, domain=domain)
        spd_colors = [rgb_to_hex(color_range.color(item)) for item in spd_bins]
    else:
        spd_colors = [rgb_to_hex(color) for color in wind_rose.legend_parameters.colors]

    spd_labels = _speed_labels(spd_bins, units=wind_speed.header.unit)
    dir_bins = np.arange(-22.5 / 2, 370, 22.5)
    dir_labels = (dir_bins[:-1] + dir_bins[1:]) / 2
    total_count = df.shape[0]
    calm_count = df.query("wind_speed == 0").shape[0]
    rose = (
        df.assign(
            WindSpd_bins=lambda df: pd.cut(
                df["wind_speed"], bins=spd_bins, labels=spd_labels, right=True
            )
        )
        .assign(
            WindDir_bins=lambda df: pd.cut(
                df["wind_dir"], bins=dir_bins, labels=dir_labels, right=False
            )
        )
        .replace({"WindDir_bins": {360: 0}})
        .groupby(by=["WindSpd_bins", "WindDir_bins"])
        .size()
        .unstack(level="WindSpd_bins")
        .fillna(0)
        .assign(calm=lambda df: calm_count / df.shape[0])
        .sort_index(axis=1)
        .applymap(lambda x: x / total_count * 100)
    )
    fig = go.Figure()
    for i, col in enumerate(rose.columns):
        fig.add_trace(
            go.Barpolar(
                r=rose[col],
                theta=rose.index.categories,
                name=col,
                marker_color=spd_colors[i],
                hovertemplate="frequency: %{r:.2f}%"
                + "<br>"
                + "direction: %{theta:.2f}"
                + "\u00B0 deg"
                + "<br>",
            )
        )

    fig.update_traces(
        text=[
            "North",
            "N-N-E",
            "N-E",
            "E-N-E",
            "East",
            "E-S-E",
            "S-E",
            "S-S-E",
            "South",
            "S-S-W",
            "S-W",
            "W-S-W",
            "West",
            "W-N-W",
            "N-W",
            "N-N-W",
        ]
    )

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else 'Wind Rose',
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(
        autosize=True,
        polar_angularaxis_rotation=90,
        polar_angularaxis_direction="clockwise",
        dragmode=False,
        margin=dict(l=20, r=20, t=55, b=20),
        title=fig_title,
    )

    return fig


def psych_chart(
    psych: PsychrometricChart, data: BaseCollection = None,
    title: str = None, show_title: bool = False, polygon_pmv: PolygonPMV = None,
    strategies: List[Strategy] = [Strategy.comfort],
    strategy_parameters: StrategyParameters = StrategyParameters(),
    solar_data: HourlyContinuousCollection = None,
    colors: List[Color] = None
) -> Figure:
    """Create a psychrometric chart.

    Args:
        psych: A ladybug PsychrometricChart object.
        data: A ladybug DataCollection object.
        title: A title for the plot. Defaults to None.
        show_title: A boolean to show or hide the title. Defaults to False.
        polygon_pmv: A ladybug PolygonPMV object. If provided, polygons will be drawn.
            Defaults to None.
        strategies: A list of strategies to be applied to the chart. Accepts a list of
            Stragegy objects. Defaults to out of the box StrategyParameters object.
        strategy_parameters: A StrategyParameters object. Defaults to None.
        solar_data: An annual hourly continuous data collection of irradiance
            (or radiation) in W/m2 (or Wh/m2) that aligns with the data
            points on the psychrometric chart. This is only required when
            plotting a "Passive Solar Heating" strategy polygon on the chart.
            The irradiance values should be incident on the orientation of
            the passive solar heated windows. So using global horizontal
            radiation assumes that all windows are skylights (like a
            greenhouse). Defaults to None.
        colors: A list of colors to be used for the comfort polygons. Defaults to None.

    Returns:
        A plotly figure.
    """
    return _psych_chart(psych, data, title, show_title, polygon_pmv, strategies,
                        strategy_parameters, solar_data, colors)


def sunpath(
    sunpath: Sunpath, data: HourlyContinuousCollection = None,
    colorset: Colorset = Colorset.original(), min_range: float = None,
    max_range: float = None, title: str = None, show_title: bool = False
) -> Figure:
    """ Plot Sunpath.

    Args:
        sunpath: A Ladybug Sunpath object.
        data: An HourlyContinuousCollection object to be plotted on the sunpath. Defaults
            to None.
        colorset: A Ladybug Colorset object. Defaults to ColorSet.original.
        min_range: Minimum value for the colorbar. If not set, the minimum value will be
            set to the minimum value of the data. Defaults to None.
        max_range: Maximum value for the colorbar. If not set, the maximum value will be
            set to the maximum value of the data. Defaults to None.
        title: A string to be used as the title of the plot. Defaults to None.
        show_title: A boolean to show or hide the title of the plot. Defaults to False.

    Returns:
        A plotly Figure.
    """
    df = dataframe()
    time_zone = sunpath.time_zone

    altitudes, azimuths = [], []
    for time in df['times']:
        date_time = DateTime(time.month, time.day, time.hour, time.minute)
        altitudes.append(sunpath.calculate_sun_from_date_time(date_time).altitude)
        azimuths.append(sunpath.calculate_sun_from_date_time(date_time).azimuth)

    df['altitude'] = altitudes
    df['azimuth'] = azimuths

    if data:
        assert isinstance(data, HourlyContinuousCollection), 'data must be an'
        f' HourlyContinuousCollection. Instead got {type(data)}.'

        var_name = data.header.data_type.name
        var_unit = data.header.unit
        var_colorscale = [rgb_to_hex(color) for color in colorset]
        chart_title = 'Sunpath - ' + var_name if title is None else title

        # add data to the dataframe
        df[var_name] = Series(data).values
        # filter the whole dataframe based on sun elevations
        solpos = df.loc[df["altitude"] > 0, :]

        data_max = 5 * ceil(solpos[var_name].max() / 5)
        data_min = 5 * floor(solpos[var_name].min() / 5)

        var_range = [data_min, data_max]
        if min_range is not None:
            var_range[0] = min_range
        if max_range is not None:
            var_range[1] = max_range
    else:
        solpos = df.loc[df["altitude"] > 0, :]
        chart_title = 'Sunpath' if title is None else title

    tz = "UTC"
    try:
        times = pd.date_range(
            "2019-01-01 00:00:00", "2020-01-01", closed="left", freq="H", tz=tz
        )
    except TypeError:
        times = pd.date_range(
            "2019-01-01 00:00:00", "2020-01-01", inclusive="left", freq="H", tz=tz
        )
    delta = timedelta(days=0, hours=time_zone - 1, minutes=0)
    times = times - delta

    if not data:
        var_color = rgb_to_hex(colorset[-1])
        marker_size = 3
    else:
        var_color = '#8c8e91'
        vals = solpos[var_name]
        marker_size = (((vals - vals.min()) / vals.max()) + 1) * 4

    fig = go.Figure()
    # draw altitude circles
    for i in range(10):
        pt = []
        for j in range(361):
            pt.append(j)

        fig.add_trace(
            go.Scatterpolar(
                r=[90 * cos(radians(i * 10))] * 361,
                theta=pt,
                mode="lines",
                line_color="silver",
                line_width=1,
                hovertemplate="Altitude circle<br>" + str(i * 10) + "\u00B0deg",
                name="",
            )
        )

    # Draw annalemma
    if not data:
        fig.add_trace(
            go.Scatterpolar(
                r=90 * np.cos(np.radians(solpos["altitude"])),
                theta=solpos["azimuth"],
                mode="markers",
                marker_color=var_color,
                marker_size=marker_size,
                marker_line_width=0,
                customdata=np.stack(
                    (
                        solpos["day"],
                        solpos["month_names"],
                        solpos["hour"],
                        solpos["altitude"],
                        solpos["azimuth"],
                    ),
                    axis=-1,
                ),
                hovertemplate="month: %{customdata[1]}"
                + "<br>day: %{customdata[0]:.0f}"
                + "<br>hour: %{customdata[2]:.0f}:00"
                + "<br>sun altitude: %{customdata[3]:.2f}"
                + "\u00B0deg"
                + "<br>sun azimuth: %{customdata[4]:.2f}"
                + "\u00B0deg"
                + "<br>",
                name="",
            )
        )
    else:
        fig.add_trace(
            go.Scatterpolar(
                r=90 * np.cos(np.radians(solpos['altitude'])),
                theta=solpos["azimuth"],
                mode="markers",
                marker=dict(
                    color=solpos[var_name],
                    size=marker_size,
                    line_width=0,
                    colorscale=var_colorscale,
                    cmin=var_range[0],
                    cmax=var_range[1],
                    colorbar=dict(thickness=10, title=var_unit + "<br>  "),
                ),
                customdata=np.stack(
                    (
                        solpos["day"],
                        solpos["month_names"],
                        solpos["hour"],
                        solpos["altitude"],
                        solpos["azimuth"],
                        solpos[var_name],
                    ),
                    axis=-1,
                ),
                hovertemplate="month: %{customdata[1]}"
                + "<br>day: %{customdata[0]:.0f}"
                + "<br>hour: %{customdata[2]:.0f}:00"
                + "<br>sun altitude: %{customdata[3]:.2f}"
                + "\u00B0deg"
                + "<br>sun azimuth: %{customdata[4]:.2f}"
                + "\u00B0deg"
                + "<br>"
                + "<br><b>"
                + var_name
                + ": %{customdata[5]:.2f}"
                + var_unit
                + "</b>",
                name="",
            )
        )

    # draw equinox and sostices
    for date in pd.to_datetime(["2019-03-21", "2019-06-21", "2019-12-21"]):
        times = pd.date_range(date, date + pd.Timedelta("24h"), freq="5min", tz='UTC')
        times = times - delta
        solpos = pd.DataFrame()
        solpos['times'] = times
        solpos.set_index("times", drop=False, append=False,
                         inplace=True, verify_integrity=False)

        azimuth, altitude = [], []
        for time in times:
            azimuth.append(sunpath.calculate_sun_from_date_time(
                DateTime(time.month, time.day, time.hour, time.minute)).azimuth)
            altitude.append(sunpath.calculate_sun_from_date_time(
                DateTime(time.month, time.day, time.hour, time.minute)).altitude)

        solpos['azimuth'] = azimuth
        solpos['altitude'] = altitude

        solpos = solpos.loc[solpos['altitude'] > 0, :]

        # This sorting is necessary for the correct drawing of lines
        alts = list(90 * np.cos(np.radians(solpos.altitude)))
        azis = list(solpos.azimuth)
        azi_alt = {azis[i]: alts[i] for i in range(len(azis))}
        azi_alt_sorted = {k: azi_alt[k] for k in sorted(azi_alt)}

        fig.add_trace(
            go.Scatterpolar(
                r=list(azi_alt_sorted.values()),
                theta=list(azi_alt_sorted.keys()),
                mode="markers",
                marker=dict(color=var_color, size=2.5),
                customdata=solpos.altitude,
                hovertemplate="<br>sun altitude: %{customdata:.2f}"
                + "\u00B0deg"
                + "<br>sun azimuth: %{theta:.2f}"
                + "\u00B0deg"
                + "<br>",
                name="",
            )
        )

    # draw sunpath on the 21st of each other month
    for date in pd.to_datetime(["2019-01-21", "2019-02-21", "2019-4-21", "2019-5-21"]):
        times = pd.date_range(date, date + pd.Timedelta("24h"), freq="5min", tz=tz)
        times = times - delta
        solpos = pd.DataFrame()
        solpos['times'] = times
        solpos.set_index("times", drop=False, append=False,
                         inplace=True, verify_integrity=False)

        azimuth, altitude = [], []
        for time in times:
            azimuth.append(sunpath.calculate_sun_from_date_time(
                DateTime(time.month, time.day, time.hour, time.minute)).azimuth)
            altitude.append(sunpath.calculate_sun_from_date_time(
                DateTime(time.month, time.day, time.hour, time.minute)).altitude)

        solpos['azimuth'] = azimuth
        solpos['altitude'] = altitude

        solpos = solpos.loc[solpos["altitude"] > 0, :]

        # This sorting is necessary for the correct drawing of lines
        alts = list(90 * np.cos(np.radians(solpos.altitude)))
        azis = list(solpos.azimuth)
        azi_alt = {azis[i]: alts[i] for i in range(len(azis))}
        azi_alt_sorted = {k: azi_alt[k] for k in sorted(azi_alt)}

        fig.add_trace(
            go.Scatterpolar(
                r=list(azi_alt_sorted.values()),
                theta=list(azi_alt_sorted.keys()),
                mode="markers",
                marker=dict(color=var_color, size=2.5),
                customdata=solpos.altitude,
                hovertemplate="<br>sun altitude: %{customdata:.2f}"
                + "\u00B0deg"
                + "<br>sun azimuth: %{theta:.2f}"
                + "\u00B0deg"
                + "<br>",
                name="",
            )
        )

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis=dict(tickfont_size=10, visible=False),
            angularaxis=dict(
                tickfont_size=10,
                rotation=90,  # start position of angular axis
                direction="clockwise",
            ),
        ),
        autosize=False,
        template='plotly_white',
        title_x=0.5,
        dragmode=False,
        margin=dict(l=20, r=20, t=33, b=20),
        title=fig_title,
    )

    return fig


def bar_chart_with_table(data: List[MonthlyCollection],
                         min_range: float = None, max_range: float = None,
                         colors: List[Color] = None,
                         title: str = None,
                         show_title: bool = False,
                         stack: bool = False) -> Figure:
    """Create a plotly bar chart figure from multiple ladybug monthly or daily data.

    Args:
        data: A list of ladybug monthly data.
        min_range: Minimum value for the legend. If not set will be calculated
            from the data. Defaults to None.
        max_range: Maximum value for the legend. If not set will be calculated
            from the data. Defaults to None.
        colors: A list of ladybug color objects. The length of this list needs to match
            the length of data argument. If not set, random colors will be used.
            Defaults to None.
        title: A string to be used as the title of the plot. If not set, the
            names of data will be used to create a title for the chart. Defaults to None.
        show_title: A boolean to set whether to show the title of the chart.
            Defaults to False.
        stack: A boolean to determine whether to stack the data. Defaults to False which
            will show data side by side.

    Returns:
        A plotly figure.
    """
    assert len(data) > 0 and all([isinstance(item, MonthlyCollection)
                                  for item in data]), 'Only a list of ladybug '\
        f' monthly data is supported. Instead got {type(data)}'

    if colors:
        assert len(colors) == len(data), 'Length of colors argument needs to match'\
            f' the length of data argument. Instead got {len(colors)} and {len(data)}'

    colors = colors if colors else [Color(randint(0, 255), randint(0, 255),
                                          randint(0, 255)) for item in data]

    # set the range of y-axis if provided
    y_range = None
    if min_range is not None and max_range is not None:
        y_range = [min_range, max_range]
    fig_specs = [[{"type": "bar"}], [{"type": "table"}]]
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1, specs=fig_specs)

    names = []

    for count, item in enumerate(data):
        var = item.header.data_type.name
        var_unit = item.header.unit
        color = colors[count] if colors else None
        bar = _monthly_bar(item, var, var_unit, color)
        fig.add_trace(bar, row=1, col=1)
        names.append(var)

    # add table
    values, colors = group_monthly(data, colors)
    table = go.Table(
        header=dict(values=None, fill_color='#ffffff'),
        cells=dict(values=values, fill_color=colors))

    fig.add_trace(table, row=2, col=1)

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else ' - '.join(names),
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    # move legend upwards as mode data is loaded
    legend_height = 1.2 if len(data) <= 3 else 1.2 + (len(data)-3)/10

    fig.update_layout(
        barmode='relative' if stack else 'group',
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title=fig_title,
        legend={
            'x': 0,
            'y': legend_height,
        }
    )
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period",
                     showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1,
                     linecolor="black", mirror=True, range=y_range)

    return fig
