from transformers import BartTokenizer, BartForConditionalGeneration
import torch
import config

class ESGSummarizer:
    """BART-based abstractive summarization for ESG insights"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading BART model on {self.device}...")
        
        self.tokenizer = BartTokenizer.from_pretrained(config.SUMMARIZATION_MODEL)
        self.model = BartForConditionalGeneration.from_pretrained(config.SUMMARIZATION_MODEL)
        self.model.to(self.device)
        self.model.eval()
    
    def generate_executive_summary(self, risk_analysis: dict, 
                                   sec_text: str, 
                                   news_samples: list) -> str:
        """
        Generate a 2-sentence executive summary explaining the risk.
        This is the "why" behind the numbers.
        """
        # Create context for summarization
        risk_level = risk_analysis['risk_level']
        greenwashing_score = risk_analysis['greenwashing_score']
        sec_sentiment = risk_analysis['sec_sentiment']
        news_sentiment = risk_analysis['news_sentiment']
        
        # Build input text for BART
        context = f"""
        Risk Analysis Summary:
        - Greenwashing Risk: {risk_level} ({greenwashing_score:.2f})
        - SEC Disclosure Sentiment: {sec_sentiment:.2f}
        - News Coverage Sentiment: {news_sentiment:.2f}
        
        SEC Claims: {sec_text[:500]}
        
        Recent News Headlines:
        {' '.join(news_samples[:5])}
        
        Generate a 2-sentence executive summary explaining why this company has {risk_level.lower()} greenwashing risk.
        """
        
        try:
            inputs = self.tokenizer(context, return_tensors='pt', 
                                   max_length=1024, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs['input_ids'],
                    max_length=150,
                    min_length=40,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
            
            summary = self.tokenizer.decode(summary_ids[0], 
                                           skip_special_tokens=True)
            
            # Ensure it's roughly 2 sentences
            sentences = summary.split('.')
            if len(sentences) > 2:
                summary = '. '.join(sentences[:2]) + '.'
            
            return summary
        
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._generate_template_summary(risk_level, 
                                                   greenwashing_score,
                                                   news_sentiment)
    
    def _generate_template_summary(self, risk_level: str, 
                                   greenwashing_score: float,
                                   news_sentiment: float) -> str:
        """Fallback template-based summary"""
        
        if risk_level == 'High':
            reason = "significant discrepancy between positive corporate disclosures and negative media coverage"
            implication = "This suggests potential greenwashing or unrealized commitments"
        elif risk_level == 'Medium':
            reason = "moderate gap between stated ESG goals and public perception"
            implication = "Further investigation into actual performance is recommended"
        else:
            reason = "alignment between corporate disclosures and media sentiment"
            implication = "The company appears to be following through on stated commitments"
        
        return f"Risk is {risk_level.lower()} due to {reason}. {implication}."
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """General purpose document summarization"""
        
        if len(text) < 100:
            return text
        
        try:
            inputs = self.tokenizer(text, return_tensors='pt',
                                   max_length=1024, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                summary_ids = self.model.generate(
                    inputs['input_ids'],
                    max_length=max_length,
                    min_length=50,
                    num_beams=4,
                    early_stopping=True
                )
            
            return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        except Exception as e:
            print(f"Error summarizing: {e}")
            # Return first N words as fallback
            words = text.split()[:100]
            return ' '.join(words) + '...'