"""Helper functions to create Ladybug charts."""

from __future__ import annotations
from enum import Enum
from typing import List, Tuple
from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, MonthlyPerHourCollection
from ladybug.color import Color, Colorset
from ladybug.header import Header
from ladybug.analysisperiod import AnalysisPeriod
from ladybug_geometry.geometry2d import Mesh2D
from ladybug_geometry.geometry2d.pointvector import Point2D


def discontinuous_to_continuous(
        data: HourlyDiscontinuousCollection) -> Tuple[HourlyContinuousCollection,
                                                      List[float, float]]:
    """Fill the gaps in Discontinuous data to create Continuous data.

    Args:
        data: A Ladybug HourlyDiscontinuousCollection.

    Returns:
        A tuple of two items

        -   A Ladybug HourlyContinuousCollection.

        -   A List of two floats representing min and max values of the data.
    """

    assert isinstance(data, HourlyDiscontinuousCollection), 'Only' \
        f' HourlyDiscontinuousCollection is supported. instead got {type(data)}'

    hoys = [dt.hoy for dt in data.datetimes]
    hoy_val = dict(zip(hoys, data.values))
    # We need to find the range of the data here before we inject None values
    data_range = [min(hoy_val.values()), max(hoy_val.values())]

    values = []
    for count in range(8760):
        if count in hoy_val:
            values.append(hoy_val[count])
        else:
            values.append(None)

    header = Header(data.header.data_type, data.header.unit,
                    AnalysisPeriod(), data.header.metadata)

    return HourlyContinuousCollection(header, values), data_range


def rgb_to_hex(color: Color) -> str:
    """Convert a RGB color to Hex color."""

    return f'#{color.r:02X}{color.g:02X}{color.b:02X}'


class ColorSet(Enum):
    """Colors for a legend."""
    annual_comfort = 'annual_comfort'
    benefit = 'benefit'
    benefit_harm = 'benefit_harm'
    black_to_white = 'black_to_white'
    blue_green_red = 'blue_green_red'
    cloud_cover = 'cloud_cover'
    cold_sensation = 'cloud_sensation'
    ecotect = 'ecotect'
    energy_balance = 'energy_balance'
    energy_balance_storage = 'energy_balance_storag'
    glare_study = 'glare_study'
    harm = 'harm'
    heat_sensation = 'heat_sensation'
    multi_colored = 'multi_colored'
    multicolored_2 = 'multicolored_2'
    multicolored_3 = 'multicolored_3'
    nuanced = 'nuanced'
    openstudio_palette = 'openstudio_palette'
    original = 'original'
    peak_load_balance = 'peak_load_balance'
    shade_benefit = 'shade_benefit'
    shade_benefit_harm = 'shade_benefit_harm'
    shade_harm = 'shade_harm'
    shadow_study = 'shadow_study'
    therm = 'therm'
    thermal_comfort = 'thermal_comfort'
    view_study = 'view_study'


color_set = {
    'annual_comfort': Colorset.annual_comfort(),
    'benefit': Colorset.benefit(),
    'benefit_harm': Colorset.benefit_harm(),
    'black_to_white': Colorset.black_to_white(),
    'blue_green_red': Colorset.blue_green_red(),
    'cloud_cover': Colorset.cloud_cover(),
    'cold_sensation': Colorset.cold_sensation(),
    'ecotect': Colorset.ecotect(),
    'energy_balance': Colorset.energy_balance(),
    'energy_balance_storage': Colorset.energy_balance_storage(),
    'glare_study': Colorset.glare_study(),
    'harm': Colorset.harm(),
    'heat_sensation': Colorset.heat_sensation(),
    'multi_colored': Colorset.multi_colored(),
    'multicolored_2': Colorset.multicolored_2(),
    'multicolored_3': Colorset.multicolored_3(),
    'nuanced': Colorset.nuanced(),
    'openstudio_palette': Colorset.openstudio_palette(),
    'original': Colorset.original(),
    'peak_load_balance': Colorset.peak_load_balance(),
    'shade_benefit': Colorset.shade_benefit(),
    'shade_benefit_harm': Colorset.shade_benefit_harm(),
    'shade_harm': Colorset.shade_harm(),
    'shadow_study': Colorset.shadow_study(),
    'therm': Colorset.therm(),
    'thermal_comfort': Colorset.thermal_comfort(),
    'view_study': Colorset.view_study()
}


def mesh_to_coordinates(mesh: Mesh2D) -> List[List[List[float], List[float]]]:
    """Convert vertices of Ladybug 2D mesh to coordinates that Plotly can use.

    Args:
        mesh: Ladybug 2D mesh.

    Returns:
        A list of lists of coordinates where each list has two lists. The first has 
        x coordinates and the second has y coordinates.
    """
    cords = []
    for face in mesh.faces:
        x_cords = []
        y_cords = []
        for vert in face:
            x_cords.append(mesh.vertices[vert].x)
            y_cords.append(mesh.vertices[vert].y)
        # Add first cordinate to the end to close the polygon
        x_cords.append(x_cords[0])
        y_cords.append(y_cords[0])
        cords.append([x_cords, y_cords])

    return cords


def verts_to_coordinates(points: List[Point2D], close: bool = True) -> Tuple[List[float], List[float]]:
    """Convert a list of Ladybug Point2Ds to coordinates that Plotly can use.

    Args:
        points: A list of Ladybug Point2Ds.
        close: Boolean to close the polygon. Default: True.

    Returns:
        A tuple of two items

        -   A list of x coordinates.
        -   A list of y coordinates.
    """

    x_cords, y_cords = [], []
    for point in points:
        x_cords.append(point.x)
        y_cords.append(point.y)

    if close:
        x_cords.append(x_cords[0])
        y_cords.append(y_cords[0])

    return x_cords, y_cords


def get_monthly_values(data: MonthlyPerHourCollection) -> List[List[float]]:
    """Get month wise MonthlyPerHour values.

    Args:
        data: A ladybug MonthlyPerHourCollection object.

    Returns:
        A list of lists of monthly values where the length of each list is 24.
    """
    values = []
    for i in range(24, 312, 24):
        values.append([data.values[j] for j in range(i-24, i)])
    return values
