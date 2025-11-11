#!/usr/bin/env python3
"""
Extract restaurant information from Bangkok OSM data using pyosmium.

This script processes OpenStreetMap data to extract detailed information about
restaurants in Bangkok province, including names, locations, cuisines, and other
relevant details.
"""

import osmium
import csv
import json
from collections import defaultdict
from typing import Dict, List, Any


class RestaurantHandler(osmium.SimpleHandler):
    """
    Handler to extract restaurant data from OSM files.

    This handler processes nodes, ways, and relations tagged with amenity=restaurant
    and extracts detailed information about each restaurant.
    """

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.restaurants = []
        self.way_nodes = {}  # Store way geometries for calculating centroids

    def _extract_tags(self, tags) -> Dict[str, str]:
        """Extract all tags as a dictionary."""
        return {tag.k: tag.v for tag in tags}

    def _is_restaurant(self, tags_dict: Dict[str, str]) -> bool:
        """Check if the entity is a restaurant."""
        amenity = tags_dict.get('amenity', '')
        # Include restaurants and fast_food as they're both food establishments
        return amenity in ['restaurant', 'fast_food']

    def _extract_restaurant_info(self, osm_type: str, osm_id: int,
                                 location, tags_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract restaurant information from tags.

        Args:
            osm_type: Type of OSM element (node, way, relation)
            osm_id: OSM ID
            location: Location object (for nodes) or None
            tags_dict: Dictionary of tags

        Returns:
            Dictionary containing restaurant information
        """
        info = {
            'osm_type': osm_type,
            'osm_id': osm_id,
            'name': tags_dict.get('name', 'N/A'),
            'name_en': tags_dict.get('name:en', ''),
            'name_th': tags_dict.get('name:th', ''),
            'amenity': tags_dict.get('amenity', ''),
            'cuisine': tags_dict.get('cuisine', ''),
            'diet': tags_dict.get('diet:vegetarian', ''),
            'phone': tags_dict.get('phone', ''),
            'website': tags_dict.get('website', ''),
            'opening_hours': tags_dict.get('opening_hours', ''),
            'address': tags_dict.get('addr:full', ''),
            'street': tags_dict.get('addr:street', ''),
            'housenumber': tags_dict.get('addr:housenumber', ''),
            'postcode': tags_dict.get('addr:postcode', ''),
            'district': tags_dict.get('addr:district', ''),
            'subdistrict': tags_dict.get('addr:subdistrict', ''),
            'province': tags_dict.get('addr:province', ''),
            'city': tags_dict.get('addr:city', ''),
            'outdoor_seating': tags_dict.get('outdoor_seating', ''),
            'takeaway': tags_dict.get('takeaway', ''),
            'delivery': tags_dict.get('delivery', ''),
            'wheelchair': tags_dict.get('wheelchair', ''),
            'internet_access': tags_dict.get('internet_access', ''),
            'air_conditioning': tags_dict.get('air_conditioning', ''),
            'smoking': tags_dict.get('smoking', ''),
            'capacity': tags_dict.get('capacity', ''),
            'stars': tags_dict.get('stars', ''),
            'brand': tags_dict.get('brand', ''),
            'description': tags_dict.get('description', ''),
        }

        # Add location if available (for nodes)
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

        if self._is_restaurant(tags_dict):
            restaurant_info = self._extract_restaurant_info(
                'node', n.id, n.location, tags_dict
            )
            self.restaurants.append(restaurant_info)

    def way(self, w):
        """Process OSM ways."""
        tags_dict = self._extract_tags(w.tags)

        if self._is_restaurant(tags_dict):
            # Calculate centroid for ways
            try:
                # Get the first node's location as approximate center
                # For more accurate centroid, we'd need to average all nodes
                nodes = list(w.nodes)
                if nodes and nodes[0].location.valid():
                    location = nodes[0].location
                else:
                    location = None
            except:
                location = None

            restaurant_info = self._extract_restaurant_info(
                'way', w.id, location, tags_dict
            )
            self.restaurants.append(restaurant_info)

    def relation(self, r):
        """Process OSM relations."""
        tags_dict = self._extract_tags(r.tags)

        if self._is_restaurant(tags_dict):
            # Relations don't have direct locations
            restaurant_info = self._extract_restaurant_info(
                'relation', r.id, None, tags_dict
            )
            self.restaurants.append(restaurant_info)


def save_to_csv(restaurants: List[Dict[str, Any]], filename: str):
    """Save restaurant data to CSV file."""
    if not restaurants:
        print("No restaurants found to save.")
        return

    # Get all unique keys from all restaurants
    all_keys = set()
    for restaurant in restaurants:
        all_keys.update(restaurant.keys())

    fieldnames = sorted(list(all_keys))

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(restaurants)

    print(f"✓ Saved {len(restaurants)} restaurants to {filename}")


def save_to_json(restaurants: List[Dict[str, Any]], filename: str):
    """Save restaurant data to JSON file."""
    if not restaurants:
        print("No restaurants found to save.")
        return

    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(restaurants, jsonfile, indent=2, ensure_ascii=False)

    print(f"✓ Saved {len(restaurants)} restaurants to {filename}")


def print_statistics(restaurants: List[Dict[str, Any]]):
    """Print statistics about extracted restaurants."""
    if not restaurants:
        print("No restaurants found.")
        return

    print(f"\n{'='*60}")
    print(f"EXTRACTION STATISTICS")
    print(f"{'='*60}")
    print(f"Total restaurants found: {len(restaurants)}")

    # Count by type
    type_counts = defaultdict(int)
    for r in restaurants:
        type_counts[r['osm_type']] += 1

    print(f"\nBy OSM type:")
    for osm_type, count in sorted(type_counts.items()):
        print(f"  {osm_type}: {count}")

    # Count with names
    named = sum(1 for r in restaurants if r['name'] != 'N/A')
    print(f"\nWith names: {named} ({named/len(restaurants)*100:.1f}%)")

    # Count with locations
    with_location = sum(1 for r in restaurants if r['latitude'] is not None)
    print(f"With coordinates: {with_location} ({with_location/len(restaurants)*100:.1f}%)")

    # Count with cuisine info
    with_cuisine = sum(1 for r in restaurants if r['cuisine'])
    print(f"With cuisine info: {with_cuisine} ({with_cuisine/len(restaurants)*100:.1f}%)")

    # Top cuisines
    cuisines = defaultdict(int)
    for r in restaurants:
        if r['cuisine']:
            # Handle multiple cuisines separated by semicolon
            for cuisine in r['cuisine'].split(';'):
                cuisines[cuisine.strip()] += 1

    if cuisines:
        print(f"\nTop 10 cuisines:")
        for cuisine, count in sorted(cuisines.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {cuisine}: {count}")

    print(f"{'='*60}\n")


def main():
    """Main function to extract restaurant data."""
    import sys
    import os

    if len(sys.argv) < 2:
        print("Usage: python extract_bangkok_restaurants.py <osm_file.pbf|osm.xml>")
        print("\nExample:")
        print("  python extract_bangkok_restaurants.py bangkok_thailand.osm.pbf")
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
    print("This may take a few minutes depending on file size...\n")

    # Create handler and process file
    handler = RestaurantHandler()

    try:
        handler.apply_file(osm_file, locations=True)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

    # Print statistics
    print_statistics(handler.restaurants)

    # Save to files
    base_name = os.path.splitext(os.path.basename(osm_file))[0]
    csv_filename = f"{base_name}_restaurants.csv"
    json_filename = f"{base_name}_restaurants.json"

    save_to_csv(handler.restaurants, csv_filename)
    save_to_json(handler.restaurants, json_filename)

    print(f"\n✓ Done! Restaurant data extracted successfully.")
    print(f"\nOutput files:")
    print(f"  - {csv_filename}")
    print(f"  - {json_filename}")


if __name__ == '__main__':
    main()
