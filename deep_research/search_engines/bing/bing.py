# Bing Search Retriever

# libraries
import os
from typing import Any

import requests
import json
import logging


class BingSearch:
    """
    Bing Search Retriever
    """

    def __init__(self, query):
        """
        Initializes the BingSearch object
        Args:
            query:
        """
        self.query = query
        self.api_key = self.get_api_key()
        self.logger = logging.getLogger(__name__)

    def get_api_key(self):
        """
        Gets the Bing API key
        Returns:

        """
        try:
            api_key = os.environ["BING_API_KEY"]
        except:
            raise Exception(
                "Bing API key not found. Please set the BING_API_KEY environment variable.")
        return api_key

    async def search(self, max_results=7) -> list[Any] | list[dict[str, Any]]:
        """
        Searches the query
        Returns:

        """
        print("Searching with query {0}...".format(self.query))
        """Useful for general internet search queries using the Bing API."""

        # Search the query
        url = "https://api.bing.microsoft.com/v7.0/search"

        headers = {
            'Ocp-Apim-Subscription-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        params = {
            "responseFilter": "Webpages",
            "q": self.query,
            "count": max_results,
            "setLang": "en-GB",
            "textDecorations": False,
            "textFormat": "HTML",
            "safeSearch": "Strict"
        }

        try:

            resp = requests.get(url, headers=headers, params=params)


            if resp is None:
                return []

            search_results = json.loads(resp.text)
            error = search_results.get("error", None)
            if error:
                raise Exception(error)
            results = search_results["webPages"]["value"]
        except Exception as e:
            self.logger.error(
                f"Error parsing Bing search results: {e}. Resulting in empty response.")
            return []
        if search_results is None:
            self.logger.warning(f"No search results found for query: {self.query}")
            return []

        search_results = []

        # Normalize the results to match the format of the other search APIs
        for result in results:
            # skip youtube results
            if "youtube.com" in result["url"]:
                continue
            search_result = {
                "title": result["name"],
                "href": result["url"],
                "body": result["snippet"],
            }
            search_results.append(search_result)

        return search_results
