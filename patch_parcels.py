import json
import sys

# Additional whole features.
ADDED_FEATURES = [{
    "type":"Feature",
    "properties": {
        "ParcelID":"OriginalReynoldsFarm",
        "YearBuilt": 1922,
        "valid_from": 1922,
        "valid_to": 1957,
        "Location":"Original Reynolds Farms and Distillery",
        "Notes": f"""
        This was approximately the original site of the Reynolds Farms Nursery. The
        Reynolds family also operated a cider mill and distillery here. After the repeal
        of the 18th Amendment, Reynolds was the first <i>legal</i> distillery in Norwalk,
        producing 600 cases weekly.<p>
        When I-95 came through in the late 1950s Stephen Reynolds retired and the business
        was purchased by
        <a href="https://www.reynoldsfarms.net/our-story">a former employee who moved it
        to the present location on Richards Ave</a>.
        """,
    },
    "geometry":{
        "type":"Polygon",
        "coordinates":[[
            [-73.4359055, 41.1018789],
            [-73.43602,   41.100774],
            [-73.4345823, 41.1009411],
            [-73.4345108, 41.1019328],
            [-73.4359055, 41.1018789]]]
    }
}]

# Property key used to identify each feature
ID_FIELD = "ParcelID"

# Define manual overrides of feature.properties, keyed by ParcelID
EDITS = {
    # 4 Westview
    "5-73B-18-0": {
        "YearBuilt": 1931,
        "valid_from": 1931,
        "Notes": f"""
        In the late 1940s, <a href="https://www.rotonhill.com/mainframes">Philip Scribner
        Rand</a> (1906-1995) lived here with his family. Rand was the much-younger brother
        of James Rand, the Chairman of Remington-Rand. Philip also worked at the company,
        as an engineer. He was interested in radio interference and Ham radio (W1DBM), and
        while he lived here there was a tall antenna in the side yard.
        """
    },
    # 5 Westview
    "5-73B-8-0": {
        "YearBuilt": 1916,
        "valid_from": 1963,
        "Notes": f"""
        The oldest home on Westview was built here in about 1916 by Edward & Sarah Lagerin.
        Edward was a house painter and paperhanger whose parents lived nearby on Flax Hill
        Road. When the Lagerins died in the mid-1950s the house was first taken over by their
        daughter Catherine, and then later by their son Nelson. Nelson Lagerin was a radio
        technician with the Norwalk Traffic and Parking Department. After Nelson died the
        house was rebuilt in 1994.
        """
    },
    # 14 Westview
    "5-73A-13-0": {
        "YearBuilt": 1940,
        "valid_from": 1940,
        "Notes": f"""
        Among the residents here were <a href="https://www.rotonhill.com/mainframes">
        Cuthbert Hurd</a>, the Director of Applied Science at IBM, and Paleontologist
        <a href="https://en.wikipedia.org/wiki/Betty_Kellett_Nadeau">Betty Kellett Nadeau</a>.
        <p>The original house was replaced in 2017.
        """
    },
    # 15 Westview
    "5-73B-10-0": {
        "Notes": f"""
        This was the first home built by Godfrey Shaw on Westview Lane. Shaw would go on
        to build most of the other houses on the lane over the following decade. In about
        1975 the large original lot was subdivided into seven smaller parcels.<p>
        The Shaws apparently lived in the house initially, and then in 1931 sold the
        place to Helen and Howard Rankin Wilkes (1905-1996). Howard Wilkes was a stock
        broker, and led the effort to save the <a href="https://maps.app.goo.gl/3ktaWXxHrCt7AjqNA">
        old Brookside School on Flax Hill Road</a>. When that failed, he led the parent's
        association in advocating for the construction of the current school on Highland Ave.<p>
        In 1946 this house was purchased by Marcell and Jane Rand. Marcell was the
        son of James Rand, the Chairman of Remington-Rand (later Sperry-Rand), and was the
        Vice President of International Operations.
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
        "YearBuilt": 1780,
        "valid_from": 1780,
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
        <a href="https://en.wikipedia.org/wiki/C._E._Hooper">Claude E. Hooper</a>, who
        measured radio audience sizes, much like Nielsen later did for television. In
        the late 1940s radio people would ask each other "How's your Hooper?" to see
        how popular their shows were.
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
        In 1865 this was the home of Josiah Tristram (1827-1886), who played a role in the
        <a href="https://www.rotonhill.com/the-adams-express-robbery">Adams Express
        Train Robbery</a>. The first arrests took place here under the watchful eye
        of famous detective Alan Pinkerton.<p>
        Josiah's son William Henry Tristram (1865-1931) was the popular postman on the
        Rowayton rural route. He lived here until the early 1920s.
        """
    },
    "5-78-4-0": {
        "Notes": f"""
        In the 1930s and 1940s, this was the home of Calvin Ira Crocker (1875-1951). Crocker
        was the Chief Engineer for the New York ferries. He was also the Chief Engineer for
        the construction of the Queenboro Bridge, and in 1927 was described as the Chief
        Engineer for the Brooklyn and Manhattan Bridges.<p>
        Crocker's wife was the former Mary Lavinia Broadhurst (1885-1968), and this was her
        house. She had inherited the house from her parents in the 1920s, and in fact she
        lived there for many years after Calvin died.
        """
    },
    # 387 Flax Hill Rd
    "5-73B-6-0": {
        "Notes": f"""
        21-year-old Augusta Getner moved into this house when she married John Zilske in 1909.
        John was a florist at the Traendly greenhouses. He died in 1949, but Augusta celebrated
        her 100th birthday at this same house in 1988.
        """
    },
    # 388 Flax Hill Rd
    "5-78-3-0": {
        "Notes": f"""
        This house has a Norwalk Historical Society plaque that reads "Lewis Raymond Sr House c. 1810".
        This house is wood framed, but Lewis Raymond Jr was a brickmason, so his nearby house at
        26 Keeler is made of brick.<p>
        In the 1930s this was the home of Douglas Pairman Hall, a well-known architect specializing
        in theaters, and his wife Aimee Green Hall.
        """
    },
    # 398 Flax Hill Rd
    "5-78-2-0": {
        "Notes": f"""
        Alexander Getner (1873-1954) was a florist at the Traendly greenhouses. He and his wife
        Magdelena lived here or hereabouts from the early 1900s until Magdelena died in 1962.
        A map from 1923 shows that "Aleck & Megy" Getner owned much of the adjoining land that
        is now Primrose Court and Iris Court.<p>
        Alexander's sister Augusta was married to John Zilske. The Zilskes lived across Flax Hill,
        and John was also a gardener at Traendly's.
        """
    },
    # 459 Flax Hill Rd
    "5-72-3-0": {
        "Notes": f"""
        This was the old location of Brookside School, one of the oldest schools in Norwalk.
        It is unclear when it opened, but in 1901 Samuel Richards Reed spoke about attending
        the school back in 1847, so it was open by then, at least. The school was shut down in
        1939, and its replacement opened on Highland Ave. in 1954.<p>
        This property was later purchased by Harry J. Getner, the president of the
        Connecticut Ice Machine Company, who had attended the school as a child. In the
        1960s he remodeled the building, keeping its character but giving it a new life as a
        residence.
        """
    }, 
    # 51 Rampart Rd
    "5-73A-14-0": {
        "Notes": f"""
        This was originally built as the Photography Studio of Alice B. Shaw. Shaw had
        previously been the manager of Manugian's in South Norwalk, and had a long portrait
        photography career. Alice Shaw's husband was real estate developer Godfrey Shaw. The
        two of them lived at 23 Westview Lane, and there was a convenient path through the
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
        James Augustine Farrell, the President of U.S. Steel, first built a mansion on this
        property in 1913. That mansion immediately burned down, so in 1916 he built a second
        one, and that one's still standing (see the whole story at
        <a href="https://www.historicrowayton.org/the-farrell-estate-rock-ledge">Historic
        Rowayton</a>).<p>
        After the Farrells died in the early 1940s, Darien resident James Rand, the
        Chairman of Remington-Rand, bought the mansion as a headquarters for his company.
        The first practical commercial computer, the UNIVAC I, was developed in the barns
        across Highland Ave, now the Rowayton Library. Post-war Remington-Rand executives
        Douglas MacArthur and Leslie R. Groves worked out of this location.
        """,
        "valid_from": 1913,
        "YearBuilt": 1913,
    },
    # 284 Highland Ave
    "5-81-157-0": {
        "Notes": f"""
        This home has a historical plaque identifying it as the "William H Lockwood House
        c. 1870". In 1878, Lockwood was living here with his parents-in-law Dilazon and
        Hannah Allen. They were the first people alerted when their neighbor
        <a href="https://www.rotonhill.com/the-case-of-the-miserly-millionaire">Johan
        Heinrich Schulte was brutally murdered.</a>.
        """
    },
    # 297 Highland Ave
    "5-80-30-0": {
        "Notes": f"""
        This home was built by Ira Ford Hoyt (1824-1887), who was a lumber dealer and builder.
        His mother Hannah Smith Hoyt lived up the street in 354 Highland Ave, and his
        namesake Captain Ira Ford lived in 347 Flax Hill Rd.<p>
        Ira's son Dudley Ely Hoyt (1866-1921) eventually took over the house. He was also a builder,
        who among other things built the original Norwalk Yacht Club building. Dudley must have
        named after Dudley Pettibone Ely, the first mayor of South Norwalk.<p>
        Dudley had a
        daughter named Margaret Rachel Hoyt (1905-2001), later known as Margaret Hoyt Smith.
        Margaret became the first female architect in Norwalk. She designed a part of
        the cap of the Chrysler building, the Norwalk Historical Society Museum, and a number of
        houses in Rowayton. Margaret took over the family home from her parents and raised her
        children there. In 1959 she sold the land to the city so it could build Brien McMahon
        High School. The 100-year-old house was moved across the street to its present location.
        """
    },
    # 354 Highland Ave
    "5-81-1-0": {
        "Notes": f"""
        This was the home Aaron Gregory Hoyt and his wife Hannah Smith Bouton. Aaron died in
        1836, and Hannah lived here until her death in 1873. Their son Ira Ford Hoyt, who
        would eventually live down the street at 297 Highland Ave, was named after their
        brother-in-law Captain Ira Ford. Hannah's sister Phebe went to Troy to marry the
        steamboat Captain, but when he retired they moved back to Norwalk in 347 Flax Hill
        Rd, just up the street.<p>
        Aaron and Hannah are buried in the tiny Hoyt-Bouton Cemetery on Witch Lane.
        """,
    },
    # 26 Keeler Ave
    "5-73B-1A-0": {
        "Notes": f"""
        A Norwalk Historical Society plaque on this house says "Lewis Raymond Jr. House 1829".
        Lewis Raymond Jr. was a brickmason, and this is accordingly a brick house. In fact,
        it is generally regarded as the first brick house built in Norwalk. Lewis Raymond Sr
        lived nearby at 388 Flax Hill Rd, according to the plaque on that house.
        """
    },
    # 23 Richards Ave
    "5-71-14-0": {
        "YearBuilt": 1957,
        "valid_from": 1957,
        "Notes": f"""
        This is <a href="https://www.reynoldsfarms.net/">Reynolds Farms Nursery</a>. Reynolds
        Farms was originally on Scribner, and was consumed by the construction of I-95. The
        business was taken over by an employee and moved to the present location.
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
    # Explicitly add some features
    features.extend(ADDED_FEATURES)

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

    sys.stderr.write(f"Added {len(ADDED_FEATURES)} features\n")
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
