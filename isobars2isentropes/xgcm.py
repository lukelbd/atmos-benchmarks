#!/usr/bin/env python3
# Interpolate to isentropic levels
# NOTE: File cannot have any print statements! Need to capture output of time command.
import os
import sys

import numpy as np

# import metpy.calc as mcalc
import xarray as xr
from xgcm import Grid

# deactivate for easier debugging
# File, with optional decoding
if len(sys.argv) != 3:
    raise ValueError("Require two input args.")

filename = sys.argv[1]
nt = int(sys.argv[2])  # number of time chunks; 0 to disable chunking
dir = filename.split("/")[0]

if nt:  # 1 chunk per level
    N = 100000  # max chunk size for space (want to chunk each timestep separately)
    chunks = {"time": nt, "plev": N, "lat": N, "lon": N}
    data = xr.open_dataset(filename, chunks=chunks, decode_times=False)
else:
    data = xr.open_dataset(filename, decode_times=False)

# Interpoland
# thlev = np.array([*range(260, 360, 10), *range(360, 400, 20), *range(400, 800, 50)])
# thlev = np.array([*range(300, 360, 10), *range(360, 400, 20)])
# thlev = np.arange(240,400,20)  # must be ascending!
thlev = [265, 275, 285, 300, 315, 330, 350, 370, 395, 430, 475, 530, 600, 700, 850]
thlev = np.array(thlev)


# Compute theta (adapted from the ncl script with constants from metpy)
p0 =  1000.0
kappa = 0.285629847
theta = data['t'] * (p0 / data['plev']) ** kappa
theta.name = 'thlev'

# create grid object
grid = Grid(data, coords={'Z':{'center':'plev'}}, periodic=False)

# Create output datasets
out = xr.Dataset()

# we need to manually broadcast here, since the pressure is 1D
plev, t = xr.broadcast(data['plev'], data['t'])

# pressure is log-interpolated
out['p'] = np.exp(grid.transform(np.log(plev), 'Z', thlev, target_data=theta))

# The other variables just regularly
for var in ['u','v','t']:
    out[var] = grid.transform(data[var], 'Z', thlev, target_data=theta)


# Save file
outname = f"{dir}/isentropes_py{nt}.nc"
if os.path.exists(outname):
    os.remove(outname)
out.to_netcdf(outname, mode="w")  # specify whether we did chunking


# # # assert that the results are the same
# # # the ordering seems to be the other way around for metpy
# # thlev = [265, 275, 285, 300, 315, 330, 350, 370, 395, 430, 475, 530, 600, 700, 850]
# # thlev = np.array(thlev)

# # from metpy.units import units
# # import metpy.calc as mcalc


# # # # First check if the theta values come out the same...Seems very close
# # # theta_test = mcalc.potential_temperature(plev, t)

# # # Coordinates
# # time = data['time']
# # plev = data['plev']
# # lat = data['lat']
# # lon = data['lon']

# # # Variables
# # u = data['u']
# # v = data['v']
# # t = data['t']
# # t = t * units.kelvin
# # thlev = thlev.astype('float32') * units.kelvin
# plev = plev.values.astype('float32') * units.hectopascals

# # Interpolation
# # The returned 'p' are pressure along each isentrope
# p, t_th, u_th, v_th = mcalc.isentropic_interpolation(
#     thlev, plev, t.values * units.kelvin, u.values, v.values, axis=1, tmpk_out=True
# )
# dims = ('time', 'thlev', 'lat', 'lon')
# p = xr.Variable(dims, p.astype('float32'), {'long_name': 'pressure', 'units': 'hPa'})
# t_th = xr.Variable(dims, t_th.astype('float32'), t.attrs)
# u_th = xr.Variable(dims, u_th.astype('float32'), u.attrs)
# v_th = xr.Variable(dims, v_th.astype('float32'), v.attrs)



# # Make dataset, add variables and coordinates
# # NOTE: Put coordinates in first, so they come first in ncdump
# thlev = xr.Variable(
#     "thlev", thlev, {"long_name": "potential_temperature", "units": "K"}
# )
# out_check = xr.Dataset({}, coords={"time": time, "thlev": thlev, "lat": lat, "lon": lon})
# for name, data in zip(("p", "t", "u", "v"), (p, t_th, u_th, v_th)):
#     out_check[name] = data

# print(out_check)
