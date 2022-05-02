#!/usr/bin/env python
# coding: utf-8

# <img align="right" src="../../additional_data/banner_siegel.png" style="width:1000px;">

# # Advanced Xarray
# 
# * [**Sign up to the JupyterHub**](https://www.phenocube.org/) to run this notebook interactively from your browser
# * **Compatibility:** Notebook currently compatible with the Open Data Cube environments of the University of Wuerzburg
# * **Products used**: `Sentinel-2`
# * **Prerequisites**:  Users of this notebook should have a basic understanding of:
#     * How to run a [Jupyter notebook](01_jupyter_introduction.ipynb)
#     * The basic structure of the eo2cube [satellite datasets](02_eo2cube.ipynb)
#     * How to browse through the available [products and measurements](03_products_and_measurements.ipynb) of the eo2cube datacube 
#     * How to [load data from the eo2cube datacube](04_loading_data_and_basic_xarray.ipynb) 

# ## Background
# 
# The Python library `xarray` simplifies working with labelled multi-dimension arrays. The library introduces labels in the forms of dimensions, coordinates and attributes on top of `numpy` arrays. This structure allows easier and more effective handling of remote sensing raster data in a Python environment. Therefore, it is essential to fully understand the structure of an `xarray`. A first introduction into the usage of `xarray` within the eo2cube environment was given in ["04_loading_data_and_basic_xarray"](04_loading_data_and_basic_xarray.ipynb). This notebook builds on this gained knowledge and attempts to give a deeper understanding of the `xarray` data structure of raster data. If you are interested in learning more about the structures of the original `xarray`, have a look at this [**"introduction to xarray" notebook**](intro_to_xarray.ipynb) within the "intro_to_python" directory.
# To get more information about the `xarray` package, visit the [offical documentation website](http://xarray.pydata.org/en/stable/).
# 
# ## Description
# 
# This notebook introduces users to the `xarray` library within the datacube environment. It aims to deepen the understanding of the `xarray` structure as a container for remote sensing raster data. Also it introduces useful `xarray` functions to effectivly work with raster data in the eo2cube environment. Within this notebook the following topics are covered:
# 
# * Application of built-in `xarray` functions for analyzing raster data
# 
# ***

# ## Setting up
# ### Load packages
# 
# The `datacube` package is required to query the eo2cube datacube database and load the requested data. The `with_ui_cbk` function from `odc.ui` enables a progress bar when loading large amounts of data. The `xarray` and `numpy` package are needed for the different methods and analysis steps within this notebook. 

# In[1]:


import datacube
from odc.ui import with_ui_cbk
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

dc = datacube.Datacube(app = "nb_understand_ndArrays")


# ### Datacube connection and load data
# 
# First we connect to the datacube and load an example dataset from the eo2cube.

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


# <a id='index_array3'></a>
# ## **Advanced Indexing**
# ### 1) Temporal Subset

# In the earlier tutorial we introduced `isel()`and `sel()` for indexing data. For both methods a **slicing** operator exists. If the function `slice()` is passed onto the index function, the dataset can be sliced. 
# The first example uses the slicing by position method to select the first five scenes in `data_1`. The start value is included and the stop value is excluded.
# 
# #### I. Using index number

# In[ ]:


#slice(0,5)
#ds.isel(time=slice(0,5)).time
#ds.isel(time = [0,1,2,3,4]).time


# In[ ]:


ds.isel(time=slice(0,5))


# This example uses the slicing by label method to select the scenes between "2020-01-02" and "2020-01-12". Note, that when using the `slice()` function with the `sel()` method, both start and stop value are included.
# 
# #### II. Using `datetime64` data

# In[ ]:


print(ds.sel(time=slice("2020-12-01","2020-12-25"))) 

#ds.sel(time=slice("2020-01-01", "2020-02-31")) # error
#ds.sel(time=slice("2018-01-01", "2018-01-31")) # wrong time frame


# In[ ]:


#ds.sel(time=slice("2020-01-01", "2020-01-31")).time


# #### III. Using other time dimensions
# 
# `xarray` also includes some useful features for the inspection of the time dimension. It allows to easily extract additional information from a dataset. The following code automatically groups the time dimension in seasons ("DJF", "MAM", JJA", "SON"). Since `ds` only contains scens from winter months, only the label "DJF" will appear. There are a lot of other `time` dimensions arguments, e.g. `month`, `week`, `weekday`, `dayofyear`.

# In[ ]:


#ds.time
#using special .dt accessor
#ds.time.dt


# In[ ]:


ds.time.dt.season


# It is also possible to extract the "day of year" for a time step.

# In[ ]:


ds.time.dt.dayofyear


# In[ ]:


ds.groupby('time.season').mean()


# ### 2) Spatial Subset
# It is possible to index and **slice within the x and y dimensions**. The following example selects the value for each band of the pixel in the second colum of the raster and the fifth row of the raster (`x=2,y=5`)

# In[ ]:


ds.isel(x=2, y=5)
#ds.isel(x=[0,1,2], y=5)


# ### 3) Combining Temporal and Spatial Subset
# 
# Again, this method can be combined with the `slice()` operator to do a spatial subset of the dataset based on the position of the pixels. If you know the actual coordinate (x,y) value (extent) of the spatial subset area, use the `sel()` function.
# Additionally, this subset can also be sliced in the time dimensions.
# 
# The following example subsets the `ds` by the spatial location of the pixels. Only the pixels from the first to the fifth column and the pixels from the first to the fifth row are included in the output. Also the scenes where filtered in the time dimension between the first and fifth time step.

# In[ ]:


ds2 = ds.isel(time=slice(0,5), x= slice(0,5), y=slice(0,5))
ds2

#ds2.time
#plt.scatter(ds2.x.values, ds2.y.values)


# ## **Data Manipulation & Statistics**
# 
# This notebook presents some basic built-in functions of the `xarray` library to manipulate and transform data in a `xarray.Dataset`. In this notebook only a fraction of the available `xarray` functions are presented. For a complete overview of all the available functions and tools of the `xarray` package please visit the [documentation website](http://xarray.pydata.org/en/stable/). The [notebook 07](07_basic_analysis.ipynb) will cover this topic with a focus on an application oriented remote sensing approach.
# 
# ###  1) Statistical Operation
# 
# The simple built-in functions allow the user to do simple calculations with a `xarray.Dataset`.
# The **basic math** built-in `xarray` functions are:
# * `min()`, `max()`
# * `mean()`, `median()`
# * `sum()`
# * `std()`
# 
# The following code demonstrates the easy use of the `max()` function to extract the maximum value of the red band in the `ds` dataset.

# In[ ]:


print(ds.red.max())


# To apply a function to every value of a specified dimension (e.g. to calculate the mean of every time step) the `dim` argument in the basic math function must be define with the dimension label.
# 
# This examples calculates the mean of the `red` band for each pixel (defined by the unique `x`, `y` combination) over every time step. The result is a data array which can be used for further time series visualization and analysis.

# In[ ]:


print(ds.red.mean(dim=["x", "y"]))

#ds.red.mean(dim=["x", "y"]).values
#plt.plot(ds.red.mean(dim=["x", "y"]).values)


# This examples works the other way around. It calculates the standard deviation of every pixel (`x`, `y`) over all timesteps of the dataset `ds`.

# In[ ]:


print(ds.red.std(dim="time"))


# Remember, to access the raw `numpy` array that stores the values of the resulting `xarray.DataArrays`, the suffix `.values` is needed. This allows you to work with the "actual" data values.

# In[ ]:


print(ds.blue.sum(dim=["x","y"]).values)
#plt.plot(ds.blue.sum(dim=["x","y"]).values)


# ### 2) Conditional Operation

# Using conditional operation can be very helpful when we need to analyse satellite scenes or pixels lies within our interests. The `where()` function provides the option to **mask** a `xarray.Dataset` based on a logical condition. By default, the function converts all values that match the condition to NaN values. This is extremly useful when applied in combination with a binary mask to mask your data to the desired values. The argument `other` let´s you define a subset value for all values that match the condition (default is `nan`). The argument `drop` drops all values which do not match with the condition.
# The following example masks the datatset `ds` to only the values which have a reflectance value of greater than 700 in the `red` band.

# In[ ]:


print(ds.where(ds.red > 700))
#print(ds.where(ds.red < 700))


# This code subsets all zeros in the red band of the dataset `ds` in the first time stamp with the new value -9999.

# In[ ]:


replace = ds.red.isel(time=0).where(ds.red != 0, other = -9999)
#replace.values.min()


# The implemented `xarray` function `isin()` allows to **test each value** of `xarray.Dataset` or `xarray.DataArray` whether it is in the elements defined within the function. It returns a boolean array which can be used as a mask.
# This example checks all the values of the `red` measurement if the value is in an array from 0 to 550.

# In[ ]:


mask_red = ds.red.isin(range(550))
print(mask_red)

#plt.imshow(mask_red) #error
#plt.imshow(mask_red.isel(time=3))


# The created mask can easily be combined with the `where()` function to filter the dataset based on the predefined mask. In this case the `ds` dataset is masked with previously defined mask `mask_red`, which was based on a logical test if values of the `red` band are within a certain range of values.

# In[ ]:


print(ds.where(mask_red)) #masking


# ### 3) Resampling
# Working with time series data, resampling is necessary if we want the data product aligns with the temporal window are interested in.

#  - **resample()**
# 
# The **`resample()` method** allows to summarise the `xarray.Dataset` to bigger or smaller chunks based on a dimension. It handels both upsampling and downsampling. The argument `time` needs to be defined like a datetime-like coordinate. In the following example we resample the `ds` dataset to a monthly time intervall (`time = "m"`) and than calculate the median value for every resample chunk. _(this process takes a little while to run)_

# In[ ]:


print(ds.resample(time='m').median())


#  - **groupby() method**
# 
# The **`groupby()` method** can also be used within the `xarray` library to *aggregate data over time*. Time aggregation arguments can be e.g. "time.year", "time.season", "time.month", "time.week", "time.day".
# The code below groups the `ds` dataset into two groups by year. Therefore, a new "dimension" `year` is created. Then the median for each `year` is calculated. _(this process takes a little while to run)_

# In[ ]:


print(ds.groupby("time.year").median(dim="time"))


# ### 4) Interpolation
# Interpolation is a common solution dealing with missing remote sensing data, either caused by coarse temporal resolution of the satellite, high cloud cover or bad quality of the scenes. For example, sometimes a scene of a specfic date is not available in the dataset. With the implemented `interp()` it is possible to **interpolate data** for predefined time steps. The function takes the next usable scene before and after the specified date and interpolates their values (default interpolation method is "linear") to build a new `xarray.Dataset`.
# 
# In this example, the `ds` dataset has missing scenes on the "2020-12-08". The `interp()` function builds a "new" scene based on an linear interpolation from the two measurments before and after the new time step.

# In[ ]:


print(ds.time)


# In[ ]:


ds_interp = ds.interp(time=["2020-12-08"])
print(ds_interp)


# The `merge()` function allows to **merge/join** `xarray.Datasets` or variables. By default the `merge()` function uses an "inner" join as merging operation. 
# In our example the interpolated `xarray.Dataset` created above is merged to the `ds` dataset by using the default `merge()` function.

# In[ ]:


print(ds.merge(ds_interp).time)


# The `xarray` package contains a variety of other useful functions in addition to those shown here. There is a function for almost every operation needed in data analysis. For more information about the `xarray` package visit the [documentation website](http://xarray.pydata.org/en/stable/) or work through the [notebook]() in the "intro_to_python" folder.
# 
# The `xarray.Datasets` in the eo2cube datacube environment are a useful and effective structure for handeling remote sensing raster data. In this notebook you learned the basic structure and application methods of `xarray.Datasets`and `xarray.DataArrays`. However, it is very useful to not only work with the "raw" datasets and values. Sometimes it is necessary to get a visual overview of the data. The next [notebook 06](06_plotting.ipynb) will cover how to plot `xarray` raster data nicely and efficient. This is a very useful application, as it is often more convenient to visualize the raster data.

# ## Recommended next steps
# 
# To continue working through the notebooks in this beginner's guide, the following notebooks are designed to be worked through in the following order:
# 
# 1. [Jupyter Notebooks](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/01_jupyter_introduction.ipynb)
# 2. [eo2cube](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/02_eo2cube_introduction.ipynb)
# 3. [Loading Data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/03_data_lookup_and_loading.ipynb)
# 4. [Xarray I: Data Structure](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/04_xarrayI_data_structure.ipynb)
# 5. ***Xarray II: Index and Statistics (this notebook)***
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
# 
# ## Additional information
# 
# <font size="2">This notebook for the usage in the Open Data Cube entities of the [Department of Remote Sensing](http://remote-sensing.org/), [University of Wuerzburg](https://www.uni-wuerzburg.de/startseite/), is adapted from [Geoscience Australia](https://github.com/GeoscienceAustralia/dea-notebooks), published using the Apache License, Version 2.0. Thanks! </font>
# 
# **License:** The code in this notebook is licensed under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0). 
# Digital Earth Australia data is licensed under the [Creative Commons by Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) license.
# 
# 
# **Contact:** If you would like to report an issue with this notebook, you can file one on [Github](https://github.com).
# 
# **Last modified:** February 2021
