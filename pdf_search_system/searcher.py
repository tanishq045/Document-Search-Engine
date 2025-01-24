from elasticsearch import Elasticsearch
from typing import List, Dict
from .config import ELASTICSEARCH_CONFIG

class PDFSearcher:
    def __init__(self, elasticsearch_url: str = None, index_name: str = None):
        self.es = Elasticsearch(elasticsearch_url or ELASTICSEARCH_CONFIG["url"])
        self.index_name = index_name or ELASTICSEARCH_CONFIG["index_name"]

    def basic_search(self, query: str) -> List[Dict]:
        """Simple content search."""
        search_query = {
            "query": {
                "match": {
                    "content": query
                }
            }
        }
        try:
            response = self.es.search(index=self.index_name, body=search_query)
            return response["hits"]["hits"]
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def advanced_search(self, 
                   query: str, 
                   fields: List[str] = None,
                   highlight: bool = True,
                   min_score: float = None,
                   size: int = 10) -> Dict:
        """Advanced search with multiple fields and highlighting."""
        if fields is None:
            fields = ["content", "title", "keywords"]

        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": fields,
                    "type": "best_fields",
                    "tie_breaker": 0.3
                }
            },
            "size": size,
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    # Limit fragment size and number of fragments
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    },
                    "title": {
                        "fragment_size": 100,
                        "number_of_fragments": 1
                    }
                }
            }
        }

        if min_score:
            search_query["min_score"] = min_score

        try:
            response = self.es.search(
                index=self.index_name, 
                body=search_query
            )
            return response
        except Exception as e:
            print(f"Search error: {str(e)}")
            return {}
    
    