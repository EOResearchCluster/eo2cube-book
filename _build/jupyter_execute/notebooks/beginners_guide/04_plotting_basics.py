#!/usr/bin/env python
# coding: utf-8

# <img align="right" src="images/banner_siegel.png" style="width:1000px;">

# # Plotting data

# ## Description
# 
# This notebook introduces users plotting within the datacube environment. It aims to introduces useful options to effectivly visualize raster data in the eo2cube environment. Within this notebook the following topics are covered:
# 
# * Plotting `True Color Composite` and `False Color Composite`
# * Plotting `Histogram` to show frequency distributions
# * Creating `2D-pseudocolor plot` to illustrate spatial variance
# * Creating `Facet Plot` to visualize time series
# * `Masking` scene
# 
# ***

# ## Setting up
# ### Load packages

# In[1]:


import datacube
from odc.ui import with_ui_cbk #processing bar for loading data
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt #matplotlib is a plotting for creating static, animated, and interactive visualizations
import pandas as pd
import seaborn as sns
import hvplot.xarray
get_ipython().run_line_magic('matplotlib', 'inline')
#this line allows plotting within the JupyterLab

import holoviews as hv #holoviews allows interactive plotting
hv.extension('bokeh') #this line allows plotting with the Bokeh server


# In this script, we need to use two functions from a python script (.py) stored in this environment. 
# 
# To import the functions to the current script, we need a relative path to the file and import display_map, rgb (the name of the functions) from DEAPlotting (the name of the file). `sys.path.append()` is used to add a specific path to the python file. 

# In[ ]:


from dea_tools.plotting import display_map, rgb #this line allows us to use specific functions written in another script


# In this example, we will use `data` which contains scenes of the s2_l2a_bavaria product from December 2019 to Februray 2020.
# 
# ### Load Data

# In[ ]:


dc = datacube.Datacube(app = '06_plotting')


# In[ ]:


data = dc.load(product= "s2_l2a",
             x= [12.94 ,13.05],
             y= [53.88,53.94],
             output_crs = "EPSG:32632",
             time = ("2020-05-01", "2020-07-31"),
             measurements= ["blue", "green", "red","nir", "swir_1", "SCL"],
             resolution = (-10,10),
             group_by = "solar_day",
             progress_cbk=with_ui_cbk())

data


# Let's have a look of our data.

# In[ ]:


data


# ## **RGB Image**

# To have a first view of our data, we can use the function `rgb()` defined in our written script DEAPlotting. It can be found under the folder Scripts where we do the import. rgb( ) can be used to plot different bands in the Data Variables in the red, blue, and green channels (in this order). If we input all three bands accordingly into the channels, it is called a **true color composite**, otherwise it is plotted as a **false color composite**.
# 
# However, we have to pay attention that the function can only plot in two dimensions (longitude and latitude). Hence, we can only input data array from a single time stamp. Here, we plot only the first time stamp (time = [0]), with col="time" argument we define the collapse of time dimension. We can look for the band name under Data Variables of the data set.

# #### **1) True Color Composite**
# With True color composite we input all bands accordingly.

# In[ ]:


rgb(data.isel(time=[4]), bands=['red', 'green', 'blue'], col="time")


# #### **2) False Color Composite**
# Here we visualize Land/Water composite. You can also try out [different combinations](https://gsp.humboldt.edu/OLM/Courses/GSP_216_Online/lesson3-1/composites.html) which fit for different purposes.

# In[ ]:


rgb(data.isel(time=[4]), bands=['nir', 'swir_1', 'red'], col="time")


# ## **Histogram**
# Besides, we can look at distribution of pixel values by plotting a histogram (i.e. using plot() for a multi-temporal xarray dataset). We can see most of the pixel reflectances lie between 400 and 1000.

# In[ ]:


data.green.plot()
#data['coastal_aerosol'].plot(color='green')


# ## **Scatterplot**

# In[ ]:


data[['red','green']].isel(time=1).plot.scatter(x='red',y='green', color='navy')
plt.title("Correlation of Red and Green bands", fontsize=18)


# ## **2D pcolormesh**
# #### **1) Plotting Single Band**
# We can also directly plot single individual band using xarray functionality. Important to note that it only take one time stamp and one data variable by default. Here we plot coastal aerosol band with the plot function. A specific [colormap](https://matplotlib.org/stable/tutorials/colors/colormaps.html) can be added with the cmap argument and all ther functionality of matplotlib are also available. The argument robust can be used to remove outliners.

# In[ ]:


data.red.isel(time=[4]).plot(robust=True, cmap=plt.cm.plasma, figsize=(8,6))

plt.title("Red Band") #title
plt.tight_layout() #remove excessive space in layout
plt.show() #show plot


# #### **2) Facet Plot**
# We can plot facet plot with the col="time" argument to show all time stamps. Note that plotting too many time stamps at once is not recommanded.

# In[ ]:


#data.isel(time=[0,2,4,6,8,10]).green.plot()
data.isel(time=[0,4,5,7,9,11]).green.plot(robust=True, col="time", col_wrap=3)


# #### **3) Masking**
# We can also mask out area in the plot. The following code excludes the cloud area (scl = 9).

# <img align="left" src="scl.png" style="width:250px;">

# In[ ]:


# Combining masking in facet plot
data.isel(time=[0,4,5,7,9,11]).green.where(data.SCL != 9).plot(robust=True, col="time", col_wrap=3)


# #### **5) Interactive Layout**
# Also, interative call of different scene is possible to explore around the data.

# In[ ]:


from eo2cube_tools.plot import plot_band, plot_rgb

plot_band(data)
#plot_band(data[['red','green','blue']].resample(time='2W').mean())


# In[ ]:


plot_rgb(data)


# ## **Time Series Linechart**
# Xarray’s plotting capabilities are centered around DataArray objects, and its functionality is a thin wrapper around matplotlib. Hence, many Matplotlib functionalities, such as `plt.title()`, can be easily called. 
# 
# To produce time series plot, we can reduce the dimensions of longitude and latitude with `mean(dim=["longitude","latitude"])` so that we get a single value of the whole area for every single time stamps. The resulting array can be used to plot a linechart with `matplotlib.pyplot`(plt) framework.

# In[ ]:


masked = data.green.where(data.SCL != 9)
week_data = masked.median(dim=["x","y"]).resample(time='1w').mean()
ts_plot = week_data.plot(color="orangered", marker="d", markersize=8) #dimension reduction
ts_plot

plt.title("Temporal Dynamics of Green Band", fontsize=15) #define title with matplotlib
plt.ylabel("Reflectance") #labels
plt.xlabel("Date")
plt.tight_layout() #remove excessive space in layout
plt.show() #display plot


# Additional arguments can be passed directly to the matplotlib function. We can, for example, also plot histogram with the data array.

# ## **Using Pandas and Seaborn**
# In the plotting basics, we have learnt how to create graphics using xarray and pyplot. Yet, we can also utilize pandas and seaborn library with their more developed tools to improve the visuals of our plot. It requires more code but meanwhile gives more flexibility for plot customization.

# In[ ]:


#data.to_dataframe()


# In[ ]:


df2 = data[["green","swir_1"]].mean(dim=["x","y"]).to_dataframe() #convert to pandas
df2.head()


# In[ ]:


df2 = df2.drop(['spatial_ref'], axis=1) #delete unneeded columns
df2.head()


# In[ ]:


ax3 = sns.pairplot(df2[["green","swir_1"]]) #pairplot
plt.suptitle("Correlation between SWIR and Green") #main title
plt.tight_layout()
plt.show()


# In[ ]:


ax4 = sns.violinplot(data=df2, orient='h') #violin plot

ax4.set_yticks(range(2)) #needed to generate two y-tick labels
ax4.set_yticklabels(['Green','SWIR 1']) #List of y-tick labels


# ## Recommended next steps
# 
# To continue with the beginner's guide, the following notebooks are designed to be worked through in the following order:
# 
# 1. [Jupyter Notebooks](01_jupyter_introduction.ipynb)
# 2. [eo2cube](02_eo2cube.ipynb)
# 3. [Products and Measurements](03_products_and_measurements.ipynb)
# 4. [Loading data](04_loading_data.ipynb)
# 5. [Advanced xarrays operations](05_advanced_xarray.ipynb)
# 6. **Plotting data (this notebook)**
# 7. [Basic analysis of remote sensing data](07_basic_analysis.ipynb)
# 8. [Parallel processing with Dask](08_parallel_processing_with_dask.ipynb)

# ***
# 
# ## Further Reading
# For users who are not familar with basics functionality and plottings of matplotlib, please check on the following external tutorial to learn about:
# 
# 1) [Short Introduction of Matplotlib](https://towardsdatascience.com/matplotlib-tutorial-learn-basics-of-pythons-powerful-plotting-library-b5d1b8f67596)
# 
# *  Plotting options and parameters of Matplotlib
# 
# 2) [Introduction to Plotting in Python Using Matplotlib](https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-with-matplotlib/introduction-to-matplotlib-plots/).
# 
# *  Introduction to pyplot module
# *  Customize Plots Using Matplotlib (Tick, Label, Title, Marker, Color, etc.)
# 
# 3) Working With Datetime Objects in Python
# 
# *  [Introduction to Datetime Object](https://www.earthdatascience.org/courses/use-data-open-source-python/use-time-series-data-in-python/date-time-types-in-pandas-python/)
# *  [Customize Matplotlibe Dates Ticks on the x-axis in Python](https://www.earthdatascience.org/courses/scientists-guide-to-plotting-data-in-python/plot-with-matplotlib/introduction-to-matplotlib-plots/plot-time-series-data-in-python/)
# 
# <br>
# To continue working through the notebooks in this beginner's guide, the following notebooks are designed to be worked through in the following order:
# 
# 1. [Jupyter Notebooks](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/01_jupyter_introduction.ipynb)
# 2. [eo2cube](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/02_eo2cube_introduction.ipynb)
# 3. [Loading Data](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/03_data_lookup_and_loading.ipynb)
# 4. [Xarray I: Data Structure](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/04_xarrayI_data_structure.ipynb)
# 5. [Xarray II: Index and Statistics](https://github.com/eo2cube/eo2cube_notebooks/blob/main/get_started/intro_to_eo2cube/05_xarrayII.ipynb)
# 6. ***Plotting data (this notebook)***
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
