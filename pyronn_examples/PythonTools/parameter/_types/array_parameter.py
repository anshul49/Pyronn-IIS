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

from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy
from typing import Sequence, Type

import numpy as np

from ...unit import Unit, Units

from .._protocols import Validator, ArrayParameter
from .._validators import ArrayValidator


@dataclass(frozen=True)
class Array(ArrayParameter):
    """
    Immutable str parameter implementation enriched by metadata.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Properties:
        value: parameter value
        shape: current shape of array (numpy-ordering; read-only)
        max_shape: max array size; None means unrestricted size (optional)
        step: step of array (optional)
        default: default value (optional)
        name: name of parameter (optional)
        unit: unit of value (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: Sequence = ()
    max_shape: tuple | None = None
    step: int | None = None
    default: Sequence = None  # type: ignore (see __post_init__)
    name: str = ''
    unit: Unit | str = ''
    description: str = ''
    readonly: bool = False
    parameter_type: type = field(default=Sequence, init=False)
    shape: tuple = field(default=(1, 0), init=False)
    _validator: Type[Validator] = field(default=ArrayValidator, init=False)

    def __post_init__(self) -> None:
        shape = np.array(self.value).shape
        object.__setattr__(self, 'shape', tuple(shape))
        # None indicates "not set" -> in this case use "value"
        if self.default is None:
            object.__setattr__(self, 'default', deepcopy(self.value))
        self._validator.validate(self)

    @classmethod
    def from_dict(cls, input_dict: dict) -> Array:
        """Reconstruct Parameter from dict."""
        return cls(
            value=input_dict['value'],
            max_shape=input_dict['max_shape'],
            step=input_dict['step'],
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
            'max_shape': self.max_shape,
            'step': self.step,
            'default': self.default,
            'name': self.name,
            'unit': repr(self.unit) if isinstance(self.unit, Enum) else self.unit,
            'description': self.description,
            'readonly': self.readonly,
        }

    def to_default(self) -> Array:
        """Create new Array with same metadata as current object, but with default value."""
        return self.with_value(self.default)

    def with_value(self, value: Sequence) -> Array:
        """
        Create new Array with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        return Array(
            value=value,
            max_shape=self.max_shape,
            step=self.step,
            default=self.default,
            name=self.name,
            unit=self.unit,
            description=self.description,
            readonly=self.readonly,
        )
