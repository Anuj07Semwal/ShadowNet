
from pinecone import Pinecone
from langchain_huggingface import HuggingFaceEmbeddings
from src.config import settings


class CNASPineconeStore:

    INDEX_NAME = "cnas-fir-index"
    EXPECTED_DIMENSION = 1024

    def __init__(self, mode: str = "query"):
        """
        mode: 'query' (default) or 'ingest'.
        In 'query' mode we only connect to Pinecone index and DO NOT load embedding models.
        In 'ingest' mode we load embedding models to create vectors.
        """

        self.mode = mode

        api_key = settings.pinecone_api_key

        if not api_key:
            raise ValueError("PINECONE_API_KEY is missing")

        # Connect Pinecone client (lightweight)
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(self.INDEX_NAME)

        print(f"✓ Pinecone index connected: {self.INDEX_NAME}")

        # Embedding model is only required when ingesting
        self.embeddings = None

        if self.mode == "ingest":
            if not settings.allow_runtime_embeddings:
                print("[WARNING] Loading embeddings for ingest; ensure this runs offline")

            print("[Embeddings] Loading model: BAAI/bge-m3")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-m3",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

            print("✓ Embedding model loaded")

            # Verify dimension
            test_vector = self.embeddings.embed_query("CNAS FIR investigation")
            dimension = len(test_vector)
            print(f"✓ Embedding dimension: {dimension}")
            if dimension != self.EXPECTED_DIMENSION:
                raise ValueError(f"Expected embedding dimension {self.EXPECTED_DIMENSION}, got {dimension}")

    # =========================================================
    # UPSERT
    # =========================================================

    def upsert(self, vectors):
        if not vectors:
            return
        self.index.upsert(vectors=vectors)

    # =========================================================
    # QUERY
    # =========================================================

    def query(self, query_vector, top_k=5, fir_id=None):
        kwargs = {"vector": query_vector, "top_k": top_k, "include_metadata": True}
        if fir_id:
            kwargs["filter"] = {"fir_id": {"$eq": fir_id}}
        response = self.index.query(**kwargs)
        return response.matches