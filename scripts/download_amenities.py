import fire
import requests
import json
import pandas as pd
import re


OVERPASS_URL = "http://overpass-api.de/api/interpreter"
WHITESPACE_PATTERN = re.compile(r'\s+')


def get_amenities(amenity_type, central_point=(14.673671, 121.045322), radius=10000):
    """
    Sends a request to OSM via Overpass API to get amenities data within a certain radius around a given point
    for the specified amenity type
    
    Parameters
        amenity_type: Str, type of amenity, see list at https://wiki.openstreetmap.org/wiki/Key:amenity
        central_point: Tuple(float, float) default is around QC, give parameters (check from GMaps) if you want to explore other central point
        radius: in meters. Check from GMaps how far is the boundary of NCR from central point
    Returns:
        data: Dictionary JSON containing amenities data
    """
    
    print("Downloading amenities data via Overpass API...")
          
    overpass_query = f"""
      [out:json];
      ( node['amenity'='{amenity_type}'](around:{radius},{central_point[0]}, {central_point[1]});
        way['amenity'='{amenity_type}'](around:{radius},{central_point[0]}, {central_point[1]});
        rel['amenity'='{amenity_type}'](around:{radius},{central_point[0]}, {central_point[1]});
      );
      out center;
      """
    
    try:
        response = requests.get(OVERPASS_URL, 
                              params={'data': overpass_query})
        data = response.json()
    except Exception as e:
        raise e
    return data


def is_blank_name(text):
    text = re.sub(WHITESPACE_PATTERN, '', text)
    return len(text) == 0


def transform_json_to_list(data):
    """
    Parameters:
        data: Dictionary JSON containing amenities data
    Returns:
        amenities_data: Array of amenities data
        
        Example data:
        [{'amenity': 'Tourism Oriented Police Station, Donsol',
          'amenity_type': 'police',
          'id': 25679365,
          'lat': 12.911192,
          'lon': 123.588915},
          ...
    """
    
    print("Parsing data...")
    amenities = data['elements']
    print(f"{len(amenities)} amenities found!")

    amenities_data = []
    for amenity in amenities:
        amenity_data = {}
        amenity_data['id'] = amenity['id']
        
        # Do not include blank names
        amenity_name = amenity['tags'].get('name', '')
        if is_blank_name(amenity_name):
            continue
        
        amenity_data['amenity'] = amenity_name
        amenity_data['amenity_type'] = amenity['tags']['amenity']
        
        if 'center' in amenity:
            amenity_data['lat'] = amenity['center']['lat']
            amenity_data['lon'] = amenity['center']['lon']
        else:
            amenity_data['lat'] = amenity['lat']
            amenity_data['lon'] = amenity['lon']
            
        amenities_data.append(amenity_data)
    return amenities_data


def save_to_df(amenities_list, filename):
    """
    Parameters:
        amenities_list: Array of amenities data
        filename: filename to save csv
    """
    amenities_df = pd.DataFrame(amenities_list, 
                                columns=['id', 'lat', 'lon', 'amenity_type', 'amenity'])
    amenities_df.to_csv(filename, index=False)
    print(f"Saved file to {filename}")


def download_amenities(amenity_type='hospital', origin_x=14.673671, origin_y=121.045322, radius=10000):
    amenities_data_json = get_amenities(amenity_type=amenity_type,
                                        central_point=(origin_x, origin_y),
                                        radius=radius)

    amenities_list = transform_json_to_list(amenities_data_json)
    
    filename = f"./{amenity_type}.csv"
    save_to_df(amenities_list, filename)


if __name__ == "__main__":
    fire.Fire(download_amenities)