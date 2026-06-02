from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config.config import settings
import os
import pickle

class VectorStoreManager:
    def __init__(self):
        self.persist_path = os.path.join(settings.CHROMA_DB_PATH, "bm25_data.pkl")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        self.documents = self._load_documents()
        self.retriever = self._create_retriever()

    def _load_documents(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading documents: {e}")
        return []

    def _create_retriever(self):
        if not self.documents:
            return None
        return BM25Retriever.from_documents(self.documents)

    def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        new_docs = self.text_splitter.create_documents(texts, metadatas=metadatas)
        self.documents.extend(new_docs)
        
        # Re-create retriever with all documents
        self.retriever = BM25Retriever.from_documents(self.documents)
        
        # Save documents
        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        with open(self.persist_path, "wb") as f:
            pickle.dump(self.documents, f)

    def search(self, query: str, k: int = 5):
        if self.retriever is None:
            return []
        # BM25Retriever doesn't have a direct 'search' method like VectorStore
        # but we can use get_relevant_documents
        docs = self.retriever.invoke(query)
        return docs[:k]

    def get_retriever(self):
        return self.retriever

vector_store_manager = VectorStoreManager()
