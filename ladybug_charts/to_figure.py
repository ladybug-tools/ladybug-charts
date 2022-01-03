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
from ._helper import discontinuous_to_continuous, rgb_to_hex, ColorSet, color_set

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug.windrose import WindRose
from ladybug.color import Color
from ladybug_pandas.series import Series
from ladybug import psychrometrics as psy
from ladybug.sunpath import Sunpath
from ladybug.psychchart import PsychrometricChart
from ladybug.dt import DateTime

# set white background in all charts
pio.templates.default = 'plotly_white'


def heat_map(hourly_data: Union[HourlyContinuousCollection, HourlyDiscontinuousCollection],
             min_range: float = None, max_range: float = None,
             colorset: ColorSet = ColorSet.original) -> Figure:
    """Create a plotly heat map figure from Ladybug Hourly data.

    Args:
        hourly_data: A Ladybug HourlyContinuousCollection object or a Ladybug
            HourlyDiscontinuousCollection object.
        min_range: The minimum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        max_range: The maximum value for the legend of the heatmap. If not set, value
            will be calculated based on data. Defaults to None.
        colorset: A ColorSets object. Defaults to Original Ladybug Colorset.

    Returns:
        A plotly figure.
    """
    assert isinstance(hourly_data, (HourlyContinuousCollection,
                      HourlyDiscontinuousCollection)), 'Only Ladybug'\
        ' HourlyContinuousCollection and HourlyDiscontinuousCollection are supported.'\
        f' Instead got {type(hourly_data)}'

    if isinstance(hourly_data, HourlyDiscontinuousCollection):
        hourly_data = discontinuous_to_continuous(hourly_data)

    var = hourly_data.header.data_type.name
    df = dataframe()
    series = Series(hourly_data)
    df[var] = series.values
    var_unit = df[var].dtype.name.split('(')[-1].split(')')[0]

    if min_range != None and max_range != None:
        range_z = [min_range, max_range]
    elif min_range != None and max_range == None:
        range_z = [min_range, 5 * ceil(df[var].max() / 5)]
    elif min_range == None and max_range != None:
        range_z = [5 * floor(df[var].min() / 5), max_range]
    else:
        # Set maximum and minimum according to data
        range_z = [5 * floor(df[var].min() / 5), 5 * ceil(df[var].max() / 5)]

    fig = go.Figure(
        data=go.Heatmap(
            y=df["hour"],
            x=df["UTC_time"].dt.date,
            z=df[var],
            zmin=range_z[0],
            zmax=range_z[1],
            colorscale=[rgb_to_hex(color) for color in color_set[colorset.value]],
            customdata=np.stack((df["month_names"], df["day"]), axis=-1),
            hovertemplate=(
                "<b>"
                + var
                + ": %{z} "
                + var_unit
                + "</b><br>Month: %{customdata[0]}<br>Day: %{customdata[1]}<br>Hour: %{y}:00<br>"
            ),
            name="",
            colorbar=dict(title=var_unit),
        )
    )

    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_yaxes(title_text="Hours of the day")

    fig.update_layout(
        template='plotly_white',
        margin=dict(
            l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title={
            'text': var,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
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
        text=[f'{round(val, 2)} {var_unit}' for val in data.values],
        textposition='auto',
        customdata=np.stack((df["month_names"],), axis=-1),
        hovertemplate=(
            '<br>%{y} '
            + var_unit
            + ' in %{customdata[0]}'
            + '<extra></extra>'),
        marker_color=rgb_to_hex(color),
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
        name=var
    )


def bar_chart(data: Union[List[MonthlyCollection], List[DailyCollection]],
              chart_title: str = None,
              colors: List[Color] = None,
              stack: bool = False) -> Figure:
    """Create a plotly bar chart figure from multiple ladybug monthly or daily data.

    Args:
        data: A list of ladybug monthly data or a list of ladybug daily data.
        chart_title: A string to be used as the title of the plot. If not set, the
            names of data will be used to create a title for the chart. Defaults to None.
        colors: A list of ladybug color objects. The length of this list needs to match
            the length of data argument. If not set, random colors will be used.
            Defaults to None.
        stack: A boolean to determine whether to stack the data. Defaults to False which
            will show data side by side.

    Returns:
        A plotly figure.
    """
    assert len(data) > 0 and all([isinstance(item, (MonthlyCollection, DailyCollection))
                                  for item in data]), 'Only a list of ladybug '\
        f' monthly data or ladybug daily data is supported. Instead got {type(data)}'

    if colors:
        assert len(colors) == len(data), 'Length of colors argument needs to match'\
            f' the length of data argument. Instead got {len(colors)} and {len(data)}'

    fig = go.Figure()
    names = []

    for count, item in enumerate(data):

        if isinstance(item, MonthlyCollection):
            var = item.header.data_type.name
            var_unit = item.header.unit
            color = colors[count] if colors else None
            bar = _monthly_bar(item, var, var_unit, color)
            fig.add_trace(bar)
            names.append(var)
        else:
            var = item.header.data_type.name
            var_unit = item.header.unit
            color = colors[count] if colors else None
            bar = _daily_bar(item, var, var_unit, color)
            fig.add_trace(bar)
            names.append(var)

    chart_title = chart_title if chart_title else ' - '.join(names)

    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_layout(
        barmode='relative' if stack else 'group',
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title={
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend={
            'x': 0,
            'y': 1.2,
        }
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def _bar_chart_single_data(data: Union[MonthlyCollection, DailyCollection],
                           chart_type: str = 'monthly', chart_title: str = None,
                           color: Color = None) -> Figure:
    """Create a plotly bar chart figure from a ladybug monthly or daily data object.

    Args:
        data: A ladybug monthly or daily data object.
        chart_type: A string to determine the type of chart to be created.
            Accepted values are 'monthly' and 'daily'. Defaults to 'monthly'.
        chart_title: A string to be used as the title of the plot. If not set, the
            names of data will be used to create a title for the chart. Defaults to None.
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

    chart_title = chart_title if chart_title else var

    fig = go.Figure(bar)
    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")
    fig.update_yaxes(title_text='('+var_unit+')')
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        yaxis_nticks=13,
        title={
            'text': chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def monthly_bar_chart(data: MonthlyCollection,
                      chart_title: str = None,
                      color: Color = None) -> Figure:
    """Create a plotly  bar chart figure from a ladybug monthly data object.

    Args:
        data: A ladybug MonthlyCollection object.
        chart_title: A string to be used as the title of the plot. If not set, the name
            of the data will be used. Defaults to None.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """
    assert isinstance(data, MonthlyCollection), 'Only ladybug monthly data is'\
        f' supported. Instead got {type(data)}'

    return _bar_chart_single_data(data, 'monthly', chart_title=chart_title, color=color)


def daily_bar_chart(data: DailyCollection,
                    chart_title: str = None,
                    color: Color = None) -> Figure:
    """Create a plotly bar chart figure from a ladybug daily data object.

    Args:
        data: A ladybug DailyCollection object.
        chart_title: A string to be used as the title of the plot. If not set, the name
            of the data will be used. Defaults to None.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """
    assert isinstance(data, DailyCollection), 'Only ladybug daily data is'\
        f' supported. Instead got {type(data)}'

    return _bar_chart_single_data(data, 'daily', chart_title=chart_title, color=color)


def hourly_line_chart(data: HourlyContinuousCollection, color: Color = None) -> Figure:
    """Create a plotly line chart figure from a ladybug hourly continuous data object.

    Args:
        data: A ladybug HourlyContinuousCollection object.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """

    assert isinstance(data, HourlyContinuousCollection), 'Only ladybug hourly continuous'\
        f' data is supported. Instead got {type(data)}'

    var = data.header.data_type.name
    var_unit = data.header.unit
    var_color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))

    df = dataframe()
    series = Series(data)
    df[var] = series.values

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
    )

    return fig


def per_hour_line_chart(data: HourlyContinuousCollection,
                        color: Color = None) -> Figure:
    """Create a plotly per hour line chart figure from a ladybug hourly continuous data.

    Args:
        data: A ladybug HourlyContinuousCollection object.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """

    assert isinstance(data, HourlyContinuousCollection), 'Only ladybug hourly continuous'\
        f' data is supported. Instead got {type(data)}'

    var = data.header.data_type.name
    var_unit = data.header.unit
    var_color = color if color else Color(
        randint(0, 255), randint(0, 255), randint(0, 255))

    df = dataframe()
    series = Series(data)
    df[var] = series.values

    data_max = 5 * ceil(df[var].max() / 5)
    data_min = 5 * floor(df[var].min() / 5)
    range_y = [data_min, data_max]

    var_month_ave = df.groupby(["month", "hour"])[var].median().reset_index()

    fig = make_subplots(
        rows=1,
        cols=12,
        subplot_titles=MONTHS,
    )

    for i in range(12):

        fig.add_trace(
            go.Scatter(
                x=df.loc[df["month"] == i + 1, "hour"],
                y=df.loc[df["month"] == i + 1, var],
                mode="markers",
                marker_color=rgb_to_hex(var_color),
                opacity=0.5,
                marker_size=3,
                name=MONTHS[i],
                showlegend=False,
                customdata=df.loc[df["month"] == i + 1, "month_names"],
                hovertemplate=(
                    "<b>"
                    + var
                    + ": %{y:.2f} "
                    + var_unit
                    + "</b><br>Month: %{customdata}<br>Hour: %{x}:00<br>"
                ),
            ),
            row=1,
            col=i + 1,
        )

        fig.add_trace(
            go.Scatter(
                x=var_month_ave.loc[var_month_ave["month"] == i + 1, "hour"],
                y=var_month_ave.loc[var_month_ave["month"] == i + 1, var],
                mode="lines",
                line_color=rgb_to_hex(var_color),
                line_width=3,
                name=None,
                showlegend=False,
                hovertemplate=(
                    "<b>" + var + ": %{y:.2f} " + var_unit + "</b><br>Hour: %{x}:00<br>"
                ),
            ),
            row=1,
            col=i + 1,
        )

        fig.update_xaxes(range=[0, 25], row=1, col=i + 1)
        fig.update_yaxes(range=range_y, row=1, col=i + 1)

    fig.update_xaxes(
        ticktext=["6", "12", "18"], tickvals=["6", "12", "18"], tickangle=0
    )
    fig.update_layout(
        template='plotly_white',
        dragmode=False,
        margin=dict(l=20, r=20, t=55, b=20),
        title={
            'text': var + f' ({var_unit})',
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
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


def wind_rose(wind_rose: WindRose, title: str = 'Wind Rose', legend: bool = True,
              colorset: ColorSet = ColorSet.original) -> Figure:
    """Create a windrose plot.

    Args:
        wind_rose: A ladybug WindRose object.
        title: A title for the plot. Defaults to Wind Rose.
        legend: A boolean to show/hide legend. Defaults to True.
        colorset: A ladybug colorset object. Defaults to ColorSet.original.

    Returns:
        A plotly figure.
    """

    assert isinstance(wind_rose, WindRose), 'Ladybug WindRose object is required.'\
        f' Instead got {type(wind_rose)}'

    wind_speed = wind_rose.analysis_data_collection
    wind_dir = wind_rose.direction_data_collection

    if isinstance(wind_speed, HourlyDiscontinuousCollection):
        wind_speed = discontinuous_to_continuous(wind_speed)
        wind_dir = discontinuous_to_continuous(wind_dir)

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

    spd_colors = [rgb_to_hex(color) for color in color_set[colorset.value]]
    spd_bins = [-1, 0.5, 1.5, 3.3, 5.5, 7.9, 10.7, 13.8, 17.1, 20.7, np.inf]
    spd_labels = _speed_labels(spd_bins, units="m/s")
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
    if title != "":
        fig.update_layout(title=title, title_x=0.5)
    fig.update_layout(
        autosize=True,
        polar_angularaxis_rotation=90,
        polar_angularaxis_direction="clockwise",
        showlegend=legend,
        dragmode=False,
        margin=dict(l=20, r=20, t=55, b=20),
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig


def _humidity_ratio(dbt: float, rh: float) -> float:
    if dbt == None or rh == None:
        return 0.0
    return psy.humid_ratio_from_db_rh(dbt, rh)


def psych_chart(psych: PsychrometricChart,
                data: Union[HourlyContinuousCollection,
                            HourlyDiscontinuousCollection] = None,
                colorset: ColorSet = ColorSet.original, title: str = None) -> Figure:
    """Create a psychrometric chart.

    Args:
        psych: A ladybug PsychrometricChart object.
        data: A ladybug HourlyDataCollection object.
        colorset: A Colorset object. Defaults to ColorSet.original which will use
            Ladybug's original colorset.
        title: A title for the plot. Defaults to None.

    Returns:
        A plotly figure.
    """

    # get dbt and rh from the psychrometric chart
    dbt = psych.temperature
    rh = psych.relative_humidity

    # We're not supporting Daily data for now
    assert not isinstance(dbt, DailyCollection), 'Ladybug PsychrometricChart created'\
        ' using DailyCollection is not supported.'

    # make sure all data collections are aligned
    if data:
        if isinstance(data, HourlyDiscontinuousCollection):
            assert HourlyDiscontinuousCollection.are_collections_aligned([data, dbt, rh]),\
                'HourlyDiscontinuousCollection objects are not aligned.'
        elif isinstance(data, HourlyContinuousCollection):
            assert HourlyContinuousCollection.are_collections_aligned([data, dbt, rh]),\
                'HourlyContinuousCollection objects are not aligned.'
        else:
            raise ValueError(f'{type(data)} object is not supported.')

    # Convert Discontinuous data to Continuous data
    if isinstance(dbt, HourlyDiscontinuousCollection):
        if data:
            data = discontinuous_to_continuous(data)
        dbt = discontinuous_to_continuous(dbt)
        rh = discontinuous_to_continuous(rh)

    # creating dataframe
    df = dataframe()
    df['DBT'] = Series(dbt).values
    df['RH'] = Series(rh).values
    df['hr'] = np.vectorize(_humidity_ratio)(dbt.values, rh.values)

    # Set maximum and minimum according to data
    data_max = 5 * ceil(df["DBT"].max() / 5)
    data_min = 5 * floor(df["DBT"].min() / 5)
    var_range_x = [data_min, data_max]

    data_max = (5 * ceil(df["hr"].max() * 1000 / 5)) / 1000
    data_min = (5 * floor(df["hr"].min() * 1000 / 5)) / 1000
    var_range_y = [data_min, data_max]

    dbt_list = list(range(-60, 60, 1))
    rh_list = list(range(10, 110, 10))

    rh_df = pd.DataFrame()
    for rh_item in rh_list:
        hr_list = np.vectorize(psy.humid_ratio_from_db_rh)(dbt_list, rh_item)
        name = "rh" + str(rh_item)
        rh_df[name] = hr_list

    fig = go.Figure()

    # Add curved lines for humidity
    for rh_item in rh_list:
        name = "rh" + str(rh_item)
        fig.add_trace(
            go.Scatter(
                x=dbt_list,
                y=rh_df[name],
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="RH " + str(rh_item) + "%",
                line=dict(width=1, color="#85837f"),
            )
        )

    # if no data is provided, plot frequency
    if not data:
        title = 'Psychrometric Chart - Frequency'
        fig.add_trace(
            go.Histogram2d(
                x=df["DBT"],
                y=df["hr"],
                name="",
                colorscale=[rgb_to_hex(color)
                            for color in color_set[colorset.value]],
                hovertemplate="",
                histnorm="",
                histfunc="count",
                autobinx=False,
                xbins=dict(start=var_range_x[0], end=var_range_x[1], size=1),
                autobiny=False,
                ybins=dict(start=var_range_y[0], end=var_range_y[1], size=0.001),
            )
        )

    # plot the data
    else:
        var = data.header.data_type.name
        var_unit = data.header.unit
        df[var] = Series(data).values

        fig.add_trace(
            go.Scatter(
                x=df["DBT"],
                y=df["hr"],
                showlegend=False,
                mode="markers",
                marker=dict(
                    size=7,
                    color=df[var],
                    showscale=True,
                    opacity=1,
                    colorscale=[rgb_to_hex(color)
                                for color in color_set[colorset.value]],
                    colorbar=dict(thickness=30, title=var_unit + "<br>  "),
                ),
                customdata=np.stack((df['RH'], df[var]), axis=-1),
                hovertemplate='Dry bulb temperature'
                + ": %{x}"
                + ' C'
                + "<br>"
                + 'Relative humidity'
                + ": %{customdata[0]}"
                + ' %'
                + "<br>"
                + 'Humidity ratio'
                + ": %{y: .2f}"
                + ' Kg water / Kg air'
                + "<br>"
                + var
                + ": %{customdata[1]}"
                + ' ' + var_unit,
                name="",
            )
        )

        title = title if title else f'Psychrometric Chart - {var}'

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        title={
            'text': title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        })

    print(var_range_x, var_range_y)
    fig.update_xaxes(
        title_text='Temperature (°C)',
        range=var_range_x,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        dtick=5
    )
    fig.update_yaxes(
        title_text='Humidity Ratio (KG water/KG air)',
        range=var_range_y,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
    )
    return fig


def sunpath(sunpath: Sunpath, data: HourlyContinuousCollection = None,
            colorset: ColorSet = ColorSet.original, min_range: float = None,
            max_range: float = None, title: str = None) -> Figure:
    """ Plot Sunpath.

    Args:
        sunpath: A Ladybug Sunpath object.
        data: An HourlyContinuousCollection object to be plotted on the sunpath. Defaults
            to None.
        colorset: A ColorSet to be used for plotting. Defaults to ColorSet.original.
        min_range: Minimum value for the colorbar. If not set, the minimum value will be
            set to the minimum value of the data. Defaults to None.
        max_range: Maximum value for the colorbar. If not set, the maximum value will be
            set to the maximum value of the data. Defaults to None.
        title: A string to be used as the title of the plot. Defaults to None.

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
        assert isinstance(data, HourlyContinuousCollection), 'data must be an'\
            f' HourlyContinuousCollection. Instead got {type(data)}.'

        var_name = data.header.data_type.name
        var_unit = data.header.unit
        var_colorscale = [rgb_to_hex(color) for color in color_set[colorset.value]]
        title = 'Sunpath - ' + var_name if title is None else title

        # add data to the dataframe
        df[var_name] = Series(data).values
        # filter the whole dataframe based on sun elevations
        solpos = df.loc[df["altitude"] > 0, :]

        data_max = 5 * ceil(solpos[var_name].max() / 5)
        data_min = 5 * floor(solpos[var_name].min() / 5)

        if min_range == None and max_range == None:
            var_range = [data_min, data_max]
        elif min_range != None and max_range == None:
            var_range = [min_range, data_max]
        elif min_range == None and max_range != None:
            var_range = [data_min, max_range]
        else:
            var_range = [min_range, max_range]

    else:
        solpos = df.loc[df["altitude"] > 0, :]
        title = 'Sunpath' if title is None else title

    tz = "UTC"
    times = pd.date_range(
        "2019-01-01 00:00:00", "2020-01-01", closed="left", freq="H", tz=tz
    )
    delta = timedelta(days=0, hours=time_zone - 1, minutes=0)
    times = times - delta

    if not data:
        var_color = "orange"
        marker_size = 3
    else:
        var_color = 'silver'
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
                    colorbar=dict(thickness=30, title=var_unit + "<br>  "),
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
                mode="lines",
                line_color=var_color,
                line_width=1,
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
                mode="lines",
                line_color=var_color,
                line_width=1,
                customdata=solpos.altitude,
                hovertemplate="<br>sun altitude: %{customdata:.2f}"
                + "\u00B0deg"
                + "<br>sun azimuth: %{theta:.2f}"
                + "\u00B0deg"
                + "<br>",
                name="",
            )
        )

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
        title={
            'text': title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    return fig
