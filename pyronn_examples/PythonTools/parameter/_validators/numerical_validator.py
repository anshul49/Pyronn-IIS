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

import numpy as np

from ...common_exceptions import ValueOutOfRangeException
from .._protocols import NumericalParameter
from .type_validator import TypeValidator


class NumericalValidator(TypeValidator):
    """Validator interface for numerical parameter."""

    @staticmethod
    def validate(parameter: NumericalParameter) -> None:
        """Validate numerical parameter."""
        TypeValidator.validate(parameter)

        value = parameter.value
        default = parameter.default
        parameter_type = parameter.parameter_type
        valid_range = parameter.range
        step = parameter.step
        dtype = parameter.dtype

        if parameter_type is not None:
            if not isinstance(step, parameter_type):
                raise TypeError(f'step is of type "{type(step)}" instead of expected type "{parameter_type}"')
            if valid_range is not None:
                if not isinstance(valid_range.minimum, parameter_type):
                    range_type = type(valid_range.minimum)
                    raise TypeError(f'range is of type "{range_type}" instead of expected type "{parameter_type}"')
                if not isinstance(valid_range.maximum, parameter_type):
                    range_type = type(valid_range.minimum)
                    raise TypeError(f'range is of type "{range_type}" instead of expected type "{parameter_type}"')
        if valid_range is not None:
            if not valid_range.in_range(default):
                raise ValueOutOfRangeException(
                    f'default value "{default}" is out of range ([{valid_range.minimum}; {valid_range.maximum}])'
                )
            if not valid_range.in_range(value):
                raise ValueOutOfRangeException(
                    f'value "{value}" is out of range ([{valid_range.minimum}; {valid_range.maximum}])'
                )
        if dtype is not None:
            try:
                np.dtype(dtype)
            except TypeError:
                raise TypeError(f'"{dtype}" cannot be converted in a valid numpy data type object')
