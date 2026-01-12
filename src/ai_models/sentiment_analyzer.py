from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from typing import List, Dict
import config

class SentimentAnalyzer:
    """FinBERT-based sentiment analyzer for financial text"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading FinBERT model on {self.device}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(config.SENTIMENT_MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(config.SENTIMENT_MODEL)
        self.model.to(self.device)
        self.model.eval()
        
        # FinBERT labels: positive, negative, neutral
        self.labels = ['positive', 'negative', 'neutral']
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of a single text"""
        if not text or len(text.strip()) < 10:
            return {'score': 0.0, 'label': 'neutral', 'confidence': 0.0}
        
        # Truncate to model's max length
        inputs = self.tokenizer(text, return_tensors='pt', 
                               truncation=True, max_length=512,
                               padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get predicted class and confidence
        probs = predictions[0].cpu().numpy()
        pred_idx = np.argmax(probs)
        label = self.labels[pred_idx]
        confidence = float(probs[pred_idx])
        
        # Convert to sentiment score (-1 to +1)
        # positive = +1, neutral = 0, negative = -1
        sentiment_scores = {'positive': 1.0, 'neutral': 0.0, 'negative': -1.0}
        score = sentiment_scores[label] * confidence
        
        return {
            'score': score,
            'label': label,
            'confidence': confidence,
            'probabilities': {
                'positive': float(probs[0]),
                'negative': float(probs[1]),
                'neutral': float(probs[2])
            }
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment of multiple texts"""
        return [self.analyze_text(text) for text in texts]
    
    def calculate_aggregate_sentiment(self, texts: List[str]) -> float:
        """Calculate average sentiment across multiple texts"""
        if not texts:
            return 0.0
        
        results = self.analyze_batch(texts)
        scores = [r['score'] for r in results]
        return float(np.mean(scores))
    
    def calculate_sentiment_delta(self, sec_text: str, news_titles: List[str]) -> Dict:
        """
        Calculate the sentiment delta between SEC disclosures and news coverage.
        This is the core "greenwashing detection" mechanism.
        """
        # Analyze SEC filing sentiment
        sec_result = self.analyze_text(sec_text)
        sec_sentiment = sec_result['score']
        
        # Analyze news sentiment
        news_sentiment = self.calculate_aggregate_sentiment(news_titles)
        
        # Calculate delta (positive delta = potential greenwashing)
        # If SEC is positive but news is negative, that's suspicious
        sentiment_delta = sec_sentiment - news_sentiment
        
        # Calculate greenwashing risk score (0 to 1)
        # High risk = SEC says good things, news says bad things
        greenwashing_score = max(0, sentiment_delta) / 2  # Normalize to 0-1
        
        # Determine risk level
        if greenwashing_score < config.RISK_THRESHOLDS['low']:
            risk_level = 'Low'
        elif greenwashing_score < config.RISK_THRESHOLDS['medium']:
            risk_level = 'Medium'
        else:
            risk_level = 'High'
        
        return {
            'sec_sentiment': sec_sentiment,
            'news_sentiment': news_sentiment,
            'sentiment_delta': sentiment_delta,
            'greenwashing_score': greenwashing_score,
            'risk_level': risk_level,
            'sec_details': sec_result,
            'news_count': len(news_titles)
        }