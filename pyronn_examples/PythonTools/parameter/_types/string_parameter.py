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
from typing import Type

from ...unit import Unit, Units

from .._protocols import Validator, ListParameter
from .._validators import SequenceValidator


@dataclass(frozen=True)
class String(ListParameter):
    """
    Immutable string parameter implementation enriched by metadata.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Properties:
        value: parameter value
        length: current length of string (read-only)
        max_length: max string length; None means unrestricted length (optional)
        step: step of array (read-only; for String always 1)
        default: default value (optional; if not specified will be automatically set to given "value")
        unit: unit of value (optional)
        name: name of parameter (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: str = ''
    max_length: int | None = None
    default: str = None  # type: ignore (see __post_init__)
    name: str = ''
    unit: Unit | str = ''
    description: str = ''
    readonly: bool = False
    parameter_type: type = field(default=str, init=False)
    length: int = field(default=1, init=False)
    step: int = field(default=1, init=False)
    _validator: Type[Validator] = field(default=SequenceValidator, init=False)

    def __post_init__(self) -> None:
        # as the class is immutable __setattr__ has to be used to change the length attribute
        object.__setattr__(self, 'length', len(self.value))

        # None indicates "not set" -> in this case use "value"
        if self.default is None:
            object.__setattr__(self, 'default', self.value)

        self._validator.validate(self)

    @classmethod
    def from_dict(cls, input_dict: dict) -> String:
        """Reconstruct Parameter from dict."""
        return cls(
            value=input_dict['value'],
            max_length=input_dict['max_length'],
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
            'max_length': self.max_length,
            'default': self.default,
            'name': self.name,
            'unit': repr(self.unit) if isinstance(self.unit, Enum) else self.unit,
            'description': self.description,
            'readonly': self.readonly,
        }

    def to_default(self) -> String:
        """Create new String with same metadata as current object, but with default value."""
        return self.with_value(self.default)

    def with_value(self, value: str) -> String:
        """
        Create new String with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        return String(
            value=str(value),
            max_length=self.max_length,
            default=self.default,
            unit=self.unit,
            name=self.name,
            description=self.description,
            readonly=self.readonly,
        )
