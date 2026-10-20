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
        "new_id": "Westview-3-pre-split",
        "source_ids": ["5-73B-11-0", "5-73B-42-0"],
        "overrides": {
            "valid_to": 1968,
        }
    },
    {
        "new_id": "Westview-5-pre-split",
        "source_ids": ["5-73B-8-0", "5-73B-40-0"],
        "overrides": {
            "YearBuilt": 1916,
            "valid_from": 1916,
            "valid_to": 1963,
        }
    },
    {
        "new_id": "Westview-7-pre-split",
        "source_ids": ["5-73B-29-0", "5-73B-50-0"],
        "overrides": {
            "valid_to": 1964,
        }
    },
    {
        "new_id": "Westview-9-pre-split",
        "source_ids": ["5-73B-9A-0", "5-73B-49-0"],
        "overrides": {
            "valid_to": 1979,
        }
    },
    {
        "new_id": "Westview-12-pre-split",
        "source_ids": ["5-73B-24-0", "5-73B-26-0"],
        "overrides": {
            "valid_to": 1959
        }
    },
    {
        "new_id": "Westview-15-pre-split",
        "source_ids": ["5-73B-10-0", "5-73B-47-0", "5-73B-46-0", "5-73B-45-0",
                       "5-73B-44-0", "5-73B-10A-0", "5-73B-51-0"],
        "overrides": {
            "valid_to": 1977
        }
    },
    {
        "new_id": "Westview-23-pre-split",
        "source_ids": ["5-73A-10-0", "5-73A-60-0", "5-73A-54-0", "5-73A-55-0"],
        "overrides": {
            "valid_to": 1955,
        },
    },
    {
        "new_id": "FlaxHill-319-pre-split",
        "source_ids": ["5-76B-5-0", "5-76B-177-0", "5-76B-191-0"],
        "overrides": {
            "valid_to": 2017,
        },
    },
    {
        "new_id": "FlaxHill-341-pre-split",
        "source_ids": ["5-73B-22-0", "5-73B-39-0"],
        "overrides": {
            "valid_to": 1959
        }
    },
    {
        "new_id": "FlaxHill-343-pre-split",
        "source_ids": ["5-73B-21-0", "5-73B-48-0"],
        "overrides": {
            "valid_to": 1979
        }
    },
    {
        "new_id": "TraendlyGreenhouses",
        "source_ids": ["5-79-59-0", "5-79-60-0", "5-79-61-0", "5-79-62-0", "5-79-63-0", "5-79-64-0",
                       "5-79-65-0", "5-79-66-0", "5-79-75-0", "5-79-76-0", "5-79-77-0", "5-79-78-0",
                       "5-79-79-0", "5-79-80-0", "5-79-81-0", "5-79-82-0", "5-79-83-0", "5-79-84-0",
                       "5-79-85-0", "5-79-86-0", "5-79-57-0", "5-79-56-0", "5-79-55-0", "5-79-54-0",
                       "5-79-52-0", "5-79-51-0", "5-79-50-0", "5-79-49-0", "5-79-48-0", "5-79-47-0",
                       "5-79-46-0", "5-79-45-0", "5-79-44-0", "5-79-43-0", "5-79-42-0", "5-79-41-0",
                       "5-79-40-0", "5-79-39-0", "5-79-38-0", "5-79-37-0", "5-79-36-0", "5-79-35-0",
                       "5-79-34-0", "5-79-33-0", "5-79-32-0", "5-79-31-0", "5-79-30-0", "5-79-29-0",
                       "5-79-28-0", "5-79-27-0", "5-79-26-0", "5-79-25-0", "5-79-24-0", "5-79-23-0",
                       "5-79-22-0", "5-79-21-0", "5-79-20-0", "5-79-19-0", "5-79-18-0", "5-79-17-0",
                       "5-79-16-0", "5-79-7-0",  "5-79-6-0"],
        "overrides": {
            "YearBuilt": 1912,
            "valid_from": 1912,
            "valid_to": 1960,
            "Location": "Traendly Farms",
            "Notes": f"""
            Traendly was the largest supplier of flowers to New York City, all grown in 50
            greenhouses on either side of Five Mile River in Norwalk and Darien. Traendly
            operated from about 1912 or so until the late 1950s. When they shut down the
            greenhouses they tried to sell this land to Sperry-Rand for a manufacturing
            facility, but their bruising 3-year attempt to re-zone the area was ultimately
            denied due to fierce opposition from the local community.<p>
            To be clear, these roads were not here when the greenhouses were operating.
            """
        }
    },
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

        # We're generally combining parcels because they were at some point split,
        # so we're dealing with the more recent, split parcels. So if we set a
        # 'valid_to' year in the overrides above, then we'll generally want to
        # copy that to 'valid_from' in the source parcels (which come later
        # historically).
        if "valid_to" in merged_props:
            valid_to_val = merged_props["valid_to"]
            for f in matched:
                if "properties" not in f or f["properties"] is None:
                    f["properties"] = {}
                f["properties"]["valid_from"] = valid_to_val

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
