import json
import sys

# Property key used to identify each feature
ID_FIELD = "ParcelID"

# Define manual overrides keyed by parcel identifier
EDITS = {
    # 4 Westview
    "5-73B-18-0": {
        "YearBuilt": 1931,
        "valid_from": 1931,
        "Notes": f"""
        In the late 1940s, <a href="https://www.rotonhill.com/mainframes">Philip Scribner
        Rand</a> (1906-1995) lived here with his family. Rand was the much-younger brother
        of James Rand, the Chairman of Remington-Rand. Philip also worked at the company,
        as an engineer. He was interested in radio interference and Ham radio, and while he
        lived here there was a tall antenna in the side yard.
        """
    },
    # 5 Westview
    "5-73B-8-0": {
        "YearBuilt": 1916,
        "valid_from": 1963,
        "Notes": "The oldest home on Westview was here in 1916. It was replaced in 1994."
    },
    # 14 Westview
    "5-73A-13-0": {
        "YearBuilt": 1940,
        "valid_from": 1940,
        "Notes": f"""
        The original house was replaced in 2017. Among the residents here were:<ul>
        <li><a href="https://www.rotonhill.com/mainframes">Cuthbert Hurd</a>, the
        Director of Applied Science at IBM.
        <li>Paleontologist <a href="https://en.wikipedia.org/wiki/Betty_Kellett_Nadeau">
        Betty Kellett Nadeau</a>.
        </ul>
        """
    },
    # 15 Westview
    "5-73B-10-0": {
        "Notes": f"""
        This was the first home built by Godfrey Shaw on Westview Ln. Shaw would go on
        to build most of the other houses on the lane over the following decade. In about
        1975 the large original lot was subdivided into seven smaller parcels.<p>
        Among the residents of this house were Marcell and Jane Rand. Marcell was the
        son of the Chairman of Remington-Rand (later Sperry-Rand), and was the Vice
        President of International Operations.
        """
    },
    # 16 Westview. It shows up as 1950, but I'm confident the Howes were living here at
    # least in 1946.
    "5-73A-18-0": {
        "YearBuilt": 1946,
        "valid_from": 1946,
        "Notes": f"""
        Paul Griswold Howes, the Director-Curator of the Bruce Museum in Greenwich,
        lived here from 1946 until his death in 1984.
        """
    },
    # 17 Westview. It was rebuilt, so we want to note the earlier house.
    "5-73B-46-0": {
        "YearBuilt": 1979,
        "Notes": f"""
        This house was apparently rebuilt in 2006.
        """
    },
    # 23 Westview
    "5-73A-10-0": {
        "Notes": f"""
        Godfrey and Alice Shaw lived here from about 1940 to 1968. Godfrey
        Shaw was a real estate developer, and he built most of the houses on Westview
        that went up in the 1930s and 1940s. The original house at 23 Westview burned
        down in 1987. The current house is largely new but retains many of the original
        features.
        """
    },
    # 319 Flax Hill Rd
    "5-76B-5-0": {
        "YearBuilt": 1770,
        "valid_from": 1770,
        "Notes": f"""
        The historic home on this lot was demolished in 2017. See
        <a href="https://www.thehour.com/news/article/Historic-1770s-era-home-on-Flax-Hill-Road-torn-10934471.php">
        this article in the The Norwalk Hour</a> for the story, along with excellent photos of the
        original house.
        """
    },
    # 341 Flax Hill Rd
    "5-73B-22-0": {
        "YearBuilt": 1760,
        "valid_from": 1760,
        "Notes": f"""
        This was the homestead of Sally Ann Keeler, who inherited much of the land
        around here when her father David Lockwood died in 1835. The original house
        burned down in 1912, and was replaced that year by William G Shaw. There's
        much more detail about all this in 
        <a href="https://www.rotonhill.com/the-keeler-property">The Keeler Property</a>.
        """
    },
    # 343 Flax Hill Rd
    "5-73B-21-0": {
        "Notes": f"""
        The home currently at 3 Rochelle originally faced Flax Hill, and the lot that
        is now 343 Flax Hill was its circular driveway. When the lot was split in 1979
        the house was reversed to face Rochelle.<p>
        From about 1936 until his death in 1954, this was the home of
        <a href="https://en.wikipedia.org/wiki/C._E._Hooper">Claude Hooper</a>, who
        measured radio audience sizes, much like Nielsen later did for television.
        """
    },
    # 347 Flax Hill Rd
    "5-73B-20-0": {
        "Notes": f"""
        <a href="https://www.rotonhill.com/neighbors/captain-ira-ford">Captain Ira Ford</a>
        lived here from the 1840s until his death in 1858. His wife was the former Phebe
        Bouton, whose sister Hannah lived nearby at 354 Highland Ave.<p>
        This house has a Norwalk Historical Society plaque that notes that
        <a href="https://www.rotonhill.com/neighbors/george-platt">George and Mary Platt</a>
        lived here in the 1860s.<p>
        Alexander and Maria Rummler lived here in the early 1900s. Alexander was an artist
        and sat on the Board of Education. Maria was the first woman elected to the Norwalk
        City Council.
        """
    },
    # 378 Flax Hill Rd
    "5-78-5-0": {
        "Notes": f"""
        In 1865 this was the home of Josiah Tristram, who played a role in the
        <a href="https://www.rotonhill.com/the-adams-express-robbery">Adams Express
        Robbery</a>. The first two arrests of the perpetrators took place here.
        """
    },
    "5-73B-6-0": {
        "Notes": f"""
        21-year-old Augusta Getner moved into this house when she married John Zilske in 1909.
        John died in 1949, but Augusta celebrated her 100th birthday at this house in 1988.
        """
    },
    # 51 Rampart Rd
    "5-73A-14-0": {
        "Notes": f"""
        This was originally built as the Photography Studio of Alice B. Shaw. Shaw had
        previously been the manager of Manugian's in South Norwalk, and had a long portrait
        photography career. Alice Shaw's husband was real estate developer Godfrey Shaw. The
        two of them lived at 23 Westview Ln, and there was a convenient path through the
        woods for Alice to get to her studio. 
        """
    },
    # 6 Oak Hill Rd
    "5-73B-42-0": {
        "valid_from": 1968,
    },
    # 40 Highland Ave
    "6-16C-1-0": {
        "Location": "The Rockledge Mansion at 40 Highland Ave",
        "Notes": f"""
        James Augustine
        Farrell, the then-president of U.S. Steel, first built a mansion on this property
        in 1913. That mansion immediately burned down, so he built another one by 1916, and
        that one's still standing (see the whole story at
        <a href="https://www.historicrowayton.org/the-farrell-estate-rock-ledge">Historic
        Rowayton</a>).<p>
        After the Farrells died in the early 1940s, Darien resident James Rand, the
        Chairman of Remington-Rand, bought the mansion as a headquarters for his company.
        The first practical commercial computer was developed in the barns across Highland
        Ave, now the Rowayton Library. Post-war Remington-Rand executives Douglas MacArthur
        and Leslie R. Groves worked out of this location.
        """,
        "valid_from": 1913,
        "YearBuilt": 1913,
    },
    # 297 Highland Ave
    "5-80-30-0": {
        "Notes": f"""
        This home was built by Ira Ford Hoyt (1824-1887), who was a lumber dealer and builder.
        His mother Hannah Smith Hoyt lived up the street in 354 Highland Ave, and his
        namesake Captain Ira Ford lived in 347 Flax Hill Rd.<p>
        Ira's son Dudley (1866-1921) eventually took over the house. He was also a builder,
        who among other things built the original Norwalk Yacht Club building. Dudley had a
        daughter named Margaret Rachel Hoyt (1905-2001). Margaret became a qualified architect,
        the first in Norwalk. She designed a part of the cap of the Chrysler
        building, the Norwalk Historical Society Museum, and a number of houses in Rowayton.
        Margaret took over the family home in turn, and raised here children there. In 1959
        she sold the land to the city so they could build Brien McMahon High School. The
        house itself was moved across the street to its present location.
        """
    },
    # 354 Highland Ave
    "5-81-1-0": {
        "Notes": f"""
        This was the home Aaron Gregory Hoyt and his wife Hannah Smith Bouton. Aaron died in
        1836, and Hannah lived here until she died in 1873. Hannah's sister Phebe traveled to
        Troy, NY to marry Captain Ira Ford, but once Ira retired they moved back to Norwalk, into
        347 Flax Hill Rd, just up the street. Hannah named her son Ira Ford Hoyt, after the
        captain. Ira F. Hoyt would later live in 297 Highland, just down the street.<p>
        Aaron and Hannah are buried in the tiny Hoyt-Bouton Cemetery on Witch Lane.
        """,
    },
    # Rowayton Woods. This is the survivor of de-duplication, so we want it to represent
    # the whole development.
    "5-80-200-1/01": {
        "Location": "Rowayton Woods Dr",
    },
    "5-79-3-0": {
        "Location": "Brookside Cemetery",
        "valid_from": 1724,
        "YearBuilt": 1724,
    },
    "5-79-1-0": {
        "Location": "Union Cemetery",
        "valid_from": 1849,
        "YearBuilt": 1849,
    },
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
