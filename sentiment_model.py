import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        """Initialize the VADER sentiment analyzer"""
        try:
            # Download required NLTK data
            nltk.download('vader_lexicon', quiet=True)
            self.sia = SentimentIntensityAnalyzer()
            # Initialize dictionaries to store unique place sentiments
            self.place_sentiments = defaultdict(list)
            logger.info("Sentiment analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {str(e)}")
            raise

    def predict_sentiment(self, text, place_name=None):
        """Predict sentiment score for a given text and store by place"""
        try:
            if not isinstance(text, str):
                return 0.5  # Return neutral sentiment for non-string input
            
            # Get sentiment scores
            scores = self.sia.polarity_scores(text)
            
            # Convert compound score to range [0,1]
            normalized_score = (scores['compound'] + 1) / 2
            
            # Store sentiment score for the place if place_name is provided
            if place_name:
                self.place_sentiments[place_name].append(normalized_score)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Error predicting sentiment: {str(e)}")
            return 0.5  # Return neutral sentiment on error

    def get_top_places(self, places_dict, n=3):
        """Get top n places based on average sentiment scores"""
        try:
            # Calculate average sentiment for each place
            place_averages = {}
            for place, scores in places_dict.items():
                if scores:  # Only include places with sentiment scores
                    avg_sentiment = sum(scores) / len(scores)
                    place_averages[place] = avg_sentiment

            # Sort places by sentiment score and get top n
            sorted_places = sorted(place_averages.items(), 
                                 key=lambda x: x[1], 
                                 reverse=True)
            
            # Return top n unique places
            top_places = []
            seen_places = set()
            
            for place, score in sorted_places:
                if place not in seen_places:
                    top_places.append({
                        'name': place,
                        'sentiment_score': score
                    })
                    seen_places.add(place)
                    if len(top_places) == n:
                        break
            
            return top_places

        except Exception as e:
            logger.error(f"Error getting top places: {str(e)}")
            return []

    def reset_sentiments(self):
        """Reset stored sentiments"""
        self.place_sentiments.clear()

    def analyze_reviews(self, reviews_df):
        """Analyze multiple reviews and return top places"""
        try:
            # Reset previous sentiments
            self.reset_sentiments()
            
            # Process each review
            for _, row in reviews_df.iterrows():
                place_name = row.get('Place')
                review_text = row.get('Review')
                
                if place_name and review_text:
                    self.predict_sentiment(str(review_text), place_name)
            
            # Get top places
            return self.get_top_places(self.place_sentiments)
            
        except Exception as e:
            logger.error(f"Error analyzing reviews: {str(e)}")
            return []