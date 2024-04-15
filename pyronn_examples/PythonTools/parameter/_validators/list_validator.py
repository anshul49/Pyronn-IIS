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

from ...common_exceptions import ValueOutOfRangeException
from .._protocols import ListParameter
from .type_validator import TypeValidator


class SequenceValidator(TypeValidator):
    """Validator interface for numerical parameter."""

    @staticmethod
    def validate(parameter: ListParameter) -> None:
        """Validate numerical parameter."""
        TypeValidator.validate(parameter)

        value = parameter.value
        len_default = len(parameter.default)
        length = parameter.length
        max_length = parameter.max_length

        if len(value) != length:
            raise ValueError(f'value length ({len(value)}) does not match set current length ({length})')

        if max_length is not None and len_default > max_length:
            raise ValueOutOfRangeException(f'default list has too many elements ({len_default} out of {max_length})')
        if max_length is not None and length > max_length:
            raise ValueOutOfRangeException(f'list has too many elements ({length} out of {max_length})')
