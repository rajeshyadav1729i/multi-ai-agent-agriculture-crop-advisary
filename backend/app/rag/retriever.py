from typing import List, Dict, Any, Optional
from app.rag.document_loader import load_scheme_documents
from app.rag.embeddings import SimpleVectorStore

class SchemeRAGRetriever:
    _instance = None

    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self.is_indexed = False
        self.raw_documents: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SchemeRAGRetriever()
            cls._instance.initialize()
        return cls._instance

    def initialize(self):
        chunks = load_scheme_documents()
        docs = [c.to_dict() for c in chunks]
        self.raw_documents = docs
        self.vector_store.build_index(docs)
        self.is_indexed = True

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.is_indexed:
            self.initialize()
            
        results = self.vector_store.search(query, top_k=top_k)
        retrieved_items = []
        for doc, score in results:
            item = dict(doc)
            item["relevance_score"] = round(float(score), 4)
            retrieved_items.append(item)
        return retrieved_items

    def get_all_schemes_summary(self) -> List[Dict[str, Any]]:
        # Group documents by scheme_id to return clean list for Scheme library page
        if not self.is_indexed:
            self.initialize()

        schemes_dict = {}
        for doc in self.raw_documents:
            sid = doc["scheme_id"]
            if sid not in schemes_dict:
                schemes_dict[sid] = {
                    "scheme_id": sid,
                    "title": doc["title"],
                    "source": doc["source"],
                    "portal": doc["portal"],
                    "sections": {},
                    "description": ""
                }
            sec_title = doc["section"]
            schemes_dict[sid]["sections"][sec_title] = doc["content"]
            if "OBJECTIVE" in sec_title.upper() or not schemes_dict[sid]["description"]:
                schemes_dict[sid]["description"] = doc["content"]

        return list(schemes_dict.values())
