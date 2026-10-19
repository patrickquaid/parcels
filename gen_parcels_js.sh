#!/bin/sh
(
    set -e
    echo "var parcelData = "
    cat Parcels_Norwalk_CT.geojson | \
    python3 localize-parcels.py | \
    python3 patch_parcels.py | \
    python3 combine_parcels.py
) > parcels.js.tmp || exit 1
mv parcels.js.tmp parcels.js

