import pandas as pd
import fire


def merge_all_amenities(amenities_files, filename='amenities.csv'):
    amenities_files = amenities_files.split(',')
    
    amenities_df = pd.concat([pd.read_csv(file) for file in amenities_files])
    amenities_df.to_csv(filename, index=False)
    print(f'Merged all files to {filename}...')
    

if __name__ == "__main__":
    fire.Fire(merge_all_amenities)