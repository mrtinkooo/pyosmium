# Bangkok POI Data Extraction with PyOsmium

This project uses [pyosmium](https://github.com/osmcode/pyosmium) to extract detailed information from OpenStreetMap data for Bangkok province, Thailand. Currently supports extraction of:

- **Restaurants** - Detailed restaurant information including cuisine, amenities, and contact details
- **Rail Stations** - Train, subway, BTS, MRT, and light rail stations
- **Bus Stops** - Public bus stops and bus stations

## Quick Start

```bash
# 1. Install pyosmium
pip install osmium

# 2. Download Bangkok OSM data
wget https://download.geofabrik.de/asia/thailand-latest.osm.pbf

# 3. Extract restaurants
python extract_bangkok_restaurants.py thailand-latest.osm.pbf

# 4. Extract transit (rail stations and bus stops)
python extract_bangkok_transit.py thailand-latest.osm.pbf

# 5. Results will be in CSV and JSON files
# - thailand-latest_restaurants.csv / .json
# - thailand-latest_rail_stations.csv / .json
# - thailand-latest_bus_stops.csv / .json
# - thailand-latest_all_transit.csv / .json
```

## Overview

PyOsmium is a Python library that provides fast and flexible bindings to the Libosmium C++ library for working with OpenStreetMap data. This project demonstrates how to use pyosmium to extract specific point-of-interest data from OSM files.

## Features

### Restaurant Extraction (`extract_bangkok_restaurants.py`)

- **Comprehensive Data Extraction**: Extracts 30+ attributes per restaurant including:
  - Names (English, Thai, and default)
  - Location coordinates (latitude/longitude)
  - Cuisine types
  - Contact information (phone, website)
  - Address details (street, district, postcode)
  - Amenities (outdoor seating, takeaway, delivery, WiFi, A/C)
  - Accessibility (wheelchair access)
  - Business hours
  - And more...

### Transit Extraction (`extract_bangkok_transit.py`)

- **Rail Stations**: Extracts all types of rail transit including:
  - BTS Skytrain stations
  - MRT Subway stations
  - Train stations and halts
  - Light rail and tram stops
  - Monorail stations
  - Station codes, line colors, and network information

- **Bus Stops**: Extracts public bus infrastructure including:
  - Regular bus stops
  - Bus stations
  - Route references
  - Stop facilities (shelter, bench, lighting)

- **Comprehensive Attributes**: For each transit point:
  - Precise coordinates (latitude/longitude)
  - Names in multiple languages (EN, TH)
  - Network and operator information
  - Accessibility features
  - Facilities and amenities

### Common Features

- **Multiple OSM Entity Types**: Handles data represented as nodes, ways, and relations
- **Dual Output Formats**: Exports data to both CSV and JSON formats
- **Detailed Statistics**: Provides insights about extracted data
- **Fast Processing**: Leverages pyosmium's C++ backend for efficient processing

## Requirements

- Python 3.8+
- pyosmium library

## Installation

1. **Clone this repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd pyosmium
   ```

2. **Install pyosmium**:
   ```bash
   pip install osmium
   ```

## Getting OSM Data for Bangkok

You have several options to obtain OpenStreetMap data for Bangkok:

### Option 1: Geofabrik (Recommended for large areas)

Download pre-processed OSM data from Geofabrik:

1. Visit [Geofabrik Thailand](https://download.geofabrik.de/asia/thailand.html)
2. Download `thailand-latest.osm.pbf` (entire Thailand, ~200MB)
3. Or look for Bangkok-specific extracts if available

```bash
wget https://download.geofabrik.de/asia/thailand-latest.osm.pbf
```

### Option 2: BBBike Extract

BBBike offers custom city extracts:

1. Visit [BBBike Bangkok](https://extract.bbbike.org/)
2. Select Bangkok area on the map
3. Choose format (PBF recommended)
4. Download the extract

### Option 3: Overpass API (For smaller/custom areas)

Use Overpass Turbo for custom queries:

1. Visit [Overpass Turbo](https://overpass-turbo.eu/)
2. Use this query for Bangkok restaurants:

```overpass
[out:xml][timeout:300];
area["name:en"="Bangkok"]["admin_level"="4"]->.searchArea;
(
  node["amenity"="restaurant"](area.searchArea);
  way["amenity"="restaurant"](area.searchArea);
  relation["amenity"="restaurant"](area.searchArea);
);
out body;
>;
out skel qt;
```

3. Export as OSM XML or use the Overpass API directly

### Option 4: osmium-tool for filtering

If you have Thailand data and want only Bangkok:

```bash
# Install osmium-tool
apt-get install osmium-tool

# Extract Bangkok area (you'll need a polygon file)
osmium extract -p bangkok.poly thailand-latest.osm.pbf -o bangkok.osm.pbf
```

## Usage

### Extracting Restaurants

Run the restaurant extraction script with an OSM file:

```bash
python extract_bangkok_restaurants.py <osm_file>
```

**Examples:**

```bash
# Using Thailand PBF file
python extract_bangkok_restaurants.py thailand-latest.osm.pbf

# Using Bangkok extract
python extract_bangkok_restaurants.py bangkok.osm.pbf

# Using OSM XML file
python extract_bangkok_restaurants.py bangkok.osm
```

### Extracting Transit (Rail Stations & Bus Stops)

Run the transit extraction script with an OSM file:

```bash
python extract_bangkok_transit.py <osm_file>
```

**Examples:**

```bash
# Using Thailand PBF file
python extract_bangkok_transit.py thailand-latest.osm.pbf

# Using Bangkok extract
python extract_bangkok_transit.py bangkok.osm.pbf
```

### Output

#### Restaurant Output

The restaurant script generates two output files:

1. **CSV file** (`<input>_restaurants.csv`): Spreadsheet-compatible format
2. **JSON file** (`<input>_restaurants.json`): Machine-readable structured data

Example restaurant output structure:

```json
{
  "osm_type": "node",
  "osm_id": 123456789,
  "name": "Som Tam Nua",
  "name_en": "Som Tam Nua",
  "name_th": "ส้มตำนัว",
  "amenity": "restaurant",
  "cuisine": "thai;isaan",
  "latitude": 13.7465,
  "longitude": 100.5308,
  "phone": "+66 2 xxx xxxx",
  "website": "https://example.com",
  "opening_hours": "11:00-22:00",
  "street": "Siam Square Soi 5",
  "district": "Pathum Wan",
  "province": "Bangkok",
  "outdoor_seating": "yes",
  "air_conditioning": "yes"
}
```

#### Transit Output

The transit script generates **six output files**:

**Rail Stations:**
1. `<input>_rail_stations.csv` - All rail stations in CSV format
2. `<input>_rail_stations.json` - All rail stations in JSON format

**Bus Stops:**
3. `<input>_bus_stops.csv` - All bus stops in CSV format
4. `<input>_bus_stops.json` - All bus stops in JSON format

**Combined:**
5. `<input>_all_transit.csv` - All transit points in CSV format
6. `<input>_all_transit.json` - All transit points in JSON format

Example rail station output:

```json
{
  "osm_type": "node",
  "osm_id": 987654321,
  "type": "rail_station",
  "transit_type": "BTS Skytrain",
  "name": "Siam",
  "name_en": "Siam",
  "name_th": "สยาม",
  "latitude": 13.7465,
  "longitude": 100.5348,
  "network": "BTS",
  "operator": "Bangkok Mass Transit System",
  "line": "Sukhumvit Line;Silom Line",
  "ref": "CEN",
  "colour": "green;dark_green",
  "wheelchair": "yes",
  "platforms": "4"
}
```

Example bus stop output:

```json
{
  "osm_type": "node",
  "osm_id": 456789123,
  "type": "bus_stop",
  "transit_type": "Bus",
  "name": "Victory Monument",
  "name_en": "Victory Monument",
  "name_th": "อนุสาวรีย์ชัยสมรภูมิ",
  "latitude": 13.7649,
  "longitude": 100.5375,
  "operator": "BMTA",
  "route_ref": "26;27;28;29",
  "shelter": "yes",
  "bench": "yes",
  "wheelchair": "yes"
}
```

## Data Fields Extracted

### Restaurant Data Fields

The restaurant script extracts the following information when available:

**Basic Information:**
- OSM type (node/way/relation) and ID
- Name (default, English, Thai)
- Amenity type (restaurant/fast_food)

**Location:**
- Latitude and longitude
- Full address
- Street, house number
- District, subdistrict
- City, province, postcode

**Cuisine & Dining:**
- Cuisine type(s)
- Dietary options (vegetarian, etc.)
- Capacity
- Star rating
- Brand

**Contact & Hours:**
- Phone number
- Website
- Opening hours
- Description

**Amenities:**
- Outdoor seating
- Takeaway availability
- Delivery service
- Wheelchair accessibility
- Internet access
- Air conditioning
- Smoking policy

### Transit Data Fields

The transit script extracts the following information when available:

**Rail Stations:**
- OSM type (node/way/relation) and ID
- Transit type (BTS Skytrain, MRT Subway, Train Station, etc.)
- Name (default, English, Thai)
- **Coordinates (latitude/longitude)**
- Network and operator information
- Line name(s) and color(s)
- Station code/reference
- Number of platforms
- Layer and level information
- Accessibility (wheelchair, toilets)
- Facilities (shelter, bench, lighting, covered)
- Website and opening hours
- Address details

**Bus Stops:**
- OSM type (node/way/relation) and ID
- Transit type (Bus)
- Name (default, English, Thai)
- **Coordinates (latitude/longitude)**
- Network and operator
- Route references (which routes serve this stop)
- Local stop ID/reference
- Facilities (shelter, bench, lighting, covered)
- Accessibility (wheelchair, tactile paving)
- Amenities (departures board, timetable, bin)
- Surface type
- Address details

## Understanding the Statistics

The script outputs helpful statistics:

```
==========================================================
EXTRACTION STATISTICS
==========================================================
Total restaurants found: 1,234

By OSM type:
  node: 1,100
  way: 130
  relation: 4

With names: 956 (77.5%)
With coordinates: 1,200 (97.2%)
With cuisine info: 487 (39.5%)

Top 10 cuisines:
  thai: 345
  japanese: 89
  italian: 67
  chinese: 54
  ...
==========================================================
```

## Tips for Better Results

1. **Use PBF format**: Faster to process than XML
2. **Bangkok-specific extracts**: Smaller files = faster processing
3. **Check data freshness**: Download recent extracts for up-to-date information
4. **Post-processing**: Consider filtering by:
   - Coordinates (to ensure Bangkok boundaries)
   - Name presence (to get named establishments)
   - Specific cuisines or amenities

## Advanced Usage

### Filtering by specific criteria

You can modify the script to add additional filters. For example, to extract only Thai restaurants:

```python
def _is_restaurant(self, tags_dict: Dict[str, str]) -> bool:
    """Check if the entity is a Thai restaurant."""
    amenity = tags_dict.get('amenity', '')
    cuisine = tags_dict.get('cuisine', '')
    return amenity == 'restaurant' and 'thai' in cuisine.lower()
```

### Processing multiple files

```bash
# Process multiple files
for file in *.osm.pbf; do
    python extract_bangkok_restaurants.py "$file"
done
```

## OpenStreetMap Data Structure

Understanding OSM data helps interpret results:

- **Nodes**: Points with coordinates (most restaurants are nodes)
- **Ways**: Polylines or polygons (buildings, areas)
- **Relations**: Logical groupings of nodes/ways

Restaurant tags in OSM:
- `amenity=restaurant`: Sit-down restaurant
- `amenity=fast_food`: Fast food establishment
- `cuisine=*`: Type of cuisine served
- Many other tags for details

## Troubleshooting

**Issue**: Script runs but finds no restaurants
- **Solution**: Verify the OSM file contains Bangkok data and has restaurant tags

**Issue**: Missing coordinates for some restaurants
- **Solution**: This is normal for ways/relations. Consider calculating centroids.

**Issue**: Many restaurants have no name
- **Solution**: This reflects OSM data quality. Consider contributing to OSM to improve data.

**Issue**: Memory errors with large files
- **Solution**: Use a Bangkok-specific extract instead of all of Thailand

## Contributing to OpenStreetMap

If you find missing or incorrect data, consider contributing back to OpenStreetMap:

1. Create an account at [openstreetmap.org](https://www.openstreetmap.org)
2. Use the online editor to add/update restaurant information
3. Help improve data quality for everyone

## Resources

- [PyOsmium Documentation](https://osmcode.org/pyosmium/)
- [OpenStreetMap Wiki - Restaurants](https://wiki.openstreetmap.org/wiki/Tag:amenity%3Drestaurant)
- [OSM Tag Info](https://taginfo.openstreetmap.org/)
- [Geofabrik Downloads](https://download.geofabrik.de/)
- [Overpass API](https://overpass-api.de/)

## License

This project is released under the MIT License. OpenStreetMap data is © OpenStreetMap contributors and available under the Open Database License (ODbL).

## Acknowledgments

- [pyosmium](https://github.com/osmcode/pyosmium) - Python bindings for Libosmium
- [OpenStreetMap](https://www.openstreetmap.org) - Collaborative map data
- [Geofabrik](https://www.geofabrik.de/) - OSM data extracts
