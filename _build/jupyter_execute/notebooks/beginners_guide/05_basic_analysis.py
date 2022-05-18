#!/usr/bin/env python
# coding: utf-8

# <img align="right" src="images/banner_siegel.png" style="width:1000px;">

# # Basic Spatial Analysis

# ## Description
# 
# In this notebook, we would present our readers a sample workflow of spatial data processing using spatial vector data and datasets in DataCube. Our aim in this notebook is to get a time series of some remote sensing indices and plot them.
# 

# In[1]:


import datacube
import numpy as np
import pandas as pd
import geopandas as gpd
import rioxarray as rio
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import odc.algo

# Set config for displaying tables nicely
# !! USEFUL !! otherwise parts of longer infos won't be displayed in tables
pd.set_option("display.max_colwidth", 200)
pd.set_option("display.max_rows", None)

# Connect to DataCube
# argument "app" --- user defined name for a session (e.g. choose one matching the purpose of this notebook)
dc = datacube.Datacube()
from odc.ui import with_ui_cbk


# ### Load Datasets
# 
# Now, we load the data with `dc.load()` using the calculated x and y ranges.

# In[ ]:


dc.list_products()


# In[ ]:


product = "s2_l2a"
measurements = dc.list_measurements()
measurements.loc[product]


# ## Load Area of interest

# First of all we have will load our region of interest

# In[ ]:


sample_fields = gpd.read_file('../sample_data/sample_fields.shp')
sample_fields = sample_fields.to_crs("EPSG:4326")
sample_fields.explore()


# Next we extract the bounding box of our shapefile

# In[ ]:


x = sample_fields.total_bounds[[0,2]] # extract longitude extents
y = sample_fields.total_bounds[[1,3]] # extract latitude extents

print('longitude_extents ' + str(x))
print('latitude_extents ' + str(y))


# Now we are ready to load our Sentinel-2 datasets for our RoI

# In[ ]:


# Load Data
ds = dc.load(product= "s2_l2a",
                  x= x,
                  y= y,
                  time = ("2020-01-01", "2020-05-31"), # specifiy time_extent
                  output_crs = "EPSG:32632",
                  measurements = ["blue", "green", "red", "nir_1"],
                  resolution = (-10,10),
                  group_by = "solar_day", 
                  #data_coverage = 100,
                  progress_cbk=with_ui_cbk())# shows progress with loading bar
ds


# Let's have a look at the different images

# In[ ]:


from dea_tools.plotting import rgb

rgb(ds , index = [3,8,9,10,12,20,25,30], bands = ["nir_1", "green", "blue"])


# ### Calculate selected Remote Sensing Indices

# Let us now calculate the NDVI. When we look at our dataset again we can see that the red and the green band are stored in uint16. In order to calculate the NDVI properly we first have to convert these into float.

# In[ ]:


ds =  odc.algo.to_f32(ds)


# Now we can apply the function and write back the results to the xarray dataset

# In[ ]:


ds['ndvi'] = (ds.nir_1 - ds.red)/(ds.nir_1 + ds.red)
ds


# In[ ]:


ds.ndvi.isel(time=3).plot()


# At the end we can just aggregate the NDVI for each time step and create a time series plot

# In[ ]:


ds.ndvi.mean(['x', 'y']).plot.line('b-^', figsize=(11,4))


# ### Loading cloud free images

# In the example above we have seen that we have a lot of clouds in our Sentinel-2 scenes. In most cases we want to avoid cloud pixels in our analysis. In order to exclude clouds from our data beforehand we can use the load_ard function.

# In[ ]:


from deafrica_tools.datahandling import load_ard
ds = load_ard(dc=dc,
            products=['s2_l2a'],
            x= x,
            y= y,
            time = ("2020-01-01", "2020-12-31"), # specifiy time_extent
            output_crs = "EPSG:32632",
            measurements = ['red', 'green', 'blue', 'nir_1'],
            resolution = (-10,10),
            group_by = "solar_day",
            mask_pixel_quality=True,
            data_coverage = 100,
            min_gooddata=0.90,    
             )


# In[ ]:


rgb(ds , index = [3,8,9], bands = ["nir_1", "green", "blue"])


# This time we will use the calculate_indices function. This function allows us to calculate multiple predefined band indices.

# In[ ]:


from deafrica_tools.bandindices import calculate_indices

ds = calculate_indices(ds, index=['NDVI','EVI','SAVI'], collection='s2')


# In[ ]:


ds


# Now we can have a look at our cloud free NDVI time series

# In[ ]:


ds.NDVI.isel(time = [1,2,3,4,5,6]).plot(col='time', cmap='RdYlGn') 


# In[ ]:


ds.NDVI.median(['x', 'y']).plot.line('b-^', figsize=(11,4))


# In[ ]:


data_frame = pd.DataFrame({"time": ds.time.values})
data_frame = data_frame.set_index('time')
data_frame['NDVI'] = ds.NDVI.median(['x', 'y']).values
data_frame['EVI'] = ds.EVI.median(['x', 'y']).values
data_frame['SAVI'] = ds.SAVI.median(['x', 'y']).values
data_frame


# In[ ]:


# define figure style
sns.set_style('darkgrid')
sns.set_context("poster", font_scale = .7)

# plot
ax = data_frame.plot(figsize=[15,7], linewidth=1)


# ## Recommended next steps

# To continue working through the notebooks in this beginner's guide, the following notebooks are designed to be worked through in the following order:
# 
# 1. [Jupyter Notebooks](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/01_jupyter_introduction.ipynb)
# 2. [eo2cube](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/02_eo2cube_introduction.ipynb)
# 3. [Loading Data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/03_data_lookup_and_loading.ipynb)
# 4. [Xarray I: Data Structure](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/04_xarrayI_data_structure.ipynb)
# 5. [Xarray II: Index and Statistics](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/05_xarrayII.ipynb)
# 6. [Plotting data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/06_plotting_basics.ipynb)
# 7. ***Spatial analysis (this notebook)***
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
# **Last modified:** May 2021
