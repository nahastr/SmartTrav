import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_csv_file(file_path):
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {file_path}")
        logger.info(f"Columns found: {df.columns.tolist()}")
        logger.info(f"Number of rows: {len(df)}")
        
        # Check for required columns
        required_columns = ['Place', 'Review', 'Location']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
        else:
            logger.info("All required columns present")
            
        # Check for empty values
        for col in df.columns:
            empty_count = df[col].isna().sum()
            if empty_count > 0:
                logger.warning(f"Column '{col}' has {empty_count} empty values")
                
        return df
    except Exception as e:
        logger.error(f"Error loading {file_path}: {str(e)}")
        return None

if __name__ == "__main__":
    # Validate both CSV files
    dining_df = validate_csv_file('data/Dining.csv')
    spots_df = validate_csv_file('data/Spots.csv') 