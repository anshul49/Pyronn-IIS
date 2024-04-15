# FRAUNHOFER IIS CONFIDENTIAL
# __________________
#
# Fraunhofer IIS
# Copyright (c) 2016-2021
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
import warnings


class PrmMetaData:
    """Werth PRM data / parser class"""

    def __init__(self):
        """
        Construct new PrmMetaData instance with given parameters.

        Attributes:
            image_width: image width
            image_height: image height
            pixel_width_in_um: pixel width in micrometer
            current_in_ua: current in microampere
            voltage_in_kv: voltage in kilovolt
            voxel_size_in_um: voxel size in micrometer
            prefilter: prefilter
            exposure_time_in_ms: exposure time in milliseconds
            number_averages: number averages
            number_projection_angles: number of projection angles
            focus_object_distance_in_mm: focus object distance in millimeter
            focus_detector_distance_in_mm: focus ditector distance in millimeter
        """
        self.image_width: int = 0
        self.image_height: int = 0
        self.pixel_width_in_um: float = 0.0

        self.current_in_ua: float = 0.0
        self.voltage_in_kv: float = 0.0
        self.voxel_size_in_um: float = 0.0
        self.prefilter: str = ''
        self.exposure_time_in_ms: float = 0.0
        self.number_averages: int = 0
        self.number_projection_angles: int = 0
        self.focus_object_distance_in_mm: float = 0.0
        self.focus_detector_distance_in_mm: float = 0.0

    @classmethod
    def fromfile(cls, filename: Path | str) -> PrmMetaData:
        """
        Create new PrmMetaData instance from file

        Args:
            filename: path to PRM file
        """
        prm_string = ''
        with open(filename, 'r') as fd:
            prm_string = fd.read()

        return cls.fromstring(prm_string)

    @classmethod
    def fromstring(cls, xml_string: str) -> PrmMetaData:
        """
        Create new PrmMetaData instance from PRM string.

        Args:
            xml_string: string with PRM
        """
        header = cls()
        header._parse_prm(xml_string)
        return header

    @property
    def magnification(self) -> float:
        if self.focus_object_distance_in_mm <= 0.0 or self.focus_object_distance_in_mm <= 0.0:
            warnings.warn('FOD and/or FDD not set - magnification cannot be calculated')
            return -1.0
        return self.focus_detector_distance_in_mm / self.focus_object_distance_in_mm

    def _parse_prm(self, prm_string: str):
        for parameter_name in prm_string.splitlines():
            data = parameter_name.split('=')
            if len(data) < 2:
                continue
            parameter_name = data[0].lower()
            parameter_value = data[1]

            if parameter_name == 'linenum':
                self.image_height = int(parameter_value.strip())
            elif parameter_name == 'colnum':
                self.image_width = int(parameter_value.strip())
            elif parameter_name == 'pixelx':
                self.pixel_width_in_um = float(parameter_value.strip()) * 1000.0
            elif parameter_name == 'current':
                self.current_in_ua = float(parameter_value.strip())
            elif parameter_name == 'voltage':
                self.voltage_in_kv = float(parameter_value.strip())
            elif parameter_name == 'orivoxelsize':
                self.voxel_size_in_um = float(parameter_value.strip()) * 1000.0
            elif parameter_name == 'filterchange':
                self.prefilter = parameter_value.strip()
            elif parameter_name == 'inttime':
                self.exposure_time_in_ms = float(parameter_value.strip())
            elif parameter_name == 'average':
                self.number_averages = int(parameter_value.strip())
            elif parameter_name == 'steps':
                self.number_projection_angles = int(parameter_value.strip())
            elif parameter_name == 'fdd':
                self.focus_detector_distance_in_mm = float(parameter_value.strip())
            elif parameter_name == 'fod':
                self.focus_object_distance_in_mm = float(parameter_value.strip())
