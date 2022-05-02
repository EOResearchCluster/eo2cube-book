#!/usr/bin/env python
# coding: utf-8

# <img align="right" src="../../additional_data/banner_siegel.png" style="width:1000px;">

# # Xarray-I: Data Structure 
# 
# * [**Sign up to the JupyterHub**](https://www.phenocube.org/) to run this notebook interactively from your browser
# * **Compatibility:** Notebook currently compatible with the Open Data Cube environments of the University of Wuerzburg
# * **Prerequisites**: There is no prerequisite learning required.
# 

# ## Background
# 
# In the previous notebook, we experienced that the data we wanna access are loaded in a form called **`xarray.dataset`**. This is the form in which earth observation data are usually stored in a datacube.
# 
# **`xarray`** is an open source project and Python package which offers a toolkit for working with ***multi-dimensional arrays*** of data. **`xarray.dataset`** is an in-memory representation of a netCDF (network Common Data Form) file. Understanding the structure of a **`xarray.dataset`** is the key to enable us work with these data. Thus, in this notebook, we are mainly dedicated to helping users of our datacube understand its data structure.
# 
# Firstly let's come to the end stage of the previous notebook, where we have loaded a data product. The data product "s2_l2a_bavaria" is used as example in this notebook.

# ## Description
# 
# The following topics are convered in this notebook:
# * **What is inside a `xrray.dataset` (the structure)?**
# * **(Basic) Subset Dataset / DataArray**
# * **Reshape a Dataset**

# In[1]:


import datacube
import pandas as pd
from odc.ui import DcViewer 
from odc.ui import with_ui_cbk
import xarray as xr
import matplotlib.pyplot as plt

# Set config for displaying tables nicely
# !! USEFUL !! otherwise parts of longer infos won't be displayed in tables
pd.set_option("display.max_colwidth", 200)
pd.set_option("display.max_rows", None)

# Connect to DataCube
# argument "app" --- user defined name for a session (e.g. choose one matching the purpose of this notebook)
dc = datacube.Datacube(app = "nb_understand_ndArrays")


# In[ ]:


# Load Data Product
ds = dc.load(product= "s2_l2a",
            x= [12.94 ,13.05],
             y= [53.88,53.94],
             output_crs = "EPSG:32632",
             time = ("2020-10-01", "2020-12-31"),
             measurements= ["blue", "green", "red","nir"],
             resolution = (-10,10),
             group_by = "solar_day",
             progress_cbk=with_ui_cbk())

ds


# In[ ]:


#da = ds.to_array().rename({"variable":"band"})
#print(da)


# In[ ]:


#ds2 = da.to_dataset(dim="time")
#ds2


# ## **What is inside a `xarray.dataset`?**
# The figure below is a diagramm depicting the structure of the **`xarray.dataset`** we've just loaded. Combined with the diagramm, we hope you may better interpret the texts below explaining the data strucutre of a **`xarray.dataset`**.
# 
# ![xarray data structure](https://live.staticflickr.com/65535/51083605166_70dd29baa8_k.jpg)

# As read from the output block, this dataset has three ***Data Variables*** , "blue", "green" and "red" (shown with colors in the diagramm), referring to individual spectral band.
# 
# Each data variable can be regarded as a **multi-dimensional *Data Array*** of same structure; in this case, it is a **three-dimensional array** (shown as 3D Cube in the diagramm) where `time`, `x` and `y` are its ***Dimensions*** (shown as axis along each cube in the diagramm).
# 
# In this dataset, there are 35 ***Coordinates*** under `time` dimension, which means there are 35 time steps along the `time` axis. There are 164 coordinates under `x` dimension and 82 coordinates under `y` dimension, indicating that there are 164 pixels along `x` axis and 82 pixels along `y` axis.
# 
# As for the term ***Dataset***, it is like a *Container* holding all the multi-dimensional arrays of same structure (shown as the red-lined box holding all 3D Cubes in the diagramm).
# 
# So this instance dataset has a spatial extent of 164 by 82 pixels at given lon/lat locations, spans over 35 time stamps and 3 spectral band.
# 
# **In summary, *`xarray.dataset`* is substantially a container for high-dimensional *`DataArray`* with common attributes (e.g. crs) attached**, :
# * **Data Variables (`values`)**: **it's generally the first/highest dimension to subset from a high dimensional array.** Each `data variable` contains a multi-dimensional array of all other dimensions.
# * **Dimensions (`dims`)**: other dimensions arranged in hierachical order *(e.g. 'time', 'y', 'x')*.
# * **Coordinates (`coords`)**: Coordinates along each `Dimension` *(e.g. timesteps along 'time' dimension, latitudes along 'y' dimension, longitudes along 'x' dimension)*
# * **Attributes (`attrs`)**: A dictionary(`dict`) containing Metadata.

# Now let's deconstruct the dataset we have just loaded a bit further to have things more clarified!:D

# * **To check existing dimensions of a dataset**

# In[ ]:


ds.dims


# * **To check the coordinates of a dataset**

# In[ ]:


ds.coords#['time']


# * **To check all coordinates along a specific dimension**
# <br>
# <img src=https://live.staticflickr.com/65535/51115452191_ec160d4514_o.png, width="450">

# In[ ]:


ds.time
# OR
#ds.coords['time']


# * **To check attributes of the dataset**

# In[ ]:


ds.attrs


# ## **Subset Dataset / DataArray**
# 
# * **To select all data of "blue" band**
# <br>
# <img src=https://live.staticflickr.com/65535/51115092614_366cb774a8_o.png, width="350">

# In[ ]:


ds.blue
# OR
#ds['blue']


# In[ ]:


# Only print pixel values
ds.blue.values


# * **To select blue band data at the first time stamp**
# <br>
# <img src=https://live.staticflickr.com/65535/51116131265_8464728bc1_o.png, width="350">

# In[ ]:


ds.blue[0]


# * **To select blue band data at the first time stamp while the latitude is the largest in the defined spatial extent**
# <img src=https://live.staticflickr.com/65535/51115337046_aeb75d0d03_o.png, width="350">

# In[ ]:


ds.blue[0][0]


# * **To select the upper-left corner pixel**
# <br>
# <img src=https://live.staticflickr.com/65535/51116131235_b0cca9589f_o.png, width="350">

# In[ ]:


ds.blue[0][0][0]


# ### **subset dataset with `isel` vs. `sel`**
# * Use `isel` when subsetting with **index**
# * Use `sel` when subsetting with **labels**

# * **To select data of all spectral bands at the first time stamp**
# <br>
# <img src=https://live.staticflickr.com/65535/51114879732_7d62db54f4_o.png, width="750">

# In[ ]:


ds.isel(time=[0])


# * **To select data of all spectral bands of year 2020** 
# <br>
# <img src=https://live.staticflickr.com/65535/51116281070_75f1b46a9c_o.png, width="750">

# In[ ]:


ds.sel(time='2020-12')
#print(ds.sel(time='2019'))


# ***Tip: More about indexing and sebsetting Dataset or DataArray is presented in the [Notebook_05](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/05_xarrayII.ipynb).***

# ## **Reshape Dataset**
# 
# * **Convert the Dataset (subset to 2019) to a *4-dimension* DataArray**

# In[ ]:


da = ds.sel(time='2020-12').to_array().rename({"variable":"band"})
da


# * **Convert the *4-dimension* DataArray back to a Dataset by setting the "time" as DataVariable (reshaped)**
# 
# ![ds_reshaped](https://live.staticflickr.com/65535/51151694092_ca550152d6_o.png)

# In[ ]:


ds_reshp = da.to_dataset(dim="time")
print(ds_reshp)


# ## Recommended next steps
# 
# If you now understand the **data structure** of `xarray.dataset` and **basic indexing** methods illustrated in this notebook, you are ready to move on to the next notebook where you will learn more about **advanced indexing** and calculating some **basic statistical parameters** of the n-dimensional arrays!:D
# 
# In case you are gaining interest in exploring the world of **xarrays**, you may lay yourself into the [Xarray user guide](http://xarray.pydata.org/en/stable/index.html).
# 
# <br>
# To continue working through the notebooks in this beginner's guide, the following notebooks are designed to be worked through in the following order:
# 
# 1. [Jupyter Notebooks](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/01_jupyter_introduction.ipynb)
# 2. [eo2cube](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/02_eo2cube_introduction.ipynb)
# 3. [Loading Data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/03_data_lookup_and_loading.ipynb)
# 4. ***Xarray I: Data Structure (this notebook)***
# 5. [Xarray II: Index and Statistics](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/05_xarrayII.ipynb)
# 6. [Plotting data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/06_plotting_basics.ipynb)
# 7. [Spatial analysis](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/07_basic_analysis.ipynb)
# 8. [Parallel processing with Dask](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/08_parallel_processing_with_dask.ipynb)
# 
# The additional notebooks are designed for users to build up both basic and advanced skills which are not covered by the beginner's guide. Self-motivated users can go through them according to their own needs. They act as complements for the guide:
# <br>
# 
# 1. [Python's file management tools](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/I_file_management.ipynb)
# 2. [Image Processing basics using NumPy and Matplotlib](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/II_numpy_image_processing.ipynb)
# 3. [Vector Processing](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/III_process_vector_data.ipynb)
# 4. [Advanced Plotting](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/IV_advanced_plotting.ipynb)

# ***
# ## Additional information
# 
# This notebook is for the usage of Jupyter Notebook of the [Department of Remote Sensing](http://remote-sensing.org/), [University of Wuerzburg](https://www.uni-wuerzburg.de/startseite/).
# 
# **License:** The code in this notebook is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). 
# 
# 
# **Contact:** If you would like to report an issue with this notebook, you can file one on [Github](https://github.com).
# 
# **Last modified:** April 2021
