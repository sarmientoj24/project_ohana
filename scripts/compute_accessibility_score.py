import geopy
import geopy.distance as dist
import numpy as np
import fire


PANDAS_MP = True

# To use modin -- a library that wraps pandas for multi-core processing
if PANDAS_MP:
    # You need to install modin first
    # pip install "modin[ray]"
    import os
    os.environ["MODIN_ENGINE"] = "ray"
    import modin.pandas as pd
    from tqdm import tqdm
    
    from modin.config import ProgressBar
    ProgressBar.enable()
    
    import ray
    ray.init()
# Use ordinary pandas
else:
    import pandas as pd
    from tqdm import tqdm
    tqdm.pandas()


def get_distance_in_km_gc(pointA, pointB):
    """
    Calculate distance between pointA and pointB using Great Circle 

    Parameters:
        pointA: Tuple(float, float)
        pointB: Tuple(float, float)
    Returns:
        distance: float, score
    """
    return dist.great_circle(pointA, pointB).km


def normalize_dist(arr):
    """
    Normalizing function from 0 to 1 

    Parameters:
        pointA: Tuple(float, float)
        pointB: Tuple(float, float)
    Returns:
        res: float, score
    """
    max_ = 1
    min_ = 0
    res = (arr - min_) / (max_ - min_)
    return res


def calculate_hansen_grav_score(distances, coeff=1.75, normalize=False):
    """
    Function for Calculate Hansen Gravitational Score according to explanation in the paper

    Parameters:
        distances: List[float], list of distance from the centroid to the amenity w/in study distance
        coeff: float, coefficient friction factor, normally 1.75, but 2.0 is applicable to cities 
        normalize: bool, if needed to normalize
    Returns:
        row: float of scores
    """
    if len(distances) == 0:
        return 0

    distances = np.array(distances)
    if normalize:
        scores = normalize_dist(distances)

    scores = scores ** coeff
    scores = [float(1)/float(x) for x in scores]
    return np.sum(scores)


def get_accessibility_score(row, amenities_tuples, max_study_area, normalize):
    """
    Function for DataFrame to calculate score per row

    Parameters:
        row: DataFrame Row
        amenities_tuples: List[Tuple],  contains array of tuples of lat and long of amenities
        max_study_area: float, maximum study area from the centroid point, in KM
        normalize_scores: bool, if needed to normalize
    Returns:
        row: DataFrame Row, with new columns
    """
    lat = row['lat']
    lon = row['lon']

    distances = []
    for i in range(len(amenities_tuples)):
        pointA = (lat, lon)
        pointB = amenities_tuples[i]

        distance = get_distance_in_km_gc(pointA, pointB)
        if distance <= max_study_area:
            distances.append(distance)
  
    accessibility_score = calculate_hansen_grav_score(
        distances, normalize=normalize)
    row['num_amenities'] = len(distances)
    row['ave_amenity_distance'] = np.mean(distances) if len(distances) > 0 else 0
    row['accessibility_score'] = accessibility_score
    return row


def get_amenities_tuples(amenities_df):
    """
    Parameters:
        amenities_df: DataFrame, contains amenities data from CSV
    Returns:
        amenities_tuples: List[Tuple], contains array of tuples of lat and long of amenities
    """
    amenities_lon = amenities_df['lon'].to_list()
    amenities_lat = amenities_df['lat'].to_list()
    
    amenities_tuples = [(amenities_lat[i], amenities_lon[i]) for i in range(len(amenities_lon))]
    return amenities_tuples


def compute_accessibility_score(
        amenities_file, centroids_file, 
        normalize=True, max_study_area=10, 
        output_file='scores.csv'):
    
    # Read files
    amenities_df = pd.read_csv(amenities_file)
    centroids_df = pd.read_csv(centroids_file)
    
    # Get amenities tuples
    amenities_tuples = get_amenities_tuples(amenities_df)
    
    # Calculate Amenity scores
    print("Calculating amenity scores...")
    
    # Multi-Process vs Single-Core Process
    if PANDAS_MP:
        amenity_scores_df = centroids_df.apply(
        get_accessibility_score, axis=1, 
        args=(amenities_tuples, max_study_area, normalize))
    else:
        amenity_scores_df = centroids_df.progress_apply(
            get_accessibility_score, axis=1, 
            args=(amenities_tuples, max_study_area, normalize))
    
    amenity_scores_df.to_csv(output_file, index=False)
    print(f"Saved file to {output_file}")
    
    if PANDAS_MP:
        ray.shutdown()
    

if __name__ == "__main__":
    fire.Fire(compute_accessibility_score)