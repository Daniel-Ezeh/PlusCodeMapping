import geopandas as gpd
from shapely.geometry import Point, Polygon
from openlocationcode import openlocationcode as olc
import pandas as pd
import numpy as np
import multiprocessing


# Load the GeoJSON of Nig states
gdf = gpd.read_file("gadm41_NGA_1.json")

# Combine all state geometries to create a single Nig boundary
ng_boundary = gdf.unary_union  # Create a single MultiPolygon that represents the entire Nig


# Define a function to create a grid of lat/lon points
def generate_grid(min_lat, max_lat, min_lon, max_lon, step_lat, step_lon):
    latitudes = np.arange(min_lat, max_lat, step_lat)
    longitudes = np.arange(min_lon, max_lon, step_lon)
    return [(lat, lon) for lat in latitudes for lon in longitudes]

# Define the function that will run in parallel
def process_chunk(chunk, gdf):
    results = []
    plus_codes_by_state = {}
    for lat, lon in chunk:
        print("%"*20)
        plus_code = olc.encode(lat, lon, 6)
        plus_code_details = olc.decode(plus_code)
        # point = Point(lon, lat)
        point = Point(plus_code_details.longitudeCenter, plus_code_details.latitudeCenter)

        # Create a polygon (bounding box) using lat/lon bounds
        polygon = Polygon([
            (plus_code_details.longitudeLo, plus_code_details.latitudeLo),
            (plus_code_details.longitudeLo, plus_code_details.latitudeHi),
            (plus_code_details.longitudeHi, plus_code_details.latitudeHi),
            (plus_code_details.longitudeHi, plus_code_details.latitudeLo)
        ])

        # Create a dictionary for plus code details
        plus_code_details_dict = {
            "codeLength": plus_code_details.codeLength,
            "latitudeCenter": plus_code_details.latitudeCenter,
            "latitudeHi": plus_code_details.latitudeHi,
            "latitudeLo": plus_code_details.latitudeLo,
            "longitudeCenter": plus_code_details.longitudeCenter,
            "longitudeHi": plus_code_details.longitudeHi,
            "longitudeLo": plus_code_details.longitudeLo
        }


        # Check if the polygon is within the Nig boundary
        if ng_boundary.contains(point):
            # Check which state this point belongs to
            for idx, row in gdf.iterrows():
                if row['geometry'].contains(point):
                # and row['geometry'].intersects(polygon):
                    print("YES "*20)
                    state_name = row['NAME_1']  # Assumed column name for state
                    if state_name not in plus_codes_by_state:
                        print("NO "*20)
                        plus_codes_by_state[state_name] = []

                    # Append data as a dictionary to results list
                    results.append({
                        'pluscode': plus_code,
                        'state': state_name,
                        'geometry': polygon.wkt,  # Store the geometry as Well-Known Text (WKT)
                        'pluscodeDetails': plus_code_details_dict 
                    })
                    break
        else:
            # Label as "offshore" if the polygon is outside the Nig boundary
            results.append({
                'pluscode': plus_code,
                'state': 'offshore',
                'geometry': polygon.wkt,  # Store the polygon as Well-Known Text (WKT)
                'pluscodeDetails': plus_code_details_dict  # Store the dictionary directly
            })

    return results


def merge_results(results):
    merged = []
    for result in results:
        merged.extend(result)  # Combine all the lists of dictionaries
    return merged


# Main block to prevent multiprocessing errors
if __name__ == '__main__':
    # Generate grid for Nig (coordinates are approximate)
    min_lat, max_lat  = 4.17, 14.01
    min_lon, max_lon = 2.58, 14.72
  
    step_lat = 0.009 
    step_lng = 0.014
    grid_points = generate_grid(min_lat, max_lat, min_lon, max_lon, step_lat, step_lng)

    # Split grid points into chunks for parallel processing
    num_chunks = multiprocessing.cpu_count()  # Use as many chunks as there are CPU cores
    chunks = np.array_split(grid_points, num_chunks)

    # Create a multiprocessing pool
    with multiprocessing.Pool() as pool:
        # Distribute chunks of data to the pool
        results = pool.starmap(process_chunk, [(chunk, gdf) for chunk in chunks])

    # Merge the results from all processes
    final = merge_results(results)

    # Convert the merged results to a DataFrame
    df = pd.DataFrame(final)

    # # Drop duplicate rows based on 'pluscode', 'geometry' and 'state'
    df = df.drop_duplicates(subset=['pluscode', 'state', 'geometry'])

    # Save the DataFrame to a CSV file
    df.to_csv('plus_codes_by_state.csv', index=False)

    print("CSV file saved as 'plus_codes_by_state.csv'")
