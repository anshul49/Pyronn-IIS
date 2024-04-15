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
from .._protocols import ArrayParameter
from .type_validator import TypeValidator


class ArrayValidator(TypeValidator):
    """Validator interface for numerical parameter."""

    @staticmethod
    def validate(parameter: ArrayParameter) -> None:
        """Validate numerical parameter."""
        TypeValidator.validate(parameter)

        shape = parameter.shape
        max_shape = parameter.max_shape
        default_shape = np.array(parameter.default).shape

        if max_shape is not None:
            if len(default_shape) > 1 and not all(map(lambda x, y: x <= y, *zip(default_shape, max_shape))):
                raise ValueOutOfRangeException(
                    f'default array has too many elements ({default_shape} out of {max_shape})'
                )
            if len(shape) > 1 and not all(map(lambda x, y: x <= y, *zip(shape, max_shape))):
                raise ValueOutOfRangeException(f'array has too many elements ({shape} out of {max_shape})')
