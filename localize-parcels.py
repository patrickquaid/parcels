import json
import sys

# Spatial bounds
MAX_EAST_LON = -73.421   # Keep if at least one coordinate is west (<)
MAX_NORTH_LAT = 41.104   # Keep if at least one coordinate is south (<)

def extract_coords(coords):
    """Recursively yields [lon, lat] coordinate pairs."""
    if not coords:
        return
    if isinstance(coords[0], (int, float)):
        yield coords
    else:
        for sub in coords:
            yield from extract_coords(sub)

def parcel_in_bounds(feature):
    geometry = feature.get("geometry")
    if not geometry or "coordinates" not in geometry:
        return False
    
    has_point_west = False
    has_point_south = False
    
    for pt in extract_coords(geometry["coordinates"]):
        lon, lat = pt[0], pt[1]
        if lon < MAX_EAST_LON:
            has_point_west = True
        if lat < MAX_NORTH_LAT:
            has_point_south = True
            
        if has_point_west and has_point_south:
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

    features = data.get("features", [])
    total_count = len(features)
    sys.stderr.write(f"Total source features: {total_count}\n")

    # Geographic crop
    in_bounds_features = [f for f in features if parcel_in_bounds(f)]
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
