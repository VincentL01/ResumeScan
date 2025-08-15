import streamlit as st

BASE_URL = st.secrets.get("BASE_URL")

CHAT_API_KEY = st.secrets.get("OPENAI_API_KEY")
CHAT_MODEL = st.secrets.get("CHAT_MODEL")

EMBED_API_KEY = st.secrets.get("EMBED_MODEL_API_KEY")
EMBED_MODEL = st.secrets.get("EMBED_MODEL")

PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = st.secrets.get("PINECONE_INDEX_NAME")

QUESTIONS = 5
EMBEDDING_DIMENSIONS = 1536
ACCEPTABLE_SCORE_THRESHOLD = 75 # %


