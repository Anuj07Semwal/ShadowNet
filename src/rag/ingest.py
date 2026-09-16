from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.rag.document_loader import FIRDocumentLoader
from src.rag.vector_store import CNASPineconeStore
from src.rag import registry
import os
import json
import logging


# ensure registry exists
registry.init_db()


class FIRIngestor:

    def __init__(self):

        # Do not connect to Pinecone / load embeddings at object construction.
        # The store will be created in ingest() with mode='ingest'.
        self.store = None

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

    def ingest(
        self,
        path: str,
        fir_id: str
        , dry_run: bool = False
    ):

        logger = logging.getLogger("cnas.ingest")
        logger.info("%s", "=" * 70)
        logger.info("CNAS FIR PINECONE INGESTION")
        logger.info("%s", "=" * 70)

        # =====================================================
        # 1. LOAD FIR
        # =====================================================

        logger.info("[1] Loading FIR...")

        document = FIRDocumentLoader.load(path, fir_id)

        # Ensure the document has a metadata attribute for the text splitter
        if not hasattr(document, "metadata"):
            document.metadata = {}

        # compute deterministic document id and content hash
        document_id = fir_id
        content_bytes = document.page_content.encode("utf-8")
        content_hash = registry.compute_hash(content_bytes)

        existing = registry.get_document(document_id)

        if existing and existing.get("content_hash") == content_hash:
            logger.info("SKIPPED: Document %s unchanged (content hash matched)", document_id)
            # Attempt to return cached vectors if available
            cache_dir = os.path.join("data", "processed", "vectors")
            cache_path = os.path.join(cache_dir, f"{document_id}.json")
            try:
                if os.path.exists(cache_path):
                    with open(cache_path, "r", encoding="utf-8") as fh:
                        return json.load(fh)
            except Exception:
                logger.exception("Failed to read cache %s", cache_path)

            return registry.list_chunks(document_id)

        if existing:
            logger.info("RE-EMBEDDED: Document %s changed — reprocessing", document_id)


        logger.info("✓ FIR loaded: %s", fir_id)
        logger.info("✓ Characters: %s", f"{len(document.page_content):,}")

        # =====================================================
        # 2. CHUNK DOCUMENT
        # =====================================================

        logger.info("[2] Creating chunks...")

        chunks = self.text_splitter.split_documents([document])

        logger.info("✓ Chunks created: %s", len(chunks))

        # =====================================================
        # 3. CREATE EMBEDDINGS
        # =====================================================

        logger.info("[3] Creating embeddings...")

        vectors = []
        # Initialize Pinecone store only for real ingestion.
        #Dry-run generates local embeddings without requiring Pinecone credentials.
        if not dry_run:
           self.store = CNASPineconeStore(mode="ingest")
        
        for i, chunk in enumerate(chunks):
            text = chunk.page_content
            if dry_run:
               vector = [0.0] * 1024
            else:
               vector = self.store.embeddings.embed_query(text)
            vector_id = f"{fir_id}_chunk_{i}"
            vectors.append({
                "id": vector_id,
                "values": vector,
                "metadata": {
                    "fir_id": fir_id,
                    "chunk_id": i,
                    "text": text,
                    "source": path,
                    "document_type": "FIR",
                },
            })
            # record chunk metadata to registry
            chunk_hash = registry.compute_hash(text.encode("utf-8"))
            if not dry_run:
                registry.upsert_chunk(document_id, str(i), vector_id, chunk_hash)

        logger.info("✓ Embeddings created: %s", len(vectors))

        if vectors:
            logger.info("✓ Vector dimension: %s", len(vectors[0]["values"]))

        # =====================================================
        # 4. UPLOAD TO PINECONE
        # =====================================================

        logger.info("[4] Uploading to Pinecone...")

        if dry_run:
            logger.info("DRY RUN: skipping Pinecone upsert and registry writes")
        else:
            self.store.upsert(vectors)

            # record document metadata as processed
            registry.upsert_document(document_id, content_hash, path, status="processed")

        # cache vectors locally for idempotent reads
        cache_dir = os.path.join("data", "processed", "vectors")
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{document_id}.json")
        try:
            with open(cache_path, "w", encoding="utf-8") as fh:
                json.dump(vectors, fh)
        except Exception:
            logger.exception("Failed to cache vectors to %s", cache_path)

        if dry_run:
            logger.info("DRY RUN: Document %s processed locally (%s vectors)", document_id, len(vectors))
        else:
            logger.info("PROCESSED: Document %s ingested and indexed (%s vectors)", document_id, len(vectors))
            logger.info("✓ Uploaded %s vectors", len(vectors))

        # =====================================================
        # 5. RESULT
        # =====================================================

        logger.info("\n✓ INGESTION COMPLETED")

        return vectors