"""Create plotly figures from pandas Dataframe."""


import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from math import ceil, floor
from plotly.graph_objects import Figure
from plotly.graph_objects import Bar
from typing import Union, List, Tuple
from random import randint

from ._to_dataframe import dataframe, Frequency
from ._helper import discontinuous_to_continuous, rgb_to_hex, ColorSet, color_set

from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyCollection, DailyCollection
from ladybug.color import Color
from ladybug_pandas.series import Series

# set white background in all charts
pio.templates.default = 'plotly_white'


def heatmap(hourly_data: Union[HourlyContinuousCollection, HourlyDiscontinuousCollection],
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


def hourly_chart(data: HourlyContinuousCollection, color: Color = None) -> Figure:
    """Create a plotly bar chart figure from a ladybug hourly continuous data object.

    Args:
        data: A ladybug HourlyContinuousCollection object.
        color: A Ladybug color object. If not set, a random color will be used. Defaults
            to None.

    Returns:
        A plotly figure.
    """

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
