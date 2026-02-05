from transformers import AutoTokenizer, AutoModel
import App.Config.Config as config
import torch
import chromadb
import numpy as np
from chromadb.utils import embedding_functions


class Rag:
    
    def __init__(self, tokenizer=config.TOKENIZER, collection_name: str = "", 
                 model=config.RAG_MODEL, chroma_path=config.CHROMA_PATH):
        
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer)
        self.model = AutoModel.from_pretrained(model)
        self.model.eval()

        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model)
        )


    def get_embeddings(self, text: str) -> np.ndarray:

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)

        cls_embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        return cls_embedding
    

    def add_example(self, title: str, description: str, code: str, theme: list):
        text = f"{title}\n{description}\n{code}"
        self.collection.add(
            documents=[text],
            ids=[title],
            metadatas=[{"title": title, "description": description, "theme": theme}],
            embeddings=self.get_embeddings(code)
        )


    def delete_example(self, title: str):
        self.collection.delete(ids=[title])


    def delete_collection(self, name: str):
        self.client.delete_collection(name=name)


    def get_examples(self, query: str, relatives: int = 3):

        resultados = self.collection.query(
            query_texts=[query],
            n_results=relatives
        )
        return resultados