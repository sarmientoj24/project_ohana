# project_ohana
An Open Source Tool for Visualizing Amenity Accessibility Data in the Philippines

# Setup Environment
1. Clone repository  
  `git clone https://github.com/sarmientoj24/project_ohana.git`
2. Install requirements.txt  
  `pip install -r requirements.txt`

# Data Processing Scripts

- `scripts/download_amenities.py`  
  Download amenities data for the given amenity type from OpenStreetMap into a single CSV file
  
  Sample Usage: 
  ```
  python scripts/download_amenities.py --amenity_type=hospital --origin_x=14.6786 --origin_y=121.0453 --radius=10000
  ```
  
- `scripts/merge_all_amenities.py`  
  Merge all CSV files containing amenities data extracted from `download_amenities.py`
  
  Sample Usage: 
  ```
  python scripts/merge_all_amenities.py --amenities_files=hospital.csv,clinic.csv,police.csv --filename=amenities.csv
  ```
  
- `scripts/compute_accessibility_score.py`  
  Calculates amenity accessibility score for each centroid (from a CSV file of centroids data) with all amenities within a maximum study distance
  
  Sample Usage: 
  ```
  python scripts/compute_accessibility_score.py --amenities_file=amenities.csv --centroids_file=centroids.csv --normalize=True --max_study_area=10 --output_file=scores.csv
  ```
 
 
