import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_csv_file(input_path, output_path):
    try:
        # Read the CSV file, skipping empty rows at the beginning
        df = pd.read_csv(input_path, skiprows=2)
        
        # Rename unnamed columns to proper names
        if 'Unnamed: 0' in df.columns:
            df = df.rename(columns={
                'Unnamed: 0': 'Place',
                'Unnamed: 1': 'Review',
                'Unnamed: 2': 'Location'
            })
        
        # Remove any remaining unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Save the cleaned CSV
        df.to_csv(output_path, index=False)
        
        logger.info(f"Successfully cleaned and saved {output_path}")
        logger.info(f"Columns: {df.columns.tolist()}")
        logger.info(f"Number of rows: {len(df)}")
        
        return df
    
    except Exception as e:
        logger.error(f"Error cleaning {input_path}: {str(e)}")
        return None

if __name__ == "__main__":
    # Clean both CSV files
    dining_df = clean_csv_file('data/Dining.csv', 'data/Dining_cleaned.csv')
    spots_df = clean_csv_file('data/Spots.csv', 'data/Spots_cleaned.csv')
    
    if dining_df is not None and spots_df is not None:
        # Display sample of cleaned data
        print("\nSample of cleaned Dining data:")
        print(dining_df.head())
        print("\nSample of cleaned Spots data:")
        print(spots_df.head()) 