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

from pathlib import Path

from PIL import Image
import numpy as np

from .raw2py import raw2py


def raws2gif(
    projection_folder: Path | str,
    projection_prefix: str,
    output_filename: Path | str,
    skip_projections: int = 5,
    downsample_factor: int = 4,
    scaling_value: float | None = None,
    resize_to: tuple[int, int] | None = None,
    frame_duration_in_ms: int = 200,
    loop_count: int = 0,
):
    """Generate a GIF from all EZRT RAW projections in a folder.

    Args:
        projection_folder: path to folder with projections
        projection_prefix: projection file prefix (e.g. image for image_0000.raw)
        output_filename: path and filename of generated GIF
        skip_projections: number of projection to skip during GIF creation (to save memory / disk space)
        downsample_factor: downsample factor to make more sparse projections (to save memory / disk space)
        scaling_value: greyscale truncating / scaling factor (if None GIF is not scaled)
        resize_to: resize image to new width / height (if None GIF is not resized)
        frame_duration_in_ms: duration of one frame in ms
        loop_count: number of loops until it stops (0: forever)
    """
    projection_folder = Path(projection_folder)

    if not projection_folder.is_dir():
        raise FileNotFoundError('projection folder does not exist')
    if skip_projections < 1:
        raise ValueError('value for skip projections must be > 0')
    if downsample_factor < 1:
        raise ValueError('downsampling factor must be > 0')
    if scaling_value is not None and not 0.0 <= scaling_value <= 1.0:
        raise ValueError('scaling factor must be between 0.0 and 1.0')
    if loop_count < 0:
        raise ValueError('loop count must be >= 0')
    if frame_duration_in_ms < 1:
        raise ValueError('frame duration must be > 0')

    max_greyvalue = 0
    min_greyvalue = 65536

    pattern = f'{projection_prefix}_*.raw'

    if scaling_value is not None:
        for filepath in sorted(projection_folder.glob(pattern))[::skip_projections]:
            image = raw2py(filepath, switch_order=True)[1][::downsample_factor, ::downsample_factor]
            current_min = image.min()
            current_max = image.max()
            if current_min < min_greyvalue:
                min_greyvalue = current_min
            if current_max > max_greyvalue:
                max_greyvalue = current_max

        max_greyvalue = max_greyvalue - int(np.floor(scaling_value * max_greyvalue))

        if min_greyvalue > 255:
            min_greyvalue = int(min_greyvalue / 255)
        if max_greyvalue > 255:
            max_greyvalue = int(max_greyvalue / 255)

    # use generator to avoid needing an image array
    def projection_generator(
        g_projection_folder: str | Path, g_pattern: str, g_min_greyvalue: int, g_max_greyvalue: int
    ):
        for g_filepath in sorted(Path(g_projection_folder).glob(g_pattern))[::skip_projections]:
            g_image = raw2py(g_filepath, switch_order=True)[1][::downsample_factor, ::downsample_factor]

            if scaling_value is not None:
                g_image = np.copy(g_image)
                # truncate
                g_image[g_image > g_max_greyvalue] = g_max_greyvalue

            if g_image.max() <= 255:
                g_image = g_image.astype(np.uint8)
            else:
                g_image = (g_image // 256).astype(np.uint8)

            if scaling_value is not None:
                # scale
                g_image = ((g_image - g_min_greyvalue) / (g_max_greyvalue - g_min_greyvalue)) * 255
                g_image = np.floor(g_image).astype(np.uint8)

            pil_image = Image.fromarray(g_image)
            if resize_to is not None:
                pil_image.resize(resize_to, Image.Resampling.BILINEAR)

            yield pil_image

    images = projection_generator(projection_folder, pattern, min_greyvalue, max_greyvalue)
    next(images).save(
        fp=output_filename,
        format='GIF',
        append_images=images,
        save_all=True,
        duration=frame_duration_in_ms,
        loop=loop_count,
    )

    return min_greyvalue, max_greyvalue
