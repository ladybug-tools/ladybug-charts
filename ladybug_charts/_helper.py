"""Helper functions to create Ladybug charts."""

from __future__ import annotations
from enum import Enum
from typing import List, Tuple
from ladybug.datacollection import HourlyContinuousCollection, \
    HourlyDiscontinuousCollection, BaseCollection
from ladybug.color import Color, Colorset


def discontinuous_to_continuous(
        data: HourlyDiscontinuousCollection) -> HourlyContinuousCollection:
    """Fill the gaps in Discontinuous data to create Continuous data."""

    assert isinstance(data, HourlyDiscontinuousCollection), 'Only' \
        f' HourlyDiscontinuousCollection is supported. instead got {type(data)}'

    hoys = [dt.hoy for dt in data.datetimes]
    hoy_val = dict(zip(hoys, data.values))

    values = []
    for count in range(8760):
        if count in hoy_val:
            values.append(hoy_val[count])
        else:
            values.append(None)

    return HourlyContinuousCollection(data.header, values)


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
