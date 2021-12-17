"""Create plotly figures from pandas Dataframe."""

import numpy as np
import plotly.io as pio
import plotly.graph_objects as go
from enum import Enum
from pandas import DataFrame as Df
from plotly.graph_objects import Figure
from ._update_dataframe import update_dataframe_for_heatmap
from math import ceil, floor


class DataPoint(Enum):
    """Variable names for the EPW data."""
    dry_bulb_temperature = 'Dry Bulb Temperature'
    dew_point_temperature = 'Dew Point Temperature'
    relative_humidity = 'Relative Humidity'
    atmospheric_station_pressure = 'Atmospheric Station Pressure'
    extraterrestrial_horizontal_radiation = 'Extraterrestrial Horizontal Radiation'
    extraterrestrial_direct_normal_radiation = 'Extraterrestrial Direct Normal Radiation'
    horizontal_infrared_radiation_intensity = 'Horizontal Infrared Radiation Intensity'
    global_horizontal_radiation = 'Global Horizontal Radiation'
    direct_normal_radiation = 'Direct Normal Radiation'
    diffuse_horizontal_radiation = 'Diffuse Horizontal Radiation'
    global_horizontal_illuminance = 'Global Horizontal Illuminance'
    direct_normal_illuminance = 'Direct Normal Illuminance'
    diffuse_horizontal_illuminance = 'Diffuse Horizontal Illuminance'
    zenith_luminance = 'Zenith Luminance'
    wind_direction = 'Wind Direction'
    wind_speed = 'Wind Speed'
    total_sky_cover = 'Total Sky Cover'
    opaque_sky_cover = 'Opaque Sky Cover'
    visibility = 'Visibility'
    ceiling_height = 'Ceiling Height'
    precipitation_weather_observation = 'Precipitation Weather Observation'
    precipitation_weather_codes = 'Precipitation Weather Codes'
    precipitable_water = 'Precipitable Water'
    aerosol_optical_depth = 'Aerosol Optical Depth'
    snow_depth = 'Snow Depth'
    days_since_last_snowfall = 'Days Since Last Snowfall'
    albedo = 'Albedo'
    liquid_precipitation_depth = 'Liquid Precipitation Depth'
    liquid_precipitation_quantity = 'Liquid Precipitation Quantity'


def heatmap(df: Df, var: DataPoint,
            min_range: float = None, max_range: float = None) -> Figure:
    """Create a plotly heatmap figure.

    Args:
        df: A ladybug-pandas dataframe.
        var: A Datapoint object.
        min_range: The minimum value for the legend of the heatmap. Defaults to None.
        max_range: The maximum value for the legend of the heatmap. Defaults to None.

    Returns:
        A plotly figure.
    """
    df = update_dataframe_for_heatmap(df)
    var = var.value
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
            customdata=np.stack((df["month_names"], df["day"]), axis=-1),
            hovertemplate=(
                "<b>"
                + var
                + ": %{z:.2f} "
                + var_unit
                + "</b><br>Month: %{customdata[0]}<br>Day: %{customdata[1]}<br>Hour: %{y}:00<br>"
            ),
            name="",
            colorbar=dict(title=var_unit),
        )
    )

    fig.update_xaxes(dtick="M1", tickformat="%b", ticklabelmode="period")

    fig.update_yaxes(title_text="Hours of the day")
    fig.update_xaxes(title_text="Days of the year")

    pio.templates.default = 'plotly_white'
    fig.update_layout(template='plotly_white', margin=dict(
        l=20, r=20, t=33, b=20), yaxis_nticks=13)
    fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
    fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

    return fig
