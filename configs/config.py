from dataclasses import asdict, dataclass



@dataclass
class EmbeddingConfig:
    embedding_model: str = "gemini-embedding-2-preview"
    embedding_dim: int = 1536
    
    
if __name__=="__main__":
    print(asdict(EmbeddingConfig()))