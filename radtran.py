
# coding: utf-8

# # Radiative Transfer Project
# **Spring 2017  
# Drew Camron and Matt Cann**

# ## Important Reading
# [python-hdf4 (aka pyhdf) module docs](http://fhs.github.io/python-hdf4/)  
# [sample modis import](http://hdfeos.org/zoo/LAADS/MOD08_D3_Cloud_Fraction_Liquid.py)  
# [sample cloudsat import](http://hdfeos.org/zoo/OTHER/2010128055614_21420_CS_2B-GEOPROF_GRANULE_P_R04_E03.hdf.py)

# ## Importing and cleaning data

# In[1]:

get_ipython().magic('matplotlib inline')
from pyhdf.SD import *
from pyhdf.VS import *
from pyhdf.V import *
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

lat_m = dslat_m.get()    # MODIS swath latitude
lon_m = dslon_m.get()    # MODIS swath longitude
ct_mi = dsct_m.get()

at = dsct_m.attributes()
at


# Here we can pull in some of the provided attributes. The data are not scaled or offset, but we will make sure to NaN invalid data.

# In[4]:

_FillValue = at['_FillValue']
vra = at['valid_range']
ctname_m = at['long_name']
ctunits_m = at['units']

invalid = np.logical_or(ct_mi < vra[0], ct_mi > vra[1], ct_mi == _FillValue)
ct_m = ct_mi.astype(float)    # cleaned MODIS cloud-top height data
ct_m[invalid] = np.nan


# Now, the cloudsat data have coordinating information hidden in the HDF vdata, which we will investigate and extract below.

# In[5]:

vsc = hc.vstart()
vsc.vdatainfo()


# In[6]:

latc = vsc.attach('Latitude')
latc.setfields('Latitude')
n,_,_,_,_ = latc.inquire()
lat_c = np.array(latc.read(n))    # cloudsat path latitudes
latc.detach()

lonc = vsc.attach('Longitude')
lonc.setfields('Longitude')
n,_,_,_,_ = lonc.inquire()
lon_c = np.array(lonc.read(n))    # cloudsat path longitudes
lonc.detach()


# In[7]:

c.datasets()


# In[8]:

dshgt_c = c.select('Height')
dsref_c = c.select('Radar_Reflectivity')

hgt_ci = dshgt_c.get()
ref_ci = dsref_c.get()


# As the data descriptors are a headache and a half to by-hand pull out of the HDF vgroups, they were inspected manually with HDFVIEW and imported here. Height were unscaled/unoffset, Reflectivity were scaled by 100.

# In[9]:

hgtc_name = 'Height of range bin in Reflectivity/Cloud Mask above reference surface (~mean sea level).'
hgtc_units = 'm'

vra = [-5000,30000]
_FillValue = -9999

invalid = np.logical_or(hgt_ci < vra[0], hgt_ci > vra[1], hgt_ci == _FillValue)
hgt_c = hgt_ci.astype(float)      # cleaned height data
hgt_c[invalid] = np.nan


# In[16]:

refc_name = 'Radar Reflectivity Factor'
refc_units = 'dBZe'
refc_scale = 100

vra = [-4000,5000]
_FillValue = -8192

invalid = np.logical_or(ref_ci < vra[0], ref_ci > vra[1], ref_ci == _FillValue)
ref_c_pre = ref_ci.astype(float)
ref_c_pre[invalid] = np.nan
ref_c = ref_c_pre / refc_scale    # cleaned and scaled cloudsat reflectivity data


# Finally, we'll close all of our open files and datasets.
m.end()
hm.close()

vsc.end()
c.end()
hc.close()
# ## Now we can do some data analysis!

# First, we want to pull out every cloud-top height data point with a lat, lon pair corresponding to our cloudsat data.

# In[17]:

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

test = lon_m
test[test < 0] = test[test < 0] + 360

fig = plt.figure()
ax = plt.axes(projection=ccrs.Mercator())
ax.set_xticks(np.arange(163,192,4))
ax.set_yticks(np.arange(-4,21,4))
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
fig.suptitle(ctname_m)
c = plt.contourf(test,lat_m,ct_m,cmap='Blues_r',transform=ccrs.Mercator())
cb = plt.colorbar(c)
cb.set_label('Meters')


# In[18]:

ax.get_extent()


# In[19]:

test2 = lon_c
test2[test2 < 0] = test2[test2 < 0] + 360


# In[26]:

winlon = np.logical_or(test2 > 164, test2 < 190)
winlat = np.logical_or(lat_c > -3, lat_c < 18)

fig = plt.figure()
fig.suptitle(refc_name)
ax = plt.axes()
c = plt.contourf(ref_c[17500:19500][:].T)
ax.invert_yaxis()
ax.set_ylabel('Range Bin')
ax.set_xlabel('Orbit Bin (Arbitrary)')
cb = plt.colorbar()
cb.set_label(refc_units)

