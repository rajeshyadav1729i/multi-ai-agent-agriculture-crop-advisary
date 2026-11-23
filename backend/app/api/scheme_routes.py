from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from app.rag.retriever import SchemeRAGRetriever

router = APIRouter(prefix="/api/schemes", tags=["Schemes"])
retriever = SchemeRAGRetriever.get_instance()

@router.get("")
async def get_all_schemes():
    schemes = retriever.get_all_schemes_summary()
    return {
        "total": len(schemes),
        "schemes": schemes
    }

@router.get("/search")
async def search_schemes(q: str = Query(..., description="Query terms for scheme search")):
    results = retriever.retrieve(q, top_k=5)
    return {
        "query": q,
        "results": results
    }
