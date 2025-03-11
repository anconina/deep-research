from duckduckgo_search import DDGS

class Duckduckgo:
    """
    Duckduckgo API Retriever
    """
    def __init__(self, query):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
        }
        self.ddg = DDGS(headers=headers)
        self.query = query

    async def search(self, max_results=5):
        """
        Performs the search
        :param query:
        :param max_results:
        :return:
        """
        try:


            search_response = self.ddg.text(self.query, region='wt-wt', max_results=max_results)
        except Exception as e:
            print(f"Error: {e}. Failed fetching sources. Resulting in empty response.")
            search_response = []
        return search_response