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

import os
import threading
import queue
import json
from pathlib import Path
from typing import Any

import numpy as np
import PIL
import PIL.Image

from .raw2py import raw2py
from .py2raw import py2raw
from .ezrt_header import EzrtHeader
from .common_types import ImageFormat, IMAGEFORMATS  # IMAGEFORMATS for compatibility reasons, will be removed


class ImageIO:
    """Image IO Base class"""

    def __init__(self, imageformat: ImageFormat = ImageFormat.AUTO):
        self.imageformat = imageformat

    @staticmethod
    def autodetect_image_format(filepath: Path | str) -> ImageFormat:
        """
        Try to detect image format based on file suffix.

        Args:
            filepath: filepath to analyse

        Returns:
            imageformat instance
        """
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()

        if suffix == '.raw':
            imageformat = ImageFormat.RAW_EZRT
        elif suffix in ('.tif', '.tiff'):
            imageformat = ImageFormat.TIFF
        elif suffix == '.png':
            imageformat = ImageFormat.PNG
        elif suffix == '.bmp':
            imageformat = ImageFormat.BMP
        else:
            raise ValueError(f'file suffix {suffix} not supported - AUTO mode couldn\'t recognize image format')

        return imageformat

    @staticmethod
    def add_file_suffix(filename: str, imageformat: ImageFormat) -> str:
        """
        Add file suffix of image type (case-insensitive) to filename.

        Args:
            filename: filepath to add suffix to
            imageformat: target image format for saving (see ImageFormat for options)

        Returns
            filename with suffix
        """
        suffix = ''
        lower_case_filename = filename.lower()
        if imageformat == ImageFormat.PNG:
            if not lower_case_filename.endswith('.png'):
                suffix = '.png'
        elif imageformat == ImageFormat.TIFF:
            if not (lower_case_filename.endswith('.tif') or lower_case_filename.endswith('.tiff')):
                suffix = '.tif'
        elif imageformat == ImageFormat.BMP:
            if not lower_case_filename.endswith('.bmp'):
                suffix = '.bmp'
        elif imageformat in (ImageFormat.RAW_EZRT, ImageFormat.RAW_BINARY):
            if not lower_case_filename.endswith('.raw'):
                suffix = '.raw'
        else:
            raise NotImplementedError(f'image format "{imageformat}" not supported')

        return f'{filename}{suffix}'

    @staticmethod
    def remove_file_suffix(filename: str, imageformat: ImageFormat) -> str:
        """
        Remove file suffix of image type (case-insensitive) from filename.

        Args:
            filename: filepath to remove suffix from
            imageformat: target image format for saving (see ImageFormat for options)

        Returns:
            filename without suffix
        """
        lower_case_filename = filename.lower()
        if imageformat == ImageFormat.PNG:
            if lower_case_filename.endswith('.png'):
                filename = filename[:-4]
        elif imageformat == ImageFormat.TIFF:
            if lower_case_filename.endswith('.tif'):
                filename = filename[:-4]
            elif lower_case_filename.endswith('.tiff'):
                filename = filename[:-5]
        elif imageformat == ImageFormat.BMP:
            if lower_case_filename.endswith('.bmp'):
                filename = filename[:-4]
        elif imageformat in (ImageFormat.RAW_EZRT, ImageFormat.RAW_BINARY):
            if lower_case_filename.endswith('.raw'):
                filename = filename[:-4]
        else:
            raise NotImplementedError(f'image format "{imageformat}" not supported')

        return filename


class ImageLoader(ImageIO):
    """This class allows for loading different formats (stated by ImageFormat) into 2D numpy arrays."""

    def __init__(self, imageformat: ImageFormat = ImageFormat.AUTO):
        """
        Construct new ImageLoader with imageformat.
        AUTO mode tries to guess the format depending on the suffix; if it is .raw the EZRT format is assumed.

        Args:
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO
        """
        super().__init__(imageformat)

    @staticmethod
    def load_metadata(
        filepath: Path | str, imageformat: ImageFormat = ImageFormat.AUTO
    ) -> tuple[dict, EzrtHeader | None]:
        """
        Load metadata from file with given filename and with specified image format.

        Args:
            filepath: filepath to load from (with or without file extension)
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO

        Returns:
            metadata dict
        """
        filepath = Path(filepath)

        if imageformat == ImageFormat.AUTO:
            imageformat = ImageIO.autodetect_image_format(filepath)

        metadata = {}
        if imageformat in (ImageFormat.TIFF, ImageFormat.BMP, ImageFormat.PNG, ImageFormat.RAW_BINARY):
            try:
                info_path = filepath.parent / 'info.json'
                if not info_path.is_file() or info_path.stat().st_size <= 0:
                    raise FileNotFoundError
                with open(info_path, 'r', encoding='utf8') as file:
                    metadata = dict(json.load(file)[filepath.stem])
            # if info.json does not exist, use image shape as metadata
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                image_shape = np.array(PIL.Image.open(filepath)).shape
                metadata['image_width'] = int(image_shape[1])
                metadata['image_height'] = int(image_shape[0])
            ezrt_header = EzrtHeader(0, 0, metadata=metadata)
        elif imageformat == ImageFormat.RAW_EZRT:
            ezrt_header = EzrtHeader.fromfile(filepath)
            metadata = ezrt_header.metadata
        else:
            raise NotImplementedError(f'image format "{imageformat}" not supported')

        return metadata, ezrt_header

    @staticmethod
    def load_image(
        filepath: Path | str,
        imageformat: ImageFormat = ImageFormat.AUTO,
        dtype=np.uint16,
        load_metadata: bool = False,
    ) -> tuple[np.ndarray, dict[str, Any], EzrtHeader | None]:
        """
        Load file with given filename and with specified image format into a 2D numpy array if possible.

        Args:
            filepath: filepath to load from (with or without file extension)
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO
            dtype: numpy dtype as which the image is loaded
            load_metadata: flag if metadata and/or header should be loaded (if not an empty dict / None is returned)

        Returns:
            image file as 2D nparray and the metadata dict
        """
        filepath = Path(filepath)

        if imageformat == ImageFormat.AUTO:
            imageformat = ImageIO.autodetect_image_format(filepath)

        metadata = {}
        ezrt_header = None
        if load_metadata:
            metadata, ezrt_header = ImageLoader.load_metadata(filepath, imageformat)

        if imageformat in (ImageFormat.TIFF, ImageFormat.BMP, ImageFormat.PNG):
            image = np.array(PIL.Image.open(filepath))
        elif imageformat == ImageFormat.RAW_BINARY:
            image = np.fromfile(filepath, dtype=dtype)
        elif imageformat == ImageFormat.RAW_EZRT:
            ezrt_header, image = raw2py(filepath, switch_order=True)
            if not load_metadata:
                ezrt_header = None
        else:
            raise NotImplementedError(f'image format "{imageformat}" not supported')

        return image.astype(dtype), metadata, ezrt_header

    def load_current_metadata(self, filepath: str) -> tuple[dict, EzrtHeader | None]:
        """
        Load metadata from file with given filename and with image format used in constructor.

        Args:
            filepath: filepath to load from (with or without file extension)

        Returns:
            metadata dict
        """
        return ImageLoader.load_metadata(filepath, self.imageformat)

    def load(self, filepath: str, dtype=np.uint16, load_metadata: bool = False):
        """
        Load file with given filename and with image format used in constructor into a 2D numpy array if possible.

        Args:
            filepath: filepath to load from (with or without file extension)
            dtype: numpy dtype as which the image is loaded
            load_metadata: flag if metadata and/or header should be loaded (if not an empty dict / None is returned)

        Returns:
            image file as 2D nparray and the metadata dict
        """
        return ImageLoader.load_image(filepath, self.imageformat, dtype, load_metadata)


class ImageSaver(ImageIO):
    """This class allows for saving numpy arrays in different formats (stated by ImageFormat)."""

    def __init__(self, imageformat: ImageFormat = ImageFormat.AUTO):
        """
        Construct new ImageSaver with imageformat.

        Args:
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO
        """
        super().__init__(imageformat)

    @staticmethod
    def save_image(
        image: np.ndarray,
        filename: str,
        imageformat: ImageFormat = ImageFormat.AUTO,
        savefolder: Path | str = '.',
        ezrt_header: EzrtHeader | None = None,
        metadata: dict | None = None,
        overwrite_info: bool = True,
    ):
        """
        Save image (2D numpy array) with specified image format. If a metadata dict is provided it either saved into an
        info JSON file or in case of the image format 'RAW_EZRT' saved into the EZRT header.

        Args:
            image: 2D numpy array
            filename: filename to save to (with or witout file extension)
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO
            savefolder: folder to save to, defaults to CWD
            ezrt_header: header to use (has priority over metadata!); width & height fields are extracted from image
            metadata: dict with image metadata, defaults to None (only used if no ezrt_header is given!)
            overwrite_info: Flag if info.json should be created or overwritten (ignored for EZRT_RAW format)

        Raises:
            NotImplementedError: if non supported image format is requested
            ValueError: if input image has wrong shape
        """
        image_dimension = len(image.shape)
        if not (image_dimension == 2 or (image_dimension == 3 and image.shape[0] == 1)):
            raise ValueError(f'only 2D images supported (is: {len(image.shape)}D)')

        if image_dimension == 3:
            image = image[0, :, :]

        savefolder = Path(savefolder)
        if not savefolder.is_dir():
            raise ValueError(f'given save folder path is not a valid directory ("{savefolder}")')

        filename = filename.strip()
        if imageformat == ImageFormat.AUTO:
            imageformat = ImageIO.autodetect_image_format(filename)

        image_id = ImageIO.remove_file_suffix(filename, imageformat)
        filename = ImageIO.add_file_suffix(filename, imageformat)
        savepath = savefolder / filename

        # save image in specified format
        if imageformat == ImageFormat.RAW_EZRT:
            header = None
            if ezrt_header is not None:
                header = ezrt_header
                header.image_width = image.shape[1]
                header.image_height = image.shape[0]
            elif metadata is not None:
                header = EzrtHeader(
                    image.shape[1], image.shape[0], image.dtype.itemsize * 8, number_of_images=1, metadata=metadata
                )
            py2raw(image, savepath, input_header=header)
        elif imageformat == ImageFormat.TIFF:
            PIL.Image.fromarray(image).save(savepath)
        elif imageformat == ImageFormat.PNG:
            pil_image = PIL.Image.new('I', (image.shape[1], image.shape[0]))
            pil_image.frombytes(image.tobytes(), 'raw', "I;16")
            pil_image.save(savepath)
        elif imageformat == ImageFormat.BMP:
            if image.dtype == np.uint16:
                PIL.Image.fromarray((image // 256).astype(np.uint8)).save(savepath)
            else:
                PIL.Image.fromarray(image.astype(np.uint8)).save(savepath)
        elif imageformat == ImageFormat.RAW_BINARY:
            image.tofile(str(savepath))

        if ezrt_header is None and metadata is None or imageformat == ImageFormat.RAW_EZRT or savefolder == '':
            return

        if ezrt_header is not None:
            metadata = ezrt_header.metadata

        # save metadata in info.json
        infofilepath = savefolder / 'info.json'
        if overwrite_info:
            # open with a+, so a file is created if none is found
            with open(infofilepath, 'a+', encoding='utf8') as file:
                # goto beginning of file and read it if not empty
                file.seek(0)
                info_dict = json.load(file) if os.fstat(file.fileno()).st_size > 0 else {}
                # delete old content
                file.seek(0)
                file.truncate()
                # write new content
                info_dict[image_id] = metadata
                json.dump(info_dict, file, indent=4)
        else:
            if not infofilepath.is_file():
                raise FileNotFoundError(f'info.json could not be found (searched at {infofilepath})')
            with open(infofilepath, 'a+', encoding='utf8') as file:
                file.write(f'"{image_id}": ')
                json.dump(metadata, file, indent=4)
                file.write(',\n')

    def save(
        self,
        image: np.ndarray,
        filename: str,
        savefolder: Path | str = '',
        metadata: dict | None = None,
        overwrite_info: bool = False,
        ezrt_header: EzrtHeader | None = None,
    ):
        """
        Save image (2D numpy array) with image format used in constructor. If a metadata dict is provided it either
        saved into an info JSON file or in case of the image format 'RAW_EZRT' saved into the EZRT header.

        Args:
            image: 2D numpy array
            filename: filename to save to (with or witout file extension)
            savefolder: folder to save to, defaults to None
            ezrt_header: header to use (has priority over metadata!); width & height fields are extracted from image
            metadata: dict with image metadata, defaults to None (only used if no ezrt_header is given!)
            overwrite_info: Flag if info.json should be overwritten (ignored for EZRT_RAW format)

        Raises:
            NotImplementedError: if non supported image format is requested
            ValueError: if input image has wrong shape
        """
        ImageSaver.save_image(image, filename, self.imageformat, savefolder, ezrt_header, metadata, overwrite_info)


class ImageDeleter(ImageIO):
    """This class allows for deleting different formats (stated by ImageFormat) of images."""

    def __init__(self, imageformat: ImageFormat = ImageFormat.AUTO):
        """
        Construct new ImageDeleter with imageformat.

        Args:
            imageformat: target image format for deletion (see ImageFormat for options), defaults to AUTO
        """
        super().__init__(imageformat)

    @staticmethod
    def delete_image(
        filename: str,
        imageformat: ImageFormat = ImageFormat.AUTO,
        deletefolder: Path | str = '.',
        has_metadata: bool = False,
    ):
        """
        Delete image (2D numpy array) with given image format. Optionally its metadata json can also be deleted
        (if applicable).

        Args:
            filename: filename to delete (with or witout file extension)
            imageformat: target image format for saving (see ImageFormat for options), defaults to AUTO
            deletefolder: folder to delete from, defaults to CWD
            has_metadata: has image metadata to delete, defaults to False
        """
        deletefolder = Path(deletefolder)
        if not deletefolder.is_dir():
            raise ValueError(f'given delete folder path is not a valid directory ("{deletefolder}")')

        filename = filename.strip()
        if imageformat == ImageFormat.AUTO:
            imageformat = ImageIO.autodetect_image_format(filename)

        image_id = ImageIO.remove_file_suffix(filename, imageformat)
        filename = ImageIO.add_file_suffix(filename, imageformat)
        image_path = deletefolder / filename

        if imageformat != ImageFormat.RAW_EZRT and has_metadata:
            infofilepath = deletefolder / 'info.json'
            if infofilepath.is_file() and infofilepath.stat().st_size:
                with open(infofilepath, 'r+', encoding='utf8') as file:
                    info_dict = json.load(file)
                    if image_id in info_dict:
                        # delete old content
                        file.seek(0)
                        file.truncate()
                        # write new content
                        info_dict.pop(image_id)
                        json.dump(info_dict, file, indent=4)

        image_path.unlink()  # removes file

    def delete(self, filename: str, deletefolder: str = '', has_metadata: bool = False):
        """
        Delete image (2D numpy array) with image format used in constructor. Optionally its metadata json can also be
        deleted (if applicable).

        Args:
            filename: filename to delete (with or witout file extension)
            deletefolder: folder to delete from, defaults to ''
            has_metadata: has image metadata to delete, defaults to False
        """
        ImageDeleter.delete_image(filename, self.imageformat, deletefolder, has_metadata)


class ImageConverter(ImageIO):
    """This class allows for converting image files to different formats (stated by ImageFormat)."""

    def __init__(
        self, imageformat_in: ImageFormat = ImageFormat.AUTO, imageformat_out: ImageFormat = ImageFormat.RAW_EZRT
    ):
        """
        Construct new ImageConverter with input and output ImageFormat.

        Args:
            imageformat_in: target image format for input (see ImageFormat for options), defaults to AUTO
            imageformat_out: target image format for output (see ImageFormat for options), defaults to RAW_EZRT
        """
        super().__init__(imageformat_in)
        self.imageformat_out = imageformat_out

    @staticmethod
    def convert_image(
        filepath_in: Path | str,
        filepath_out: Path | str,
        imageformat_in: ImageFormat = ImageFormat.AUTO,
        imageformat_out: ImageFormat = ImageFormat.RAW_EZRT,
        dtype=np.uint16,
        load_metadata: bool = False,
        ezrt_header: EzrtHeader | None = None,
    ):
        """
        Convert image at path with input image format to another image with a different imageformat.

        Args:
            filepath_in: filepath of image to convert (with or witout file extension)
            filepath_out: filepath of converted image
            imageformat_in: target image format for original image (see ImageFormat for options), defaults to AUTO
            imageformat_out: target image format for converted image (see ImageFormat for options), defaults to AUTO
            dtype: numpy dtype as which the image is loaded
            load_metadata: flag if metadata should be loaded (if not an empty dict is returned)
            ezrt_header: header to use (has priority over metadata!); width & height fields are extracted from image
        """
        filepath_in = Path(filepath_in)
        filepath_out = Path(filepath_out)
        if imageformat_in == ImageFormat.AUTO:
            imageformat_in = ImageIO.autodetect_image_format(filepath_in)

        if imageformat_out == imageformat_in:
            return

        image, _, header = ImageLoader.load_image(filepath_in, imageformat_in, dtype, load_metadata)
        if ezrt_header is not None:
            header = ezrt_header
        ImageSaver.save_image(image, filepath_out.name, imageformat_out, filepath_out.parent, ezrt_header=header)

    def convert(
        self,
        filepath_in: Path | str,
        filepath_out: Path | str,
        dtype=np.uint16,
        load_metadata: bool = False,
        ezrt_header: EzrtHeader | None = None,
    ):
        """
        Convert image at path with input image format to another image with a different imageformat. ImageFormat are as
        defined in constructor.

        Args:
            filepath_in: filepath of image to convert (with or witout file extension)
            filepath_out: filepath of converted image
            dtype: numpy dtype as which the image is loaded
            load_metadata: flag if metadata should be loaded (if not an empty dict is returned)
            ezrt_header: to use for metadata or as header (has priority over metadata!)
        """
        ImageConverter.convert_image(
            filepath_in,
            filepath_out,
            self.imageformat,
            self.imageformat_out,
            dtype=dtype,
            load_metadata=load_metadata,
            ezrt_header=ezrt_header,
        )


class ImageSaveQueue(threading.Thread):
    """
    Queue based image save thread. If a metadata dict is provided it either saved into an
    info json file or in case of the image format 'RAW_EZRT' saved into the EZRT header.
    """

    def __init__(
        self,
        savefolder: Path | str = '',
        save_metadata: bool = True,
        maxqueuesize: int = 50,
        imageformat: ImageFormat = ImageFormat.TIFF,
        imagesaver: ImageSaver | None = None,
    ):
        """
        Construct new ImageSaveQueue.

        Args:
            savefolder: folder to save to, defaults to ''
            save_metadata: state if metadata should be saved, defaults to True
            maxqueuesize: max size of save queue, defaults to 50
            imageformat: target image format for saving (see ImageFormat for options), defaults to TIFF
            imagesaver: ImageSaver instance to use (if None, instance is created), defaults to None
        """
        super().__init__()
        if imageformat == ImageFormat.AUTO:
            raise ValueError('AUTO mode not available for save queue')
        if maxqueuesize <= 0:
            raise ValueError(f'max queue size must be > 0 (is: {maxqueuesize})')

        # if no image saver is specified, use default
        if imagesaver is None:
            self._imagesaver = ImageSaver(imageformat)
        else:
            self._imagesaver = imagesaver
            self._imagesaver.imageformat = imageformat

        self.savefolder = Path(savefolder)
        self.is_ready = threading.Event()

        self._queue = queue.Queue(maxsize=maxqueuesize)
        self._save_metadata = save_metadata
        self._stop_requested = False
        self.error_event = threading.Event()
        self.error = None

        if self._save_metadata and self._imagesaver.imageformat != ImageFormat.RAW_EZRT:
            if not self.savefolder.is_dir():
                raise ValueError(f'save folder directory not found ("{savefolder}")')
            self._infofilepath = os.path.join(self.savefolder, 'info.json')
            with open(self._infofilepath, 'w', encoding='utf8') as file:
                file.write('{\n')

        self.start()

    def clear_error(self):
        """Clear errors of Thread."""
        self.error_event.clear()
        self.error = None

    def put(self, image: np.ndarray, filename: str, metadata: dict | None = None):
        """
        Put image and corresponding metadata to the save queue. Image is saved under the given filename.

        Args:
            image: input image to save (2D numpy array)
            filename: name of saved file
            metadata: dict with image metadata, defaults to None

        Raises:
            OSError: if the save queue is full
        """
        if self._stop_requested:
            return
        try:
            self._queue.put((image, filename, metadata), timeout=5.0)
        except queue.Full:
            raise OSError(f'image write buffer full ({self._queue.qsize()} / {self._queue.maxsize})')

    def run(self):
        """Overwritten run function of Thread. Is executed when "start()" is called."""
        self.is_ready.set()

        while True:
            try:
                image, filename, metadata = self._queue.get()
                # if stop is requested empty the queue
                if image is None:
                    self._queue.task_done()
                    while not self._queue.empty():
                        try:
                            self._queue.get(block=False)
                        except queue.Empty:
                            continue
                        self._queue.task_done()
                    break

                if not self._save_metadata:
                    metadata = None
                self._imagesaver.save(image, filename, self.savefolder, metadata)
                self._queue.task_done()
            except Exception as e:
                self.error = e
                self.error_event.set()
                try:
                    self._queue.task_done()
                except ValueError:
                    # thrown if queue is already empty
                    # as it cannot be determined if the queue was already empty when the error occured,
                    # this exception is ignored
                    pass

    def finish(self):
        """Stops save procedure and make thread ready to be joined."""
        self._stop_requested = True
        self._queue.put((None, None, None), timeout=5.0)
        if self.is_alive():
            # wait for queue to be empty
            self._queue.join()
            if self._save_metadata and self._imagesaver.imageformat != ImageFormat.RAW_EZRT:
                with open(self._infofilepath, 'a+', encoding='utf8') as file:
                    file.write('"default": {}\n}')
