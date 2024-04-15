## Quickstart
This section will show you the basic steps of using pyronn layers for projection based on an easy example. The source code of the example is in "pyronn_examles/example_parallel_2d.py", you can find other examples in folder "pyronn_examples".

First of all, we need a sinogram and the geometry of it.
```python
from pyronn.ct_reconstruction.geometry.geometry import Geometry
from pyronn.ct_reconstruction.helpers.trajectories.circular_trajectory import circular_trajectory_2d

volume_size = 256
volume_shape = [volume_size, volume_size]
volume_spacing = [1, 1]

# Detector Parameters:
detector_shape = [800]
detector_spacing = [1]

# Trajectory Parameters:
number_of_projections = 360
angular_range = 2 * np.pi

# create Geometry class
geometry = Geometry()
geometry.init_from_parameters(volume_shape=volume_shape,volume_spacing=volume_spacing,
                            detector_shape=detector_shape,detector_spacing=detector_spacing,
                            number_of_projections=number_of_projections,angular_range=angular_range,
                            trajectory=circular_trajectory_2d)
```
You must create a instance of `Geometry` to let the pyronn get this geometry information. [Click](#Geometry) to know more information about `Geometry`.

If you don't have a scanner, you can also use pyronn to do the simulation.
```python
from pyronn.ct_reconstruction.helpers.phantoms import shepp_logan
from pyronn.ct_reconstruction.layers.projection_2d import ParallelProjection2D

phantom = shepp_logan.shepp_logan_enhanced(volume_shape)
# Add required batch dimension
phantom = torch.tensor(np.expand_dims(phantom, axis=0).copy(),dtype=torch.float32).cuda()

# ------------------ Call Layers ------------------
sinogram = ParallelProjection2D().forward(phantom,**geometry)
```
You must make sure that the geometry for projection and reconstruction is absolutely the same.
`ParalleProjection2d().forward(phantom, **geometry)` will perform as a scanner.

To implement a FBP algorithm, we need to filter the sinogram first.
```python
import torch
from pyronn.ct_reconstruction.helpers.filters import filters

reco_filter = torch.tensor(filters.shepp_logan_2D(geometry.detector_shape, geometry.detector_spacing, geometry.number_of_projections)).cuda()
x = torch.fft.fft(sinogram,dim=-1,norm="ortho")

x = torch.multiply(x,reco_filter)
x = torch.fft.ifft(x,dim=-1,norm="ortho").real
```
Please be aware of the shape of your filter. In module `filters` you can find more filters we provide

After this, with only one line, you can get the reconstruction result.
```python
from pyronn.ct_reconstruction.layers.backprojection_2d import ParallelBackProjection2D

reco = ParallelBackProjection2D().forward(x.contiguous(), **geometry)

reco = reco.cpu().numpy()
```
Please be aware that in pyronn, projection and reconstruction are separated into two different class.
And don't forget to detach it from gpu.

## Geometry
The `Geometry` class can be initial from parameters, json files or EZRT files. The type of geometry(parallel beam, fan beam and cone beam) 
is depended on the trajectory you provide. 
The properties are saved in a dictionary named parameter_dict. Here's the properties of `Geometry`.

| Keys                      | Description                                                                                           |
|---------------------------|-------------------------------------------------------------------------------------------------------|
| volume_shape              | [volume_Z, volume_X, Volume_Y]                                                                        |
| volume_spacing            | spacing for each axis                                                                                 |
| volume_origin             | coordinate of the volume origin                                                                       |
| detector_shape            | [detector_height, detector_width                                                                      |
| detector_spacing          | spacing for detector                                                                                  |
| detector_origin           | coordinate of the detector center                                                                     |
| number_of_projections     | projection amount                                                                                     |
| angular_range             | can be a 2-elements list or a float value. If only one value is provide, the range will be [0, value] |
| sinogram_shape            | shape of the sinogram, will be calculate automatically                                                |
| source_detector_distance  | distance between source and detector, not pixel distance                                              |
| source_isocenter_distance | distance between source and iso-center, not pixel distance                                            |
| trajectory                | the result of the trajectory  calculation function                                                    |
| projection_multiplier     | will be calculated automatically                                                                      |
| step_size                 | sample step size, default value is 0.2                                                                |

The functions provide by  `Geometry`:

| functions           | Description                                        |
|---------------------|----------------------------------------------------|
| fan_angle           | get the trajectory angle values                    |
| cone_angle          | get the trajectory angle values                    |
| set_detector_shift  | shift the origin if necessary                      |
| set_volume_slice    | (this one is not working right now)                |
| set_angle_range     | modify the project angle                           |
| swap_axis           | set the direction of the rotation of the system    |
| slice_the_geometry  | divide the geometry into several smaller geometry  |



