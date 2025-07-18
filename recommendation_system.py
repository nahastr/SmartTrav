# recommendation_system.py
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TourismRecommender:
    def __init__(self, dining_df, spots_df, sentiment_analyzer):
        """Initialize with separate dataframes for dining and spots"""
        try:
            logger.info("Initializing TourismRecommender...")
            logger.info(f"Dining DataFrame shape: {dining_df.shape}")
            logger.info(f"Spots DataFrame shape: {spots_df.shape}")
            
            self.dining_df = self._clean_dataframe(dining_df)
            self.spots_df = self._clean_dataframe(spots_df)
            self.sentiment_analyzer = sentiment_analyzer
            
            # Process both dataframes
            self.dining_df = self._process_dataframe(self.dining_df, 'dining')
            self.spots_df = self._process_dataframe(self.spots_df, 'spot')
            
            logger.info("TourismRecommender initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TourismRecommender: {str(e)}")
            raise

    def _clean_dataframe(self, df):
        """Clean and prepare dataframe"""
        try:
            logger.info(f"Original DataFrame columns: {df.columns.tolist()}")
            
            # Remove any unnamed columns
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            
            # Map common column names to standard names
            column_mapping = {
                'name': 'Place',
                'place_name': 'Place',
                'place': 'Place',
                'location': 'Location',
                'city': 'Location',
                'address': 'Location',
                'review': 'Review',
                'reviews': 'Review',
                'comment': 'Review'
            }
            
            # Convert column names to lowercase for case-insensitive mapping
            df.columns = df.columns.str.lower().str.strip()
            
            # Rename columns based on mapping
            df = df.rename(columns=column_mapping)
            
            logger.info(f"Mapped DataFrame columns: {df.columns.tolist()}")
            
            # Check required columns
            required_columns = ['Place', 'Location', 'Review']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                # Try to identify suitable columns for missing ones
                for missing_col in missing_columns:
                    if missing_col == 'Place':
                        # Look for any column containing 'name' or 'place'
                        possible_cols = [col for col in df.columns if 'name' in col or 'place' in col]
                        if possible_cols:
                            df[missing_col] = df[possible_cols[0]]
                    elif missing_col == 'Location':
                        # Look for any column containing 'city', 'location', or 'address'
                        possible_cols = [col for col in df.columns if 'city' in col or 'location' in col or 'address' in col]
                        if possible_cols:
                            df[missing_col] = df[possible_cols[0]]
                    elif missing_col == 'Review':
                        # Look for any column containing 'review', 'comment', or 'feedback'
                        possible_cols = [col for col in df.columns if 'review' in col or 'comment' in col or 'feedback' in col]
                        if possible_cols:
                            df[missing_col] = df[possible_cols[0]]
            
            # Verify required columns exist after mapping
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Required columns still missing after mapping: {missing_columns}")
            
            # Fill NaN values
            df['Review'] = df['Review'].fillna("No review available")
            df['Location'] = df['Location'].fillna("Unknown")
            df['Place'] = df['Place'].fillna("Unknown Place")
            
            # Standardize location names (convert to lowercase)
            df['Location'] = df['Location'].str.lower().str.strip()
            
            logger.info(f"Final DataFrame columns: {df.columns.tolist()}")
            logger.info(f"Sample data:\n{df.head()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning dataframe: {str(e)}")
            raise

    def _process_dataframe(self, df, category):
        """Process dataframe to add sentiment scores and type"""
        try:
            logger.debug(f"Processing {category} dataframe with columns: {df.columns.tolist()}")
            
            # Get top places based on sentiment analysis
            top_places = self.sentiment_analyzer.analyze_reviews(df)
            
            # Create a set of top place names for filtering
            top_place_names = {place['name'] for place in top_places}
            
            # Filter dataframe to include only top places
            df_filtered = df[df['Place'].isin(top_place_names)].copy()
            
            # Add sentiment scores and category type
            for place in top_places:
                mask = df_filtered['Place'] == place['name']
                df_filtered.loc[mask, 'sentiment_score'] = place['sentiment_score']
            
            df_filtered['type'] = category
            
            logger.info(f"Processed {category} dataframe successfully")
            return df_filtered
            
        except Exception as e:
            logger.error(f"Error processing {category} dataframe: {str(e)}")
            raise

    def get_recommendations(self, search_location, top_n=3):
        """Get recommendations based on location and sentiment scores"""
        try:
            # Standardize search location
            search_location = search_location.lower().strip()
            logger.info(f"Getting recommendations for location: {search_location}")
            
            # Debug location matching
            logger.debug(f"Available locations in spots: {self.spots_df['Location'].unique()}")
            logger.debug(f"Available locations in dining: {self.dining_df['Location'].unique()}")
            
            # Filter places by location
            tourist_places_df = self.spots_df[self.spots_df['Location'] == search_location]
            dining_spots_df = self.dining_df[self.dining_df['Location'] == search_location]
            
            logger.info(f"Found {len(tourist_places_df)} tourist places and {len(dining_spots_df)} dining spots")
            
            tourist_places = self._get_top_recommendations(tourist_places_df, top_n)
            dining_spots = self._get_top_recommendations(dining_spots_df, top_n)
            
            recommendations = {
                'tourist_places': tourist_places,
                'dining_spots': dining_spots
            }

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {'tourist_places': [], 'dining_spots': []}

    def _get_top_recommendations(self, df, top_n):
        """Get top recommendations from a dataframe based on sentiment scores"""
        recommendations = []
        seen_places = set()  # Track seen places
        
        try:
            # Group by Place and calculate average sentiment score
            place_groups = df.groupby('Place').agg({
                'sentiment_score': 'mean',
                'Location': 'first',
                'Review': 'first'
            }).reset_index()
            
            # Sort by sentiment score
            place_groups = place_groups.sort_values('sentiment_score', ascending=False)
            
            # Get unique recommendations
            for _, row in place_groups.iterrows():
                place_name = row['Place']
                
                # Skip if we've already seen this place
                if place_name in seen_places:
                    continue
                    
                recommendations.append({
                    'name': place_name,
                    'location': row['Location'],
                    'sentiment_score': row['sentiment_score'],
                    'review': row['Review'] if pd.notnull(row['Review']) else "No review available"
                })
                
                seen_places.add(place_name)
                
                # Break if we have enough unique recommendations
                if len(recommendations) >= top_n:
                    break
                
            # If we don't have enough recommendations, try to get more with lower scores
            if len(recommendations) < top_n:
                remaining_places = df[~df['Place'].isin(seen_places)].drop_duplicates('Place')
                for _, row in remaining_places.iterrows():
                    if len(recommendations) >= top_n:
                        break
                        
                    recommendations.append({
                        'name': row['Place'],
                        'location': row['Location'],
                        'sentiment_score': row.get('sentiment_score', 0.5),
                        'review': row['Review'] if pd.notnull(row['Review']) else "No review available"
                    })
                    seen_places.add(row['Place'])
                    
        except Exception as e:
            logger.error(f"Error getting top recommendations: {str(e)}")
            
        return recommendations[:top_n]  # Ensure we return exactly top_n recommendations

    def format_recommendations(self, recommendations):
        """Format recommendations for API response"""
        return [{
            'name': rec['name'],
            'location': rec['location'].title(),  # Capitalize location name
            'sentiment_score': round(rec['sentiment_score'], 2),  # Round to 2 decimal places
            'rating': self._sentiment_to_rating(rec['sentiment_score']),  # Convert sentiment to rating
            'sample_review': rec['review']
        } for rec in recommendations]

    def _sentiment_to_rating(self, sentiment_score):
        """Convert sentiment score to a 5-star rating"""
        # Convert sentiment score (0-1) to rating (1-5)
        rating = 1 + (sentiment_score * 4)  # This ensures minimum rating is 1 and maximum is 5
        return round(rating, 1)