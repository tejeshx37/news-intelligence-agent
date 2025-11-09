import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os
import nltk
from nltk.corpus import stopwords
import string
import re

nltk.download('punkt')
nltk.download('stopwords')

class FakeNewsDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=3000, stop_words='english', ngram_range=(1, 2))
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def extract_features(self, text):
        """Extract various features from text for fake news detection"""
        if pd.isna(text):
            return {
                'length': 0,
                'exclamation_count': 0,
                'question_count': 0,
                'caps_ratio': 0,
                'word_count': 0,
                'avg_word_length': 0
            }
        
        features = {}
        
        # Basic text statistics
        features['length'] = len(text)
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
        
        # Word-level features
        words = text.split()
        features['word_count'] = len(words)
        features['avg_word_length'] = np.mean([len(word) for word in words]) if words else 0
        
        return features
    
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
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def create_sample_data(self):
        """Create sample training data for fake news detection"""
        real_news = [
            "The Federal Reserve announced interest rates will remain unchanged.",
            "Local school board approves new curriculum for next academic year.",
            "City council votes to increase funding for public transportation.",
            "Weather forecast predicts sunny conditions for the weekend.",
            "New library opens downtown with expanded digital resources.",
            "Community health center receives federal grant for expansion.",
            "Local business reports steady growth in quarterly earnings.",
            "University researchers publish findings on climate change impacts.",
            "Police department implements new community policing initiative.",
            "Regional airport adds new flight destinations for travelers.",
            "Housing market shows moderate price increases this quarter.",
            "Local restaurant receives recognition for sustainability efforts.",
            "School district hires new superintendent with education background.",
            "City announces infrastructure improvements for main roads.",
            "Healthcare system introduces new patient portal system."
        ]
        
        fake_news = [
            "SHOCKING: Government hiding alien technology from public!",
            "BREAKING: Secret cure for cancer discovered but suppressed!",
            "URGENT: Mandatory microchip implants coming next month!",
            "EXCLUSIVE: Celebrity death that was completely covered up!",
            "ALERT: Dangerous chemical being added to all drinking water!",
            "SCANDAL: Politician caught in massive corruption scheme!",
            "WARNING: New virus more deadly than COVID spreading rapidly!",
            "INVESTIGATION: Schools teaching children dangerous ideologies!",
            "REVEALED: Hidden cameras found in every household appliance!",
            "CRISIS: Economy collapsing within days - prepare now!",
            "DISCOVERY: Ancient civilization proves history is wrong!",
            "EXPOSED: Mainstream media controlled by shadow government!",
            "PANIC: Food shortage will cause mass starvation next week!",
            "CONSPIRACY: Vaccines contain tracking devices!",
            "OUTRAGE: Children being taken from parents for no reason!"
        ]
        
        # Combine data
        texts = real_news + fake_news
        labels = ['real'] * len(real_news) + ['fake'] * len(fake_news)
        
        return pd.DataFrame({'text': texts, 'label': labels})
    
    def train_model(self, data=None):
        """Train the fake news detection model"""
        print("Training fake news detection model...")
        
        # Use sample data if no data provided
        if data is None:
            data = self.create_sample_data()
        
        # Preprocess text
        data['cleaned_text'] = data['text'].apply(self.preprocess_text)
        
        # Extract additional features
        feature_data = data['text'].apply(self.extract_features)
        feature_df = pd.DataFrame(feature_data.tolist())
        
        # Vectorize text
        text_features = self.vectorizer.fit_transform(data['cleaned_text'])
        
        # Combine text and statistical features
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            text_features, data['label'], 
            test_size=0.2, random_state=42, stratify=data['label']
        )
        
        X_train_stats, X_test_stats, _, _ = train_test_split(
            feature_df, data['label'], 
            test_size=0.2, random_state=42, stratify=data['label']
        )
        
        # Train model
        self.model.fit(X_train_text, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_text)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        return accuracy
    
    def save_model(self, model_path='fake_news_model.pkl', vectorizer_path='fake_vectorizer.pkl'):
        """Save the trained model and vectorizer"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"Fake news model saved to {model_path}")
        print(f"Vectorizer saved to {vectorizer_path}")
    
    def load_model(self, model_path='fake_news_model.pkl', vectorizer_path='fake_vectorizer.pkl'):
        """Load the trained model and vectorizer"""
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)
        
        print(f"Fake news model loaded from {model_path}")
        print(f"Vectorizer loaded from {vectorizer_path}")
    
    def predict_fake_news(self, text):
        """Predict if news is fake or real"""
        if not hasattr(self, 'model') or not hasattr(self, 'vectorizer'):
            raise ValueError("Model not loaded. Please load model first.")
        
        cleaned_text = self.preprocess_text(text)
        text_vec = self.vectorizer.transform([cleaned_text])
        prediction = self.model.predict(text_vec)[0]
        confidence = max(self.model.predict_proba(text_vec)[0])
        
        return {
            'prediction': prediction,
            'confidence': float(confidence),
            'is_fake': prediction == 'fake'
        }

def main():
    """Main function to train and save the fake news detection model"""
    detector = FakeNewsDetector()
    
    # Train model
    accuracy = detector.train_model()
    
    # Save model
    detector.save_model()
    
    # Test prediction
    test_text = "BREAKING: Government hiding alien technology from public!"
    result = detector.predict_fake_news(test_text)
    print(f"\nTest prediction: {result}")
    
    print(f"\nFake news detection model training completed with {accuracy:.2f} accuracy!")

if __name__ == "__main__":
    main()