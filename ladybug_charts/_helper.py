"""Helper functions to create Ladybug charts."""

from typing import List
from ladybug.datacollection import HourlyContinuousCollection, HourlyDiscontinuousCollection
from ladybug.color import Colorset


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


def rgb_to_hex(colorset: Colorset) -> List[str]:
    """Convert a RGB colors to Hex colors"""

    return [f'#{c.r:02X}{c.g:02X}{c.b:02X}' for c in colorset]
