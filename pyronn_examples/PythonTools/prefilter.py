# Copyright 2023 Simon Wittl (Deggendorf Institute of Technology)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Sequence
from enum import IntEnum
from collections import Counter


class XrayPrefilterElement(IntEnum):
    """
    Enum with most common xray prefilter elements.

    Enum value maps to ordinal number.
    """

    NONE = -1
    AL = 13
    CU = 29
    SN = 30
    GA = 31
    PB = 82

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_element_symbol(cls, symbol: str):
        symbol = symbol.lower()
        if symbol == 'none':
            return cls.NONE
        if symbol == 'al':
            return cls.AL
        if symbol == 'cu':
            return cls.CU
        if symbol == 'sn':
            return cls.SN
        if symbol == 'ga':
            return cls.GA
        if symbol == 'pb':
            return cls.PB

        raise ValueError(
            f'element symbol "{symbol}" not supported (choose from {[val.name for val in iter(XrayPrefilterElement)]})'
        )


class XrayPrefilterMaterial:
    """Xray prefilter material."""

    def __init__(self, element: XrayPrefilterElement | int | str, thickness_in_mm: float) -> None:
        """
        Create new XrayPrefilterMaterial.

        Args:
            element: element of filter (either XrayPrefilterElement instance, ordinal number or element symbol or NONE)
            thickness_in_mm: thickness of xray prefilter material in mm (ignored for NONE filter)

        Raises:
            ValueError: raised if wrong ordinal number or string representation of filter element is given
        """

        if isinstance(element, str):
            element = XrayPrefilterElement.from_element_symbol(element)
        elif isinstance(element, int):
            try:
                element = XrayPrefilterElement(element)
            except ValueError:
                raise ValueError(
                    f'element with ordinal number "{element}" not supported (choose from '
                    + ', '.join([f'{val.value} ({val.name})' for val in iter(XrayPrefilterElement)])
                    + ')'
                )

        if element is not XrayPrefilterElement.NONE and thickness_in_mm <= 0.0:
            raise ValueError(f'prefilter thickness must be > 0.0 mm (is {thickness_in_mm})')

        self.element: XrayPrefilterElement = element  # type: ignore
        self.thickness_in_mm: float = float(thickness_in_mm) if element is not XrayPrefilterElement.NONE else 0.0

    def __hash__(self) -> int:
        if self.element == XrayPrefilterElement.NONE:
            return hash(self.element)
        return hash((self.element, self.thickness_in_mm))

    def __eq__(self, other: XrayPrefilterMaterial) -> bool:
        if self.element == XrayPrefilterElement.NONE and other.element == XrayPrefilterElement.NONE:
            return True
        return self.element == other.element and self.thickness_in_mm == other.thickness_in_mm

    @classmethod
    def from_tuple(cls, material_tuple: tuple[XrayPrefilterElement | int | str, float]) -> XrayPrefilterMaterial:
        """
        Create new instance of XrayPrefilterMaterial via its tuple representation ("(material, thickness)").

        Args:
            material_tuple: tuple representation of filter, e.g. ('AL', 0.5)

        Raises:
            similar to constructor.

        Returns:
            XrayPrefilterMaterial instance
        """
        return cls(material_tuple[0], material_tuple[1])

    def as_tuple(self) -> tuple[XrayPrefilterElement, float]:
        """Return tuple representation of current filter material ("(material, thickness)")."""
        return self.element, self.thickness_in_mm

    @classmethod
    def from_str(cls, material_string: str) -> XrayPrefilterMaterial:
        """
        Create new instance of XrayPrefilterMaterial via its string representation "<material>_<thickness>mm".

        Args:
            material_tuple: string representation of filter, e.g. "AL_0.5mm"

        Raises:
            similar to constructor.

        Returns:
            XrayPrefilterMaterial instance
        """
        material_string = material_string.lower()
        if material_string == 'none':
            return cls(XrayPrefilterElement.NONE, 0.0)

        if not material_string.endswith('mm') or '_' not in material_string:
            raise ValueError(
                'wrong material string format (must be "<material>_<thickness>mm" (e.g. "AL_0.5mm"), is:'
                f' {material_string})'
            )
        material_str, thickness_str = material_string.split('_')
        return cls(material_str.upper(), float(thickness_str[:-2]))

    def __str__(self) -> str:
        """Return string representation of current filter material ("<material>_<thickness>mm")."""
        if self.element == XrayPrefilterElement.NONE:
            return 'NONE'
        return f'{XrayPrefilterElement(self.element).name}_{self.thickness_in_mm:.4f}mm'


class XrayPrefilter:
    """Xray prefilter class which defineds a "xray prefilter" by combining different prefilter materials."""

    def __init__(self, prefilter_materials: XrayPrefilterMaterial | list[XrayPrefilterMaterial] | None = None) -> None:
        """
        Create new XrayPrefilter.

        Args:
            prefilter_materials: list of xray prefilter material instances (optional)
        """
        if isinstance(prefilter_materials, XrayPrefilterMaterial):
            prefilter_materials = [prefilter_materials]
        self._materials = [] if prefilter_materials is None else prefilter_materials

    def __eq__(self, other: XrayPrefilter) -> bool:
        # order should not matter in prefilter -> list with same content but different order are equal
        return Counter(self.materials) == Counter(other.materials)

    @property
    def materials(self) -> list[XrayPrefilterMaterial]:
        """Material composition of prefilter as list."""
        return self._materials

    @materials.setter
    def materials(self, materials: XrayPrefilterMaterial | list[XrayPrefilterMaterial] | None):
        if isinstance(materials, XrayPrefilterMaterial):
            materials = [materials]
        self._materials = [] if materials is None else materials

    def add_material(self, new_prefilter_material: XrayPrefilterMaterial):
        """Add filter material to compostion."""
        if XrayPrefilterMaterial.from_str('NONE') in self.materials:
            raise ValueError('NONE prefilter not composable - must be the only material in prefilter')
        if new_prefilter_material == XrayPrefilterMaterial.from_str('NONE') and len(self.materials) > 0:
            raise ValueError('NONE prefilter not composable - must be the only material in prefilter')

        self.materials.append(new_prefilter_material)

    @classmethod
    def from_sequence(
        cls, prefilter_materials: Sequence[tuple[XrayPrefilterElement | int | str, float]]
    ) -> XrayPrefilter:
        """
        Create new XrayPrefilter from a list of tuple representations of the single filter materials.

        Args:
            prefilter_materials: list with materials in tuple representation, e.g. [('AL', 0.5), ('CU', 0.2)]

        Returns:
            XrayPrefilter instance
        """
        prefilter = cls()
        for material_tuple in prefilter_materials:
            material = XrayPrefilterMaterial.from_tuple(material_tuple)
            prefilter.add_material(material)
        return prefilter

    def as_tuples(self) -> tuple[tuple[XrayPrefilterElement, float], ...]:
        """Return current prefilter as list of materials in tuple representation."""
        return tuple([material.as_tuple() for material in self.materials])

    @classmethod
    def from_str(cls, prefilter_string: str) -> XrayPrefilter:
        """
        Create new XrayPrefilter from the string representation of the single filter materials.

        Args:
            prefilter_materials: list with materials in tuple representation, e.g. "CU_0.1000mm+AL_0.5000mm"

        Returns:
            XrayPrefilter instance
        """
        if prefilter_string == 'NONE':
            prefilter = cls()
            prefilter.add_material(XrayPrefilterMaterial.from_str('NONE'))
            return prefilter

        prefilter_materials = prefilter_string.split('+')

        prefilter = cls()
        for material_str in prefilter_materials:
            material = XrayPrefilterMaterial.from_str(material_str)
            prefilter.add_material(material)
        return prefilter

    def __str__(self) -> str:
        """Return string representation of current prefilter."""
        return '+'.join(map(str, self.materials))
