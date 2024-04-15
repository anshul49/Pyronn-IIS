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
from typing import Any, Type

from ...unit import Unit, Units

from .._protocols import Validator, Parameter
from .._validators import DefaultValidator


@dataclass(frozen=True)
class GenericData(Parameter):
    """
    Immutable generic data parameter implementation enriched by metadata.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Differences to other Parameter (e.g. Int):
    - there is no type checking happening for GenericData, but parameter type is set to act as a type hint.
    - depending on the set value, serializability is not guaranteed!
    - default value is not automatically set to value!

    Properties:
        value: parameter value
        default: default value (optional)
        name: name of parameter (optional)
        unit: unit of value (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: Any = None
    default: Any = None
    name: str = ''
    unit: Unit | str = ''
    description: str = ''
    readonly: bool = False
    parameter_type: type = field(default=int, init=False)
    _validator: Type[Validator] = field(default=DefaultValidator, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'parameter_type', type(self.value))
        self._validator.validate(self)

    @classmethod
    def from_dict(cls, input_dict: dict) -> GenericData:
        """Reconstruct Parameter from dict."""
        return cls(
            value=input_dict['value'],
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
            'default': self.default,
            'name': self.name,
            'unit': repr(self.unit) if isinstance(self.unit, Enum) else self.unit,
            'description': self.description,
            'readonly': self.readonly,
        }

    def to_default(self) -> GenericData:
        """Create new GenericData with same metadata as current object, but with default value."""
        return self.with_value(self.default)

    def with_value(self, value: Any) -> GenericData:
        """
        Create new GenericData with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        return GenericData(
            value=value,
            default=self.default,
            name=self.name,
            unit=self.unit,
            description=self.description,
            readonly=self.readonly,
        )
