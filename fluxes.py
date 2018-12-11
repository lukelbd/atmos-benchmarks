#!/usr/bin/env python3
################################################################################
# Get fluxes with python
################################################################################
# First load file
import os
import sys
import xarray as xr
xr.DataArray.mean
filename = sys.argv[1]
toggle = bool(int(sys.argv[2])) # toggle
if toggle:
    N = 100000 # max chunk size for lon/lat dimensions; want to chunk each 2D slice separately
    # N = 1000 # this made no difference
    chunks = {'time':1, 'plev':1, 'lat':N, 'lon':N} # one chunk per horizontal slice, works pretty well
    data = xr.open_dataset(filename, chunks=chunks, decode_times=False)
else:
    data = xr.open_dataset(filename, decode_times=False)

# Next perform calculations
emf = ((data['u'] - data['u'].mean('lon')) * (data['v'] - data['v'].mean('lon'))).mean('lon')
ehf = ((data['t'] - data['t'].mean('lon')) * (data['v'] - data['v'].mean('lon'))).mean('lon')
emf.name = 'emf'
ehf.name = 'ehf'
emf.attrs = {'long_name':'eddy momentum flux', 'units':'m**2/s**2'}
ehf.attrs = {'long_name':'eddy heat flux', 'units':'K*m/s'}

# Save file
out = xr.Dataset({'emf':emf, 'ehf':ehf})
outname = f'fluxes_py{int(toggle)}.nc'
if os.path.exists(outname):
    os.remove(outname)
out.to_netcdf(outname, mode='w') # specify whether we did chunking
