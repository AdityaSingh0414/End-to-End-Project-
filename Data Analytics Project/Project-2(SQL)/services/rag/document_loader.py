from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
import os

def load_document(file_path):
    """Loads a document and returns text."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
    elif ext == '.txt':
        loader = TextLoader(file_path)
    elif ext == '.csv':
        loader = CSVLoader(file_path)
    else:
        raise ValueError("Unsupported file type")
        
    return loader.load()
