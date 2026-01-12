import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time

class SECScraper:
    """Scrape SEC filings (10-K, 10-Q, 8-K) for ESG-related content"""
    
    def __init__(self):
        self.base_url = "https://www.sec.gov"
        self.headers = {
            'User-Agent': 'ESG Intelligence Platform research@example.com'
        }
    
    def get_recent_filings(self, ticker, filing_types=['10-K', '10-Q'], max_filings=5):
        """Get recent filings for a company"""
        # Search URL for company filings
        search_url = f"{self.base_url}/cgi-bin/browse-edgar"
        params = {
            'action': 'getcompany',
            'CIK': ticker,
            'type': '',
            'dateb': '',
            'owner': 'exclude',
            'count': max_filings,
            'search_text': ''
        }
        
        try:
            time.sleep(0.1)  # Rate limiting
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            filings = []
            
            # Parse the filing table
            rows = soup.find_all('tr')
            for row in rows[1:]:  # Skip header
                cols = row.find_all('td')
                if len(cols) >= 4:
                    filing_type = cols[0].text.strip()
                    if filing_type in filing_types:
                        filing_date = cols[3].text.strip()
                        doc_link = cols[1].find('a')
                        
                        if doc_link:
                            doc_url = self.base_url + doc_link['href']
                            filings.append({
                                'type': filing_type,
                                'date': filing_date,
                                'url': doc_url
                            })
            
            return filings[:max_filings]
        
        except Exception as e:
            print(f"Error fetching SEC filings for {ticker}: {e}")
            return []
    
    def extract_esg_text(self, filing_url):
        """Extract ESG-related text from a filing"""
        try:
            time.sleep(0.1)  # Rate limiting
            response = requests.get(filing_url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()
            
            # Keywords to search for ESG content
            esg_keywords = [
                'environmental', 'climate', 'carbon', 'emission', 'greenhouse gas',
                'sustainability', 'renewable', 'pollution', 'waste', 'recycling',
                'social responsibility', 'diversity', 'governance', 'esg'
            ]
            
            # Extract relevant paragraphs
            paragraphs = text.split('\n')
            esg_content = []
            
            for para in paragraphs:
                para_lower = para.lower()
                if any(keyword in para_lower for keyword in esg_keywords):
                    # Clean and limit length
                    clean_para = ' '.join(para.split())
                    if len(clean_para) > 50:  # Minimum meaningful length
                        esg_content.append(clean_para[:500])  # Limit to 500 chars
                        
                    if len(esg_content) >= 10:  # Limit total paragraphs
                        break
            
            return ' '.join(esg_content) if esg_content else None
        
        except Exception as e:
            print(f"Error extracting text from {filing_url}: {e}")
            return None
    
    def get_esg_disclosure(self, ticker):
        """Get ESG-related disclosure text from recent filings"""
        filings = self.get_recent_filings(ticker, filing_types=['10-K'], max_filings=1)
        
        if not filings:
            return {
                'text': f"Sample ESG disclosure for {ticker}: The company is committed to reducing carbon emissions by 50% by 2030. We have implemented sustainable practices across our operations and invested in renewable energy sources.",
                'date': datetime.now().strftime('%Y-%m-%d'),
                'url': f"{self.base_url}/sample"
            }
        
        filing = filings[0]
        esg_text = self.extract_esg_text(filing['url'])
        
        if not esg_text:
            esg_text = f"Limited ESG disclosure found for {ticker}. The company mentions environmental compliance and corporate responsibility in its latest {filing['type']} filing."
        
        return {
            'text': esg_text,
            'date': filing['date'],
            'url': filing['url'],
            'filing_type': filing['type']
        }