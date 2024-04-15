# CTMT Python Tools

The CTMT Python Tools contain commonly used functions for working with Python @ EZRT, such as:

- common Exceptions and useful types (Range, ROI)
- simple loading and saving .raw & .rek data with full EZRT header, datatype and compression support
- loading and queued saving of image data (supported formats: png, bmp, raw (binary), raw (ezrt), png, tiff)
- loading and saving of VTI volumes
- saving of projection folder and volumes as .gif
- projection folder analysis tools
- batch manipulation of files in same folder (data & header)
- parsing of Volex metadata XML & Werth PRM file (partial)
  
## Example Usage

### Use the EzrtHeader class

```python
from PythonTools.ezrt_header import ACQUISITIONGEOMETRY, EzrtHeader

# new EZRT header for 10x8 16-bit projections via helix
ezrt_header = EzrtHeader(10, 8, 16)
ezrt_header.voltage_in_kv = 100.0
ezrt_header.current_in_ua = 1000.0
ezrt_header.acquisition_geometry = ACQUISITIONGEOMETRY.HELIX_CT

# new EZRT header to / from buffer or file
buffer = ezrt_header.tobytes()
ezrt_header.tofile(path_to_file)
ezrt_header = EzrtHeader.frombuffer(buffer)
ezrt_header = EzrtHeader.fromfile(path_to_file)

# add header to image data or file
ezrt_header.add_to_buffer(buffer)
ezrt_header.add_to_file(path_to_file)

# overwrite existing EZRT header of file (validates old header before)
ezrt_header.add_to_file(path_to_file, overwrite_data=True)

# force overwriting data of file
ezrt_header.add_to_file(path_to_file, overwrite_data=True, validate_if_ezrt_header=False)

# easily create new header for normal circular CT
header = EzrtHeader.create_for_conventional_3D_ct(100, 50, 16, number_projection_angles=1200, fdd_in_mm=100.0,
                                                  fod_in_mm=10.0, detector_width_in_um=1000000,
                                                  detector_height_in_um=1000000)
```

### Simple loading and saving of .rek or .raw files

```python
import numpy as np

from PythonTools.py2raw import py2raw
from PythonTools.raw2py import raw2py
from PythonTools.rek2py import rek2py
from PythonTools.py2rek import py2rek

# save numpy array as .rek file with minimal Ezrt header
volume_data = np.ones((10, 8, 6), dtype=np.uint16)
py2rek(volume_data, rek_file_path)

# optional: use dedicated EzrtHeader instance as header
ezrt_header = EzrtHeader(10, 8, 16, 6)
ezrt_header.voltage_in_kv = 100.0
py2rek(volume_data, rek_file_path, input_header=ezrt_header)

# load .rek again
header, loaded_volume_data = rek2py(rek_file_path)

# saving and loading raw files is similar
projection_data = np.ones((10, 8))
py2raw(projection_data, raw_file_path)
header, loaded_projection_data = raw2py(raw_file_path)
```

### Image IO

```python
import numpy as np

from PythonTools.imageio import ImageFormat, ImageLoader, ImageSaver, ImageSaveQueue

# loader which loads exclusively .raws (similar to raw2py); header is loaded as metadata dict
imageloader = ImageLoader(imageformat=ImageFormat.RAW_EZRT)
image, metadata, header = imageloader.load(raw_file_path)

# loader tries to find out file format (is also default)
# if file is a Ezrt raw, the metadata comes from the header; otherwise a dedicated info.json can used
imageloader = ImageLoader(imageformat=ImageFormat.AUTO)
# filepath can be path to png, bmp, raw (ezrt), png, tiff (raw binary cannot be detected)
image, metadata, header = imageloader.load(file_path)

# saver tries to find out file format from suffix (is default)
projection_data = np.ones((10, 8))
metadata = {'image_width': 1, 'image_height': 1, 'measurement_id': 2}
imagesaver = ImageSaver()
imagesaver.save(projection_data, raw_file_path, metadata=metadata)

# save images asynchronously with metadata (in this case as TIF, metadata saved as JSON)
image_save_queue = ImageSaveQueue(save_folder_path, imageformat=ImageFormat.TIFF)
image_save_queue.put(projection_data, 'project_file_name_1', metadata)
image_save_queue.put(projection_data, 'project_file_name_2', metadata)
image_save_queue.finish()
```

More info about the metadata dict can be found [here](https://git01.iis.fhg.de/ctmt/ct-control/pyct#known-image-metadata-keywords).

### Range class

```python
from PythonTools.common_types import Range

Range.value_between_limits(10, 9, 11) # True
Range.value_between_limits(8, 9, 11)  # False

range = Range(0, 2)
range.in_range(1)  # True
range.in_range(3)  # False
```

### Batch header manipulation and image conversion

```python
import numpy as np

from PythonTools.batch_header_manipulator import BatchHeaderManipulator
from PythonTools.batch_header_manipulator import BatchImageConverter
from PythonTools.ezrt_header import EzrtHeader

files_with_headers = BatchHeaderManipulator(path_to_folder)

# Change header information and save them
print('old voltage [kV]:', files_with_headers.headers[0].voltage_in_kv)  # e.g. old voltage [kV]: 100.0
files_with_headers.change_attribute_all('voltage_in_kv', 125.0, save_headers=True)

# Load new headers and print them
print('new voltage [kV]:', files_with_headers.headers[0].voltage_in_kv)  # new voltage [kV]: 125.0

# create header for circular CT - image size is detected automatically
header = EzrtHeader.create_for_conventional_3D_ct(0, 0, 16, number_projection_angles=1200, fdd_in_mm=100.0,
                                                  fod_in_mm=10.0, detector_width_in_um=100000,
                                                  detector_height_in_um=100000)

# load tifs in folder and save them with the given header as .raw
BatchImageConverter(relative_path_to_data, '*.tif', ezrt_header=header).save()
```

### Apply custom processing to header and projections

```python
import numpy as np

from PythonTools.batch_header_manipulator import BatchProjectionManipulator
from PythonTools.ezrt_header import EzrtHeader

# option 1 (default): projection image data not loaded, but iterated; changes not persistent unless the save flag is
# used or the data is processed in the iterator. Has lower memory footprint, higher CPU & I/O load.
bhm = BatchProjectionManipulator('test/test_data/raw_series/')
# option 2: projection image data loaded to RAM. Has high memory footprint, lower CPU & I/O load.
bhm = BatchProjectionManipulator('test/test_data/raw_series/', load_projection_data=True)

def some_function(header: EzrtHeader, image: np.ndarray, new_i0: int, add_to_img: int = 100):
    """
    Must be of prototype:
       func(header: EzrtHeader, image: np.ndarray, *args, **kwargs) -> EzrtHeader, np.ndarray
    """
    header.inull_value = new_i0
    image += add_to_img
    return header, image

# process all data
bhm.execute_function_all(some_function, args=(10,), kwargs={'add_to_img': 200})
# process all data and save
bhm.execute_function_all(some_function, args=(10,), kwargs={'add_to_img': 200}, save=True)
# process only data at certain index (int this case: 1)
bhm.execute_function_by_index(1, some_function, args=(10,), kwargs={'add_to_img': 200})
# iterate over data
for header, image in bhm.iterate_function(some_function, args=(10,), kwargs={'add_to_img': 200}):
    # do something with data
```

## Dependencies

The default install via pip will **only install minimal dependencies** (e.g. numpy) to keep the module lightweight!
If the full feature range is needed, use the requirements.txt file via `pip install -r requirements.txt`.

If only specific functionality in addition to the default install is needed, consult the following list:

| Functionality                       | Needed Package(s) |                               Command                               |
| ----------------------------------- | :---------------: | :-----------------------------------------------------------------: |
| rek lz4 compression support         |        lz4        |                          `pip install lz4`                          |
| vti support                         |        vtk        |                          `pip install vtk`                          |
| projection scaling                  |      opencv       |            `pip install opencv-contrib-python-headless`             |
| dark/flat (=offset/gain) correction |  ctmt-algorithms  | see [here](https://git01.iis.fhg.de/ctmt/utilities/ctmt-algorithms) |
| simple beam hardening correction    |  ctmt-algorithms  | see [here](https://git01.iis.fhg.de/ctmt/utilities/ctmt-algorithms) |
