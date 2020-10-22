#!/usr/bin/env bash
# Interpolate to isentropic surfaces
source ./header.sh
for data in ${datas[@]}; do
  # Header
  init $data

  # Python with MetPy method
  bench "MetPy" python metpy.py $data 0

  # Python with MetPy method
  bench "MetPy + Dask" python metpy.py $data 10

  # Python with xgcm
  bench "xgcm" python xgcm.py $data 0

  # Python with xgcm
  bench "xgcm + Dask" python xgcm.py $data 10

  # NCL method
  # NOTE: NCL needs special dyld library path but so does brew, screws
  # up Homebrew if we set it, so set it locally
  export DYLD_LIBRARY_PATH="/opt/local/lib/libgcc"
  bench "NCL" ncl -Q -n "filename=\"$data\"" "outname=\"${name}/out/ncl.nc\"" ncl.ncl
  export DYLD_LIBRARY_PATH=""

  # NCL in parallel by splitting timesteps with ncks
  # export DYLD_LIBRARY_PATH="/usr/local/lib/gcc/4.9"
  # bench "NCL Parallel" nclparallel "$data"
  # export DYLD_LIBRARY_PATH=""
done
