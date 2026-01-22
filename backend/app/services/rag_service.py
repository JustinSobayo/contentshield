import os
import logging
from typing import List, Optional
from app.core.config import settings
import google.generativeai as genai

# CRITICAL: Configure API key for the underlying library
if settings.GEMINI_API_KEY:
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    genai.configure(api_key=settings.GEMINI_API_KEY)

import chromadb
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.llms.gemini import Gemini

logger = logging.getLogger(__name__)

# Configure LlamaIndex to use Gemini
embed_model = GeminiEmbedding(
    model_name="models/embedding-001", api_key=settings.GEMINI_API_KEY
)
Settings.embed_model = embed_model
Settings.llm = Gemini(model="models/gemini-flash-latest", api_key=settings.GEMINI_API_KEY)

class RAGService:
    def __init__(self, persist_dir: Optional[str] = None, data_dir: Optional[str] = None):
        # Default to paths relative to the backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.persist_dir = persist_dir or os.path.join(backend_dir, "chroma_db")
        self.data_dir = data_dir or os.path.join(backend_dir, "policy_docs")
        
        logger.info(f"RAG Service initializing with persist_dir: {self.persist_dir} and data_dir: {self.data_dir}")
        
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.chroma_collection = self.client.get_or_create_collection("policy_violations")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.index = None
        self._initialize_index()

    def _initialize_index(self):
        """Initializes the index from storage or builds it if it doesn't exist."""
        try:
            count = self.chroma_collection.count()
            if count > 0:
                logger.info(f"Loading existing index from ChromaDB ({count} documents)...")
                self.index = VectorStoreIndex.from_vector_store(
                    self.vector_store, storage_context=self.storage_context
                )
            else:
                logger.info("Index is empty. Building new index...")
                self.ingest_documents()
        except Exception as e:
            logger.error(f"Failed to initialize RAG index: {str(e)}")
            self.index = None

    def ingest_documents(self):
        """Ingests documents from the policy_docs directory."""
        if not os.path.exists(self.data_dir):
            logger.error(f"Data directory {self.data_dir} does not exist.")
            return

        try:
            logger.info(f"Loading documents from {self.data_dir}...")
            reader = SimpleDirectoryReader(input_dir=self.data_dir)
            documents = reader.load_data()
            
            if not documents:
                logger.warning("No documents found to ingest.")
                return

            logger.info(f"Starting ingestion of {len(documents)} documents. This may take a while due to Gemini API rate limits.")
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context,
                show_progress=True
            )
            logger.info("Successfully indexed documents.")
        except Exception as e:
            logger.error(f"Failed to ingest documents: {str(e)}")
            if "429" in str(e) or "Resource exhausted" in str(e):
                logger.error("QUOTA LIMIT REACHED")

    def query(self, platform: str, query_text: str, similarity_top_k: int = 5) -> str:
        """Queries the index for relevant policy snippets."""
        # Try to re-initialize if index is missing (e.g. failed on startup)
        if not self.index:
            logger.info("RAG Index not initialized. Attempting re-initialization...")
            self._initialize_index()

        if not self.index:
            logger.warning("RAG Index STILL not initialized. Returning empty context (fallback to general knowledge).")
            return ""

        try:
            # We add the platform to the query to guide retrieval
            enhanced_query = f"Regarding {platform} policies: {query_text}"
            query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)
            response = query_engine.query(enhanced_query)
            return str(response)
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return ""

# Initialize global service instance
rag_service = RAGService()
