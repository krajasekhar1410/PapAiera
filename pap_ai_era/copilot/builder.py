import os
import re
import pickle
import logging
from typing import List, Dict

try:
    from pypdf import PdfReader
    from rank_bm25 import BM25Okapi
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    logging.warning("Optional dependencies for Copilot are not installed. Run `pip install pypdf rank_bm25 nltk`")

logger = logging.getLogger(__name__)

class KnowledgeBuilder:
    """Builds a lightweight BM25 search index from a PDF handbook."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.index_path = os.path.join(self.data_dir, 'bm25_index.pkl')
        self.corpus_path = os.path.join(self.data_dir, 'corpus.pkl')

        try:
            nltk.data.find('tokenizers/punkt_tab')
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt_tab')
            nltk.download('punkt')
            nltk.download('stopwords')
            
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text: str) -> str:
        """Removes excessive whitespace and unprintable chars."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def tokenize(self, text: str) -> List[str]:
        """Tokenize and stem text for BM25."""
        tokens = word_tokenize(text.lower())
        # Remove punctuation and stopwords
        tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        return tokens

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def build_from_pdf(self, pdf_path: str):
        """Reads the PDF, chunks it, and builds the BM25 index."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        print(f"Reading PDF from {pdf_path}...")
        reader = PdfReader(pdf_path)
        
        corpus_chunks = []
        metadata = []

        # We will parse page by page
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            
            clean = self.clean_text(text)
            chunks = self.chunk_text(clean)
            
            for chunk in chunks:
                if len(chunk) > 50: # Only keep meaningful chunks
                    corpus_chunks.append(chunk)
                    metadata.append({"page": i + 1})

            if i % 50 == 0:
                print(f"Processed {i} pages...")

        print(f"Total chunks extracted: {len(corpus_chunks)}")
        
        print("Tokenizing corpus...")
        tokenized_corpus = [self.tokenize(doc) for doc in corpus_chunks]

        print("Building BM25 Index...")
        bm25 = BM25Okapi(tokenized_corpus)

        print("Saving index to disk...")
        with open(self.index_path, 'wb') as f:
            pickle.dump(bm25, f)
            
        with open(self.corpus_path, 'wb') as f:
            pickle.dump({"chunks": corpus_chunks, "metadata": metadata}, f)

        print(f"Knowledge Base built successfully in {self.data_dir}")

if __name__ == "__main__":
    # Script to build the index locally
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    pdf_file = os.path.join(base_dir, 'docs', 'epdf.pub_handbook-of-pulping-and-papermaking-second-edition.pdf')
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    builder = KnowledgeBuilder(data_dir=data_dir)
    builder.build_from_pdf(pdf_file)
