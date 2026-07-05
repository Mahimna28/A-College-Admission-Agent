"""
rag_engine.py — Simple RAG for College Admission Agent
Uses in-memory vector store (upgrade to ChromaDB/PostgreSQL for production)
"""
import os
import json
from typing import List, Dict
import numpy as np

# Simple in-memory document store (replace with real DB in production)
_DOCUMENTS: List[Dict] = []
_EMBEDDINGS: List[List[float]] = []

def ingest_documents(documents: List[Dict]):
    """Load documents into the RAG store.
    documents: [{"title": "...", "content": "...", "source": "..."}, ...]
    """
    global _DOCUMENTS, _EMBEDDINGS
    _DOCUMENTS = documents
    # In production, use Watsonx embeddings API here
    # For now, use simple keyword-based matching as fallback
    _EMBEDDINGS = []  # placeholder for real embeddings

def retrieve_context(query: str, top_k: int = 3) -> str:
    """Retrieve relevant documents for a query."""
    if not _DOCUMENTS:
        return ""
    
    query_lower = query.lower()
    scores = []
    for doc in _DOCUMENTS:
        content = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
        # Simple keyword overlap scoring
        score = sum(1 for word in query_lower.split() if len(word) > 3 and word in content)
        scores.append((score, doc))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    top_docs = [doc for _, doc in scores[:top_k]]
    
    if not top_docs or scores[0][0] == 0:
        return ""
    
    context_parts = []
    for doc in top_docs:
        context_parts.append(f"--- From {doc.get('source', 'Official Document')} ---\n{doc.get('content', '')}")
    
    return "\n\n".join(context_parts)

# Initialize with sample admission data
_SAMPLE_DOCS = [
    {
        "title": "Admission Policy 2025",
        "content": "Admission is based on JEE Main / NEET / CET scores depending on the course. Minimum 60% in 12th standard required. Reservation: 15% SC, 7.5% ST, 27% OBC, 10% EWS as per Government of India norms. Management quota seats available at 15% higher fees.",
        "source": "Admission Brochure"
    },
    {
        "title": "B.Tech CSE Eligibility",
        "content": "B.Tech CSE requires JEE Main score of 120+ and 75% in 12th (Physics, Chemistry, Maths). Fees: ₹2,50,000/year. Scholarship available for JEE Main 180+ scorers.",
        "source": "Course Catalogue"
    },
    {
        "title": "Scholarship Information",
        "content": "Merit scholarships: 100% fee waiver for JEE Main 250+, 50% for 200+. State scholarships available for SC/ST students. Apply before July 15.",
        "source": "Financial Aid Office"
    },
    {
        "title": "Document Checklist",
        "content": "Required: 1) 10th Marksheet, 2) 12th Marksheet, 3) Entrance Exam Scorecard, 4) Caste Certificate (if applicable), 5) Domicile Certificate, 6) Aadhaar Card, 7) Passport Photos, 8) Application Fee Receipt (₹1,500).",
        "source": "Admissions Office"
    },
    {
        "title": "Reservation & Quota",
        "content": "All India Quota: 15%. State Quota: 85% for state residents. Management Quota: 15% of total seats. NRI quota available for some courses. Verify category certificates at document verification.",
        "source": "Government Guidelines"
    },
]

ingest_documents(_SAMPLE_DOCS)