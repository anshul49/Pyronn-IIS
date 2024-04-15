# FRAUNHOFER IIS CONFIDENTIAL
# __________________
#
# Fraunhofer IIS
# Copyright (c) 2016-2021
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

from typing import Callable, Literal
from dataclasses import dataclass, asdict
from enum import IntEnum
from math import isclose


ProgressCallback = Callable[[int, int], None]


class USERLEVEL(IntEnum):
    """User level for UI applications (deprecated)."""

    OPERATOR = 0
    MAINTAINER = 1
    ADMIN = 2


class UserLevel(IntEnum):
    """User level for UI applications."""

    OPERATOR = 0
    MAINTAINER = 1
    ADMIN = 2


class SEVERITY(IntEnum):
    """Severity classes (deprecated)."""

    INFO = 0
    WARNING = 1
    ERROR = 2


class Severity(IntEnum):
    """Severity classes."""

    INFO = 0
    WARNING = 1
    ERROR = 2


class DeviceState(IntEnum):
    UNINITIALIZED = 0
    INITIALIZING = 1
    IDLE = 2
    MOVING = 3
    ERROR = 4


class ShutterState(IntEnum):
    """Xray source shutter state"""

    NONE = 0
    CLOSED = 1
    OPEN = 2


class CTIMAGETYPE(IntEnum):
    """Typical CT image types (deprecated)."""

    DARK = 0
    FLAT = 1
    BPM = 2
    PROJECTION = 3


class CtImageType(IntEnum):
    """Typical CT image types."""

    DARK = 0
    FLAT = 1
    BPM = 2
    PROJECTION = 3


class IMAGEFORMATS(IntEnum):
    """
    Supported image formats (deprecated).
    AUTO mode tries to guess the format (if .raw the EZRT format is assumed)
    """

    RAW_BINARY = 0
    RAW_EZRT = 1
    PNG = 2
    TIFF = 3
    BMP = 4
    AUTO = 5  # only for loading

    @classmethod
    def from_suffix(cls, suffix: str):
        suffix = suffix.lower()
        if suffix.endswith('tif') or suffix.endswith('tiff'):
            return cls.TIFF
        if suffix.endswith('raw'):
            return cls.RAW_EZRT
        if suffix.endswith('png'):
            return cls.PNG
        if suffix.endswith('bmp'):
            return cls.BMP

        raise ValueError(f'suffix {suffix} not supported')


class ImageFormat(IntEnum):
    """
    Supported image formats.
    AUTO mode tries to guess the format (if .raw the EZRT format is assumed)
    """

    RAW_BINARY = 0
    RAW_EZRT = 1
    PNG = 2
    TIFF = 3
    BMP = 4
    AUTO = 5  # only for loading

    @classmethod
    def from_suffix(cls, suffix: str):
        suffix = suffix.lower()
        if suffix.endswith('tif') or suffix.endswith('tiff'):
            return cls.TIFF
        if suffix.endswith('raw') or suffix == 'raw_ezrt':
            return cls.RAW_EZRT
        if suffix.endswith('png'):
            return cls.PNG
        if suffix.endswith('bmp'):
            return cls.BMP

        raise ValueError(f'suffix {suffix} not supported')


class ACQUISITIONMODE(IntEnum):
    """Acquisition mode enum. Contains options to control acquisition behavior (deprecated)."""

    SINGLE_SHOT = 0
    MULTI_SHOTS = 1
    CONTINUOUS = 2


class AcquisitionMode(IntEnum):
    """Acquisition mode enum. Contains options to control acquisition behavior."""

    SINGLE_SHOT = 0
    MULTI_SHOTS = 1
    CONTINUOUS = 2


class TRIGGERMODE(IntEnum):
    """Trigger mode enum. Contains options to control trigger behavior (deprecated)."""

    INTERNAL = 0
    SOFTWARE = 1
    POSITIVE_EDGE = 2
    NEGATIVE_EDGE = 3
    POSITIVE_GATE = 4
    NEGATIVE_GATE = 5


class TriggerMode(IntEnum):
    """Trigger mode enum. Contains options to control detector trigger behavior."""

    INTERNAL = 0
    SOFTWARE = 1
    POSITIVE_EDGE = 2
    NEGATIVE_EDGE = 3
    POSITIVE_GATE = 4
    NEGATIVE_GATE = 5


@dataclass
class AxisOffsetParameter:
    """Parameter to link a offset to an axis."""

    axis_id: str = ''
    """Axis to which the offset should be linked or empty for constant value"""

    offset: float = 0.0
    """The desired value at axis position 0"""

    invert_direction: bool = False
    """True if the calculated value should increase as the linked axis position decreases"""

    @classmethod
    def fromdict(cls, info_dict: dict):
        """Construct from dict. Needs to have the keys "axis_id", "offset" and "invert_direction"."""
        if not ('axis_id' in info_dict and 'offset' in info_dict and 'invert_direction' in info_dict):
            raise ValueError('input dict must contain the "axis_id", "offset" and "invert_direction" keys')

        info = cls(info_dict['axis_id'], info_dict['offset'], info_dict['invert_direction'])
        return info

    @property
    def sign(self) -> Literal[-1, 1]:
        return -1 if self.invert_direction else 1

    def apply_offset(self, axis_position: float = 0) -> float:
        """
        Apply this axis offset to an axis position

        Args:
            axis_position: Actual position of the axis if one is linked to the offset

        Returns:
            Position with offset
        """
        return self.offset + self.sign * axis_position

    def update_offset(self, desired_position: float, axis_position: float = 0):
        """
        Update offset value. Direction of offset is not changed.

        Args:
            desired_position: Target value after offset application
            axis_position: Actual position of the axis if one is linked to the offset
        """
        self.offset = desired_position - self.sign * axis_position


@dataclass
class FodParameter(AxisOffsetParameter):
    """Parameter for focus object distance."""


@dataclass
class FddParameter(AxisOffsetParameter):
    """Parameter for focus detector distance."""


class TriggerOutputMode(IntEnum):
    """Actor trigger output mode."""

    OFF = 0
    """No trigger output."""

    CUSTOM = 1
    """Custom mode, if no present mode fits."""

    EDGE = 2
    """Trigger is signaled as signal edge ("fixed gap"). Logic depends on LogicLevel and LogicActiveState settings."""

    GATE = 3
    """Continuous active trigger signal (e.g. trigger with internal frequency)"""

    POSITION_TABLE = 4
    """Trigger based on a custom lookup table."""


class LogicLevel(IntEnum):
    """Digital logic level."""

    CUSTOM = 0
    TTL_5V = 5
    HTL_24V = 24


class LogicActiveState(IntEnum):
    """Digital logic active state."""

    ACTIVE_LOW = 0
    """Negative logic (e.g. edge trigger at --__)."""

    ACTIVE_HIGH = 1
    """Positive logic (e.g. edge trigger at __--)."""


@dataclass
class TriggerOutputParameter:
    """Parameter for actor trigger output."""

    trigger_per_position_delta: float
    """Number of triggers emitted within 1 mm / deg movement."""

    impulse_duration_in_us: float
    """Duration of trigger impulse in µs. Polarity depending on logic level."""

    max_number_of_triggers: int | None = None
    """Maximum number of triggers emitted. If None, amount is not limited."""

    number_of_pre_triggers: int = 0
    """Number of pre-triggers before start position is reached (does not count towards max number of triggers)."""

    start_position: float | None = None
    """Start position in mm or deg (optional)."""

    end_position: float | None = None
    """End position in mm or deg (optional)."""

    digital_output_port: int | None = None
    """Trigger output port number."""

    logic_level: LogicLevel = LogicLevel.TTL_5V
    """Logic level for trigger output port (default: 5V)."""

    logic_active_state: LogicActiveState = LogicActiveState.ACTIVE_HIGH
    """Logic active state for trigger output port (default: active high)."""

    def __post_init__(self):
        if self.impulse_duration_in_us < 0:
            raise ValueError('trigger impulse duration must be > 0')
        if self.number_of_pre_triggers < 0:
            raise ValueError('number of pre triggers must be >= 0')
        if self.max_number_of_triggers is not None and self.max_number_of_triggers < 0:
            raise ValueError('max number of triggers must be >= 0')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, input_dict: dict):
        """Construct from dict. Needs to have the keys "axis_id", "offset" and "invert_direction"."""
        if not ('trigger_per_position_delta' in input_dict and 'impulse_duration_in_us' in input_dict):
            raise ValueError('dict must contain the "trigger_per_position_delta" and "impulse_duration_in_us" keys')

        return cls(**input_dict)


class AXISTYPE(IntEnum):
    """Axis type enum (deprecated)."""

    LINEAR = 0
    LINEAR_UM = 1
    ROTATIONAL = 2
    GONIOMETER = 3


class AxisType(IntEnum):
    """Axis type enum."""

    LINEAR = 0
    LINEAR_UM = 1
    ROTATIONAL = 2
    GONIOMETER = 3


class REFERENCEMODE(IntEnum):
    """Reference mode enum. Contains options for axis reference (deprecated)."""

    MOVE_TO_ZERO = 0
    GOTO_NEGATIVE_LIMIT = 1
    GOTO_POSITIVE_LIMIT = 2
    GOTO_SWITCH_LIMIT = 3
    CUSTOM = 4
    INITIALISE = 5
    SET_POSITION_TO_ZERO = 6
    GOTO_ENCODER_INDEX_IMPULSE = 7


class ReferenceMode(IntEnum):
    """Reference mode enum. Contains options for axis reference."""

    MOVE_TO_ZERO = 0
    GOTO_NEGATIVE_LIMIT = 1
    GOTO_POSITIVE_LIMIT = 2
    GOTO_SWITCH_LIMIT = 3
    CUSTOM = 4
    INITIALISE = 5
    SET_POSITION_TO_ZERO = 6
    GOTO_ENCODER_INDEX_IMPULSE = 7


class EZRT_HEADER_DTYPES(IntEnum):
    """Data types used in EZRT header (deprecated)."""

    # integer numbers
    INT8 = 7
    UINT8 = 8
    INT16 = 15
    UINT16 = 16
    INT32 = 31
    UINT32 = 32
    INT64 = 63
    UINT64 = 64
    # floating point numbers
    FLOAT = 24
    DOUBLE = 53


class EzrtHeaderDType(IntEnum):
    """Data type used in EZRT header."""

    # integer numbers
    INT8 = 7
    UINT8 = 8
    INT16 = 15
    UINT16 = 16
    INT32 = 31
    UINT32 = 32
    INT64 = 63
    UINT64 = 64
    # floating point numbers
    FLOAT = 24
    DOUBLE = 53


class ACQUISITIONGEOMETRY(IntEnum):
    """CT acquisition geometry (deprecated)."""

    CONVENTIONAL_3DCT = 0
    SWING_LAMINOGRAPHY = 1
    HELIX_CT = 2
    PARALLEL_CONE_CT = 3
    PARALLEL_CONE_SWING_LAMINOGRAPHY = 4
    STACKED_FANBEAM = 5
    STACKED_FANBEAM_SWING_LAMINOGRAPHY = 6
    OBJ_Z_SHIFT = 100
    ARBITRARY = 0x7FFFFFFF


class AcquisitionGeometry(IntEnum):
    """CT acquisition geometry."""

    CONVENTIONAL_3DCT = 0
    SWING_LAMINOGRAPHY = 1
    HELIX_CT = 2
    PARALLEL_CONE_CT = 3
    PARALLEL_CONE_SWING_LAMINOGRAPHY = 4
    STACKED_FANBEAM = 5
    STACKED_FANBEAM_SWING_LAMINOGRAPHY = 6
    OBJ_Z_SHIFT = 100
    ARBITRARY = 0x7FFFFFFF


class CTALGORITHM(IntEnum):
    """CT reconstruction algorithm (deprecated)."""

    CYLINDRICAL_FBP = 0
    FBP = 1
    ART = 2
    ART2 = 3
    TOMOSYNTH = 100


class CtAlgorithm(IntEnum):
    """CT reconstruction algorithms."""

    CYLINDRICAL_FBP = 0
    FBP = 1
    ART = 2
    ART2 = 3
    TOMOSYNTH = 100


class CTFILTER(IntEnum):
    """CT filter (deprecated)."""

    NONE = -1
    SHEPP_LOGAN = 0
    LAMBDA = 1
    RAM_LAK = 2
    SHEPP_LOGAN_MODIFIED = 10
    HAMMING_GENERALIZED = 11
    PARABOLIC = 12
    HANN_VARIABLE_CUTOFF = 13


class CtFilter(IntEnum):
    """CT filter."""

    NONE = -1
    SHEPP_LOGAN = 0
    LAMBDA = 1
    RAM_LAK = 2
    SHEPP_LOGAN_MODIFIED = 10
    HAMMING_GENERALIZED = 11
    PARABOLIC = 12
    HANN_VARIABLE_CUTOFF = 13


class CTALGORITHMPLATFORM(IntEnum):
    """CT reconstruction platform (deprecated)."""

    CPU = 0
    GPUCUDA = 1
    DYNAMIC = 2
    GPUOPENCL = 3
    CPUOPENCL = 4


class CtAlgorithmPlatform(IntEnum):
    """CT reconstruction platform."""

    CPU = 0
    GPUCUDA = 1
    DYNAMIC = 2
    GPUOPENCL = 3
    CPUOPENCL = 4


class CTPROJECTIONPADDING(IntEnum):
    """Projection padding used during reconstruction (deprecated)."""

    NONE = 0
    CIRCLE = 1
    COSINE = 2
    SIMPLE_MULTISCAN = 100


class CtProjectionPadding(IntEnum):
    """Projection padding used during reconstruction."""

    NONE = 0
    CIRCLE = 1
    COSINE = 2
    SIMPLE_MULTISCAN = 100


class Range:
    """
    A class to represent a value range in the form minimum <= value <= maximum.
    (Can be used with any Python object implementing __le__ & __ge__)
    """

    def __init__(self, minimum: int | float, maximum: int | float):
        """
        Construct new Range with given limits (int / float supported).

        Args:
            minimum: minimum value to be in range
            maximum: maximum value to be in range

        Raises:
            ValueError: if minimum bigger than maximum or maximum is smaller than minimum
        """
        self._minimum = 0
        self._maximum = 1
        self.set_range(minimum, maximum)

    def __str__(self) -> str:
        return f'[{self.minimum}; {self.maximum}]'

    def __eq__(self, compared_range):
        return isclose(self.minimum, compared_range.minimum, abs_tol=1e-6) and isclose(
            self.maximum, compared_range.maximum, abs_tol=1e-6
        )

    def __iter__(self):
        """
        Iterator for whole range (including maximum value).
        For floating point numbers, the hardcoded step size is 0.1
        """
        step = 0.1
        if isinstance(self.minimum, int) and isinstance(self.maximum, int):
            step = 1

        current_value = self.minimum
        while current_value <= self.maximum or isclose(current_value, self.maximum, abs_tol=1e-3):
            yield current_value
            current_value += step

    @staticmethod
    def value_between_limits(value: int | float, minimum: int | float, maximum: int | float) -> bool:
        """
        Checks if value is within or equal to limits.

        Args:
            value: value to be checked against range
            minimum: minimum value to be in range
            maximum: maximum value to be in range

        Returns:
            true if the value is between minimum and maximum ore close to one

        Raises:
            ValueError: if the minimum is greater than the maximum
        """
        if minimum > maximum:
            raise ValueError('minimum must be smaller than maximum or equal')

        return (
            minimum < value < maximum or isclose(value, minimum, abs_tol=1e-6) or isclose(value, maximum, abs_tol=1e-6)
        )

    @property
    def minimum(self) -> int | float:
        """
        Minimum value to be in range. When using this property the range is not checked for consistency
        so use set_range if possible.

        Returns:
            minimum value
        """
        return self._minimum

    @minimum.setter
    def minimum(self, new_minimum: int | float):
        self._minimum = new_minimum

    @property
    def maximum(self) -> int | float:
        """
        Maximum value to be in range. When using this property the range is not checked for consistency
        so use set_range if possible.

        Returns:
            maximum value
        """
        return self._maximum

    @maximum.setter
    def maximum(self, new_maximum: int | float):
        self._maximum = new_maximum

    def set_range(self, minimum: int | float, maximum: int | float):
        """
        Sets the valid range to check against.

        Args:
            minimum: minimum value to be in range
            maximum: maximum value to be in range
        """
        if minimum > maximum:
            raise ValueError('minimum must be smaller than or equal to maximum')

        self._minimum = minimum
        self._maximum = maximum

    def in_range(self, value: int | float) -> bool:
        """
        Checks if given value is in range.

        Args:
            value: value to be checked against range

        Returns:
            true if in range
        """
        return self.value_between_limits(value, self._minimum, self._maximum)

    @property
    def range(self) -> tuple[int | float, int | float]:
        """
        Returns the current range as tuple.

        Returns:
            tuple (min, max)
        """
        return self._minimum, self._maximum


class ROI:
    """
    A class to represent ROI (region of interests; sometimes called AOIs). Mostly used for detector image size handling.
    """

    def __init__(self, x: Range = Range(0, 1), y: Range = Range(0, 1)):
        """
        Construct new ROI from Ranges (default: 0->1 / 0->1)

        Args:
            x: range of values in x
            y: range of values in y
        """
        self._x = x
        self._y = y

    def __str__(self):
        return f'x: {self._x.minimum} -> {self._x.maximum}; y: {self._y.minimum} -> {self._y.maximum}'

    def __eq__(self, compared_roi):
        return self.x == compared_roi.x and self.y == compared_roi.y

    @classmethod
    def from_values(cls, x0: int | float, x1: int | float, y0: int | float, y1: int | float):
        """
        Construct new ROI from single values (int / float supported).

        Args:
            x0: start of x range
            x1: end of x range
            y0: start of y range
            y1: end of y range
        """
        return cls(x=Range(x0, x1), y=Range(y0, y1))

    @property
    def values(self) -> tuple[int | float, int | float, int | float, int | float]:
        """ROI values: x_min, x_max, y_min, y_max"""
        return self._x.minimum, self._x.maximum, self._y.minimum, self._y.maximum

    @property
    def x(self) -> Range:
        """x range of ROI (e.g. range of rows)"""
        return self._x

    @x.setter
    def x(self, new_x_range: Range):
        if not isinstance(new_x_range, Range):
            raise ValueError(f'x argument must be of type Range instead of "{type(new_x_range)}"')
        self._x = new_x_range

    @property
    def y(self) -> Range:
        """y range of ROI (e.g. range of columns)"""
        return self._y

    @y.setter
    def y(self, new_y_range: Range):
        if not isinstance(new_y_range, Range):
            raise ValueError(f'y argument must be of type Range instead of "{type(new_y_range)}"')
        self._y = new_y_range

    def shape(self, numpy_order: bool = False) -> tuple[int | float, int | float]:
        """
        Returns shape of ROI (x size (row), y size (column)). Optionally in numpy compliant order
        (y size (column), x size (row)).

        Args:
            numpy_order: Flag to enable numpy compliant return order for images

        Returns:
            tuple(x distance, y distance)
        """
        if numpy_order:
            return self.y.maximum - self.y.minimum, self.x.maximum - self.x.minimum

        return self.x.maximum - self.x.minimum, self.y.maximum - self.y.minimum
