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

from typing import Protocol, Any, Type, runtime_checkable

from ..common_types import Range
from ..unit import Unit

from numpy.typing import DTypeLike

# Validator protocols


class Validator(Protocol):
    """Validator interface for parameter."""

    @staticmethod
    def validate(parameter: Parameter):
        """Validate numerical parameter."""


# Parameter protocols


@runtime_checkable
class Parameter(Protocol):
    """Protocol interface for Parameter with metadata."""

    value: Any
    default: Any
    unit: Unit | str
    name: str
    description: str
    readonly: bool
    parameter_type: type
    _validator: Type[Validator]

    def to_default(self) -> Parameter:  # type: ignore
        """Create new Parameter with same metadata as current object, but with default value."""

    def with_value(self, value: Any) -> Parameter:  # type: ignore
        """
        Create new Parameter with same metadata as current object, but with new value.

        Args:
            value: new value to set
        """

    def to_dict(self) -> dict:  # type: ignore
        """Convert Parameter to dict."""

    @classmethod
    def from_dict(cls, dict) -> Parameter:  # type: ignore
        """Reconstruct Parameter from dict."""


class NumericalParameter(Parameter, Protocol):
    """Protocol interface for numerical parameters."""

    range: Range | None
    step: Any
    dtype: DTypeLike


class PathParameter(Parameter, Protocol):
    """Protocol interface for numerical parameters."""

    is_file: bool
    file_suffixes: tuple[str, ...]


class ListParameter(Parameter, Protocol):
    """Protocol interface for numerical parameters."""

    length: int
    max_length: int | None
    step: int


class ArrayParameter(Parameter, Protocol):
    """Protocol interface for numerical parameters."""

    shape: tuple
    max_shape: tuple | None
    step: tuple
