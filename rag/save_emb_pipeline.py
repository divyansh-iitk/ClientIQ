from rag.data_prep.load_data import get_tickets
from rag.vector_store.embeddings import EmbeddingManager
from rag.vector_store.save_embeddings import save_embeddings
import time
import os
from dotenv import load_dotenv
load_dotenv()


ticket_data = get_tickets()

texts = [ticket["text"] for ticket in ticket_data]

embedding_manager = EmbeddingManager()

def insert_embeddings(txt: list[str], ticket_data: list) -> None:
    
    l = 700

    batch_size = 100

    while l < len(ticket_data):

        r = min(l + batch_size, len(ticket_data))

        embeddings = embedding_manager.create_embeddings_doc(txt[l:r])
        print(f"Generated {r} embeddings")

        save_embeddings(ticket_data[l:r], embeddings)
        print(f"Saved {r} embeddings")
        
        if r < len(ticket_data):
            time.sleep(60)

        l = r
        


if __name__=="__main__":
    insert_embeddings(texts, ticket_data)