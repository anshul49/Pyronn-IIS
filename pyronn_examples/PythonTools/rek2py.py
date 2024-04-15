# FRAUNHOFER IIS CONFIDENTIAL
# __________________
#
# Fraunhofer IIS
# Copyright (c) 2015-2021
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

import os
import gzip

from pathlib import Path
from typing import Callable
from threading import Event

import numpy as np
from numpy.typing import NDArray

try:
    import lz4.frame  # type: ignore
except ModuleNotFoundError:
    pass

from .common_types import ProgressCallback
from .ezrt_header import EzrtHeader


class LoadingOperationStopped(Exception):
    """Raised if loading operation was stopped via the stop event."""

    pass


def rek2py(
    filepath: Path | str,
    switch_order: bool = False,
    slices: int | tuple[int, int] | None = None,
    compression: str | None = None,
    progress_callback: ProgressCallback | None = None,
    stop_event: Event | None = None,
    **kwargs,
) -> tuple[EzrtHeader, NDArray]:
    """
    Read a .rek volume file into an internal Python representation (3-dim numpy array) and its header.

    Args:
        filepath: file path to .rek file
        switch_order: toggle order of numpy array shape (True: (#images, H, W); False (W, H, #images))
        slices: if not None load only slice(s) as stated in int / tuple
        compression: compression algorithm to use (currently supported: None (=uncompressed), lz4, gzip)
        progress_callback: callback to report load progress func(int, int) -> None
        stop_event: event to set if loading should be aborted
        **kwargs: further arguments for compression algorithm

    Returns:
        tuple with EzrtHeader object and 3D numpy array representation of .rek file
    """
    filepath = Path(filepath)
    if not filepath.is_file():
        raise FileNotFoundError(f'given path is not a file [{filepath}]')

    if compression is None:
        with open(filepath, 'rb') as f:
            ezrt_header, image = _read_volume(f, slices, progress_callback, stop_event)
    elif compression == 'lz4':
        try:
            with lz4.frame.open(filepath, mode='rb', **kwargs) as f:
                ezrt_header, image = _read_volume(f, slices, progress_callback, stop_event)
        except NameError:
            raise NameError('to use lz4 compression, the lz4 module must be installed via "pip install lz4"')
    elif compression == 'gzip':
        with gzip.open(filepath, 'rb', **kwargs) as f:
            ezrt_header, image = _read_volume(f, slices, progress_callback, stop_event)
    else:
        raise ValueError('compression algorithm not supported')

    # import image payload data to numpy array (excluding header)
    if switch_order:
        # row-major indexing -> this is what is used by numpy (default)
        shape = ezrt_header.number_of_images, ezrt_header.image_height, ezrt_header.image_width
    else:
        shape = ezrt_header.image_width, ezrt_header.image_height, ezrt_header.number_of_images

    return ezrt_header, image.reshape(shape)


def _read_volume(
    file,
    slices: int | tuple[int, int] | None,
    progress_callback: ProgressCallback | None = None,
    stop_event: Event | None = None,
) -> tuple[EzrtHeader, NDArray]:
    # get file size reliably (even if volume is compressed)
    old_file_position = file.tell()
    file.seek(0, os.SEEK_END)
    filesize = file.tell()
    file.seek(old_file_position, os.SEEK_SET)

    if filesize < 2048:
        raise ValueError(f'wrong input file size (must be >= 2048; is: {filesize})')

    header_buffer = file.read(2048)
    ezrt_header = EzrtHeader.frombuffer(header_buffer[:2048])  # type: ignore
    dtype = EzrtHeader.convert_to_numpy_bitdepth(ezrt_header.bit_depth)
    itemsize = dtype().itemsize  # type:ignore - most of the time "2" for np.uint16

    if slices is None:
        chunk_size = 104_857_600
        chunk_size_itemsize = chunk_size // itemsize
        filesize = filesize - 2048
        filesize_itemsize = filesize // itemsize
        raw_file_data = np.empty(filesize_itemsize, dtype=dtype)
        i = 0
        # TODO: switch back to walrus operator as soon as https://github.com/python/mypy/pull/13284 is merged to mypy
        chunk = file.read(chunk_size)
        while chunk:
            if stop_event is not None and stop_event.is_set():
                raise LoadingOperationStopped('loading rek volume aborted')
            current_offset_itemsize = i * chunk_size_itemsize
            next_chunk_size = min(chunk_size_itemsize, filesize_itemsize - current_offset_itemsize)
            raw_file_data[current_offset_itemsize : current_offset_itemsize + next_chunk_size] = np.frombuffer(
                chunk, dtype=dtype
            )
            if progress_callback is not None:
                progress_callback(min(current_offset_itemsize * itemsize + chunk_size, filesize), filesize)
            i += 1
            chunk = file.read(chunk_size)
    else:
        stride = ezrt_header.image_height * ezrt_header.image_width
        if isinstance(slices, int):
            offset = slices
            end = offset + 1
        else:
            offset = slices[0]
            end = slices[1]
        ezrt_header.number_of_images = end - offset
        file.seek(2048 + itemsize * offset * stride)
        raw_file_data = file.read(itemsize * stride * ezrt_header.number_of_images)
        raw_file_data = np.frombuffer(raw_file_data, dtype=dtype)

    return ezrt_header, raw_file_data
