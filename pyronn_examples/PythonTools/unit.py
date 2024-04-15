# FRAUNHOFER IIS CONFIDENTIAL
# __________________
#
# Fraunhofer IIS
# Copyright (c) 2016-2023
# All Rights Reserved.
#
# This file is part of the PythonTools project.
#
# NOTICE:  All information contained herein is, and remains the property of Fraunhofer IIS and its suppliers, if any.
# The intellectual and technical concepts contained herein are proprietary to Fraunhofer IIS and its suppliers and may
# be covered by German and Foreign Patents, patents in process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is strictly forbidden unless prior written
# permission is obtained from Fraunhofer IIS.

from __future__ import annotations


from dataclasses import dataclass
from enum import Enum


class Unit(Enum):
    def __str__(self) -> str:
        return str(self.value)


class Length(Unit):
    nm = 'nm'
    um = 'µm'
    mm = 'mm'
    m = 'm'
    km = 'km'


class Mass(Unit):
    mg = 'mg'
    g = 'g'
    kg = 'kg'


class Force(Unit):
    mN = 'N'
    N = 'N'
    kN = 'kN'
    MN = 'MN'


class Angle(Unit):
    rad = 'rad'
    deg = 'deg'


class Voltage(Unit):
    uV = 'µV'
    mV = 'mV'
    V = 'V'
    kV = 'kV'
    MV = 'MV'


class Current(Unit):
    uA = 'µA'
    mA = 'mA'
    A = 'A'
    kA = 'kA'


class Power(Unit):
    uW = 'uW'
    mQ = 'mW'
    W = 'W'
    kW = 'kW'
    MW = 'MW'
    GW = 'GW'


class Frequency(Unit):
    Hz = 'Hz'
    kHz = 'kHz'
    MHz = 'MHz'
    GHz = 'GHz'


class Time(Unit):
    ns = 'ns'
    us = 'µs'
    ms = 'ms'
    sec = 'sec'
    min = 'min'
    h = 'h'
    d = 'd'


class Velocity(Unit):
    mmps = 'mm/s'
    mps = 'm/s'
    kmh = 'km/h'


class Acceleration(Unit):
    mmps2 = 'mm/s²'
    mps2 = 'm/s²'
    kmh2 = 'km/h²'


class Currency(Unit):
    Euro = '€'
    Dollar = '$'


class Count(Unit):
    """Indicates that number is a count of entities."""

    Misc = ''
    Pixel = 'px'
    HorizontalPixel = 'hpx'
    VerticalPixel = 'vpx'

    def __str__(self) -> str:
        if self.value == '':
            return ''
        return 'px'


@dataclass(frozen=True)
class Units:
    """Naive units enum. Might be subject to change (e.g. easier handling of 1000th nominators)"""

    Mass = Mass
    Force = Force
    Length = Length
    Angle = Angle
    Voltage = Voltage
    Current = Current
    Power = Power
    Frequency = Frequency
    Time = Time
    Velocity = Velocity
    Acceleration = Acceleration
    Count = Count
    Currency = Currency

    @staticmethod
    def try_from_string(encoded_str: str) -> Unit | str:
        """Try to reconstruct Unit class from Enum string repr. If not possible, simply return input string."""
        if len(encoded_str) <= 5:
            return encoded_str

        if encoded_str[0] != '<' or encoded_str[-1] != '>' or ':' not in encoded_str:
            return encoded_str

        sanitized_str = encoded_str.replace('>', '').replace('<', '')
        colcon_idx = sanitized_str.find(':')

        enum_name, enum_value = sanitized_str[:colcon_idx].split('.')

        try:
            matching_enum = getattr(Units, enum_name)
            return getattr(matching_enum, enum_value)
        except AttributeError:
            return encoded_str
