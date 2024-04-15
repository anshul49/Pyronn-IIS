# FRAUNHOFER IIS CONFIDENTIAL
# __________________
#
# Fraunhofer IIS
# Copyright (c) 2023
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

from typing import Sequence, Type
from enum import Enum
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import DTypeLike

from ...common_types import Range
from ...unit import Unit, Units

from .._protocols import Validator, NumericalParameter
from .._validators import NumericalValidator


@dataclass(frozen=True)
class Int(NumericalParameter):
    """
    Immutable integer parameter implementation enriched by metadata.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Properties:
        value: parameter value
        range: valid integer range of value; None means unrestricted range (optional)
        step: hint for step amount of value (not enforced - just for UI purposes, optional)
        dtype: numpy data type object or its string representation (optional)
        default: default value (optional; if not specified will be automatically set to given "value")
        unit: unit of value (optional)
        name: name of parameter (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: int = 0
    range: Range | Sequence[int] | None = None
    step: int = 1
    dtype: DTypeLike = None
    default: int = None  # type: ignore (see __post_init__)
    unit: Unit | str = ''
    name: str = ''
    description: str = ''
    readonly: bool = False
    parameter_type: type = field(default=int, init=False)
    _validator: Type[Validator] = field(default=NumericalValidator, init=False)

    def __post_init__(self) -> None:
        # change given sequence internally to Range, which automatically checks for valid borders
        if isinstance(self.range, Sequence):
            if len(self.range) != 2:
                raise ValueError('range must be a Sequence with 2 int elements (min, max) or a Range object')
            # as the class is immutable __setattr__ has to be used to change the range attribute
            object.__setattr__(self, 'range', Range(self.range[0], self.range[1]))

        # None indicates "not set" -> in this case use "value"
        if self.default is None:
            object.__setattr__(self, 'default', self.value)

        self._validator.validate(self)

        if self.dtype is None:
            object.__setattr__(self, 'dtype', np.dtype(np.int64))
        else:
            object.__setattr__(self, 'dtype', np.dtype(self.dtype))

    @classmethod
    def from_dict(cls, input_dict: dict) -> Int:
        """Reconstruct Parameter from dict."""
        return cls(
            value=input_dict['value'],
            range=Range(input_dict['range'][0], input_dict['range'][1]) if input_dict['range'] is not None else None,
            step=input_dict['step'],
            dtype=input_dict['dtype'],
            default=input_dict['default'],
            name=input_dict['name'],
            unit=Units.try_from_string(input_dict['unit']),
            description=input_dict['description'],
            readonly=input_dict['readonly'],
        )

    def to_dict(self) -> dict:
        """Convert Parameter to dict."""
        return {
            'value': self.value,
            'range': (self.range.minimum, self.range.maximum) if self.range is not None else None,  # type: ignore
            'step': self.step,
            'dtype': self.dtype.str,  # type: ignore
            'default': self.default,
            'name': self.name,
            'unit': repr(self.unit) if isinstance(self.unit, Enum) else self.unit,
            'description': self.description,
            'readonly': self.readonly,
        }

    def to_default(self) -> Int:
        """Create new Int with same metadata as current object, but with default value."""
        return self.with_value(self.default)

    def with_value(self, value: int) -> Int:
        """
        Create new Int with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        return Int(
            value=value,
            range=self.range,
            step=self.step,
            dtype=self.dtype,
            default=self.default,
            name=self.name,
            unit=self.unit,
            description=self.description,
            readonly=self.readonly,
        )
