import json
import sys

# Define your boundary thresholds
MAX_EAST_LON = -73.426846   # Retain if at least one point is west (<) of this line
MAX_NORTH_LAT = 41.104265   # Retain if at least one point is south (<) of this line

INPUT_FILE = "parcels.in"
OUTPUT_FILE = "parcels.out"

def extract_coords(coords):
    """
    Recursively extracts all [lon, lat] coordinate pairs 
    from Polygon or MultiPolygon coordinate arrays.
    """
    if not coords:
        return
    # If the first item is a number, this is a [lon, lat] point
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
            
        # Once both conditions are satisfied, we can stop checking points
        if has_point_west and has_point_south:
            return True
            
    return False

def main():
    print(f"Loading {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_FILE}'. Check the filename/path.")
        sys.exit(1)

    features = data.get("features", [])
    total_count = len(features)
    print(f"Total features loaded: {total_count}")

    # Filter features
    filtered_features = [f for f in features if parcel_in_bounds(f)]
    kept_count = len(filtered_features)

    data["features"] = filtered_features

    print(f"Features kept: {kept_count} (Removed {total_count - kept_count})")
    print(f"Writing filtered dataset to {OUTPUT_FILE}...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # separators=(',', ':') strips out extra whitespace to minimize file size
        json.dump(data, f, separators=(',', ':'))

    print("Done! File size substantially reduced.")

if __name__ == "__main__":
    main()
