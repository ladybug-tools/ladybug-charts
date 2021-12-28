"""Create plotly figures from pandas Dataframe."""


import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from math import ceil, floor
from plotly.graph_objects import Figure
from plotly.graph_objects import Bar
from plotly.subplots import make_subplots
from typing import Union, List, Tuple
from random import randint

from ._to_dataframe import dataframe, Frequency, MONTHS
from ._helper import discontinuous_to_continuous, rgb_to_hex, ColorSet, color_set

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug.color import Color
from ladybug_pandas.series import Series

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


def wind_rose(wind_speed: HourlyContinuousCollection, wind_dir: HourlyContinuousCollection,
              month: List[int] = [1, 12], hour: List[int] = [1, 24],
              title: str = 'Wind Rose', legend: bool = True,
              colorset: ColorSet = ColorSet.original) -> Figure:
    """Create a windrose plot.

    Args:
        wind_speed: A ladybug hourly continuous data object for wind speed.
        wind_dir: A ladybug hourly continuous data object for wind direction.
        month: A list of months to plot. Defaults to [1, 12].
        hour: A list of hours to plot. Defaults to [1, 24].
        title: A title for the plot. Defaults to Wind Rose.
        legend: A boolean to show/hide legend. Defaults to True.
        colorset: A ladybug colorset object. Defaults to ColorSet.original.

    Returns:
        A plotly figure.
    """

    assert isinstance(wind_speed, HourlyContinuousCollection) \
        and isinstance(wind_dir, HourlyContinuousCollection), 'Only ladybug hourly'\
        ' continuous data is supported in both wind_speed and wind_dir.'

    df = dataframe()
    series = Series(wind_speed)
    df['wind_speed'] = series.values
    series = Series(wind_dir)
    df['wind_dir'] = series.values

    start_month = month[0]
    end_month = month[1]
    start_hour = hour[0]
    end_hour = hour[1]
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
