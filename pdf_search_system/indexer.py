import os
import re
from typing import List, Dict, Optional
from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from PyPDF2 import PdfReader
from .config import ELASTICSEARCH_CONFIG, INDEX_MAPPINGS
from .utils import get_pdf_paths, format_date

class PDFDocumentIndexer:
    def __init__(self, elasticsearch_url: str = None, index_name: str = None):
        self.es = Elasticsearch(elasticsearch_url or ELASTICSEARCH_CONFIG["url"])
        self.index_name = index_name or ELASTICSEARCH_CONFIG["index_name"]

    def extract_text_and_metadata(self, pdf_path: str) -> Optional[Dict]:
        """
        Extract text and metadata from a PDF file with improved metadata handling.
        
        Args:
            pdf_path (str): Path to the PDF file
        
        Returns:
            Optional[Dict]: Extracted document metadata and content
        """
        try:
            reader = PdfReader(pdf_path)
            
            # Extract text
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Extract metadata
            metadata = reader.metadata or {}
            
            # Try to extract title from multiple sources
            title = (
                # 1. Try getting title from metadata
                metadata.get("/Title", "") or 
                # 2. Try filename (remove extension)
                os.path.splitext(os.path.basename(pdf_path))[0] or 
                # 3. Fallback to generic title
                "Untitled Document"
            )
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Truncate very long titles
            title = title[:200] if len(title) > 200 else title
            
            # Extract author with fallback
            author = (
                metadata.get("/Author", "") or 
                "Unknown Author"
            )
            
            # Clean up author
            author = re.sub(r'\s+', ' ', author).strip()
            author = author[:100] if len(author) > 100 else author
            
            # Format creation date
            try:
                creation_date = metadata.get("/CreationDate", "")
                if creation_date.startswith("D:"):
                    # Remove "D:" prefix and parse
                    creation_date = creation_date[2:16]  # YYYYMMDDHHMMSS
                    creation_date = datetime.strptime(creation_date, "%Y%m%d%H%M%S").isoformat()
                else:
                    creation_date = datetime.now().isoformat()
            except (ValueError, TypeError):
                creation_date = datetime.now().isoformat()
            
            # Extract keywords
            keywords = metadata.get("/Keywords", "")
            keywords = re.sub(r'\s+', ' ', keywords).strip()
            
            return {
                "file_name": os.path.basename(pdf_path),
                "content": text.strip(),
                "title": title,
                "author": author,
                "creation_date": creation_date,
                "keywords": keywords
            }
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None
    

    def is_index_populated(self) -> bool:
        """
        Check if the index has already been populated with documents.
        
        Returns:
        bool: True if documents exist in the index, False otherwise
        """
        try:
            # Check total number of documents in the index
            result = self.es.count(index=self.index_name)
            return result['count'] > 0
        except Exception as e:
            print(f"Error checking index population: {str(e)}")
            return False


    def index_exists(self) -> bool:
        """
        Check if the Elasticsearch index exists.
        
        Returns:
        bool: True if index exists, False otherwise
        """
        try:
            return self.es.indices.exists(index=self.index_name)
        except Exception as e:
            print(f"Error checking index existence: {str(e)}")
            return False

    def create_index_if_not_exists(self, documents: List[Dict] = None) -> None:
        """
        Create index if it doesn't exist, with optional document indexing.
        
        Args:
        documents (List[Dict], optional): List of documents to index if creating new index
        """
        if not self.index_exists():
            self.create_index()
            print(f"Index '{self.index_name}' created successfully")
    
        # Only index documents if the index is empty
        if documents and not self.is_index_populated():
            self.bulk_index_documents(documents)
            print(f"Indexed {len(documents)} documents")
        elif self.is_index_populated():
            print("Index is already populated. Skipping indexing.")


    def create_index(self) -> None:
        """Create Elasticsearch index with mappings."""
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
        self.es.indices.create(index=self.index_name, body=INDEX_MAPPINGS)
        print(f"Index '{self.index_name}' created successfully")

    def bulk_index_documents(self, documents: list) -> None:
        """Bulk index documents into Elasticsearch."""
        actions = [
            {"_index": self.index_name, "_source": doc}
            for doc in documents
            if doc is not None
        ]
        
        if not actions:
            print("No valid documents to index")
            return

        try:
            success, failed = helpers.bulk(self.es, actions, stats_only=True)
            print(f"Successfully indexed {success} documents")
            if failed:
                print(f"Failed to index {failed} documents")
        except Exception as e:
            print(f"Bulk indexing error: {str(e)}")

    