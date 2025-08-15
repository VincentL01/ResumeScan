import streamlit as st
from typing import List
import numpy as np
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from app.configs import EMBED_API_KEY, BASE_URL, EMBED_MODEL, PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_DIMENSIONS


class VectorStore:
    def __init__(self, index_name: str = None):
        self.pc_client = self.__init_pinecone()
        self.embed_client = self.__get_embed_client()
        if index_name:
            self.index_name = index_name
        else:
            self.index_name = PINECONE_INDEX_NAME
    
    def __init_pinecone(self):
        if not PINECONE_API_KEY:
            raise ValueError("Pinecone API key not found in secrets.")
        
        pc = Pinecone(api_key=PINECONE_API_KEY, pool_threads=10)
        return pc

    def __get_embed_client(self):
        if not EMBED_API_KEY:
            raise ValueError("OpenAI API key not found in secrets.")
        
        client = OpenAI(api_key=EMBED_API_KEY, base_url=BASE_URL)
        return client

    def get_embedding(self, text: str) -> List[float]:
        text = text.replace("\n", " ")
        return self.embed_client.embeddings.create(input = [text], model=EMBED_MODEL).data[0].embedding

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        texts = [text.replace("\n", " ") for text in texts]
        response = self.embed_client.embeddings.create(input = texts, model=EMBED_MODEL)
        return [np.array(item.embedding) for item in response.data]

    def create_index_if_not_exists(self):
        if not self.pc.has_index(self.index_name):
            self.pc.create_index(
                name=self.index_name,
                dimension=EMBEDDING_DIMENSIONS,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1",
                )
            )

    def upsert_to_pinecone(self, vectors: List[dict], namespace: str = "resumescan"):
        self.create_index_if_not_exists()
        index = self.pc.Index(self.index_name)
        index.upsert(vectors=vectors, namespace=namespace)

    def retrieve(self, query: str, top_k: int, namespace: str = "resumescan"):
        query_emb = self.get_embedding(query)
        
        retrieved_docs = []
        docs = self.pc.Index(self.index_name).query(
            vector=query_emb,
            namespace=namespace,
            include_metadata=True,
            include_values=True,
            top_k=top_k
        )
        
        for doc in docs['matches']:
            retrieved_docs.append(doc['values'])
        
        return retrieved_docs


