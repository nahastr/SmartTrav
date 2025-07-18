from flask import Flask, request, jsonify, render_template
import pandas as pd
import logging
import traceback
from sentiment_model import SentimentAnalyzer
from recommendation_system import TourismRecommender

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global variables for models
sentiment_analyzer = None
recommender = None

def initialize_models():
    """Initialize the sentiment analyzer and recommender"""
    global sentiment_analyzer, recommender
    
    try:
        logger.info("Starting model initialization...")
        
        # Initialize sentiment analyzer
        if sentiment_analyzer is None:
            logger.info("Creating sentiment analyzer...")
            sentiment_analyzer = SentimentAnalyzer()
            logger.info("Sentiment analyzer created successfully")

        # Load CSV files
        logger.info("Loading CSV files...")
        try:
            dining_df = pd.read_csv('data/Dining_cleaned.csv')
            spots_df = pd.read_csv('data/Spots_cleaned.csv')
            
            logger.debug(f"Dining.csv columns: {dining_df.columns.tolist()}")
            logger.debug(f"Spots.csv columns: {spots_df.columns.tolist()}")
            
            logger.info(f"Loaded CSV files successfully")
            
        except Exception as e:
            logger.error(f"Error loading CSV files: {str(e)}")
            raise

        # Initialize recommender
        if recommender is None:
            logger.info("Creating recommender...")
            recommender = TourismRecommender(dining_df, spots_df, sentiment_analyzer)
            logger.info("Recommender created successfully")
        
        logger.info("Model initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during initialization: {str(e)}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        logger.info(f"Received search request: {data}")
        
        if not data or 'location' not in data:
            return jsonify({"error": "Missing location parameter"}), 400

        location = data['location'].lower().strip()  # Standardize location
        logger.info(f"Searching for location: {location}")
        
        # Initialize models if not already done
        if sentiment_analyzer is None or recommender is None:
            initialize_models()

        # Get recommendations
        recommendations = recommender.get_recommendations(location)
        logger.info(f"Raw recommendations: {recommendations}")
        
        if not recommendations['tourist_places'] and not recommendations['dining_spots']:
            logger.warning(f"No recommendations found for location: {location}")
            return jsonify({
                "places": [],
                "dining": [],
                "message": f"No places found in {location}"
            })

        # Format recommendations
        tourist_places = recommender.format_recommendations(recommendations['tourist_places'])
        dining_spots = recommender.format_recommendations(recommendations['dining_spots'])
        
        logger.info(f"Formatted tourist places: {tourist_places}")
        logger.info(f"Formatted dining spots: {dining_spots}")

        return jsonify({
            "places": tourist_places,
            "dining": dining_spots
        })

    except Exception as e:
        error_msg = f"Error processing search request: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return jsonify({
            "error": "An error occurred while processing your request",
            "details": str(e)
        }), 500

@app.route('/recommendations', methods=['GET'])
def get_recommendations():
    location = request.args.get('location')
    
    # Filter by location first
    dining_filtered = dining_df[dining_df['Location'] == location]
    spots_filtered = spots_df[spots_df['Location'] == location]
    
    # Get top 3 by sentiment score
    dining_recommendations = dining_filtered.nlargest(3, 'sentiment_score').to_dict('records')
    spots_recommendations = spots_filtered.nlargest(3, 'sentiment_score').to_dict('records')
    
    return jsonify({
        'dining': dining_recommendations,
        'spots': spots_recommendations
    })

if __name__ == '__main__':
    try:
        logger.info("Starting Flask application...")
        initialize_models()
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
