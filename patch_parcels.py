import json
import sys

# Property key used to identify each feature
ID_FIELD = "ParcelID"

# Define manual overrides keyed by parcel identifier
EDITS = {
    # The city has an incorrect date for #4 Westview
    "5-73B-18-0": {
        "YearBuilt": 1931,
        "valid_from": 1931,
    },
    # Add a "valid_from" date + notes for #5 Westview
    "5-73B-8-0": {
        "YearBuilt": 1916,
        "valid_from": 1963,
        "Notes": "The oldest home on Westview was here in 1916, and replaced in 1994."
    },
    # These are the parcels that Westview-7-pre-split split into, in 1964
    "5-73B-29-0": {
        "valid_from": 1964,
    },
    "5-73B-50-0": {
        "valid_from": 1964,
    },
    # These are the parcels that Westview-15-pre-split split into, in 1977
    "5-73B-10-0": {
        "valid_from": 1977,
    },
    "5-73B-47-0": {
        "valid_from": 1977,
    },
    "5-73B-46-0": {
        "valid_from": 1977,
    },
    "5-73B-45-0": {
        "valid_from": 1977,
    },
    "5-73B-44-0": {
        "valid_from": 1977,
    },
    "5-73B-10A-0": {
        "valid_from": 1977,
    },
    "5-73B-51-0": {
        "valid_from": 1977,
    },
    "5-73B-20-0": {
        "Notes": f"""
        <ul><li><a href="https://www.rotonhill.com/neighbors/captain-ira-ford">Captain Ira Ford</a> lived here in the 1840s.
        <li><a href="https://www.rotonhill.com/neighbors/george-platt">George and Mary Platt</a> lived here in the 1860s
        <li>Alexander and Maria Rummler lived here in the early 1900s.
        </ul>
        """
    }
}

def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        sys.stderr.write(f"Error parsing JSON from stdin: {e}\n")
        sys.exit(1)

    features = data.get("features", [])
    patched_count = 0

    for feat in features:
        props = feat.setdefault("properties", {})
        
        # Check standard casing variants if ID_FIELD doesn't match directly
        parcel_id = str(
            props.get(ID_FIELD) or 
            props.get("PARCEL_ID") or 
            props.get("parcel_id") or 
            props.get("MAP_BLOCK_LOT") or 
            ""
        ).strip()

        if parcel_id in EDITS:
            overrides = EDITS[parcel_id]
            props.update(overrides)

            patched_count += 1

    sys.stderr.write(f"Patched {patched_count} features out of {len(features)} total.\n")

    # Stream out 1 feature per line
    sys.stdout.write('{\n"type": "FeatureCollection",\n"features": [\n')
    for i, feature in enumerate(features):
        line = json.dumps(feature, separators=(',', ':'))
        if i < len(features) - 1:
            sys.stdout.write(f"  {line},\n")
        else:
            sys.stdout.write(f"  {line}\n")
    sys.stdout.write(']\n}\n')

if __name__ == "__main__":
    main()
