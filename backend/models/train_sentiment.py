import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import re

nltk.download('punkt')
nltk.download('stopwords')

class SentimentTrainer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
        self.model = LogisticRegression(random_state=42)
        
    def preprocess_text(self, text):
        """Clean and preprocess text data"""
        if pd.isna(text):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def create_sample_data(self):
        """Create sample training data for sentiment analysis"""
        positive_texts = [
            "This is amazing! I love this product.",
            "Great news! The economy is improving.",
            "Fantastic article, very informative.",
            "Excellent work by the team.",
            "Wonderful news about the environment.",
            "Outstanding performance this quarter.",
            "Brilliant analysis of the situation.",
            "Superb coverage of the event.",
            "Incredible breakthrough in science.",
            "Positive developments in healthcare.",
            "Good news for investors today.",
            "Promising results from the study.",
            "Successful launch of the new product.",
            "Impressive growth in revenue.",
            "Thrilled about this announcement."
        ]
        
        negative_texts = [
            "This is terrible news.",
            "Worst article I've read today.",
            "Disappointing results from the company.",
            "Awful situation developing.",
            "Negative impact on the economy.",
            "Poor performance this quarter.",
            "Concerning developments in politics.",
            "Bad news for the environment.",
            "Unfortunate events unfolding.",
            "Crisis situation getting worse.",
            "Alarming statistics released today.",
            "Devastating impact on communities.",
            "Shocking revelations in the report.",
            "Disturbing trends emerging.",
            "Tragic outcome for the victims."
        ]
        
        neutral_texts = [
            "The weather today is cloudy.",
            "Market opened at 9:30 AM.",
            "The meeting lasted two hours.",
            "New policy announced yesterday.",
            "Quarterly report released today.",
            "The event took place downtown.",
            "Stock price remained unchanged.",
            "Conference scheduled for next week.",
            "Data shows current trends.",
            "Announcement made this morning.",
            "Report details the findings.",
            "Meeting concluded without resolution.",
            "Statistics indicate steady growth.",
            "Presentation covered key points.",
            "Analysis completed last month."
        ]
        
        # Combine data
        texts = positive_texts + negative_texts + neutral_texts
        labels = ['positive'] * len(positive_texts) + ['negative'] * len(negative_texts) + ['neutral'] * len(neutral_texts)
        
        return pd.DataFrame({'text': texts, 'sentiment': labels})
    
    def train_model(self, data=None):
        """Train the sentiment analysis model"""
        print("Training sentiment analysis model...")
        
        # Use sample data if no data provided
        if data is None:
            data = self.create_sample_data()
        
        # Preprocess text
        data['cleaned_text'] = data['text'].apply(self.preprocess_text)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            data['cleaned_text'], data['sentiment'], 
            test_size=0.2, random_state=42, stratify=data['sentiment']
        )
        
        # Vectorize text
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        # Train model
        self.model.fit(X_train_vec, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def save_model(self, model_path='sentiment_model.pkl', vectorizer_path='vectorizer.pkl'):
        """Save the trained model and vectorizer"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Model saved to {model_path}")
        print(f"Vectorizer saved to {vectorizer_path}")
    
    def load_model(self, model_path='sentiment_model.pkl', vectorizer_path='vectorizer.pkl'):
        """Load the trained model and vectorizer"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        print(f"Model loaded from {model_path}")
        print(f"Vectorizer loaded from {vectorizer_path}")
    
    def predict_sentiment(self, text):
        """Predict sentiment for new text"""
        if not hasattr(self, 'model') or not hasattr(self, 'vectorizer'):
            raise ValueError("Model not loaded. Please load model first.")
        
        cleaned_text = self.preprocess_text(text)
        text_vec = self.vectorizer.transform([cleaned_text])
        prediction = self.model.predict(text_vec)[0]
        confidence = max(self.model.predict_proba(text_vec)[0])
        
        return {
            'sentiment': prediction,
            'confidence': float(confidence)
        }

def main():
    """Main function to train and save the sentiment model"""
    trainer = SentimentTrainer()
    
    # Train model
    accuracy = trainer.train_model()
    
    # Save model
    trainer.save_model()
    
    # Test prediction
    test_text = "This is great news about the economy!"
    result = trainer.predict_sentiment(test_text)
    print(f"\nTest prediction: {result}")
    
    print(f"\nModel training completed with {accuracy:.2f} accuracy!")

if __name__ == "__main__":
    main()