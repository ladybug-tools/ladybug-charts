"""Objects to suport Ladybug charts."""

from enum import Enum


class Strategy(Enum):
    """Strategies to apply to the psychrometric chart."""
    evaporative_cooling = 'Evaporative Cooling'
    mas_night_ventilation = 'Mass + Night Vent'
    occupant_use_of_fans = 'Occupant Use of Fans'
    capture_internal_heat = 'Capture Internal Heat'
    passive_solar_heating = 'Passive Solar Heating'


class StrategyParameters:
    """Strategy parameters for psychrometric charts."""

    def __init__(self,
                 day_above_comfort: int = 12,
                 night_below_comfort: int = 3,
                 fan_air_speed: int = 1,
                 balance_temperature: int = 12.8,
                 solar_heating_capacity: int = 50,
                 time_constant: int = 8) -> None:

        self._day_above_comfort = day_above_comfort
        self._night_below_comfort = night_below_comfort
        self._fan_air_speed = fan_air_speed
        self._balance_temperature = balance_temperature
        self._solar_heating_capacity = solar_heating_capacity
        self._time_constant = time_constant

    @property
    def day_above_comfort(self) -> int:
        """Get the day above comfort."""
        return self._day_above_comfort

    @day_above_comfort.setter
    def day_above_comfort(self, value: int) -> None:
        """Set the day above comfort."""
        self._day_above_comfort = value

    @property
    def night_below_comfort(self) -> int:
        """Get the night below comfort."""
        return self._night_below_comfort

    @night_below_comfort.setter
    def night_below_comfort(self, value: int) -> None:
        """Set the night below comfort."""
        self._night_below_comfort = value

    @property
    def fan_air_speed(self) -> int:
        """Get the fan air speed."""
        return self._fan_air_speed

    @fan_air_speed.setter
    def fan_air_speed(self, value: int) -> None:
        """Set the fan air speed."""
        self._fan_air_speed = value

    @property
    def balance_temperature(self) -> int:
        """Get the balance temperature."""
        return self._balance_temperature

    @balance_temperature.setter
    def balance_temperature(self, value: int) -> None:
        """Set the balance temperature."""
        self._balance_temperature = value

    @property
    def solar_heating_capacity(self) -> int:
        """Get the solar hating capacity."""
        return self._solar_heating_capacity

    @solar_heating_capacity.setter
    def solar_heating_capacity(self, value: int) -> None:
        """Set the solar hating capacity."""
        self._solar_heating_capacity = value

    @property
    def time_constant(self) -> int:
        """Get the time constant."""
        return self._time_constant

    @time_constant.setter
    def time_constant(self, value: int) -> None:
        """Set the time constant."""
        self._time_constant = value

    def __str__(self) -> str:
        return f'StrategyParameters(day_above_comfort={self.day_above_comfort},'\
            f' night_below_comfort={self.night_below_comfort},' \
            f' fan_air_speed={self.fan_air_speed},'\
            f' balance_temperature={self.balance_temperature},'\
            f' solar_heating_capacity={self.solar_heating_capacity},' \
            f' time_constant={self.time_constant})'
