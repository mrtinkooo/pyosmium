#!/usr/bin/env python3
"""
Extract transit station information (rail stations and bus stops) from Bangkok OSM data using pyosmium.

This script processes OpenStreetMap data to extract detailed information about
rail stations (train, subway, BTS, MRT, etc.) and bus stops in Bangkok province,
including names, locations, transit types, and other relevant details.
"""

import osmium
import csv
import json
from collections import defaultdict
from typing import Dict, List, Any


class TransitHandler(osmium.SimpleHandler):
    """
    Handler to extract rail station and bus stop data from OSM files.

    This handler processes nodes, ways, and relations tagged with various
    public transport tags and extracts detailed information.
    """

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.rail_stations = []
        self.bus_stops = []

    def _extract_tags(self, tags) -> Dict[str, str]:
        """Extract all tags as a dictionary."""
        return {tag.k: tag.v for tag in tags}

    def _is_rail_station(self, tags_dict: Dict[str, str]) -> bool:
        """
        Check if the entity is a rail station.

        Includes: train stations, subway, light rail, tram, monorail, etc.
        """
        railway = tags_dict.get('railway', '')
        public_transport = tags_dict.get('public_transport', '')

        # Railway stations and stops
        rail_types = [
            'station',          # Main railway station
            'halt',             # Small railway stop
            'tram_stop',        # Tram stop
            'subway_entrance',  # Subway entrance
            'train_station_entrance',  # Station entrance
        ]

        # Check railway tag
        if railway in rail_types:
            return True

        # Check public_transport tag for station
        if public_transport == 'station':
            return True

        # Check for station tag with usage=main (sometimes used)
        if tags_dict.get('station') in ['subway', 'light_rail', 'monorail', 'train']:
            return True

        return False

    def _is_bus_stop(self, tags_dict: Dict[str, str]) -> bool:
        """
        Check if the entity is a bus stop.

        Includes: bus stops, bus stations, and bus platforms.
        """
        highway = tags_dict.get('highway', '')
        public_transport = tags_dict.get('public_transport', '')
        amenity = tags_dict.get('amenity', '')

        # Bus stop markers
        if highway == 'bus_stop':
            return True

        # Public transport stops/platforms for buses
        if public_transport in ['stop_position', 'platform']:
            # Check if it's for buses
            bus_tags = tags_dict.get('bus', '')
            if bus_tags == 'yes' or public_transport == 'stop_position':
                return True

        # Bus stations (larger facilities)
        if amenity == 'bus_station':
            return True

        return False

    def _get_transit_type(self, tags_dict: Dict[str, str]) -> str:
        """Determine the specific type of transit."""
        railway = tags_dict.get('railway', '')
        station = tags_dict.get('station', '')
        public_transport = tags_dict.get('public_transport', '')
        network = tags_dict.get('network', '')
        operator = tags_dict.get('operator', '')

        # Specific rail types
        if 'BTS' in network or 'BTS' in operator:
            return 'BTS Skytrain'
        if 'MRT' in network or 'MRT' in operator:
            return 'MRT Subway'
        if railway == 'subway_entrance' or station == 'subway':
            return 'Subway'
        if station == 'light_rail' or railway == 'tram_stop':
            return 'Light Rail/Tram'
        if station == 'monorail':
            return 'Monorail'
        if railway == 'station':
            return 'Train Station'
        if railway == 'halt':
            return 'Train Halt'

        # Default
        return railway or station or public_transport or 'Unknown'

    def _extract_rail_station_info(self, osm_type: str, osm_id: int,
                                   location, tags_dict: Dict[str, str]) -> Dict[str, Any]:
        """Extract rail station information from tags."""
        info = {
            'osm_type': osm_type,
            'osm_id': osm_id,
            'type': 'rail_station',
            'transit_type': self._get_transit_type(tags_dict),
            'name': tags_dict.get('name', 'N/A'),
            'name_en': tags_dict.get('name:en', ''),
            'name_th': tags_dict.get('name:th', ''),
            'railway': tags_dict.get('railway', ''),
            'station': tags_dict.get('station', ''),
            'public_transport': tags_dict.get('public_transport', ''),
            'network': tags_dict.get('network', ''),
            'operator': tags_dict.get('operator', ''),
            'line': tags_dict.get('line', ''),
            'ref': tags_dict.get('ref', ''),  # Station code/reference
            'colour': tags_dict.get('colour', ''),  # Line color
            'layer': tags_dict.get('layer', ''),
            'level': tags_dict.get('level', ''),
            'platforms': tags_dict.get('platforms', ''),
            'wheelchair': tags_dict.get('wheelchair', ''),
            'toilets': tags_dict.get('toilets', ''),
            'shelter': tags_dict.get('shelter', ''),
            'bench': tags_dict.get('bench', ''),
            'lit': tags_dict.get('lit', ''),
            'covered': tags_dict.get('covered', ''),
            'website': tags_dict.get('website', ''),
            'opening_hours': tags_dict.get('opening_hours', ''),
            'address': tags_dict.get('addr:full', ''),
            'street': tags_dict.get('addr:street', ''),
            'district': tags_dict.get('addr:district', ''),
            'subdistrict': tags_dict.get('addr:subdistrict', ''),
            'province': tags_dict.get('addr:province', ''),
        }

        # Add location
        if location and location.valid():
            info['latitude'] = location.lat
            info['longitude'] = location.lon
        else:
            info['latitude'] = None
            info['longitude'] = None

        return info

    def _extract_bus_stop_info(self, osm_type: str, osm_id: int,
                               location, tags_dict: Dict[str, str]) -> Dict[str, Any]:
        """Extract bus stop information from tags."""
        info = {
            'osm_type': osm_type,
            'osm_id': osm_id,
            'type': 'bus_stop',
            'transit_type': 'Bus',
            'name': tags_dict.get('name', 'N/A'),
            'name_en': tags_dict.get('name:en', ''),
            'name_th': tags_dict.get('name:th', ''),
            'highway': tags_dict.get('highway', ''),
            'public_transport': tags_dict.get('public_transport', ''),
            'amenity': tags_dict.get('amenity', ''),
            'network': tags_dict.get('network', ''),
            'operator': tags_dict.get('operator', ''),
            'route_ref': tags_dict.get('route_ref', ''),  # Bus routes serving this stop
            'local_ref': tags_dict.get('local_ref', ''),  # Local stop ID
            'ref': tags_dict.get('ref', ''),
            'shelter': tags_dict.get('shelter', ''),
            'bench': tags_dict.get('bench', ''),
            'lit': tags_dict.get('lit', ''),
            'covered': tags_dict.get('covered', ''),
            'wheelchair': tags_dict.get('wheelchair', ''),
            'tactile_paving': tags_dict.get('tactile_paving', ''),
            'departures_board': tags_dict.get('departures_board', ''),
            'timetable': tags_dict.get('timetable', ''),
            'bin': tags_dict.get('bin', ''),
            'surface': tags_dict.get('surface', ''),
            'address': tags_dict.get('addr:full', ''),
            'street': tags_dict.get('addr:street', ''),
            'district': tags_dict.get('addr:district', ''),
            'subdistrict': tags_dict.get('addr:subdistrict', ''),
            'province': tags_dict.get('addr:province', ''),
        }

        # Add location
        if location and location.valid():
            info['latitude'] = location.lat
            info['longitude'] = location.lon
        else:
            info['latitude'] = None
            info['longitude'] = None

        return info

    def node(self, n):
        """Process OSM nodes."""
        tags_dict = self._extract_tags(n.tags)

        if self._is_rail_station(tags_dict):
            station_info = self._extract_rail_station_info(
                'node', n.id, n.location, tags_dict
            )
            self.rail_stations.append(station_info)
        elif self._is_bus_stop(tags_dict):
            stop_info = self._extract_bus_stop_info(
                'node', n.id, n.location, tags_dict
            )
            self.bus_stops.append(stop_info)

    def way(self, w):
        """Process OSM ways."""
        tags_dict = self._extract_tags(w.tags)

        # Get approximate location from first node
        try:
            nodes = list(w.nodes)
            if nodes and nodes[0].location.valid():
                location = nodes[0].location
            else:
                location = None
        except:
            location = None

        if self._is_rail_station(tags_dict):
            station_info = self._extract_rail_station_info(
                'way', w.id, location, tags_dict
            )
            self.rail_stations.append(station_info)
        elif self._is_bus_stop(tags_dict):
            stop_info = self._extract_bus_stop_info(
                'way', w.id, location, tags_dict
            )
            self.bus_stops.append(stop_info)

    def relation(self, r):
        """Process OSM relations."""
        tags_dict = self._extract_tags(r.tags)

        if self._is_rail_station(tags_dict):
            station_info = self._extract_rail_station_info(
                'relation', r.id, None, tags_dict
            )
            self.rail_stations.append(station_info)
        elif self._is_bus_stop(tags_dict):
            stop_info = self._extract_bus_stop_info(
                'relation', r.id, None, tags_dict
            )
            self.bus_stops.append(stop_info)


def save_to_csv(data: List[Dict[str, Any]], filename: str):
    """Save data to CSV file."""
    if not data:
        print(f"No data found to save to {filename}.")
        return

    # Get all unique keys
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())

    fieldnames = sorted(list(all_keys))

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"✓ Saved {len(data)} items to {filename}")


def save_to_json(data: List[Dict[str, Any]], filename: str):
    """Save data to JSON file."""
    if not data:
        print(f"No data found to save to {filename}.")
        return

    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(data)} items to {filename}")


def print_rail_statistics(stations: List[Dict[str, Any]]):
    """Print statistics about extracted rail stations."""
    if not stations:
        print("No rail stations found.")
        return

    print(f"\n{'='*60}")
    print(f"RAIL STATION STATISTICS")
    print(f"{'='*60}")
    print(f"Total rail stations found: {len(stations)}")

    # Count by OSM type
    type_counts = defaultdict(int)
    for s in stations:
        type_counts[s['osm_type']] += 1

    print(f"\nBy OSM type:")
    for osm_type, count in sorted(type_counts.items()):
        print(f"  {osm_type}: {count}")

    # Count by transit type
    transit_counts = defaultdict(int)
    for s in stations:
        transit_counts[s['transit_type']] += 1

    print(f"\nBy transit type:")
    for transit_type, count in sorted(transit_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {transit_type}: {count}")

    # Count with names
    named = sum(1 for s in stations if s['name'] != 'N/A')
    print(f"\nWith names: {named} ({named/len(stations)*100:.1f}%)")

    # Count with locations
    with_location = sum(1 for s in stations if s['latitude'] is not None)
    print(f"With coordinates: {with_location} ({with_location/len(stations)*100:.1f}%)")

    # Count by network
    networks = defaultdict(int)
    for s in stations:
        if s['network']:
            networks[s['network']] += 1

    if networks:
        print(f"\nBy network:")
        for network, count in sorted(networks.items(), key=lambda x: x[1], reverse=True):
            print(f"  {network}: {count}")

    # Count by operator
    operators = defaultdict(int)
    for s in stations:
        if s['operator']:
            operators[s['operator']] += 1

    if operators:
        print(f"\nBy operator:")
        for operator, count in sorted(operators.items(), key=lambda x: x[1], reverse=True):
            print(f"  {operator}: {count}")

    print(f"{'='*60}")


def print_bus_statistics(stops: List[Dict[str, Any]]):
    """Print statistics about extracted bus stops."""
    if not stops:
        print("\nNo bus stops found.")
        return

    print(f"\n{'='*60}")
    print(f"BUS STOP STATISTICS")
    print(f"{'='*60}")
    print(f"Total bus stops found: {len(stops)}")

    # Count by OSM type
    type_counts = defaultdict(int)
    for s in stops:
        type_counts[s['osm_type']] += 1

    print(f"\nBy OSM type:")
    for osm_type, count in sorted(type_counts.items()):
        print(f"  {osm_type}: {count}")

    # Count with names
    named = sum(1 for s in stops if s['name'] != 'N/A')
    print(f"\nWith names: {named} ({named/len(stops)*100:.1f}%)")

    # Count with locations
    with_location = sum(1 for s in stops if s['latitude'] is not None)
    print(f"With coordinates: {with_location} ({with_location/len(stops)*100:.1f}%)")

    # Count with shelter
    with_shelter = sum(1 for s in stops if s['shelter'] == 'yes')
    print(f"With shelter: {with_shelter} ({with_shelter/len(stops)*100:.1f}%)")

    # Count by operator
    operators = defaultdict(int)
    for s in stops:
        if s['operator']:
            operators[s['operator']] += 1

    if operators:
        print(f"\nBy operator:")
        for operator, count in sorted(operators.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {operator}: {count}")

    print(f"{'='*60}\n")


def main():
    """Main function to extract transit data."""
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python extract_bangkok_transit.py <osm_file.pbf|osm.xml>")
        print("\nExample:")
        print("  python extract_bangkok_transit.py bangkok_thailand.osm.pbf")
        print("\nTo download Bangkok OSM data:")
        print("  1. Visit: https://download.geofabrik.de/asia/thailand.html")
        print("  2. Download thailand-latest.osm.pbf (or use a Bangkok extract)")
        print("  3. Or use Overpass API for Bangkok-specific data")
        sys.exit(1)

    osm_file = sys.argv[1]

    if not os.path.exists(osm_file):
        print(f"Error: File '{osm_file}' not found.")
        sys.exit(1)

    print(f"Processing OSM file: {osm_file}")
    print("Extracting rail stations and bus stops...")
    print("This may take a few minutes depending on file size...\n")

    # Create handler and process file
    handler = TransitHandler()

    try:
        handler.apply_file(osm_file, locations=True)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

    # Print statistics
    print_rail_statistics(handler.rail_stations)
    print_bus_statistics(handler.bus_stops)

    # Save to files
    base_name = os.path.splitext(os.path.basename(osm_file))[0]

    # Save rail stations
    if handler.rail_stations:
        rail_csv = f"{base_name}_rail_stations.csv"
        rail_json = f"{base_name}_rail_stations.json"
        save_to_csv(handler.rail_stations, rail_csv)
        save_to_json(handler.rail_stations, rail_json)

    # Save bus stops
    if handler.bus_stops:
        bus_csv = f"{base_name}_bus_stops.csv"
        bus_json = f"{base_name}_bus_stops.json"
        save_to_csv(handler.bus_stops, bus_csv)
        save_to_json(handler.bus_stops, bus_json)

    # Save combined data
    all_transit = handler.rail_stations + handler.bus_stops
    if all_transit:
        combined_csv = f"{base_name}_all_transit.csv"
        combined_json = f"{base_name}_all_transit.json"
        save_to_csv(all_transit, combined_csv)
        save_to_json(all_transit, combined_json)

    print(f"\n✓ Done! Transit data extracted successfully.")
    print(f"\nOutput files:")
    if handler.rail_stations:
        print(f"  Rail stations:")
        print(f"    - {base_name}_rail_stations.csv")
        print(f"    - {base_name}_rail_stations.json")
    if handler.bus_stops:
        print(f"  Bus stops:")
        print(f"    - {base_name}_bus_stops.csv")
        print(f"    - {base_name}_bus_stops.json")
    if all_transit:
        print(f"  Combined:")
        print(f"    - {base_name}_all_transit.csv")
        print(f"    - {base_name}_all_transit.json")


if __name__ == '__main__':
    main()
