from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List
from configs.config import EmbeddingConfig
from logger import logging

class EmbeddingManager:
    def __init__(self, model_name: str = EmbeddingConfig.embedding_model, embedding_dim: int = EmbeddingConfig.embedding_dim):
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            self.model = GoogleGenerativeAIEmbeddings(
                model=self.model_name,
                output_dimensionality=self.embedding_dim
                )
            logging.info(f"Embedding model loaded successfully. Embedding dimensions = {self.model.output_dimensionality}")
        except Exception as e:
            logging.error(f"Error loading model {self.model_name}: {e}")
            raise
    
    def create_embeddings_doc(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            raise ValueError("Model not loaded")
        if not texts:
            return []
        embeddings = self.model.embed_documents(texts)
        logging.info(f"Generated {len(embeddings)} embeddings, dimension={len(embeddings[0])}")
        return embeddings
    
    def create_embeddings_query(self, text: str) -> List[float]:
        if not self.model:
            raise ValueError("Model not loaded")
        if not text:
            return []
        embedding = self.model.embed_query(text)
        logging.info(f"Generated query embedding, dimension={len(embedding)}")
        return embedding