from typing import Dict

ELASTICSEARCH_CONFIG = {
    "url": "http://localhost:9200",
    "index_name": "pdf_documents",
    "index_settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1
    }
}

INDEX_MAPPINGS: Dict = {
    "settings": {
        "index": {
            "highlight.max_analyzed_offset": 5000000,  # Increase max offset
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "file_name": {"type": "keyword"},
            "content": {
                "type": "text",
                "analyzer": "english",
                "index_options": "offsets",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256}
                }
            },
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword", "ignore_above": 256}
                }
            },
            "author": {"type": "keyword"},
            "creation_date": {
                "type": "date",
                "format": "strict_date_time||strict_date_optional_time||epoch_millis"
            },
            "keywords": {"type": "text"}
        }
    }
}