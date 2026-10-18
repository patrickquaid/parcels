import json
import sys
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

# Primary property name used for identification
ID_FIELD = "ParcelID"

# Define merges here:
# Key: The new ParcelID to assign to the merged feature
# Value: Dict containing:
#   - "source_ids": ordered list of ParcelIDs to combine (first has property precedence)
#   - "overrides": optional dict of properties to explicitly set/override
MERGES = [
    {
        "new_id": "Westview-7-pre-split",
        "source_ids": ["5-73B-29-0", "5-73B-50-0"],
        "overrides": {
            "valid_from": 1947,
            "valid_to": 1963,
        }
    },
    {
        "new_id": "Westview-15-pre-split",
        "source_ids": ["5-73B-10-0", "5-73B-47-0", "5-73B-46-0", "5-73B-45-0",
                       "5-73B-44-0", "5-73B-10A-0", "5-73B-51-0"],
        "overrides": {
            "valid_from": 1927,
            "valid_to": 1977
        }
    }
]

def get_feature_id(feature):
    props = feature.get("properties") or {}
    return str(
        props.get(ID_FIELD) or
        props.get("PARCEL_ID") or
        props.get("parcel_id") or
        props.get("MAP_BLOCK_LOT") or
        ""
    ).strip()

def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write(f"Error parsing JSON from stdin: {e}\n")
        sys.exit(1)

    features = data.get("features", [])
    
    # Map ParcelID -> feature for rapid lookup
    features_by_id = {}
    for f in features:
        fid = get_feature_id(f)
        if fid:
            features_by_id[fid] = f

    # Keep track of IDs consumed by merge operations so we don't duplicate them
    consumed_ids = set()
    new_features = []

    for spec in MERGES:
        new_id = spec["new_id"]
        source_ids = spec.get("source_ids", [])
        overrides = spec.get("overrides", {})

        # Find matching features in the order provided
        matched = [features_by_id[sid] for sid in source_ids if sid in features_by_id]

        if len(matched) < len(source_ids):
            missing = set(source_ids) - {get_feature_id(m) for m in matched}
            sys.stderr.write(f"Warning: For merge '{new_id}', missing parcels: {missing}\n")

        if not matched:
            sys.stderr.write(f"Skipping merge '{new_id}': no source parcels found.\n")
            continue

        # 1. Geometry: union and dissolve shared borders
        geoms = [shape(f["geometry"]) for f in matched if f.get("geometry")]
        merged_geom = unary_union(geoms)

        # 2. Properties: start with reverse order so index 0 overwrites everything
        merged_props = {}
        for f in reversed(matched):
            merged_props.update(f.get("properties", {}))

        # Assign the new ID and apply explicit overrides
        merged_props[ID_FIELD] = new_id
        merged_props.update(overrides)

        new_features.append({
            "type": "Feature",
            "properties": merged_props,
            "geometry": mapping(merged_geom)
        })

        for sid in source_ids:
            consumed_ids.add(sid)

        sys.stderr.write(f"Merged {len(matched)} parcels into '{new_id}'.\n")

    # Combine untouched features with the newly merged features
    output_features = features
    output_features.extend(new_features)

    sys.stderr.write(
        f"Input: {len(features)} | Merged created: {len(new_features)} | Output: {len(output_features)}\n"
    )

    # Stream out 1 feature per line
    sys.stdout.write('{\n"type": "FeatureCollection",\n"features": [\n')
    for i, feature in enumerate(output_features):
        line = json.dumps(feature, separators=(',', ':'))
        if i < len(output_features) - 1:
            sys.stdout.write(f"  {line},\n")
        else:
            sys.stdout.write(f"  {line}\n")
    sys.stdout.write(']\n}\n')

if __name__ == "__main__":
    main()
