import requests
from datetime import datetime, timedelta
import config


class NewsScraper:
    """
    Generic news scraper for company ESG-related news using NewsAPI
    """

    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(config, "NEWS_API_KEY", None)
        self.base_url = "https://newsapi.org/v2/everything"

    def _clean_company_name(self, company_name: str) -> str:
        """
        Normalize company names to improve recall in news search
        """
        suffixes = [" ltd", " limited", " inc", " corporation", " corp", " plc"]
        clean = company_name.lower()
        for s in suffixes:
            clean = clean.replace(s, "")
        return clean.title().strip()

    def get_company_news(self, ticker, company_name, days_back=30):
        """
        Fetch recent ESG-related news for a company.
        Falls back to general company news if ESG-filtered search returns nothing.
        """

        # Demo mode if API key missing
        if not self.api_key:
            return self._get_sample_news(ticker, company_name)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        clean_name = self._clean_company_name(company_name)

        # Primary ESG-focused query
        esg_query = (
            f'("{clean_name}" OR "{company_name}" OR "{ticker}") '
            f'AND (ESG OR environmental OR sustainability OR climate '
            f'OR carbon OR emissions OR pollution OR governance OR social)'
        )

        params = {
            "q": esg_query,
            "searchIn": "title,description,content",
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": getattr(config, "MAX_NEWS_ARTICLES", 20),
            "apiKey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = self._parse_articles(data)

            # Fallback if no ESG news found
            if not articles:
                fallback_query = f'"{clean_name}" OR "{ticker}"'
                params["q"] = fallback_query

                response = requests.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                articles = self._parse_articles(data)

            return articles if articles else self._get_sample_news(ticker, company_name)

        except Exception as e:
            print(f"[NewsScraper] Error fetching news for {ticker}: {e}")
            return self._get_sample_news(ticker, company_name)

    def _parse_articles(self, data):
        """
        Normalize NewsAPI response into a clean list of articles
        """
        if data.get("status") != "ok":
            return []

        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "url": article.get("url", ""),
                "published_at": article.get("publishedAt", ""),
                "source": article.get("source", {}).get("name", ""),
                "content": article.get("content", ""),
            })
        return articles

    def _get_sample_news(self, ticker, company_name):
        """
        Sample news generator for demo/testing when API fails or key is missing
        """

        templates = {
            "positive": [
                f"{company_name} announces new sustainability initiative",
                f"{company_name} improves ESG ratings in latest report",
            ],
            "negative": [
                f"{company_name} faces regulatory scrutiny over environmental issues",
                f"Concerns raised about {company_name}'s governance practices",
            ],
            "neutral": [
                f"{company_name} publishes annual sustainability disclosure",
                f"{company_name} discusses ESG roadmap with investors",
            ],
        }

        now = datetime.utcnow()
        articles = []

        for i, (sentiment, titles) in enumerate(templates.items()):
            for j, title in enumerate(titles):
                articles.append({
                    "title": title,
                    "description": f"News related to {company_name}'s ESG and corporate responsibility.",
                    "url": f"https://example.com/{ticker.lower()}-{sentiment}-{j}",
                    "published_at": (now - timedelta(days=i * 7 + j)).isoformat(),
                    "source": ["Reuters", "Bloomberg", "Financial Times"][j % 3],
                    "content": f"{title}. Detailed article content goes here.",
                })

        return articles
