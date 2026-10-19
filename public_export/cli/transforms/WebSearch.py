from maltego_trx.entities import URL, Phrase
from maltego_trx.transform import DiscoverableTransform
from ddgs import DDGS

class WebSearch(DiscoverableTransform):
    """
    Searches DuckDuckGo for a keyword and returns the top URLs.
    """

    @classmethod
    def create_entities(cls, request, response):
        query = request.Value
        
        try:
            results = DDGS().text(query, max_results=3)
            if not results:
                response.addUIMessage("No results found.")
                return

            for res in results:
                title = res.get('title', 'Unknown Title')
                href = res.get('href', '')
                body = res.get('body', '')
                
                if href:
                    url_entity = response.addEntity(URL, href)
                    url_entity.addProperty("title", "Title", "strict", title)
                    url_entity.addProperty("snippet", "Snippet", "strict", body)
                    
        except Exception as e:
            response.addUIMessage(f"Search failed: {str(e)}")
