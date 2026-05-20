import os
import pickle
import logging
from typing import List, Dict, Optional
import pandas as pd

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
except ImportError:
    pass

logger = logging.getLogger(__name__)

class CopilotPapaiera:
    """
    PapAiEra Expert Advisor / Copilot.
    Uses a local BM25 knowledge index of the Handbook of Pulping and Papermaking 
    to answer technical questions and suggest operational setpoints.
    """

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
            
        self.index_path = os.path.join(self.data_dir, 'bm25_index.pkl')
        self.corpus_path = os.path.join(self.data_dir, 'corpus.pkl')

        self.bm25 = None
        self.corpus = None
        self.stop_words = None
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Loads the pre-compiled BM25 index and corpus chunks."""
        if not os.path.exists(self.index_path) or not os.path.exists(self.corpus_path):
            logger.warning("Knowledge index not found. The Copilot requires the pre-compiled knowledge base.")
            return

        with open(self.index_path, 'rb') as f:
            self.bm25 = pickle.load(f)
            
        with open(self.corpus_path, 'rb') as f:
            self.corpus = pickle.load(f)

        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()

    def _tokenize(self, text: str) -> List[str]:
        if not self.stop_words:
            # Fallback dumb tokenizer
            return text.lower().split()
        
        tokens = word_tokenize(text.lower())
        return [word for word in tokens if word.isalnum() and word not in self.stop_words]

    def search_knowledge(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        Searches the Handbook for paragraphs relevant to the query.
        Returns a list of dictionaries containing 'text' and 'metadata'.
        """
        if not self.bm25 or not self.corpus:
            raise ValueError("Knowledge base is not loaded.")

        tokenized_query = self._tokenize(query)
        # Get scores
        doc_scores = self.bm25.get_scores(tokenized_query)
        
        # Get top N indices
        top_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:top_n]
        
        results = []
        for idx in top_indices:
            if doc_scores[idx] > 0:
                results.append({
                    "text": self.corpus["chunks"][idx],
                    "metadata": self.corpus["metadata"][idx],
                    "score": doc_scores[idx]
                })
        return results

    def build_prompt(self, query: str, context_chunks: List[Dict], historian_data: Optional[pd.DataFrame] = None) -> str:
        """Constructs the prompt containing the context and the user query."""
        prompt = (
            "You are the PapAiEra Copilot, an expert in pulp and papermaking.\n"
            "You must answer the user's question STRICTLY based on the provided Knowledge Context from the Handbook of Pulping and Papermaking.\n"
            "If the context does not contain the answer, say 'I cannot find the answer in the handbook.' Do not guess.\n\n"
        )
        
        prompt += "--- KNOWLEDGE CONTEXT ---\n"
        for i, chunk in enumerate(context_chunks):
            prompt += f"[Page {chunk['metadata'].get('page', 'Unknown')}] {chunk['text']}\n\n"
            
        if historian_data is not None and not historian_data.empty:
            prompt += "--- LIVE HISTORIAN / DCS DATA ---\n"
            prompt += "The user has provided the following recent machine state averages/data:\n"
            prompt += historian_data.mean().to_string() + "\n\n"
            prompt += "Please reference this data when suggesting troubleshooting steps.\n\n"
            
        prompt += f"--- USER QUESTION ---\n{query}\n\n"
        prompt += "Expert Answer:"
        
        return prompt

    def ask_openai(self, query: str, api_key: str, historian_data: Optional[pd.DataFrame] = None, top_n: int = 5) -> str:
        """
        Full RAG pipeline using OpenAI.
        1. Searches the local handbook index.
        2. Formulates the prompt.
        3. Calls the OpenAI API to generate the final expert response.
        """
        try:
            import openai
        except ImportError:
            raise ImportError("Please install openai to use this feature: `pip install openai`")

        client = openai.OpenAI(api_key=api_key)
        
        # 1. Retrieve Context
        context = self.search_knowledge(query, top_n=top_n)
        
        # 2. Build Prompt
        prompt = self.build_prompt(query, context, historian_data)
        
        # 3. Ask LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are the PapAiEra Expert Copilot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
