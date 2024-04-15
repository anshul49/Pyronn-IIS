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
from typing import Type

from ...unit import Unit

from .._protocols import Validator, Parameter
from .._validators import TypeValidator


@dataclass(frozen=True)
class Bool(Parameter):
    """
    Immutable bool parameter implementation enriched by metadata.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Properties:
        value: parameter value
        default: default value (optional; if not specified will be automatically set to given "value")
        name: name of parameter (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: bool = False
    default: bool = None  # type: ignore (see __post_init__)
    name: str = ''
    description: str = ''
    unit: Unit | str = field(default='', init=False)
    readonly: bool = False
    parameter_type: type = field(default=bool, init=False)
    _validator: Type[Validator] = field(default=TypeValidator, init=False)

    def __post_init__(self) -> None:
        # None indicates "not set" -> in this case use "value"
        if self.default is None:
            object.__setattr__(self, 'default', self.value)

        self._validator.validate(self)

    @classmethod
    def from_dict(cls, input_dict: dict) -> Bool:
        """Reconstruct Parameter from dict."""
        return cls(
            value=input_dict['value'],
            default=input_dict['default'],
            name=input_dict['name'],
            description=input_dict['description'],
            readonly=input_dict['readonly'],
        )

    def to_dict(self) -> dict:
        """Convert Parameter to dict."""
        return {
            'value': self.value,
            'default': self.default,
            'name': self.name,
            'description': self.description,
            'readonly': self.readonly,
        }

    def to_default(self) -> Bool:
        """Create new Bool with same metadata as current object, but with default value."""
        return self.with_value(self.default)

    def with_value(self, value: bool) -> Bool:
        """
        Create new Bool with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        return Bool(
            value=value,
            name=self.name,
            default=self.default,
            description=self.description,
            readonly=self.readonly,
        )
