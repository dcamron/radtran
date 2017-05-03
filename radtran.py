
# coding: utf-8

# # Radiative Transfer Project
# **Spring 2017  
# Drew Camron and Matt Cann**

# ### Important Reading
# [python-hdf4 (aka pyhdf) module docs](http://fhs.github.io/python-hdf4/)  
# [sample modis import](http://hdfeos.org/zoo/LAADS/MOD08_D3_Cloud_Fraction_Liquid.py)  
# [sample cloudsat import](http://hdfeos.org/zoo/OTHER/2010128055614_21420_CS_2B-GEOPROF_GRANULE_P_R04_E03.hdf.py)

# In[1]:

get_ipython().magic('matplotlib inline')
from pyhdf.SD import *
from pyhdf.VS import *
from pyhdf.HDF import *
import numpy as np

in_modis = 'Data/aqua-modis_ctpres_20151225_0140.hdf'
in_cs = 'Data/cloudsat_radar_20151225.hdf'

m = SD(in_modis,SDC.READ)
c = SD(in_cs,SDC.READ)

hm = HDF(in_modis)
hc = HDF(in_cs)


# These data files are structured differently. The MODIS data stores all of its coordinates and data in datasets, to be viewed and extracted below.

# In[2]:

m.datasets() #long list of data, scroll on past


# In[3]:

dslat_m = m.select('Latitude')
dslon_m = m.select('Longitude')
dsct_m = m.select('Cloud_Top_Height')

lat_m = dslat_m.get()
lon_m = dslon_m.get()
ct_mi = dsct_m.get()

at = dsct_m.attributes()
at


# Here we can pull in some of the provided attributes. The data are not scaled or offset, but we will make sure to NaN invalid data.

# In[4]:

_FillValue = at['_FillValue']
vra = at['valid_range']
ct_name = at['long_name']
ct_units = at['units']

invalid = np.logical_or(ct_mi < vra[0], ct_mi > vra[1], ct_mi == _FillValue)
ct_m = ct_mi.astype(float)
ct_m[invalid] = np.nan


# Now, the cloudsat data have coordinating information hidden in the HDF vdata, which we will investigate and extract below.

# In[5]:

vsc = hc.vstart()
vsc.vdatainfo()


# In[6]:

latc = vsc.attach('Latitude')
latc.setfields('Latitude')
n,_,_,_,_ = latc.inquire()
#latc.read(n)


# In[7]:

c.datasets()

