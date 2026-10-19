import json
import sys
from shapely import wkt
from shapely.geometry import shape

# Bounds of the area of interest (essentially Roton Hill). Created in
# MyMaps, exporting a region by CSV.
REGION_WKT = """POLYGON ((
-73.4346649 41.1003578, -73.436167 41.1001746, -73.4360811 41.101134, -73.4388706 41.0997973,
-73.4413168 41.0982342, -73.4433338 41.0964231, -73.4453079 41.094612, -73.4474108 41.0926822,
-73.4490416 41.0914855, -73.4513447 41.0903858, -73.4536335 41.0896635, -73.4533188 41.0882942,
-73.453891 41.0876257, -73.4536621 41.0873777, -73.4532044 41.0876365, -73.4522459 41.0877443,
-73.4517739 41.08865, -73.4506724 41.0881864, -73.4505436 41.0871621, -73.4501431 41.0864828,
-73.4494421 41.0865044, -73.4481404 41.0859437, -73.4472248 41.0844558, -73.4473679 41.0835932,
-73.4471247 41.0827953, -73.4468243 41.0824287, -73.4470961 41.0813073, -73.4467385 41.0804662,
-73.4464953 41.0795388, -73.4466526 41.0777488, -73.4460089 41.0766597, -73.4461233 41.0763362,
-73.4467241 41.0763254, -73.4470818 41.0753441, -73.4469387 41.074298, -73.4479687 41.0721735,
-73.4473965 41.0712461, -73.4449789 41.070297, -73.4443352 41.068895, -73.445265 41.0666679,
-73.4463808 41.0636156, -73.4467241 41.0614638, -73.4463951 41.057915, -73.4417889 41.0550349,
-73.4387562 41.0542906, -73.4331486 41.0541827, -73.4320185 41.0552614, -73.4311745 41.0598243,
-73.4315464 41.06402, -73.4316323 41.0699897, -73.4305021 41.0709279, -73.429043 41.0720657,
-73.4281847 41.0726372, -73.4276125 41.073597, -73.4284708 41.0750906, -73.4303663 41.0769616,
-73.4307918 41.0789485, -73.4314391 41.0798677, -73.4320686 41.0808975, -73.4311244 41.0831134,
-73.4302947 41.0860165, -73.4298477 41.0865179, -73.429533 41.0875206, -73.4301195 41.087836,
-73.4299979 41.0886122, -73.4300229 41.0901109, -73.4298584 41.0908871, -73.4300372 41.0914235,
-73.4307453 41.0929706, -73.4313247 41.0947899, -73.4318397 41.0947036, -73.4325263 41.0956307,
-73.4326408 41.096725, -73.4334991 41.0967465, -73.4342859 41.0980617, -73.4343574 41.0986977,
-73.4342429 41.0988918, -73.4346649 41.1003578 ))
"""

def parcel_in_bounds(feature, region):
    geometry = feature.get("geometry")
    if not geometry or "coordinates" not in geometry:
        return False
    parcel_shape = shape(geometry)
    if not parcel_shape.is_valid:
        return False
    if region.intersects(parcel_shape):
        return True
    return False

def get_year_built(feature):
    """
    Extracts YearBuilt as an integer. Returns 0 if missing,
    null, unparseable, or <= 0.
    """
    props = feature.get("properties") or {}
    # Check common ArcGIS casing variations
    raw_year = (
        props.get("YearBuilt") or 
        props.get("YEAR_BUILT") or 
        props.get("YEARBUILT") or 
        props.get("year_built")
    )
    if raw_year is None:
        return 0
    try:
        yr = int(float(str(raw_year).strip()))
        return yr if yr > 0 else 0
    except (ValueError, TypeError):
        return 0

def geometry_key(feature):
    """
    Creates a deterministic string signature of the geometry 
    coordinates so identical outlines match exactly.
    """
    geom = feature.get("geometry")
    if not geom:
        return ""
    # Standardize precision to avoid micro-float discrepancies
    return json.dumps(geom.get("coordinates"), separators=(',', ':'))

def deduplicate_consecutive(features):
    """
    Deduplicates consecutive features that share the same outline.
    Selects the feature with a valid non-zero YearBuilt (preferring
    the earliest valid year if multiple condo units differ slightly).
    """
    if not features:
        return []

    deduped = []
    current_group = [features[0]]
    current_geom_key = geometry_key(features[0])

    for feat in features[1:]:
        geom_k = geometry_key(feat)
        if geom_k == current_geom_key and geom_k != "":
            # Same outline as the preceding entry: collect into group
            current_group.append(feat)
        else:
            # Different outline: resolve the previous group and start a new one
            deduped.append(pick_best_feature(current_group))
            current_group = [feat]
            current_geom_key = geom_k

    if current_group:
        deduped.append(pick_best_feature(current_group))

    return deduped

def pick_best_feature(group):
    """
    Picks the best feature from a group of duplicates.
    Prioritizes entries with YearBuilt > 0.
    """
    if len(group) == 1:
        return group[0]

    # Filter out entries where YearBuilt is 0 / empty
    valid_year_entries = [f for f in group if get_year_built(f) > 0]

    if valid_year_entries:
        # If multiple units in the condo development have valid years,
        # just use the first.
        return valid_year_entries[0]

    # If all entries have YearBuilt == 0, keep the first one
    return group[0]

def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write(f"Error with input: {e}\n")
        sys.exit(1)

    region = wkt.loads(REGION_WKT)
    features = data.get("features", [])
    total_count = len(features)
    sys.stderr.write(f"Total source features: {total_count}\n")

    # Geographic crop
    in_bounds_features = [f for f in features if parcel_in_bounds(f, region)]
    sys.stderr.write(f"Features within bounds: {len(in_bounds_features)}\n")

    # Keep only the properties you actually use in the map
    keys_to_keep = {"YearBuilt", "NAME", "ParcelID", "Location"}
    for f in in_bounds_features:
        f["properties"] = {k: v for k, v in f["properties"].items() if k in keys_to_keep}

    # Sequential duplicate collapse (condos/shared footprints)
    final_features = deduplicate_consecutive(in_bounds_features)

    # Fill in some properties by default
    for feat in final_features:
        props = feat.setdefault("properties", {})
        year = get_year_built(feat)
        props["valid_from"] = year if year > 0 else None

    sys.stderr.write(f"Features after deduplicating shared outlines: {len(final_features)}\n")
    sys.stderr.write(f"Removed {len(in_bounds_features) - len(final_features)} duplicate condo/sub-unit polygons.\n")

    # 3. Write output formatted 1 feature per line
    sys.stdout.write('{\n"type": "FeatureCollection",\n"features": [\n')
    for i, feature in enumerate(final_features):
        line = json.dumps(feature, separators=(',', ':'))
        if i < len(final_features) - 1:
            sys.stdout.write(f"  {line},\n")
        else:
            sys.stdout.write(f"  {line}\n")
    sys.stdout.write(']\n}\n')

    sys.stderr.write("Finished successfully.\n")

if __name__ == "__main__":
    main()
