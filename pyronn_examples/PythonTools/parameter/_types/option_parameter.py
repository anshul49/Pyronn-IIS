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

from typing import Any, Sequence, Type
from dataclasses import dataclass, field
from enum import Enum

from ...unit import Unit, Units

from .._protocols import Validator, Parameter
from .._validators import DefaultValidator


@dataclass(frozen=True)
class Option(Parameter):
    """
    Immutable option parameter implementation for sequences and enums enriched by metadata.

    Instances of Option should be created using the Option.from_* methods as these populate
    the fields automatically. Using the default constructor is not recommended and can lead to inconsistencies.

    Useful for automatic UI generation and similar tasks. Parameter is immutable so it can be used as default parameter
    in method or function signatures.

    Make sure to use the "value" property to actually access the stored value of the parameter.

    Properties:
        value: parameter value
        values: sequence with values to select from
        option: name of the option corresponding to current value (useful for enums)
        options: sequence with options to select from (useful for enums); indexing must be consistent with values
        default: default value (optional)
        unit: unit of value (optional)
        name: name of parameter (optional)
        description: additional description of parameter (optional)
        readonly: declare parameter as readonly (not enforced - just for UI purposes, optional)
    """

    value: Any
    values: Sequence
    option: str
    options: Sequence
    default: Any
    unit: Unit | str = ''
    name: str = ''
    description: str = ''
    readonly: bool = False
    parameter_type: type = str
    _validator: Validator = field(default=DefaultValidator, init=False)

    def __post_init__(self) -> None:
        self._validator.validate(self)

    @classmethod
    def from_enum(
        cls,
        value: Enum,
        default: Enum = None,  # type: ignore
        name: str = '',
        unit: Unit | str = '',
        description: str = '',
        readonly: bool = False,
    ) -> Option:
        """
        Create new Option instance from an Enum object.

        All enum fields are parsed as options and corresponding values. Note that no Enum instance is stored.

        Args:
            value: currently set enum option
            default: default enum option (optional; if not specified will be automatically set to given "value")
            unit: unit of value (optional)
            name: name of parameter (optional)
            description: additional description of parameter (optional)
        """
        return cls(
            value=value.value,
            values=tuple(type(value)._value2member_map_),  # pylint: disable=W0212
            option=value.name,
            options=tuple(type(value)._member_names_),  # pylint: disable=W0212
            default=default.value if default is not None else value.value,
            name=name,
            unit=unit,
            description=description,
            readonly=readonly,
            parameter_type=type(value),
        )

    @classmethod
    def from_sequence(
        cls,
        value: Any,
        sequence: Sequence,
        default: Any = None,
        name: str = '',
        unit: Unit | str = '',
        description: str = '',
        readonly: bool = False,
    ) -> Option:
        """
        Create new Option instance from a sequence.

        The given value must be in the sequence otherwise a ValueError is thrown.

        Args:
            value: currently set sequence element
            default: default sequence element (optional; if not specified will be automatically set to given "value")
            unit: unit of value (optional)
            name: name of parameter (optional)
            description: additional description of parameter (optional)
        """
        if value not in sequence:
            raise ValueError(f'value {value} is not registered (possible values: {sequence}])')
        if default is not None and default not in sequence:
            raise ValueError(f'default value {default} is not registered (possible values: {sequence}])')
        return cls(
            value=value,
            values=tuple(sequence),
            option=value,
            options=tuple(sequence),
            default=default if default is not None else value,
            name=name,
            unit=unit,
            description=description,
            readonly=readonly,
            parameter_type=type(sequence),
        )

    @classmethod
    def from_dict(cls, input_dict: dict) -> Option:
        """
        Reconstruct Parameter from dict.

        Note that enum Options are converted to sequence-based Options during serialization/deserialization.
        """
        return cls.from_sequence(
            value=input_dict['value'],
            sequence=input_dict['sequence'],
            default=input_dict['default'],
            name=input_dict['name'],
            unit=Units.try_from_string(input_dict['unit']),
            description=input_dict['description'],
            readonly=input_dict['readonly'],
        )

    def to_dict(self) -> dict:
        """
        Convert Parameter to dict.

        Note that enum Options are converted to sequence-based Options during serialization/deserialization.
        """
        return {
            'value': self.value,
            'sequence': self.values,
            'default': self.default,
            'name': self.name,
            'unit': repr(self.unit) if isinstance(self.unit, Enum) else self.unit,
            'description': self.description,
            'readonly': self.readonly,
            'parameter_type': repr(self.parameter_type),
        }

    @property
    def enum_value(self) -> Enum:
        """
        Current value in Enum representation.

        Only possible if Option was created from an Enum, do not use when you plan to serialize or deserialize
        this Option parameter!
        """
        if not issubclass(self.parameter_type, Enum):
            raise ValueError('no Enum type registered; this property is only available for Option created from a Enum')
        return self.parameter_type(self.value)

    @property
    def enum_default(self) -> Enum:
        """
        Default value in Enum representation.

        Only possible if Option was created from an Enum, do not use when you plan to serialize or deserialize
        this Option parameter!
        """
        if not issubclass(self.parameter_type, Enum):
            raise ValueError('no Enum type registered; this property is only available for Option created from a Enum')
        return self.parameter_type(self.default)

    def to_default(self) -> Option:
        """Create new Option with same metadata as current object, but with default value."""
        if issubclass(self.parameter_type, Enum):
            return self.with_value((self.parameter_type)(self.default))
        return self.with_value(self.default)

    def with_value(self, value: Enum | Any) -> Option:
        """
        Create new Option with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """
        if isinstance(value, Enum):
            return Option.from_enum(
                value, type(value)(self.default), self.name, self.unit, self.description, self.readonly
            )

        return Option.from_sequence(
            value, self.values, self.default, self.name, self.unit, self.description, self.readonly
        )

    def with_index(self, index: int) -> Option:
        """
        Create new Option with same metadata as current object, but with new value based on its index.

        Args:
            index: index of value to create Option with
        """
        if not 0 <= index < len(self.values):
            raise IndexError(f'index {index} is out of bounds (current number of values: {len(self.values)})')
        return Option(
            value=self.values[index],
            values=self.values,
            option=self.options[index],
            options=self.options,
            default=self.default,
            unit=self.unit,
            name=self.name,
            description=self.description,
            readonly=self.readonly,
            parameter_type=self.parameter_type,
        )
