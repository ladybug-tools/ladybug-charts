"""Recreating ladybug psychrometric chart using Plotly."""


import numpy as np
import pandas as pd
import warnings

from math import ceil, floor
from typing import List


import plotly.io as pio
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from ._helper import rgb_to_hex, mesh_to_coordinates, verts_to_coordinates
from .utils import StrategyParameters, Strategy

from ladybug.datacollection import BaseCollection, HourlyContinuousCollection
from ladybug import psychrometrics as psy
from ladybug.psychchart import PsychrometricChart
from ladybug_comfort.chart.polygonpmv import PolygonPMV
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry2d.line import LineSegment2D
from ladybug_geometry.geometry2d.polyline import Polyline2D

# set white background in all charts
pio.templates.default = 'plotly_white'


def merge_polygon_data(poly_data):
    """Merge an array of polygon comfort conditions into a single data list."""
    val_mtx = [dat.values for dat in poly_data]
    merged_values = []
    for hr_data in zip(*val_mtx):
        hr_val = 1 if 1 in hr_data else 0
        merged_values.append(hr_val)
    return merged_values


def strategy_warning(polygon_name: str) -> str:
    msg = f'Polygon "{polygon_name}" could not fit on the chart given the current'\
        ' location of the comfort polygon(s). Try moving the comfort polygon(s) by'\
        ' changing its criteria to see the missing polygon. \n'
    print(msg)


def _psych_chart(psych: PsychrometricChart, data: BaseCollection = None,
                 title: str = None, polygon_pmv: PolygonPMV = None,
                 strategies: List[Strategy] = None,
                 strategy_parameters: StrategyParameters = StrategyParameters(),
                 solar_data: HourlyContinuousCollection = None) -> Figure:
    """Create a psychrometric chart.

    Args:
        psych: A ladybug PsychrometricChart object.
        data: A ladybug DataCollection object.
        title: A title for the plot. Defaults to None.
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

    Returns:
        A plotly figure.
    """

    dbt = psych.temperature
    rh = psych.relative_humidity
    hr = [psy.humid_ratio_from_db_rh(
        dbt.values[i], rh.values[i]) for i in range(len(dbt))]

    data_max = 5 * ceil(dbt.max / 5)
    data_min = 5 * floor(dbt.min / 5)
    var_range_x = [data_min, data_max]

    data_max = (5 * ceil(max(hr) * 1000 / 5)) / 1000
    data_min = (5 * floor(min(hr) * 1000 / 5)) / 1000
    var_range_y = [data_min, data_max]

    # create dummy psych-chart to create mesh
    base_point = Point2D(var_range_x[0], 0)
    psych_dummy = PsychrometricChart(dbt, rh, base_point=base_point, x_dim=1, y_dim=1)

    # prepare for drawing humidity lines
    dbt_list = list(range(-60, 60, 1))
    rh_list = list(range(10, 110, 10))

    rh_df = pd.DataFrame()
    for rh_item in rh_list:
        hr_list = np.vectorize(psy.humid_ratio_from_db_rh)(dbt_list, rh_item)
        name = "rh" + str(rh_item)
        rh_df[name] = hr_list

    fig = go.Figure()

    ###########################################################################
    # Add curved lines for humidity
    ###########################################################################
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

    ###########################################################################
    # if no data is provided, plot frequency
    ###########################################################################
    if not data:
        title = 'Psychrometric Chart - Frequency'
        # Plot colored mesh
        cords = mesh_to_coordinates(psych_dummy.colored_mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(psych.container.value_colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines',
                )
            )

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[psych_dummy.colored_mesh.face_centroids[count].x],
                    y=[psych_dummy.colored_mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(int(psych_dummy.hour_values[count])) + ' hours' +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in psych.legend_parameters.colors],
                showscale=True,
                cmin=psych.legend_parameters.min,
                cmax=psych.legend_parameters.max,
                colorbar=dict(thickness=30, title=psych.legend_parameters.title),
            ),
        )
        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    ###########################################################################
    # Load data
    ###########################################################################
    else:
        var = data.header.data_type.name
        title = title if title else f'Psychrometric Chart - {var}'

        # add colored data mesh
        mesh, graphic_container = psych_dummy.data_mesh(data)
        cords = mesh_to_coordinates(mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(graphic_container.value_colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines'
                ))

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[mesh.face_centroids[count].x],
                    y=[mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(
                        int(graphic_container.values[count])) + ' '
                    + graphic_container.legend_parameters.title +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in graphic_container.legend_parameters.colors],
                showscale=True,
                cmin=graphic_container.legend_parameters.min,
                cmax=graphic_container.legend_parameters.max,
                colorbar=dict(
                    thickness=30, title=graphic_container.legend_parameters.title),
            ),
        )

        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    ###########################################################################
    # add polygons if requested
    ###########################################################################
    if polygon_pmv:
        poly_obj = PolygonPMV(psych_dummy)

        # collecting all the polygons
        polygons, polygon_names, polygon_data = [], [], []

        # adding comfort polygon
        comfort_poly = poly_obj.comfort_polygons[0]
        poly_name = 'Comfort'
        polygons.append(comfort_poly)
        polygon_names.append(poly_name)
        dat = poly_obj.evaluate_polygon(comfort_poly, tolerance=0.01)
        dat = dat[0] if len(dat) == 1 else poly_obj.create_collection(dat, poly_name)
        polygon_data.append(dat)

        # If other strategies are applied, add their polygons
        if strategies:

            if Strategy.evaporative_cooling in strategies:
                poly_name = 'Evaporative Cooling'
                ec_poly = poly_obj.evaporative_cooling_polygon()
                if ec_poly:
                    polygons.append(ec_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(ec_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.mas_night_ventilation in strategies:
                poly_name = 'Mass + Night Ventilation'
                nf_poly = poly_obj.night_flush_polygon(
                    strategy_parameters.day_above_comfort)
                if nf_poly:
                    polygons.append(nf_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_night_flush_polygon(
                        nf_poly, psych_dummy.original_temperature,
                        strategy_parameters.night_below_comfort,
                        strategy_parameters.time_constant, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.occupant_use_of_fans in strategies:
                poly_name = 'Occupant Use of Fans'
                fan_poly = poly_obj.fan_use_polygon(strategy_parameters.fan_air_speed)
                if fan_poly:
                    polygons.append(fan_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(fan_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.capture_internal_heat in strategies:
                poly_name = 'Capture Internal Heat'
                iht_poly = poly_obj.internal_heat_polygon(
                    strategy_parameters.balance_temperature)
                if iht_poly:
                    polygons.append(iht_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(iht_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)

            if Strategy.passive_solar_heating in strategies:
                poly_name = 'Passive Solar Heating'
                if not solar_data:
                    warnings.warn('In order to plot a passive solar heating polygon, '
                                  'you need to provide a solar data object.')
                else:
                    bal_t = strategy_parameters.balance_temperature \
                        if Strategy.capture_internal_heat in strategies else None
                    dat, delta = poly_obj.evaluate_passive_solar(
                        solar_data, strategy_parameters.solar_heating_capacity,
                        strategy_parameters.time_constant, bal_t)
                    sol_poly = poly_obj.passive_solar_polygon(delta, bal_t)
                    if sol_poly:
                        polygons.append(sol_poly)
                        polygon_names.append(poly_name)
                        dat = dat[0] if len(
                            dat) == 1 else poly_obj.create_collection(dat, poly_name)
                        polygon_data.append(dat)
                    else:
                        strategy_warning(poly_name)

        # compute comfrt and total comfort values
        polygon_comfort = [dat.average * 100 for dat in polygon_data] if \
            isinstance(polygon_data[0], BaseCollection) else \
            [dat * 100 for dat in polygon_data]
        if isinstance(polygon_data[0], BaseCollection):
            merged_vals = merge_polygon_data(polygon_data)
            total_comf_data = poly_obj.create_collection(merged_vals, 'Total Comfort')
            total_comfort = total_comf_data.average * 100
        else:
            total_comf_data = 1 if sum(polygon_data) > 0 else 0
            total_comfort = total_comf_data * 100

        # draw each polygon
        for count, polygon in enumerate(polygons):
            verts = [point for geo in polygon for point in geo.vertices]
            x_cords, y_cords = verts_to_coordinates(verts)
            fig.add_trace(
                go.Scatter(
                    x=x_cords,
                    y=y_cords,
                    line=dict(width=4),
                    showlegend=True,
                    name=polygon_names[count] + ': ' +
                    str(round(polygon_comfort[count])) + '% of time',
                    mode='lines',
                ))

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        title={
            'text': title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

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
