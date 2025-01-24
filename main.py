import time
from pdf_search_system import PDFDocumentIndexer, PDFSearcher
from pdf_search_system.utils import get_pdf_paths

def index_pdfs():
    """Function to index PDF documents"""
    print("Starting PDF indexing process...")
    start_time = time.time()
    
    indexer = PDFDocumentIndexer()
    
    # Only process PDFs if index is empty
    if not indexer.is_index_populated():
        # Get PDF paths
        pdf_directory = "Documents"
        pdf_paths = get_pdf_paths(pdf_directory)
        
        print(f"Found {len(pdf_paths)} PDF files in {pdf_directory}")
        
        # Process and extract documents
        documents = []
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"Processing PDF {i}/{len(pdf_paths)}: {pdf_path}")
            doc = indexer.extract_text_and_metadata(pdf_path)
            if doc:
                documents.append(doc)
            else:
                print(f"  - Failed to process {pdf_path}")
        
        # Create index and bulk index documents
        indexer.create_index_if_not_exists(documents)
        
        print(f"Indexed {len(documents)} out of {len(pdf_paths)} documents")
    else:
        print("Index is already populated. Skipping indexing.")
    
    end_time = time.time()
    print(f"Indexing process completed in {end_time - start_time:.2f} seconds")

def search_pdfs():
    """Function to demonstrate searching"""
    print("\nStarting PDF search demonstration...")
    searcher = PDFSearcher()
    
    # Define search terms
    search_terms = ["chip", "healthcare", "research"]
    
    for term in search_terms:
        print(f"\nSearching for term: '{term}'")
        
        # Basic search
        basic_results = searcher.basic_search(term)
        print(f"Basic Search Results for '{term}':")
        if not basic_results:
            print("  No results found.")
        for result in basic_results:
            print(f"  - Title: {result['_source'].get('title', 'Unknown Title')}")
        
        # Advanced search
        advanced_results = searcher.advanced_search(
            term, 
            highlight=True, 
            fields=["content", "title"],
            min_score=0.5
        )
        
        print(f"\nAdvanced Search Results for '{term}':")
        hits = advanced_results.get('hits', {}).get('hits', [])
        if not hits:
            print("  No results found.")
        
        for hit in hits:
            print(f"  - Title: {hit['_source']['title']}")
            print(f"    Score: {hit['_score']}")
            
            if 'highlight' in hit:
                print("    Highlights:")
                for field, highlights in hit['highlight'].items():
                    print(f"    - {field.capitalize()}: {highlights}")

def export_results(search_term):
    """Function to export search results to a file"""
    searcher = PDFSearcher()
    
    # Perform advanced search
    advanced_results = searcher.advanced_search(
        search_term, 
        highlight=True, 
        fields=["content", "title"],
        min_score=0.5,
        size=50  # Increase number of results
    )
    
    # Export results to a text file
    filename = f"search_results_{search_term}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Search Results for '{search_term}'\n")
        f.write("="*50 + "\n\n")
        
        hits = advanced_results.get('hits', {}).get('hits', [])
        if not hits:
            f.write("No results found.\n")
        
        for hit in hits:
            f.write(f"Title: {hit['_source']['title']}\n")
            f.write(f"Score: {hit['_score']}\n")
            
            if 'highlight' in hit:
                f.write("Highlights:\n")
                for field, highlights in hit['highlight'].items():
                    f.write(f"  - {field.capitalize()}: {highlights}\n")
            
            f.write("\n" + "-"*50 + "\n\n")
    
    print(f"Results exported to {filename}")

if __name__ == "__main__":
    # First, index the documents (will only create/index if index doesn't exist)
    index_pdfs()
    
    # Then, perform searches
    search_pdfs()
    
    # Optionally, export results for a specific term
    try:
        export_results("chip")
    except Exception as e:
        print(f"Error exporting results: {e}")