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

from pathlib import Path

from .._protocols import PathParameter, Validator


class PathValidator(Validator):
    """Validator interface for parameter typing."""

    @staticmethod
    def validate(parameter: PathParameter) -> None:
        """Validate numerical parameter."""
        value: Path = parameter.value
        default = parameter.default
        parameter_type = parameter.parameter_type
        is_file = parameter.is_file
        file_suffixes = parameter.file_suffixes

        if parameter_type is not None:
            if not isinstance(default, parameter_type):
                raise TypeError(
                    f'default value is of type "{type(default)}" instead of expected type "{parameter_type}"'
                )
            if not isinstance(value, parameter_type):
                raise TypeError(f'value is of type "{type(value)}" instead of expected type "{parameter_type}"')

        if is_file and len(file_suffixes) > 0:
            if value.suffix == '' or value.suffix not in file_suffixes:
                raise TypeError(
                    f'file with suffix "{value.suffix}" not supported (supported suffixes: {file_suffixes})'
                )
